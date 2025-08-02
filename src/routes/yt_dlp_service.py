from fastapi import APIRouter, Request
import subprocess

router = APIRouter()

@router.get("/ping")
def ping():
    return {"message": "pong"}

@router.post("/echo")
async def echo(request: Request):
    data = await request.json()
    return {"you_sent": data}

@router.post("/download")
async def download(request: Request):
    data = await request.json()
    destinationDirectory = data["downloadDirectory"]
    print("Received data:", data)

    def build_yt_dlp_command(data: dict) -> list:
        command = ["C:\\Tools\\yt-dlp.exe"]

        url = data.get("url", "").strip()
        ext = data.get("extension", "mp4").strip().lower()
        audio_only = data.get("audioOnly", False)
        audio_quality = data.get("audioQuality", "128k").strip()
        video_quality = data.get("videoQuality", "1080p").strip()
        embed_thumbnail = data.get("embedThumbnail", False)
        download_album_art = data.get("downloadAlbumArt", False)  # we'll ignore this for separate download
        add_metadata = data.get("addMetadata", False)

        output_template = "%(title)s - %(uploader)s.%(ext)s"

        if audio_only or ext == "mp3":
            command.append("--extract-audio")
            command.extend(["--audio-format", ext])
            command.extend(["--audio-quality", audio_quality])
            command.extend(["-f", "bestaudio"])
        else:
            command.extend(["--recode-video", ext])
            command.extend(["-f", f"bv*[height<={video_quality}]+ba/b[height<={video_quality}]"])

        if embed_thumbnail:
            command.append("--embed-thumbnail")

        if add_metadata:
            command.append("--add-metadata")

        # REMOVE --write-thumbnail so album art is NOT saved separately
        # if download_album_art:
        #     command.append("--write-thumbnail")  # <-- remove this line

        command.extend(["-o", output_template])
        command.append(url)

        return command


    cmd = build_yt_dlp_command(data)
    print("Running command:", " ".join(cmd))

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return {
            "status": "success",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "command": " ".join(cmd),
        }
    except subprocess.CalledProcessError as e:
        return {
            "status": "error",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "command": " ".join(cmd),
        }
