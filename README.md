Here is a clean, professional `README.md` file tailored specifically for your **Meet Your Family Video Studio** project.

It includes setup instructions, features, structure, and crucial notes on protecting API keys and configuring Google OAuth.

---

### Create a file named `README.md` in your project folder and paste this in:

```markdown
# 🎬 Meet Your Family — Video Studio

A full-featured Python desktop application built with **CustomTkinter**, **MoviePy**, and **OpenCV** designed to automatically generate high-quality vertical 9:16 videos (YouTube Shorts / TikTok / Reels) featuring customizable family cast members, media clips, and music overlays. Includes built-in one-click YouTube video uploading.

---

## ✨ Features

- **📱 YouTube Shorts Optimized:** Pre-configured for vertical 9:16 aspect ratio output ($720 \times 1280$).
- **🎲 One-Click Cast Randomizer:** Instantly shuffles cast selections across all roles with dynamic thumbnail previews.
- **📺 Embedded OpenCV Player:** Real-time, smooth video playback container built directly into the studio dashboard.
- **📤 Direct YouTube Upload:** Integrated Google OAuth 2.0 flow to auto-upload generated Shorts directly to your channel.
- **🎨 Custom Layout Options:** Multi-clip layout support including single, double, quad, and hexa grid compositions.

---

## 🛠️ Installation & Setup

### 1. Prerequisites
Ensure you have **Python 3.11+** installed on your system.

### 2. Clone the Repository
```bash
git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.NAME.git)
cd YOUR_REPOSITORY.NAME

```

### 3. Install Required Dependencies

Run the following command in your terminal to install all required libraries:

```powershell
py -m pip install customtkinter moviepy opencv-python pillow google-api-python-client google-auth-oauthlib google-auth-httplib2

```

---

## 📁 Directory Structure

Organize your `assets/` directory according to the structure below:

```text
├── assets/
│   ├── base_clips/          # Base background video clips
│   ├── rot_clips/           # Rotation / background filler clips
│   ├── songs/               # Audio track options (.mp3 / .wav)
│   ├── title_images/        # Overlay PNG title banners
│   └── Images/              # Cast folder images
│       ├── Dad/
│       ├── Mom/
│       ├── Aunt/
│       ├── Little SIs/
│       ├── Big Sis/
│       ├── Friend/
│       └── Mi Prima/
├── app.py                   # Main Application Entry Point
├── client_secret.json       # Google OAuth Credentials (DO NOT COMMIT)
└── README.md

```

---

## 🔐 YouTube Upload Setup (Google API)

To enable the **Upload to YouTube** button:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **YouTube Data API v3**.
3. Create an **OAuth 2.0 Desktop Client ID**.
4. Download the JSON credentials file, rename it to `client_secret.json`, and place it in the project root directory.

> ⚠️ **Security Warning:** Never commit `client_secret.json` or `token.json` to a public repository! Make sure they are listed in your `.gitignore`.

---

## 🚀 Running the Application

Launch the application by running:

```powershell
py app.py

```

### Packaging into a Standalone `.exe`

To compile the application into an executable folder for distribution using **PyInstaller**:

```powershell
pyinstaller --noconfirm --onedir --windowed `
  --add-data "assets;assets" `
  --add-data "client_secret.json;." `
  app.py

```

Find your compiled executable in the `dist/app/` directory!

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

```

```
