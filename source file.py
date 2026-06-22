# |||=======================< youtube video/audio downloader >=======================|||

# -----------------------< Import libraries >-----------------------

from pathlib import Path
import customtkinter as ctk
import yt_dlp
import threading
import re
import time
import socket
from pyautogui import alert
from tkinter import filedialog as fd

# -----------------------< Initializing >-----------------------

download_path = Path.home() / "Downloads"
path = "downloads"
if not download_path.exists():
    try:
        download_path.mkdir(parents=True, exist_ok=True)
        path = "downloads"
    except Exception:
        download_path = Path.home()
        path = "home"
stop_event = threading.Event()
window = ctk.CTk()
window.geometry("1000x500")
window.resizable(False, False)
window.title("Youtube video/audio downloader")

# -----------------------< single download logic >-----------------------

def download(url, output_format, resolution):
    format_rules = {
        "8k": "bestvideo[height<=4320]+bestaudio/best",
        "4k": "bestvideo[height<=2160]+bestaudio/best",
        "2k": "bestvideo[height<=1440]+bestaudio/best",
        "1080p": "bestvideo[height<=1080]+bestaudio/best",
        "720p": "bestvideo[height<=720]+bestaudio/best",
        "480p": "bestvideo[height<=480]+bestaudio/best",
        "360p": "bestvideo[height<=360]+bestaudio/best",
        "240p": "bestvideo[height<=240]+bestaudio/best",
        "144p": "bestvideo[height<=144]+bestaudio/best"
    }
    selected_format = format_rules.get(resolution.lower(), format_rules["720p"])
    def progress_hook(info):
        if stop_event.is_set():
            raise Exception("Download canceled")
        if info.get('status') == 'downloading':
            downloaded = info.get('downloaded_bytes', 0)
            total = info.get('total_bytes') or info.get('total_bytes_estimate') or 0
            if total:
                percent = min(downloaded / total, 1.0)
                window.after(0, lambda: download_Progressbar.set(percent))
                window.after(0, lambda: download_Label.configure(text=str(int(percent * 100)) + " %"))
        elif info.get('status') == 'finished':
            window.after(0, lambda: download_Progressbar.set(1.0))
    if output_format == "audio":
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(download_path / '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook],
            'quiet': False,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }]
        }
    else:
        ydl_opts = {
            'format': selected_format,
            'merge_output_format': 'mp4',
            'outtmpl': str(download_path / '%(title)s (%(height)sp).%(ext)s'),
            'progress_hooks': [progress_hook],
            'quiet': False,
        }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                title = info.get("title") or "Unknown title"
                window.after(0, lambda t=title: file_title.configure(text="Title : " + t))
            except Exception:
                pass

            ydl.download([url])
    except Exception as e:
        s = re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', str(e))
        s = s.strip()
        s = re.sub(r'^(ERROR|WARNING):\s*', '', s, flags=re.IGNORECASE)
        s = re.sub(r'\[generic\]\s*', '', s, flags=re.IGNORECASE)
        s = re.sub(r'\s*\[[^\]]+\]\s*$', '', s)
        lines = [ln.strip() for ln in s.splitlines() if ln.strip()]
        error_message = lines[0] if lines else s
        window.after(0, lambda: (show_main_view(), alert(text=error_message, title='Error', button='OK')))
    finally:
        window.after(0, lambda: (heading_label.configure(text="Download Complete"), go_back_button.place(x=830, y=450)))

# -----------------------< multi download logic >-----------------------

def download_one(url, output_format, resolution, log_widget):
    format_rules = {
        "8k": "bestvideo[height<=4320]+bestaudio/best",
        "4k": "bestvideo[height<=2160]+bestaudio/best",
        "2k": "bestvideo[height<=1440]+bestaudio/best",
        "1080p": "bestvideo[height<=1080]+bestaudio/best",
        "720p": "bestvideo[height<=720]+bestaudio/best",
        "480p": "bestvideo[height<=480]+bestaudio/best",
        "360p": "bestvideo[height<=360]+bestaudio/best",
        "240p": "bestvideo[height<=240]+bestaudio/best",
        "144p": "bestvideo[height<=144]+bestaudio/best"
    }
    selected_format = format_rules.get(resolution.lower(), format_rules["720p"]) if isinstance(resolution, str) else format_rules["720p"]
    def progress_hook(info):
        if stop_event.is_set():
            raise Exception("Download canceled")
        if info.get('status') == 'downloading':
            downloaded = info.get('downloaded_bytes', 0)
            total = info.get('total_bytes') or info.get('total_bytes_estimate') or 0
            if total:
                percent = min(downloaded / total, 1.0)
                window.after(0, lambda: download_Progressbar.set(percent))
                window.after(0, lambda: download_Label.configure(text=str(int(percent * 100)) + " %"))
        elif info.get('status') == 'finished':
            window.after(0, lambda: download_Progressbar.set(1.0))
    if output_format == "audio":
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(download_path / '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook],
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }]
        }
    else:
        ydl_opts = {
            'format': selected_format,
            'merge_output_format': 'mp4',
            'outtmpl': str(download_path / '%(title)s (%(height)sp).%(ext)s'),
            'progress_hooks': [progress_hook],
            'quiet': True,
        }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                title = info.get("title") or url
                window.after(0, lambda t=title: file_title.configure(text="Title : " + t))
            except Exception:
                title = url
            ydl.download([url])
        return True, title
    except Exception as e:
        s = re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', str(e))
        s = s.strip()
        s = re.sub(r'^(ERROR|WARNING):\s*', '', s, flags=re.IGNORECASE)
        s = re.sub(r'\[generic\]\s*', '', s, flags=re.IGNORECASE)
        s = re.sub(r'\s*\[[^\]]+\]\s*$', '', s)
        lines = [ln.strip() for ln in s.splitlines() if ln.strip()]
        error_message = lines[0] if lines else s
        return False, error_message

def multi_download(links_text, output_format, resolution):
    links = re.findall(r'https?://[^\s,]+' , links_text)
    if not links:
        links = [ln.strip() for ln in links_text.splitlines() if ln.strip()]
    window.after(0, lambda: (multi_link_logs.configure(state="normal"), multi_link_logs.delete("0.0", "end"), multi_link_logs.see('end'), multi_link_logs.configure(state="disabled")))
    for url in links:
        if stop_event.is_set():
            return
        success, msg = download_one(url, output_format, resolution, None)
        if success:
            append_multi_link_log(f"{msg} - Completed\n")
        else:
            append_multi_link_log(f"Error: {msg}\n")
        time.sleep(0.2)
    time.sleep(0.1)
    append_multi_link_log("download completed\n")
    window.after(0, lambda: (heading_label.configure(text="Download Complete"), go_back_button.place(x=830, y=450)))

def append_multi_link_log(message):
    def _append():
        multi_link_logs.configure(state="normal")
        multi_link_logs.insert("end", message)
        multi_link_logs.see('end')
        multi_link_logs.configure(state="disabled")
    window.after(0, _append)

# -----------------------< UI views >-----------------------

def show_main_view():
    heading_label.configure(text="Youtube Video/Audio Downloader")
    link_Entry.place(relx=0.5, y=220, anchor='center')
    set_download_path.place(x=10, y=400)
    download_Button.place(relx=0.5, y=470, anchor="center")
    file_type.place(x=200, y=400)
    file_type_label.place(x=195, y=370)
    if file_type.get() == "video":
        res.place(x=550, y=400)
        res_label.place(x=650, y=370)
    else:
        res.place_forget()
        res_label.place_forget()
    if input_link_type.get() == "Single link":
        link_Entry.place(relx=0.5, y=220, anchor='center')
        multi_link_input.place_forget()
    else:
        link_Entry.place_forget()
        multi_link_input.place(relx=0.5, y=220, anchor='center')
    download_Progressbar.place_forget()
    download_Label.place_forget()
    file_title.place_forget()
    input_link_type.place(x=320, y=400)
    input_link_type_label.place(x=345, y=370)
    multi_link_logs.place_forget()
    go_back_button.place_forget()

def show_download_view():
    heading_label.configure(text="Downloading...")
    set_download_path.place_forget()
    link_Entry.place_forget()
    download_Button.place_forget()
    file_type.place_forget()
    res.place_forget()
    file_type_label.place_forget()
    res_label.place_forget()
    input_link_type.place_forget()
    input_link_type_label.place_forget()
    download_Progressbar.set(0)
    download_Label.configure(text="0 %")
    multi_link_input.place_forget()
    if input_link_type.get() == "Single link":
        file_title.place(relx=0.5, y=250, anchor="center")
        download_Progressbar.place(relx=0.5, y=300, anchor="center")
        download_Label.place(relx=0.5, y=350, anchor="center")
        multi_link_logs.place_forget()
    else:
        file_title.place(relx=0.5, y=420, anchor="center")
        download_Progressbar.place(relx=0.5, y=450, anchor="center")
        download_Label.place(relx=0.5, y=480, anchor="center")
        multi_link_logs.place(relx=0.5, y=240, anchor="center")
        multi_link_logs.configure(state="normal")
        multi_link_logs.delete("0.0", "end")
        multi_link_logs.configure(state="disabled")

# -----------------------< button/function actions >-----------------------

def download_button():
    if not internet_connected():
        alert(text="No internet connection", title="Error", button="OK")
        return
    file_title.configure(text="Title : ")
    selected_input = input_link_type.get()
    if selected_input == "Single link":
        if link_Entry.get().strip() == "":
            threading.Thread(target=enter_link_popup).start()
            return
    else:
        if multi_link_input.get("0.0", "end").strip() == "":
            threading.Thread(target=enter_link_popup).start()
            return
    show_download_view()
    if selected_input == "Multiple links":
        links_text = multi_link_input.get("0.0", "end").strip()
        threading.Thread(
            target=multi_download,
            args=(links_text, file_type.get(), res.get()),
            daemon=True
        ).start()
    else:
        threading.Thread(
            target=download,
            args=(link_Entry.get().strip(), file_type.get(), res.get()),
            daemon=True
        ).start()

def on_file_type_change(type):
    if type == "audio":
        res.place_forget()
        res_label.place_forget()
    else:
        res.place(x=550, y=400)
        res_label.place(x=650, y=370)

def on_input_link_type_change(type):
    if type == "Single link":
        link_Entry.place(relx=0.5, y=220, anchor='center')
        multi_link_input.place_forget()
    else:
        link_Entry.place_forget()
        multi_link_input.place(relx=0.5, y=220, anchor='center')

def enter_link_popup():
    enter_link_show_label.place(x=670, y=470, anchor="center")
    time.sleep(0.5)
    enter_link_show_label.place_forget()
    time.sleep(0.5)
    enter_link_show_label.place(x=670, y=470, anchor="center")
    time.sleep(0.5)
    enter_link_show_label.place_forget()
    time.sleep(0.5)
    enter_link_show_label.place(x=670, y=470, anchor="center")
    time.sleep(0.5)
    enter_link_show_label.place_forget()

def go_Back_button():
    link_Entry.delete(0, "end")
    multi_link_input.delete("0.0", "end")
    show_main_view()

def Appearance(type):
    if type == "System Mode":
        ctk.set_appearance_mode("system")
    elif type == "Light Mode":
        ctk.set_appearance_mode("light")
    else:
        ctk.set_appearance_mode("dark")

# -----------------------< download path set function >-----------------------

def set_Download_path():
    global download_path, path, path_label
    try:
        selected = fd.askdirectory(title="Select download folder")
        if selected:
            download_path = Path(selected)
            default_dl = Path.home() / "Downloads"
            if download_path == default_dl:
                path = "downloads"
            elif download_path == Path.home():
                path = "home"
            else:
                path = "custom"
            try:
                path_label.configure(text=f"Downloads to '{download_path}'")
            except Exception:
                pass
    except Exception as e:
        alert(text=str(e), title='Error', button='OK')

# -----------------------< shutdown all threads >-----------------------

def on_closing():
    stop_event.set()
    window.destroy()

# -----------------------< check internet connection >-----------------------

def internet_connected(timeout=3):
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=timeout)
        return True
    except OSError:
        return False

# -----------------------< Main Code >-----------------------

if __name__ == "__main__":
    file_title = ctk.CTkLabel(window, text="Title : ", font=("Arial", 20))
    heading_label = ctk.CTkLabel(window, text="Youtube Video/Audio Downloader", font=("Arial", 30))
    heading_label.place(relx=0.5, y=50, anchor="center")
    file_type_label = ctk.CTkLabel(window, text="Select file type", font=("Arial", 15))
    res_label = ctk.CTkLabel(window, text="Select resolution", font=("Arial", 15))
    link_Entry = ctk.CTkEntry(window, placeholder_text="Paste Youtube link here", width=600)
    download_Button = ctk.CTkButton(window, text="Download", command=download_button)
    download_Progressbar = ctk.CTkProgressBar(window, orientation="horizontal")
    download_Label = ctk.CTkLabel(window, text="0 %", fg_color="transparent")
    file_type = ctk.CTkSegmentedButton(window, values=["video", "audio"], command=on_file_type_change)
    file_type.set("video")
    res = ctk.CTkSegmentedButton(window, values=["144p", "240p", "360p", "480p", "720p", "1080p", "2k", "4k", "8k"])
    res.set("480p")
    multi_link_input = ctk.CTkTextbox(window, width=600, height=250)
    input_link_type = ctk.CTkSegmentedButton(window, values=["Single link", "Multiple links"], command=on_input_link_type_change)
    input_link_type.set("Single link")
    input_link_type_label = ctk.CTkLabel(window, text="Select Input type", font=("Arial", 15))
    multi_link_logs = ctk.CTkTextbox(window, width=500, height=300, state="disabled")
    enter_link_show_label = ctk.CTkLabel(window, text="please enter link", font=("Arial", 15), text_color="red")
    enter_link_show_label.place_forget()
    if path == "downloads":
        path_label = ctk.CTkLabel(window, text="Downloads to 'Download folder'", font=("Arial", 15), text_color="purple")
    else:
        path_label = ctk.CTkLabel(window, text="Downloads to 'home folder'", font=("Arial", 15), text_color="purple")
    path_label.place(x=20, y=460)
    go_back_button = ctk.CTkButton(window, text="Go Back", command=go_Back_button)
    set_download_path = ctk.CTkButton(window, text="Set Download Folder", command=set_Download_path)
    appearance = ctk.CTkSegmentedButton(window, values=["System Mode", "Light Mode", "Dark Mode"], command=Appearance)
    appearance.set("System Mode")
    appearance.place(x=745, y=10)

    show_main_view()
    window.protocol("WM_DELETE_WINDOW", on_closing)
    window.mainloop()