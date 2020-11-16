from flask import Flask, send_from_directory, render_template
import gi

gi.require_version('Gst', '1.0')

from gi.repository import Gst, GObject  # noqa: E402

GObject.threads_init()
Gst.init(None)

app = Flask(__name__, template_folder='template')

DEBUG = False

if DEBUG:
    src = "videotestsrc"
else:
    src = 'v4l2src device="/dev/video0"'

launch_string = "%s ! videoconvert ! clockoverlay ! " \
                "x264enc tune=zerolatency ! mpegtsmux ! " \
                "hlssink location=video/usb_camera.%%05d.ts playlist-location=video/usb_camera.m3u8 max-files=10 target-duration=1" % src

pipeline = Gst.parse_launch(launch_string)
pipeline.set_state(Gst.State.PLAYING)


@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video/<string:file_name>')
def stream(file_name):
    video_dir = './video'
    return send_from_directory(directory=video_dir, filename=file_name)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)
