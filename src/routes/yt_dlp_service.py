from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import asyncio
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
async def download_stream(request: Request):
    data = await request.json()

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

        # Do not add --write-thumbnail to avoid separate album art file

        command.extend(["-o", output_template])
        command.append(url)

        return command

    cmd = build_yt_dlp_command(data)
    print("Running command:", " ".join(cmd))

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        text=True,
    )

    async def event_generator():
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            # Send each line as an SSE message
            yield f"data: {line.strip()}\n\n"

        await process.wait()
        yield "data: [Download complete]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
