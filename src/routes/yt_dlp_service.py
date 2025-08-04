from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import subprocess
import json

router = APIRouter()

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

        command.extend(["-o", output_template])
        command.append(url)
        return command

    cmd = build_yt_dlp_command(data)
    print("Running command:", " ".join(cmd))

    def stream_process():
        yield f"data: {json.dumps({'type': 'status', 'message': 'Download started'})}\n\n"
        yield f"data: {json.dumps({'type': 'command', 'message': ' '.join(cmd)})}\n\n"

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        for line in iter(process.stdout.readline, ''):
            line = line.strip()
            if not line:
                continue

            # Basic parsing for status vs progress vs error
            if "Downloading" in line:
                event_type = "download"
            elif "ERROR" in line or "Error" in line:
                event_type = "error"
            elif "Merger" in line or "Merging" in line:
                event_type = "merge"
            elif "Destination" in line:
                event_type = "save"
            else:
                event_type = "info"

            yield f"data: {json.dumps({'type': event_type, 'message': line})}\n\n"

        process.stdout.close()
        process.wait()

        yield f"data: {json.dumps({'type': 'done', 'message': 'Download finished'})}\n\n"

    return StreamingResponse(stream_process(), media_type="text/event-stream")
