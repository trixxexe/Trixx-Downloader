import flet as ft
import yt_dlp
import os
import threading

def main(page: ft.Page):
    # --- App Window Setup ---
    page.title = "Trixx Downloader"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#050505"
    page.padding = 30
    page.window_width = 400
    page.window_height = 700

    # --- UI Elements ---
    title_text = ft.Text("TRIXX DOWNLOADER", size=28, weight="bold", color="#ff00ff")
    subtitle_text = ft.Text("Created by Ritam / Azure\nDon't skid losers!", size=12, color="#00ffff", text_align="center")
    
    url_input = ft.TextField(
        label="Paste Video Link", 
        border_color="#00ffff", 
        color="#ffffff",
        cursor_color="#ff00ff"
    )
    
    format_dropdown = ft.Dropdown(
        label="Select Format",
        border_color="#00ffff",
        color="#ffffff",
        options=[
            ft.dropdown.Option("Video (MP4)"),
            ft.dropdown.Option("Audio Only (M4A)"),
        ],
        value="Video (MP4)"
    )

    status_text = ft.Text("Ready.", color="#aaaaaa", size=14)
    progress_bar = ft.ProgressBar(width=300, color="#ff00ff", bgcolor="#222222", value=0)
    progress_bar.visible = False

    # --- Download Logic ---
    def progress_hook(d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded = d.get('downloaded_bytes', 0)
            if total:
                percent = downloaded / total
                progress_bar.value = percent
                status_text.value = f"Downloading: {percent:.1%}"
                page.update()
        elif d['status'] == 'finished':
            status_text.value = "Finalizing file..."
            progress_bar.value = 1.0
            page.update()

    def execute_download(url, format_choice):
        # Setup Android Downloads path
        # Fallback to app directory if storage permissions aren't set yet
        download_path = os.path.join(os.environ.get('EXTERNAL_STORAGE', '/storage/emulated/0'), 'Download', 'Trixx')
        if not os.path.exists(download_path):
            try:
                os.makedirs(download_path)
            except:
                download_path = os.getcwd() # Fallback

        # Configure formats for mobile (No FFmpeg required)
        if format_choice == "Video (MP4)":
            ydl_format = 'best[ext=mp4]/best'
        else:
            ydl_format = 'bestaudio[ext=m4a]/best'

        ydl_opts = {
            'format': ydl_format,
            'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [progress_hook]
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            status_text.value = f"✔️ Saved to Downloads/Trixx"
            status_text.color = "#00ff00"
        except Exception as e:
            status_text.value = f"❌ Error: Could not download."
            status_text.color = "#ff0000"
        
        # Reset UI
        download_btn.disabled = False
        url_input.disabled = False
        format_dropdown.disabled = False
        progress_bar.visible = False
        page.update()

    def on_download_click(e):
        url = url_input.value.strip()
        if not url:
            status_text.value = "Please enter a valid link."
            status_text.color = "#ff0000"
            page.update()
            return

        # Update UI for downloading state
        status_text.value = "Starting download..."
        status_text.color = "#ffff00"
        download_btn.disabled = True
        url_input.disabled = True
        format_dropdown.disabled = True
        progress_bar.value = 0
        progress_bar.visible = True
        page.update()

        # Run download in a background thread so the app doesn't freeze
        threading.Thread(target=execute_download, args=(url, format_dropdown.value), daemon=True).start()

    download_btn = ft.ElevatedButton(
        text="DOWNLOAD", 
        bgcolor="#ff00ff", 
        color="#ffffff", 
        width=300, 
        height=50,
        on_click=on_download_click
    )

    # --- Build the Page ---
    page.add(
        ft.Column(
            [
                ft.Container(height=20),
                title_text,
                subtitle_text,
                ft.Container(height=30),
                url_input,
                format_dropdown,
                ft.Container(height=20),
                download_btn,
                ft.Container(height=20),
                progress_bar,
                status_text
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
  
