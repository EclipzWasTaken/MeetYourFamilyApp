import os
import sys
import random
import threading
import cv2
import customtkinter as ctk
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from PIL import Image
from moviepy import (
    AudioFileClip,
    CompositeVideoClip,
    ImageClip,
    TextClip,
    VideoFileClip,
    clips_array,
    concatenate_videoclips,
)
import threading
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Redirect standard output and error to devnull when running in windowed mode
if getattr(sys, 'frozen', False) and sys.stdout is None:
    sys.stdout = open(os.devnull, 'w')
if getattr(sys, 'frozen', False) and sys.stderr is None:
    sys.stderr = open(os.devnull, 'w')

# Get absolute path to resource, works for dev and for PyInstaller --onefile
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ASSETS_DIR = os.path.join(BASE_DIR, "assets")




def _youtube_upload_worker(self):
    try:
        SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
        secret_path = os.path.join(BASE_DIR, "client_secret.json")
        token_path = os.path.join(os.getcwd(), "token.json")

        creds = None

        # 1. Check if token.json exists (saved session)
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)

        # 2. If no valid saved credentials, open browser for user login
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(secret_path):
                    self.set_status("Error: client_secret.json missing!", "#EF4444")
                    return

                self.set_status("Opening browser for Google Login...", "#3B82F6")
                
                # Starts a local server and opens browser for login
                flow = InstalledAppFlow.from_client_secrets_file(secret_path, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save credentials for future uploads
            with open(token_path, "w") as token_file:
                token_file.write(creds.to_json())

        self.set_status("Uploading to YouTube...", "#3B82F6")

        youtube = build("youtube", "v3", credentials=creds)

        body = {
            "snippet": {
                "title": "Meet Your Family #Shorts",
                "description": "Generated with Video Studio! #Shorts",
                "tags": ["Shorts", "MeetYourFamily"],
                "categoryId": "24"
            },
            "status": {
                "privacyStatus": "private"  # 'private', 'unlisted', or 'public'
            }
        }

        media = MediaFileUpload(self.output_path, chunksize=-1, resumable=True)
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                self.set_status(f"Uploading... {progress}%", "#3B82F6")

        video_id = response.get("id")
        self.set_status(f"Uploaded! Video ID: {video_id}", "#10B981")

    except Exception as e:
        self.set_status(f"Upload Error: {err if 'err' in locals() else str(e)}", "#EF4444")

# App Configuration
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")


class OpenCVVideoPlayer(ctk.CTkFrame):
    """Crash-proof 9:16 Video Player widget using grid geometry."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.label = ctk.CTkLabel(self, text="", compound="center")
        self.label.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.cap = None
        self.is_playing = False
        self.video_path = None

    def load_and_play(self, video_path):
        if not video_path or not os.path.exists(video_path):
            return

        self.video_path = video_path

        if self.cap is not None:
            self.cap.release()

        self.cap = cv2.VideoCapture(video_path)

        if not self.cap.isOpened():
            return

        self.is_playing = True
        self.update_frame()

    def update_frame(self):
        if not self.is_playing or self.cap is None or not self.cap.isOpened():
            return

        ret, frame = self.cap.read()

        if ret:
            try:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                box_w = max(self.label.winfo_width(), 360)
                box_h = max(self.label.winfo_height(), 640)

                vid_h, vid_w, _ = frame.shape
                aspect_ratio = vid_w / max(vid_h, 1)

                target_w = int(box_h * aspect_ratio)
                target_h = box_h

                if target_w > box_w:
                    target_w = box_w
                    target_h = int(box_w / max(aspect_ratio, 0.01))

                img = Image.fromarray(frame)
                ctk_img = ctk.CTkImage(
                    light_image=img,
                    dark_image=img,
                    size=(max(target_w, 10), max(target_h, 10))
                )
                self.label.configure(image=ctk_img)

            except Exception as err:
                print(f"Frame Error: {err}")

            self.after(33, self.update_frame)
        else:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.after(33, self.update_frame)

    def toggle_play(self):
        if self.cap is None:
            return False
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.update_frame()
        return self.is_playing

    def stop(self):
        self.is_playing = False
        if self.cap:
            self.cap.release()
            self.cap = None


class FullscreenStudioApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Meet Your Family — Video Studio")

        # Set geometry first, then lock zoomed state to prevent UI collapse
        self.geometry("1280x720")
        self.after(100, lambda: self.state("zoomed"))
        self.configure(fg_color="#0F0F11")

        self.roles = [
            ("DAD", "Dad"),
            ("MOM", "Mom"),
            ("AUNT", "Aunt"),
            ("LITTLE SIS", "Little SIs"),
            ("BIG SIS", "Big Sis"),
            ("FRIEND", "Friend"),
            ("Mi Prima", "Mi Prima")
        ]

        self.role_pickers = {}
        # Saves directly next to where the .exe is running from
        self.output_path = os.path.join(os.getcwd(), "MeetYourFamily_Custom.mp4")

        self.create_layout()

    def get_asset_list(self, subfolder):
        folder_path = os.path.join(ASSETS_DIR, subfolder)
        if os.path.exists(folder_path):
            files = [f for f in os.listdir(folder_path) if not f.startswith('.')]
            return files if files else ["No assets found"]
        return ["No assets found"]

    def update_thumbnail(self, selected_file, folder_name, preview_label):
        img_path = os.path.join(ASSETS_DIR, "Images", folder_name, selected_file)
        if os.path.exists(img_path) and selected_file != "No assets found":
            try:
                pil_img = Image.open(img_path)
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(45, 45))
                preview_label.configure(image=ctk_img, text="")
                return
            except Exception:
                pass
        preview_label.configure(image=None, text="N/A")

    # 🎲 NEW: Randomize function for all cast members
    def randomize_cast(self):
        for role_label, (dropdown, folder_name, preview_lbl) in self.role_pickers.items():
            options = self.get_asset_list(f"Images/{folder_name}")
            valid_options = [opt for opt in options if opt != "No assets found"]
            
            if valid_options:
                chosen = random.choice(valid_options)
                dropdown.set(chosen)
                self.update_thumbnail(chosen, folder_name, preview_lbl)

    def create_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # -------------------------------------------------------------
        # LEFT COLUMN: CREATION DASHBOARD
        # -------------------------------------------------------------
        left_frame = ctk.CTkFrame(self, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        # Header
        header = ctk.CTkLabel(left_frame, text="🎬 Video Studio", font=("Segoe UI", 28, "bold"), text_color="#FFFFFF")
        header.pack(anchor="w", pady=(0, 10))

        # Scrollable Form Controls
        scroll_frame = ctk.CTkScrollableFrame(left_frame, fg_color="#18181B", corner_radius=15)
        scroll_frame.pack(fill="both", expand=True, pady=(0, 15))

        # 1. Cast Selection Header + 🎲 Randomize Button
        cast_header_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        cast_header_frame.pack(fill="x", pady=(10, 5), padx=10)

        ctk.CTkLabel(
            cast_header_frame, text="1. CAST SELECTION", font=("Segoe UI", 13, "bold"), text_color="#3B82F6"
        ).pack(side="left")

        # 🎲 Random Button
        random_btn = ctk.CTkButton(
            cast_header_frame, text="🎲 Randomize Cast", font=("Segoe UI", 11, "bold"),
            height=28, fg_color="#3F3F46", hover_color="#52525B", command=self.randomize_cast
        )
        random_btn.pack(side="right")

        for role_label, folder_name in self.roles:
            card = ctk.CTkFrame(scroll_frame, fg_color="#27272A", corner_radius=8)
            card.pack(fill="x", pady=4, padx=10)

            ctk.CTkLabel(card, text=role_label, font=("Segoe UI", 12, "bold"), width=100, anchor="w").pack(side="left", padx=10)

            preview_lbl = ctk.CTkLabel(card, text="", width=45, height=45)
            preview_lbl.pack(side="left", padx=5, pady=5)

            options = self.get_asset_list(f"Images/{folder_name}")
            dropdown = ctk.CTkOptionMenu(card, values=options, fg_color="#3F3F46", button_color="#52525B")
            dropdown.pack(side="right", fill="x", expand=True, padx=10, pady=8)

            dropdown.configure(command=lambda choice, f=folder_name, p=preview_lbl: self.update_thumbnail(choice, f, p))
            if options and options[0] != "No assets found":
                self.update_thumbnail(options[0], folder_name, preview_lbl)

            # Store references needed for randomization
            self.role_pickers[role_label] = (dropdown, folder_name, preview_lbl)

        # 2. Video & Audio Settings
        ctk.CTkLabel(scroll_frame, text="2. MEDIA SETTINGS", font=("Segoe UI", 13, "bold"), text_color="#3B82F6").pack(anchor="w", pady=(15, 10), padx=10)

        media_card = ctk.CTkFrame(scroll_frame, fg_color="#27272A", corner_radius=8)
        media_card.pack(fill="x", pady=4, padx=10)

        self.base_clip_menu = self.create_setting_row(media_card, "Base Clip:", self.get_asset_list("base_clips"))
        self.song_menu = self.create_setting_row(media_card, "Song:", self.get_asset_list("songs"))
        self.layout_menu = self.create_setting_row(media_card, "Layout:", ["single", "double", "quad", "hexa"])

        # Render Controls
        self.progress_bar = ctk.CTkProgressBar(left_frame, mode="indeterminate", height=6)
        self.progress_bar.pack(fill="x", pady=(0, 5))
        self.progress_bar.stop()

        self.status_label = ctk.CTkLabel(left_frame, text="Ready", font=("Segoe UI", 12), text_color="#A1A1AA")
        self.status_label.pack(pady=(0, 5))

        # Action Buttons Container
        btn_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(5, 0))

        self.render_btn = ctk.CTkButton(
            btn_frame, text="⚡ Render & Play", font=("Segoe UI", 14, "bold"), height=48,
            fg_color="#2563EB", hover_color="#1D4ED8", command=self.start_rendering
        )
        self.render_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.upload_btn = ctk.CTkButton(
            btn_frame, text="📤 Upload to YouTube", font=("Segoe UI", 14, "bold"), height=48,
            fg_color="#DC2626", hover_color="#B91C1C", command=self.upload_to_youtube
        )
        self.upload_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))

        # -------------------------------------------------------------
        # RIGHT COLUMN: EMBEDDED OPENCV PLAYER
        # -------------------------------------------------------------
        right_frame = ctk.CTkFrame(self, fg_color="#18181B", corner_radius=15)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(right_frame, text="📺 Video Preview", font=("Segoe UI", 18, "bold"), text_color="#FFFFFF").grid(row=0, column=0, sticky="w", padx=20, pady=15)

        self.video_player = OpenCVVideoPlayer(right_frame, fg_color="#000000", corner_radius=10)
        self.video_player.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 10))

        controls_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        controls_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 15))

        self.play_btn = ctk.CTkButton(controls_frame, text="⏸ Pause", width=100, command=self.toggle_play)
        self.play_btn.pack(side="left")

    def create_setting_row(self, parent, label_text, options):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=6)
        ctk.CTkLabel(row, text=label_text, width=90, anchor="w").pack(side="left")
        dropdown = ctk.CTkOptionMenu(row, values=options, fg_color="#3F3F46", button_color="#52525B")
        dropdown.pack(side="right", fill="x", expand=True)
        return dropdown

    def toggle_play(self):
        is_playing = self.video_player.toggle_play()
        self.play_btn.configure(text="⏸ Pause" if is_playing else "▶ Play")

    def start_rendering(self):
        self.render_btn.configure(state="disabled")
        self.status_label.configure(text="Rendering video... Please wait.", text_color="#3B82F6")
        self.progress_bar.start()

        thread = threading.Thread(target=self.render_video)
        thread.start()

    def create_sub_clip(self, rot_clips, video_length):
        pool = rot_clips.copy()
        if not pool or pool == ["No assets found"]:
            return None

        choice = random.choice(pool)
        sub_clip = VideoFileClip(os.path.join(ASSETS_DIR, "rot_clips", choice)).without_audio().with_duration(6).resized(height=720)

        while sub_clip.duration < video_length and pool:
            choice = random.choice(pool)
            next_clip = VideoFileClip(os.path.join(ASSETS_DIR, "rot_clips", choice)).resized(height=720).with_duration(random.randint(6, 12))
            sub_clip = concatenate_videoclips([sub_clip, next_clip], method="chain")

        return sub_clip.with_duration(video_length)

    def render_video(self):
        try:
            base_length = 5
            person_length = 3
            video_length = base_length + person_length * len(self.roles)

            base_filename = self.base_clip_menu.get()
            base_clip = VideoFileClip(os.path.join(ASSETS_DIR, "base_clips", base_filename))
            base_clip = base_clip.with_duration(base_length).resized(height=720).without_audio()

            font_path = os.path.join(BASE_DIR, "assets", "font.ttf")

            base_text = TextClip(
                text="Meet Your Family", font_size=160, color='blue', font=font_path, size=(1400, 900)
            ).with_duration(base_length).with_position(("center", 500))

            base_clip = CompositeVideoClip([base_clip, base_text])
            clips = [base_clip]

            title_img_path = os.path.join(ASSETS_DIR, "title_images", "Meet Your Family.png")
            text_clips = [ImageClip(title_img_path).with_duration(base_length).with_position(("center", "center"))]

            for role_label, (menu, folder_name, _) in self.role_pickers.items():
                selected_person_file = menu.get()

                title_png = os.path.join(ASSETS_DIR, "title_images", f"{role_label}.png")
                if os.path.exists(title_png):
                    text_clips.append(ImageClip(title_png).with_duration(person_length).with_position(("center", "center")))

                person_img_path = os.path.join(ASSETS_DIR, "Images", folder_name, selected_person_file)
                person_clip = ImageClip(person_img_path).with_duration(person_length).resized(height=720).with_position(("center", "center"))
                clips.append(person_clip)

            selected_song = self.song_menu.get()
            audio = AudioFileClip(os.path.join(ASSETS_DIR, "songs", selected_song)).with_duration(video_length)

            final_video = concatenate_videoclips(clips, method="chain")
            rot_clips = self.get_asset_list("rot_clips")
            sub_clip = self.create_sub_clip(rot_clips, video_length)

            if sub_clip:
                h = min(final_video.h, sub_clip.h)
                sub_clip = sub_clip.resized(height=h)
                final_video = final_video.resized(height=h)

            text_clips_concat = concatenate_videoclips(text_clips, method="chain").with_position(("center", "center"))
            final_video = CompositeVideoClip([final_video, text_clips_concat])

            TARGET_W, TARGET_H = 720, 1280
            selected_layout = self.layout_menu.get()

            if selected_layout == "double" and sub_clip:
                final_video = clips_array([[final_video], [sub_clip]]).resized((TARGET_W, TARGET_H))
            elif selected_layout == "quad" and sub_clip:
                w, h = TARGET_W // 2, TARGET_H // 2
                final_video = clips_array([
                    [final_video.resized((w, h)), sub_clip.resized((w, h))],
                    [self.create_sub_clip(rot_clips, video_length).resized((w, h)), self.create_sub_clip(rot_clips, video_length).resized((w, h))]
                ]).resized((TARGET_W, TARGET_H))
            elif selected_layout == "hexa" and sub_clip:
                w, h = TARGET_W // 2, TARGET_H // 3
                final_video = clips_array([
                    [final_video.resized((w, h)), sub_clip.resized((w, h))],
                    [self.create_sub_clip(rot_clips, video_length).resized((w, h)), self.create_sub_clip(rot_clips, video_length).resized((w, h))],
                    [self.create_sub_clip(rot_clips, video_length).resized((w, h)), self.create_sub_clip(rot_clips, video_length).resized((w, h))]
                ]).resized((TARGET_W, TARGET_H))
            else:
                final_video = final_video.resized((TARGET_W, TARGET_H))

            final_video = final_video.with_audio(audio)
            final_video.write_videofile(self.output_path, fps=24, preset='ultrafast', threads=4)

            self.after(0, self.finish_render_success)

        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}", text_color="#EF4444")
            self.progress_bar.stop()
            self.render_btn.configure(state="normal")

    def finish_render_success(self):
        self.progress_bar.stop()
        self.render_btn.configure(state="normal")
        self.status_label.configure(text="Done! Video preview playing.", text_color="#10B981")
        self.video_player.load_and_play(self.output_path)

    def upload_to_youtube(self):
        if not os.path.exists(self.output_path):
            self.status_label.configure(text="Error: No rendered video to upload!", text_color="#EF4444")
            return

        self.status_label.configure(text="Authenticating with Google...", text_color="#3B82F6")
        
        # Run upload in a separate thread so the GUI doesn't freeze
        thread = threading.Thread(target=self._youtube_upload_worker)
        thread.start()

    def _youtube_upload_worker(self):
        try:
            SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
            secret_path = os.path.join(BASE_DIR, "client_secret.json")

            if not os.path.exists(secret_path):
                self.after(0, lambda: self.status_label.configure(
                    text="Error: client_secret.json missing!", text_color="#EF4444"
                ))
                return

            # OAuth Authentication (opens a browser window for first-time login)
            flow = InstalledAppFlow.from_client_secrets_file(secret_path, SCOPES)
            credentials = flow.run_local_server(port=0)
            youtube = build("youtube", "v3", credentials=credentials)

            self.after(0, lambda: self.status_label.configure(
                text="Uploading to YouTube... Please wait.", text_color="#3B82F6"
            ))

            # Video metadata settings
            body = {
                "snippet": {
                    "title": "Meet Your Family #Shorts",
                    "description": "Generated with Video Studio! #Shorts",
                    "tags": ["Shorts", "MeetYourFamily", "Funny"],
                    "categoryId": "24"  # Category 24 = Entertainment
                },
                "status": {
                    "privacyStatus": "private"  # Options: 'private', 'unlisted', or 'public'
                }
            }

            # Prepare file upload
            media = MediaFileUpload(self.output_path, chunksize=-1, resumable=True)
            request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    self.after(0, lambda p=progress: self.status_label.configure(
                        text=f"Uploading... {p}%", text_color="#3B82F6"
                    ))

            video_id = response.get("id")
            self.after(0, lambda: self.status_label.configure(
                text=f"Uploaded! Video ID: {video_id}", text_color="#10B981"
            ))

        except Exception as e:
            self.after(0, lambda err=str(e): self.status_label.configure(
                text=f"Upload Error: {err}", text_color="#EF4444"
            ))


if __name__ == "__main__":
    app = FullscreenStudioApp()
    app.mainloop()