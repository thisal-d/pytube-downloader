

<div align="center">
  <a href="https://sourceforge.net/projects/pytube-downloader/" target="_blank"><img src="readme assets/main.ico" alt="PyTube Downloader" width="120"></a>
  <h1>PyTube Downloader</h1>
  <p><strong>Simple. Fast. Powerful YouTube Downloader.</strong></p>
  <p>
    <a href="https://sourceforge.net/projects/pytube-downloader/" target="_blank">🚀 SourceForge</a> •
    <a href="#-features">✨ Features</a> •
    <a href="#️-quick-start-guide">📦 Getting Started</a> •
    <a href="#-contribution">🤝 Contributing</a>
  </p>

[![Language: 中文](https://img.shields.io/badge/Language-中文-red)](README_zh.md)
[![Download (Latest)](https://img.shields.io/sourceforge/dm/pytube-downloader.svg?label=Downloads)](https://sourceforge.net/projects/pytube-downloader/files/latest/download)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![UI](https://img.shields.io/badge/UI-tkinter%2Bcustomtkinter-green)
![Version](https://img.shields.io/badge/version-6.2.0-orange)

---

**PyTube Downloader** is a modern, user-friendly application that makes downloading YouTube videos and playlists effortless.
With support for multiple formats, quality levels (144p–8K), and simultaneous downloads, it gives you **complete control** over your YouTube media experience.

&nbsp; &nbsp;[![Download PyTube Downloader](https://a.fsdn.com/con/app/sf-download-button)](https://sourceforge.net/projects/pytube-downloader/files/latest/download)

</div>


---

## 🖥️ User Interface Preview

![Preview](./readme%20assets/en-0.png)

---

## ✨ Features

* 🎞️ **Playlist Downloading** — Download entire playlists from a single URL.
* 🎚️ **Format & Quality Selection** — Choose from multiple formats (MP4, MP3, etc.) and qualities (144p–8K).
* 📊 **Progress Tracking** — Monitor downloads directly in the app.
* ⚡ **Simultaneous Downloads** — Save time with multiple concurrent downloads.
* ⚙️ **Automatic Downloads with Predefined Settings** — Set your preferred video quality, audio format, and download location once — PyTube will handle the rest.
* 🗂️ **Dynamic Folder Organization** — Automatically sorts files by playlist, quality, or type.
* 🌐 **Multi-Language Support** — Enjoy the app in your language:

  | Language        | Contributor                                                                                         |
  | --------------- | --------------------------------------------------------------------------------------------------- |
  | English         | -                                                                                                   |
  | 中文 (Chinese)    | [<img src="https://github.com/childeyouyu.png?size=25" width="25">](https://github.com/childeyouyu) |
  | සිංහල (Sinhala) | [<img src="https://github.com/Navindu21.png?size=25" width="25">](https://github.com/Navindu21)     |
  | தமிழ் (Tamil)   | [<img src="https://github.com/asma-mf.png?size=25" width="25">](https://github.com/asma-mf)   |

  💡 **Help us [improve existing translations](LANGUAGE_CONTRIBUTION_GUIDE_en.md/#improve-current-language-issues)** or [**add new ones**](LANGUAGE_CONTRIBUTION_GUIDE_en.md/#adding-a-new-language).
* ⌨️ **Keyboard Shortcuts** — Control the app easily with quick-access shortcut keys.

---

## ⚙️ Tech Stack

| Category          | Technologies                                                                                     |
| ----------------- | ------------------------------------------------------------------------------------------------ |
| **Language**      | Python 3.10+                                                                                     |
| **Libraries**     | `tkinter`, `customtkinter`, `pytubefix`, `pillow`, `pyautogui`, `pystray`, `pyperclip`, `hPyT`, `win11toast`, `ctkchart` |
| **External Tool** | `FFmpeg` (for video/audio processing)                                                            |

---

## 🧭 Quick Start Guide

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Thisal-D/PyTube-Downloader.git
cd PyTube-Downloader
```

### 2️⃣ Install FFmpeg

* Download from [FFmpeg.org](https://ffmpeg.org/download.html)
* Extract and copy `ffmpeg.exe` into:

  ```
  PyTube-Downloader/ffmpeg/
  ```

### 3️⃣ Install Dependencies

```bash
python dependencies_installer.py
python dependencies_updater.py
```

### 4️⃣ Run the Application

```bash
python main.py
```

### 5️⃣ Download Videos

1. Paste a YouTube video or playlist URL.
2. Choose **Single Video** or **Playlist Mode**.
3. Select your desired **format and quality**.
4. Click **Download** and track progress in real-time.
5. Find your downloaded files in the output folder — ready to enjoy!

---

## 📁 Project Structure

See [**Project Structure Guide**](PROJECT_STRUCTURE.md) for detailed folder and code layout information.

---

## 🌙 Screenshots

| Screenshots                      |
| -------------------------------- |
| ![1](./readme%20assets/en-0.png) |
| ![2](./readme%20assets/en-1.png) |
| ![3](./readme%20assets/en-2.png) |
| ![4](./readme%20assets/en-3.png) |
| ![5](./readme%20assets/en-4.png) |
| ![6](./readme%20assets/en-5.png) |
| ![7](./readme%20assets/en-6.png) |
| ![8](./readme%20assets/en-7.png) |
| ![9](./readme%20assets/en-8.png) |

---

## ⭐ Star History

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=Thisal-D/PyTube-Downloader&type=Date&theme=dark">
  <img src="https://api.star-history.com/svg?repos=Thisal-D/PyTube-Downloader&type=Date&theme=light">
</picture>

---

## 🤝 Contribution

We **welcome all kinds of contributions** — not just code!
Whether you're improving the UI, translating, enhancing themes, or helping refine documentation — **your input makes PyTube Downloader better for everyone.**

### 💡 Ways You Can Contribute

* 🧩 **Code Improvements:**
  Fix bugs, optimize performance, or suggest new features.
* 🌍 **Language Contributions:**
  Help us [**improve existing translations**](LANGUAGE_CONTRIBUTION_GUIDE_en.md/#improve-current-language-issues)
  or [**add support for new languages**](LANGUAGE_CONTRIBUTION_GUIDE_en.md/#adding-a-new-language).
* 🎨 **Theme Contributions:**
  Help us [**enhance current themes**](THEME_CONTRIBUTION_GUIDE_en.md/#improve-current-themes)
  or [**design brand new ones**](THEME_CONTRIBUTION_GUIDE_en.md/#adding-a-new-theme).
* 🧠 **Ideas & Feedback:**
  Share feature suggestions or report issues on [GitHub Issues](https://github.com/Thisal-D/PyTube-Downloader/issues).
* 🧾 **Documentation & Guides:**
  Improve readability, structure, or examples in the project documentation.

### 🛠️ Getting Started

1. **Fork** the repository.
2. **Create a new branch** for your changes.
3. **Commit** your improvements with clear messages.
4. **Submit a pull request** — we'll review and merge it soon!

> See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

> ❤️ Every contribution, big or small, is appreciated.
> Let's make PyTube Downloader even better — together!

---

## 📜 License

Licensed under the **MIT License**.
See the [LICENSE](LICENSE) file for full details.

---

## ⚠️ Disclaimer

This application is intended for **personal use only**.
Please respect **YouTube's Terms of Service** and content creators' rights when downloading videos.

---

## 👥 Contributors

| Contributor                                                                                                 | Profile                                                |
| ----------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| [<img src="https://github.com/childeyouyu.png?size=25" width="25">](https://github.com/childeyouyu)         | [youyu](https://github.com/childeyouyu)                |
| [<img src="https://github.com/Navindu21.png?size=25" width="25">](https://github.com/Navindu21)             | [Navindu Pahasara](https://github.com/Navindu21)       |
| [<img src="https://github.com/sooryasuraweera.png?size=25" width="25">](https://github.com/sooryasuraweera) | [Soorya Suraweera](https://github.com/sooryasuraweera) |
| [<img src="https://github.com/asma-mf.png?size=25" width="25">](https://github.com/asma-mf)           | [Fathima Asma](https://github.com/asma-mf)          |

---

<p align="center">
<b>Made with ❤️ by <a href="https://github.com/Thisal-D">Thisal-D</a> and contributors</b>
</p>