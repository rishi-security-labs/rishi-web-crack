# 🕷️ RISHI CRACK — Website Scraper & Offline Viewer

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Termux%20%7C%20Linux%20%7C%20Windows%20%7C%20macOS-4EAA25?style=for-the-badge&logo=linux&logoColor=white)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4.x-43B02A?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)
![Made with ❤️](https://img.shields.io/badge/Made%20with-%E2%9D%A4%EF%B8%8F-red?style=for-the-badge)

> A lightweight, Termux-friendly **Python CLI tool** that recursively scrapes any website and saves a fully browsable **offline copy** — with rewritten links, downloaded assets, and a built-in terminal file viewer.

---

## 📖 Overview

**RISHI CRACK** is a single-file Python utility that:

- **Crawls** a target website (same-domain only, up to 500 pages)
- **Downloads** HTML, CSS, JavaScript, images, and `<source>`/`srcset` assets
- **Rewrites** every internal link (anchors, stylesheets, scripts, `url(...)` in CSS) so the saved copy works **fully offline**
- **Serves a beautiful terminal viewer** to browse scraped folders and open HTML files directly in your system browser

Built for **ethical archiving, offline learning, and low-bandwidth environments** (Termux, Raspberry Pi, old laptops).

---

## ✨ Key Features

### 🕷️ Scraper Module
- 🔁 **Breadth-first recursive crawling** with a 500-page safety limit
- 🧠 **Smart URL rewriting** — relative paths between local files
- 🎨 **CSS `url(...)` rewriter** — handles both external `.css` files and inline `<style>` blocks
- 🖼️ **Full asset handling** — `<img>`, `<img srcset>`, `<source>`, `<script src>`, `<link rel="stylesheet">`, inline `style="..."`
- 🩹 **Retry logic** via `urllib3.Retry` (429 / 5xx backoff)
- 🛑 **Same-domain guard** — external links left untouched
- 📁 **Deterministic local paths** — mirrors URL structure on disk
- 🌐 **Any content-type** — non-HTML responses are saved as-is

### 📂 Viewer Module
- 📋 Lists all scraped sites with **file count + total size**
- 🗂️ **Tree-style folder browser** in the terminal
- 🌐 **One-key open** in system browser (Termux / Windows / macOS / Linux)
- 📱 **Auto-detects storage path** (Termux `~/storage/downloads`, fallback to `~/downloads`)

### 🎨 UX / Terminal
- 🌈 **Color-coded output** via `colorama`
- 🧾 **ASCII banner** + boxed menu UI
- 🔐 **Graceful Ctrl+C handling**
- 💾 **Skips already-downloaded files** (idempotent re-runs)

---

## 🗂️ Project Structure

```
rishi-crack/
├── rishi_crack.py        # Main script (scraper + viewer + menu)
├── README.md             # This file
├── LICENSE               # MIT License
└── .gitignore            # Python + OS ignores

# Generated at runtime (NOT committed):
~/storage/downloads/scraped/
└── <domain-name>/
    ├── index.html
    ├── about/
    │   └── index.html
    ├── assets/
    │   ├── style.css
    │   ├── app.js
    │   └── logo.png
    └── ...
```

---

## 🚀 Installation

### 🔧 Prerequisites
- **Python 3.8+**
- **pip**
- *(Optional, for Termux)* `termux-setup-storage` for save permissions

### 📦 Step 1 — Clone & Install

```bash
git clone https://github.com/rishi-security-labs/rishi-web-crack.git
cd rishi-crack
pip install beautifulsoup4 requests colorama
```

### 📱 Termux Setup (Android)

```bash
pkg update && pkg upgrade -y
pkg install python -y
termux-setup-storage          # Grant storage permission
git clone https://github.com/rishi-security-labs/rishi-web-crack.git
cd rishi-crack
pip install beautifulsoup4 requests colorama
python rishi_crack.py
```

### 🐧 Linux / 🍎 macOS

```bash
python3 -m pip install beautifulsoup4 requests colorama
python3 rishi_crack.py
```

### 🪟 Windows

```powershell
py -m pip install beautifulsoup4 requests colorama
py rishi_crack.py
```

---

## 🎮 Usage

Launch the tool:

```bash
python rishi_crack.py
```

You'll see an interactive menu:

```
╔══════════════════════════════════════════════════╗
║                  MAIN  MENU                      ║
╠══════════════════════════════════════════════════╣
║   [1]  🕷  Scrap Website                         ║
║   [2]  📂  View Crack Files                      ║
║   [3]  📁  Open Download Folder                  ║
║   [4]  ℹ   About                                 ║
║   [0]  ✖   Exit                                  ║
╚══════════════════════════════════════════════════╝
```

### Quick Workflow

1. Press **`1`** → paste a URL like `example.com`
2. Watch it crawl, download, and rewrite links
3. Press **`2`** → pick the scraped folder
4. Select any `.html` file → opens in your **default browser offline** ✅

### Example Session

```text
➜ URL: https://example.com

[PAGE 1] https://example.com
  [+] index.html (12.4 KB)
  [+] assets/style.css (3.1 KB)
  [+] assets/logo.png (8.7 KB)
  [HTML] index.html

[PAGE 2] https://example.com/about
  ...

✓ SCRAPE COMPLETE
  Pages  : 14
  Folder : /storage/emulated/0/Download/scraped/example.com
```

---

## ⚙️ Configuration

All tunables live at the top of `rishi_crack.py`:

| Constant | Default | Purpose |
|---|---|---|
| `TIMEOUT` | `15` | Per-request timeout (seconds) |
| `MAX_PAGES` | `500` | Hard cap on pages crawled |
| `USER_AGENT` | Chrome 120 UA | Spoofed browser identity |
| `DOWNLOAD_DIR` | Auto-detect | Root save directory |

### Storage Auto-Detection Order

1. `/storage/emulated/0/Download/scraped` *(Termux primary)*
2. `~/storage/downloads/scraped` *(Termux fallback)*
3. `~/downloads` *(generic fallback)*

No environment variables, no API keys — **zero-config**.

---

## 🛡️ Legal & Ethical Use

> ⚠️ **Use this tool responsibly.**
>
> - ✅ Scraping sites you **own** or have **permission** to archive
> - ✅ Archiving **public-domain** or **open-license** content
> - ✅ Offline reading of **your own** dashboards / docs
> - ❌ **Do NOT** bypass paywalls, login walls, or anti-bot systems
> - ❌ **Do NOT** redistribute copyrighted content
>
> Always respect `robots.txt` and the target site's Terms of Service. The author is **not responsible** for misuse.

---

## 🗺️ Roadmap

- [ ] `robots.txt` compliance toggle
- [ ] Resume interrupted scrapes
- [ ] `--depth N` CLI flag
- [ ] Export as `.zip` archive
- [ ] Built-in local HTTP server for instant preview
- [ ] Cookie / auth-header support

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/amazing-idea`
3. Commit: `git commit -m "feat: add amazing idea"`
4. Push: `git push origin feature/amazing-idea`
5. Open a **Pull Request** 🎉

Please follow **PEP 8** and keep PRs focused.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Rishi Security Labs

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
```

---

## 👤 Author

**Rishi Security Labs**
- 🔗 GitHub: [@rishi-security-labs](https://github.com/rishi-security-labs)
- 🎯 Focus: Practical security & automation tools for low-resource environments

---

<div align="center">

**⭐ If this saved you time, drop a star — it fuels more tools like this! ⭐**

Made with 🕷️ + ☕ + 💻

</div>
