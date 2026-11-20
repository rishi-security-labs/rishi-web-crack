#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RISHI CRACK — Website Scraper + Viewer
"""

import os
import re
import sys
import time
import subprocess
from urllib.parse import urljoin, urlparse, unquote

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Install karo: pip install beautifulsoup4 requests colorama")
    sys.exit(1)

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# ================= COLORS =================
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    GREEN = Fore.GREEN + Style.BRIGHT
    YELLOW = Fore.YELLOW + Style.BRIGHT
    CYAN = Fore.CYAN + Style.BRIGHT
    WHITE = Fore.WHITE + Style.BRIGHT
    MAGENTA = Fore.MAGENTA + Style.BRIGHT
    RED = Fore.RED + Style.BRIGHT
    BLUE = Fore.BLUE + Style.BRIGHT
    DIM = Style.DIM
    RESET = Style.RESET_ALL
except ImportError:
    GREEN = YELLOW = CYAN = WHITE = MAGENTA = RED = BLUE = DIM = RESET = ""


# ================= CONFIG =================
TIMEOUT = 15
MAX_PAGES = 500
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

if os.path.isdir("/storage/emulated/0/Download"):
    DOWNLOAD_DIR = "/storage/emulated/0/Download/scraped"
elif os.path.isdir(os.path.expanduser("~/storage/downloads")):
    DOWNLOAD_DIR = os.path.expanduser("~/storage/downloads/scraped")
else:
    DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "downloads")
    print(f"{YELLOW}[!] Storage permission nahi mili. Chalao: termux-setup-storage{RESET}")
    print(f"{YELLOW}[!] Fallback: {DOWNLOAD_DIR}{RESET}")


# ================= BANNER =================
def show_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    banner = f"""
{MAGENTA}    ██████╗ ██╗███████╗██╗  ██╗██╗    {CYAN} ██████╗██████╗  █████╗  ██████╗██╗  ██╗
{MAGENTA}    ██╔══██╗██║██╔════╝██║  ██║██║    {CYAN}██╔════╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝
{MAGENTA}    ██████╔╝██║███████╗███████║██║    {CYAN}██║     ██████╔╝███████║██║     █████╔╝ 
{MAGENTA}    ██╔══██╗██║╚════██║██╔══██║██║    {CYAN}██║     ██╔══██╗██╔══██║██║     ██╔═██╗ 
{MAGENTA}    ██║  ██║██║███████║██║  ██║██║    {CYAN}╚██████╗██║  ██║██║  ██║╚██████╗██║  ██╗
{MAGENTA}    ╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝╚═╝    {CYAN} ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
{RESET}
{GREEN}                  ╔══════════════════════════════════════════╗
{GREEN}                  ║   {YELLOW}WEBSITE  SCRAPER  &  FILE  VIEWER  {GREEN}     ║
{GREEN}                  ║          {WHITE}Version  1.0  {MAGENTA}✧  RISHI{GREEN}           ║
{GREEN}                  ╚══════════════════════════════════════════╝{RESET}
"""
    print(banner)


# ================= SESSION =================
def make_session():
    s = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "HEAD"]
    )
    s.mount("http://", HTTPAdapter(max_retries=retries))
    s.mount("https://", HTTPAdapter(max_retries=retries))
    s.headers.update({"User-Agent": USER_AGENT})
    return s


# ================= HELPERS =================
def sanitize_filename(name):
    name = unquote(name)
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', name)
    name = name.strip('. ')
    return name or "index"


def domain_to_folder(url):
    parsed = urlparse(url)
    host = parsed.netloc or parsed.path
    host = host.replace(":", "_")
    return sanitize_filename(host)


def is_same_domain(url, base_domain):
    try:
        return urlparse(url).netloc == base_domain
    except:
        return False


def local_path_for(url, base_url, root_dir):
    parsed = urlparse(url)
    path = parsed.path
    if not path or path == "/":
        path = "/index.html"
    if path.endswith("/"):
        path += "index.html"
    if parsed.query:
        q = sanitize_filename(parsed.query)
        path = path + "_" + q
    parts = path.split("/")
    parts = [sanitize_filename(p) for p in parts if p]
    local_path = os.path.join(root_dir, *parts)
    if not os.path.splitext(local_path)[1]:
        local_path += ".html"
    return local_path


def relative_link(from_local, to_local):
    return os.path.relpath(to_local, os.path.dirname(from_local))


def ensure_dir(path):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)


# ================= DOWNLOAD =================
def download_file(session, url, local_path, base_url, root_dir, log):
    if os.path.exists(local_path):
        return True
    try:
        r = session.get(url, timeout=TIMEOUT, stream=True)
        if r.status_code != 200:
            log(f"{DIM}  [!] {r.status_code} — {url}{RESET}")
            return False
        ensure_dir(local_path)
        with open(local_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        size = os.path.getsize(local_path)
        log(f"{GREEN}  [+] {WHITE}{os.path.relpath(local_path, root_dir)} {DIM}({size/1024:.1f} KB){RESET}")
        return True
    except Exception as e:
        log(f"{RED}  [x] {url} — {e}{RESET}")
        return False


def rewrite_css_urls(session, css_text, css_url, local_css_path, base_url, root_dir, log):
    pattern = re.compile(r'url\((["\']?)([^)"\']+)\1\)')
    def replace(match):
        raw = match.group(2).strip()
        if raw.startswith("data:"):
            return match.group(0)
        absolute = urljoin(css_url, raw)
        if not is_same_domain(absolute, urlparse(base_url).netloc):
            return match.group(0)
        target_local = local_path_for(absolute, base_url, root_dir)
        download_file(session, absolute, target_local, base_url, root_dir, log)
        rel = relative_link(local_css_path, target_local).replace("\\", "/")
        return f'url("{rel}")'
    return pattern.sub(replace, css_text)


# ================= SCRAPER =================
def scrape_website(start_url):
    log = print
    session = make_session()
    parsed_start = urlparse(start_url)
    base_domain = parsed_start.netloc
    root_folder_name = domain_to_folder(start_url)
    root_dir = os.path.join(DOWNLOAD_DIR, root_folder_name)
    os.makedirs(root_dir, exist_ok=True)

    print(f"\n{CYAN}{'═'*60}")
    print(f"  {MAGENTA}SCRAPING STARTED")
    print(f"{CYAN}{'═'*60}")
    print(f"  {WHITE}URL       : {GREEN}{start_url}")
    print(f"  {WHITE}Domain    : {GREEN}{base_domain}")
    print(f"  {WHITE}Save to   : {GREEN}{root_dir}")
    print(f"{CYAN}{'═'*60}{RESET}\n")

    visited_pages = set()
    queue = [start_url]

    while queue and len(visited_pages) < MAX_PAGES:
        current_url = queue.pop(0).split("#")[0]
        if current_url in visited_pages:
            continue
        visited_pages.add(current_url)

        print(f"\n{CYAN}[PAGE {len(visited_pages)}]{RESET} {WHITE}{current_url}{RESET}")

        try:
            r = session.get(current_url, timeout=TIMEOUT)
            if r.status_code != 200:
                print(f"{DIM}  [!] Status {r.status_code} — skip{RESET}")
                continue

            ct = r.headers.get("Content-Type", "")
            if "html" not in ct.lower():
                lp = local_path_for(current_url, start_url, root_dir)
                download_file(session, current_url, lp, start_url, root_dir, print)
                continue

            soup = BeautifulSoup(r.text, "html.parser")
            page_local = local_path_for(current_url, start_url, root_dir)
            ensure_dir(page_local)

            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                if not href or href.startswith(("mailto:", "tel:", "javascript:", "#")):
                    continue
                absolute = urljoin(current_url, href).split("#")[0]
                if not is_same_domain(absolute, base_domain):
                    continue
                if absolute not in visited_pages and len(visited_pages) + len(queue) < MAX_PAGES:
                    queue.append(absolute)
                tl = local_path_for(absolute, start_url, root_dir)
                a["href"] = relative_link(page_local, tl).replace("\\", "/")

            for link in soup.find_all("link", href=True):
                rel_attr = link.get("rel", [])
                rels = rel_attr if isinstance(rel_attr, list) else [rel_attr]
                if "stylesheet" not in [r.lower() for r in rels]:
                    continue
                absolute = urljoin(current_url, link["href"].strip())
                if not is_same_domain(absolute, base_domain):
                    continue
                tl = local_path_for(absolute, start_url, root_dir)
                if download_file(session, absolute, tl, start_url, root_dir, print):
                    try:
                        with open(tl, "r", encoding="utf-8", errors="ignore") as f:
                            css_text = f.read()
                        rewritten = rewrite_css_urls(session, css_text, absolute, tl, start_url, root_dir, print)
                        with open(tl, "w", encoding="utf-8") as f:
                            f.write(rewritten)
                    except Exception as e:
                        print(f"{YELLOW}  [!] CSS rewrite fail: {e}{RESET}")
                link["href"] = relative_link(page_local, tl).replace("\\", "/")

            for script in soup.find_all("script", src=True):
                absolute = urljoin(current_url, script["src"].strip())
                if not is_same_domain(absolute, base_domain):
                    continue
                tl = local_path_for(absolute, start_url, root_dir)
                if download_file(session, absolute, tl, start_url, root_dir, print):
                    script["src"] = relative_link(page_local, tl).replace("\\", "/")

            for img in soup.find_all("img", src=True):
                src = img["src"].strip()
                if src.startswith("data:"):
                    continue
                absolute = urljoin(current_url, src)
                if not is_same_domain(absolute, base_domain):
                    continue
                tl = local_path_for(absolute, start_url, root_dir)
                if download_file(session, absolute, tl, start_url, root_dir, print):
                    img["src"] = relative_link(page_local, tl).replace("\\", "/")

            for img in soup.find_all(attrs={"srcset": True}):
                parts_new = []
                for part in img["srcset"].split(","):
                    part = part.strip()
                    if not part:
                        continue
                    pieces = part.split()
                    url_part = pieces[0]
                    desc = " ".join(pieces[1:]) if len(pieces) > 1 else ""
                    absolute = urljoin(current_url, url_part)
                    if is_same_domain(absolute, base_domain):
                        tl = local_path_for(absolute, start_url, root_dir)
                        download_file(session, absolute, tl, start_url, root_dir, print)
                        rel = relative_link(page_local, tl).replace("\\", "/")
                        parts_new.append(f"{rel} {desc}".strip())
                    else:
                        parts_new.append(part)
                img["srcset"] = ", ".join(parts_new)

            for source in soup.find_all("source", src=True):
                absolute = urljoin(current_url, source["src"].strip())
                if not is_same_domain(absolute, base_domain):
                    continue
                tl = local_path_for(absolute, start_url, root_dir)
                if download_file(session, absolute, tl, start_url, root_dir, print):
                    source["src"] = relative_link(page_local, tl).replace("\\", "/")

            for style in soup.find_all("style"):
                if style.string:
                    rewritten = rewrite_css_urls(session, style.string, current_url, page_local, start_url, root_dir, print)
                    style.string.replace_with(rewritten)

            for tag in soup.find_all(style=True):
                style_val = tag["style"]
                def repl(m):
                    raw = m.group(2).strip()
                    if raw.startswith("data:"):
                        return m.group(0)
                    absolute = urljoin(current_url, raw)
                    if not is_same_domain(absolute, base_domain):
                        return m.group(0)
                    tl = local_path_for(absolute, start_url, root_dir)
                    download_file(session, absolute, tl, start_url, root_dir, print)
                    rel = relative_link(page_local, tl).replace("\\", "/")
                    return f'url("{rel}")'
                tag["style"] = re.sub(r'url\((["\']?)([^)"\']+)\1\)', repl, style_val)

            with open(page_local, "w", encoding="utf-8") as f:
                f.write(str(soup))
            print(f"{GREEN}  [HTML] {os.path.relpath(page_local, root_dir)}{RESET}")

        except Exception as e:
            print(f"{RED}  [x] Error: {e}{RESET}")
            continue

    print(f"\n{GREEN}{'═'*60}")
    print(f"  {MAGENTA}✓ SCRAPE COMPLETE")
    print(f"{GREEN}{'═'*60}")
    print(f"  {WHITE}Pages  : {GREEN}{len(visited_pages)}")
    print(f"  {WHITE}Folder : {GREEN}{os.path.abspath(root_dir)}")
    print(f"{GREEN}{'═'*60}{RESET}\n")

    input(f"{YELLOW}  Enter dabao menu pe jaane ke liye...{RESET}")


# ================= VIEWER =================
def list_scraped_folders():
    if not os.path.exists(DOWNLOAD_DIR):
        return []
    folders = []
    for name in sorted(os.listdir(DOWNLOAD_DIR)):
        path = os.path.join(DOWNLOAD_DIR, name)
        if os.path.isdir(path):
            files_count = 0
            total_size = 0
            for root, dirs, files in os.walk(path):
                for f in files:
                    files_count += 1
                    try:
                        total_size += os.path.getsize(os.path.join(root, f))
                    except:
                        pass
            folders.append({
                "name": name,
                "path": path,
                "files": files_count,
                "size": total_size
            })
    return folders


def open_in_browser(path):
    """HTML file ko browser mein khol"""
    try:
        if sys.platform.startswith("linux"):
            subprocess.Popen(["termux-open", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
        return True
    except Exception:
        try:
            subprocess.Popen(["xdg-open", path])
            return True
        except:
            return False


def view_folder(folder_path, folder_name):
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"\n{CYAN}{'═'*60}")
        print(f"  {MAGENTA}FOLDER: {WHITE}{folder_name}")
        print(f"{CYAN}{'═'*60}{RESET}")

        entries = []
        try:
            for item in sorted(os.listdir(folder_path)):
                full = os.path.join(folder_path, item)
                if os.path.isdir(full):
                    entries.append(("dir", item, full))
                else:
                    entries.append(("file", item, full))
        except Exception as e:
            print(f"{RED}  Error: {e}{RESET}")
            input(f"{YELLOW}  Enter...{RESET}")
            return

        dirs = [e for e in entries if e[0] == "dir"]
        files = [e for e in entries if e[0] == "file"]

        print(f"\n{WHITE}  {DIM}Folders:{RESET}")
        idx_map = {}
        i = 1
        for e in dirs:
            print(f"  {GREEN}[{i}]{RESET} {CYAN}📁 {e[1]}/{RESET}")
            idx_map[str(i)] = e
            i += 1

        print(f"\n{WHITE}  {DIM}Files:{RESET}")
        for e in files:
            size = os.path.getsize(e[2]) / 1024
            icon = "🌐" if e[1].endswith((".html", ".htm")) else "📄"
            print(f"  {GREEN}[{i}]{RESET} {WHITE}{icon} {e[1]} {DIM}({size:.1f} KB){RESET}")
            idx_map[str(i)] = e
            i += 1

        print(f"\n{CYAN}{'─'*60}{RESET}")
        print(f"  {YELLOW}[b]{RESET} Back to folder list")
        print(f"  {YELLOW}[o]{RESET} Open this folder in file manager")
        print(f"  {RED}[0]{RESET} Exit")
        print(f"{CYAN}{'─'*60}{RESET}")

        choice = input(f"\n{YELLOW}  Choice: {RESET}").strip().lower()

        if choice == "b":
            return
        elif choice == "0":
            sys.exit(0)
        elif choice == "o":
            open_in_browser(folder_path)
            input(f"{YELLOW}  Enter...{RESET}")
        elif choice in idx_map:
            kind, name, full = idx_map[choice]
            if kind == "dir":
                view_folder(full, name)
            else:
                # File — HTML toh browser mein kholo, warna info dikhao
                if name.endswith((".html", ".htm")):
                    if open_in_browser(full):
                        print(f"{GREEN}  ✓ Browser mein khola{RESET}")
                    else:
                        print(f"{RED}  Browser nahi khul paya{RESET}")
                    time.sleep(1)
                else:
                    print(f"\n{CYAN}  File: {name}{RESET}")
                    print(f"  Path: {full}")
                    print(f"  Size: {os.path.getsize(full)/1024:.2f} KB")
                    input(f"\n{YELLOW}  Enter...{RESET}")


def view_files():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"\n{CYAN}{'═'*60}")
        print(f"  {MAGENTA}VIEW  FILES")
        print(f"{CYAN}{'═'*60}{RESET}")
        print(f"  {WHITE}{DIM}Location: {DOWNLOAD_DIR}{RESET}\n")

        folders = list_scraped_folders()

        if not folders:
            print(f"{YELLOW}  Abhi koi scraped folder nahi.{RESET}")
            print(f"{WHITE}  Pehle [1] Scrap karo.{RESET}")
            input(f"\n{YELLOW}  Enter dabao back jaane ke liye...{RESET}")
            return

        for i, f in enumerate(folders, 1):
            size_mb = f["size"] / (1024 * 1024)
            print(f"  {GREEN}[{i}]{RESET} {CYAN}📁 {f['name']}{RESET}")
            print(f"      {DIM}{f['files']} files  •  {size_mb:.2f} MB{RESET}")

        print(f"\n{CYAN}{'─'*60}{RESET}")
        print(f"  {YELLOW}[b]{RESET} Back to main menu")
        print(f"  {YELLOW}[o]{RESET} Open download folder in file manager")
        print(f"  {RED}[0]{RESET} Exit")
        print(f"{CYAN}{'─'*60}{RESET}")

        choice = input(f"\n{YELLOW}  Choice: {RESET}").strip().lower()

        if choice == "b":
            return
        elif choice == "0":
            sys.exit(0)
        elif choice == "o":
            open_in_browser(DOWNLOAD_DIR)
            input(f"{YELLOW}  Enter...{RESET}")
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(folders):
                    view_folder(folders[idx]["path"], folders[idx]["name"])
            except ValueError:
                pass


# ================= SCRAP MENU =================
def scrap_menu():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"\n{CYAN}{'═'*60}")
    print(f"  {MAGENTA}SCRAP  WEBSITE")
    print(f"{CYAN}{'═'*60}{RESET}\n")
    print(f"  {WHITE}Website ka URL daalo.{RESET}")
    print(f"  {DIM}Example: https://example.com ya example.com{RESET}\n")

    url = input(f"  {YELLOW}➜ URL: {RESET}").strip()

    if not url or url.lower() in ("b", "back", "0"):
        return

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        scrape_website(url)
    except KeyboardInterrupt:
        print(f"\n\n{RED}  Interrupted!{RESET}")
        time.sleep(1)


# ================= MAIN MENU =================
def main_menu():
    while True:
        show_banner()
        print(f"{CYAN}  ╔══════════════════════════════════════════════════╗")
        print(f"{CYAN}  ║                  {MAGENTA}MAIN  MENU{CYAN}                     ║")
        print(f"{CYAN}  ╠══════════════════════════════════════════════════╣")
        print(f"{CYAN}  ║                                                  ║")
        print(f"{CYAN}  ║   {GREEN}[1]{WHITE}  🕷  Scrap Website                         {CYAN}║")
        print(f"{CYAN}  ║   {GREEN}[2]{WHITE}  📂  View Crack Files                      {CYAN}║")
        print(f"{CYAN}  ║   {GREEN}[3]{WHITE}  📁  Open Download Folder                  {CYAN}║")
        print(f"{CYAN}  ║   {GREEN}[4]{WHITE}  ℹ   About                                {CYAN}║")
        print(f"{CYAN}  ║   {RED}[0]{WHITE}  ✖   Exit                                 {CYAN}║")
        print(f"{CYAN}  ║                                                  ║")
        print(f"{CYAN}  ╚══════════════════════════════════════════════════╝{RESET}")
        print(f"\n  {DIM}Save location: {DOWNLOAD_DIR}{RESET}\n")

        choice = input(f"  {YELLOW}➜ Choice: {RESET}").strip()

        if choice == "1":
            scrap_menu()
        elif choice == "2":
            view_files()
        elif choice == "3":
            if os.path.exists(DOWNLOAD_DIR):
                open_in_browser(DOWNLOAD_DIR)
                print(f"{GREEN}  ✓ File manager mein khol diya{RESET}")
            else:
                print(f"{RED}  Folder nahi mila. Pehle scrap karo.{RESET}")
            time.sleep(1)
        elif choice == "4":
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"\n{CYAN}{'═'*60}")
            print(f"  {MAGENTA}ABOUT")
            print(f"{CYAN}{'═'*60}{RESET}")
            print(f"  {WHITE}Name     : {MAGENTA}RISHI CRACK")
            print(f"  {WHITE}Version  : {GREEN}1.0")
            print(f"  {WHITE}Features : {GREEN}Website Scraper + File Viewer")
            print(f"  {WHITE}Save Dir : {GREEN}{DOWNLOAD_DIR}{RESET}")
            print(f"{CYAN}{'═'*60}{RESET}")
            input(f"\n{YELLOW}  Enter dabao...{RESET}")
        elif choice == "0":
            print(f"\n{MAGENTA}  ✧ Goodbye! ✧{RESET}\n")
            sys.exit(0)


# ================= MAIN =================
if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{RED}  Interrupted!{RESET}\n")
        sys.exit(0)
