from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pathlib import Path
import subprocess
import json
import shutil
import os
import uuid
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/download")
async def download(request: Request):
    try:
        data = await request.json()
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON payload"})

    # Validate required fields
    url = data.get("url", "").strip()
    if not url:
        return JSONResponse(status_code=400, content={"error": "Missing 'url' in request"})

    # Use provided directory or fallback to user's Downloads
    destinationDirectory = data.get("downloadDirectory")
    if not destinationDirectory:
        destinationDirectory = str(Path.home() / "Downloads")
    else:
        destinationDirectory = os.path.abspath(destinationDirectory)

    client_ip = request.client.host or "unknown"
    logger.info(f"Client IP: {client_ip}")

    # Create unique temp folder per request
    request_id = uuid.uuid4().hex
    temp_dir = Path("temp_downloads") / f"{client_ip}_{request_id}"
    temp_dir.mkdir(parents=True, exist_ok=True)

    def build_yt_dlp_command(data: dict) -> list:
        yt_dlp_path = os.getenv("YTDLP_PATH", "C:\\Tools\\yt-dlp.exe")
        command = [yt_dlp_path]

        ext = data.get("extension", "mp4").strip().lower()
        audio_only = data.get("audioOnly", False)
        audio_quality = data.get("audioQuality", "128k").strip()
        video_quality = data.get("videoQuality", "1080p").strip()
        embed_thumbnail = data.get("embedThumbnail", False)
        add_metadata = data.get("addMetadata", False)

        output_template = str(temp_dir / "%(title)s - %(uploader)s.%(ext)s")

        if audio_only or ext == "mp3":
            command.append("--extract-audio")
            command += ["--audio-format", ext]
            command += ["--audio-quality", audio_quality]
            command += ["-f", "bestaudio"]
        else:
            command += ["--recode-video", ext]
            command += ["-f", f"bv*[height<={video_quality}]+ba/b[height<={video_quality}]"]

        if embed_thumbnail:
            command.append("--embed-thumbnail")
        if add_metadata:
            command.append("--add-metadata")

        command += ["-o", output_template, url]
        return command

    cmd = build_yt_dlp_command(data)

    def stream_process():
        yield f"data: {json.dumps({'type': 'status', 'message': 'Preparing download folder'})}\n\n"

        logger.info(f"Running command: {' '.join(cmd)}")
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

        if process.returncode != 0:
            yield f"data: {json.dumps({'type': 'error', 'message': f'yt-dlp failed with code {process.returncode}'})}\n\n"
            return

        yield f"data: {json.dumps({'type': 'status', 'message': 'Moving files to final directory'})}\n\n"

        try:
            destination_path = Path(destinationDirectory)
            destination_path.mkdir(parents=True, exist_ok=True)

            for file in temp_dir.iterdir():
                target_file = destination_path / file.name
                shutil.move(str(file), str(target_file))
                yield f"data: {json.dumps({'type': 'moved', 'message': f'Moved {file.name}'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': f'Failed to move files: {str(e)}'})}\n\n"
            return

        yield f"data: {json.dumps({'type': 'done', 'message': 'Download and move complete'})}\n\n"

        # Cleanup temp folder
        # shutil.rmtree(temp_dir, ignore_errors=True)

    return StreamingResponse(stream_process(), media_type="text/event-stream")
