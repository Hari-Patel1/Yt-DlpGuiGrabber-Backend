# 📦 Yt_Dlp Client Backend (Python + FastAPI)

This is a lightweight backend API built using **FastAPI** and **Uvicorn**, designed to integrate with the Yt_Dlp frontend Flutter application. It can be extended to support tasks like:

- Handling API requests from your Flutter app
- Managing video/audio downloads (e.g., via `yt-dlp`)
- Running Python logic (e.g., ML models, data scraping)
- User authentication, preferences, or storage

  <!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Music Tagging Backend README</title>
</head>
<body>
  <h1>Music Tagging Backend (FastAPI)</h1>

  <p>This repository contains the backend API service for the music tagging project.<br/>
  Built with FastAPI and Python, it handles metadata extraction, audio file tagging operations, and integration with the frontend app.</p>

  <h2>Features</h2>
  <ul>
    <li>REST API for receiving audio files or metadata requests</li>
    <li>Extracts metadata using FFmpeg and other audio libraries</li>
    <li>Supports tagging audio files with metadata updates</li>
    <li>Streams progress and logging for frontend consumption</li>
  </ul>

  <h2>Getting Started</h2>
  <h3>Prerequisites</h3>
  <ul>
    <li>Python 3.9 or higher</li>
    <li>FFmpeg installed and accessible in system PATH</li>
    <li>Virtual environment tool (recommended)</li>
  </ul>

  <h3>Installation</h3>
  <ol>
    <li>Clone this repository:<br/>
      <code>git clone https://github.com/yourusername/backend-repo.git</code></li>
    <li>Navigate to the project directory:<br/>
      <code>cd backend-repo</code></li>
    <li>Create and activate a virtual environment:<br/>
      <code>python -m venv venv</code><br/>
      <code>source venv/bin/activate</code> (Linux/macOS)<br/>
      <code>venv\Scripts\activate</code> (Windows)</li>
    <li>Install dependencies:<br/>
      <code>pip install -r requirements.txt</code></li>
  </ol>

  <h3>Running the Server</h3>
  <p>Use the following command to start the backend server:</p>
  <pre><code>uvicorn src.main:app --host 0.0.0.0 --port 8000</code></pre>

  <h2>API Endpoints</h2>
  <ul>
    <li><code>POST /extract-metadata</code>: Extract metadata from uploaded audio files</li>
    <li><code>POST /tag-audio</code>: Save updated tags to audio files</li>
    <li><code>GET /status</code>: Check server status and health</li>
  </ul>

  <h2>Environment Variables</h2>
  <p>Configure your environment variables in a <code>.env</code> file as needed (e.g., paths, API keys).</p>

  <h2>Testing</h2>
  <p>Run tests using:</p>
  <pre><code>pytest</code></pre>

  <h2>Contributions</h2>
  <p>Feel free to contribute by submitting issues or pull requests.</p>

  <h2>License</h2>
  <p><a href="LICENSE">MIT License</a></p>
</body>
</html>


---


