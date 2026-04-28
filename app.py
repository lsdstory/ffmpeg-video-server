from flask import Flask, request, jsonify
import subprocess
import requests
import os
import uuid
import tempfile

app = Flask(__name__)

def download_file(url, path):
    r = requests.get(url, stream=True)
    with open(path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

@app.route('/extract-frame', methods=['POST'])
def extract_frame():
    data = request.json
    video_url = data['video_url']
    timestamp = data.get('timestamp', 0)
    tmp_dir = tempfile.mkdtemp()
    video_path = os.path.join(tmp_dir, 'input.mp4')
    frame_path = os.path.join(tmp_dir, 'frame.jpg')
    download_file(video_url, video_path)
    subprocess.run(['ffmpeg', '-ss', str(timestamp), '-i', video_path, '-vframes', '1', '-q:v', '2', frame_path], check=True)
    with open(frame_path, 'rb') as f:
        import base64
        encoded = base64.b64encode(f.read()).decode('utf-8')
    return jsonify({'frame_base64': encoded, 'timestamp': timestamp})

@app.route('/cut-clip', methods=['POST'])
def cut_clip():
    data = request.json
    video_url = data['video_url']
    start = data.get('start', 0)
    length = data.get('length', 3)
    tmp_dir = tempfile.mkdtemp()
    video_path = os.path.join(tmp_dir, 'input.mp4')
    output_path = os.path.join(tmp_dir, 'output.mp4')
    download_file(video_url, video_path)
    subprocess.run(['ffmpeg', '-ss', str(start), '-i', video_path, '-t', str(length), '-c', 'copy', output_path], check=True)
    with open(output_path, 'rb') as f:
        import base64
        encoded = base64.b64encode(f.read()).decode('utf-8')
    return jsonify({'clip_base64': encoded})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
