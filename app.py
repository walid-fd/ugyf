from flask import Flask, request, send_file
import subprocess
import os
import time

app = Flask(__name__)

@app.route('/download', methods=['GET'])
def download_file():
    video_url = request.args.get('url')
    file_type = request.args.get('type', 'video')

    if not video_url:
        return "URL is missing", 400

    timestamp = int(time.time())

    if file_type == 'audio':
        file_name = f"audio_{timestamp}.mp3"
        # استخراج وتحويل الصوت بأقصى سرعة ممكنة وبدون انتظار معالجة بطيئة
        cmd = f"yt-dlp -x --audio-format mp3 --audio-quality 5 --concurrent-fragments 5 -o \"{file_name}\" \"{video_url}\""
        mimetype = 'audio/mpeg'
    else:
        file_name = f"video_{timestamp}.mp4"
        # اختيار صيغة خفيفة وسريعة جداً (-f 22/18) لضمان التحميل الفوري
        cmd = f"yt-dlp -f \"22/18/b[height<=480]\" --concurrent-fragments 5 -o \"{file_name}\" \"{video_url}\""
        mimetype = 'video/mp4'

    # تنفيذ الأمر بأقصى سرعة
    result = subprocess.run(cmd, shell=True)

    if result.returncode != 0 or not os.path.exists(file_name):
        return "Download failed", 500

    try:
        return send_file(file_name, as_attachment=True, mimetype=mimetype)
    except Exception as e:
        return str(e), 500
    finally:
        # حذف الملف فوراً بعد الإرسال لتفريغ الذاكرة
        time.sleep(1)
        if os.path.exists(file_name):
            try:
                os.remove(file_name)
                print(f"[SUPER-SPEED CLEANUP] Deleted: {file_name}")
            except Exception as e:
                print(f"[CLEANUP ERROR]: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
