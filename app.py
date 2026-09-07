import json
import os
import time
import uuid

import cv2
import numpy as np
from flask import (Flask, abort, render_template, request, send_file,
                   url_for)

from apply import stylizeImage

app = Flask(__name__)

# A phone photo is routinely 8-12 MB. Anything past that is not a
# photograph, it is someone probing the box.
app.config["MAX_CONTENT_LENGTH"] = 12 * 1024 * 1024

OUT_DIR = os.path.join(app.static_folder, "out")
os.makedirs(OUT_DIR, exist_ok=True)

# Longest edge the pipeline will touch. stylizeImage holds several
# float32 copies of the frame at once, so a 6000px camera original costs
# roughly half a gigabyte of peak RSS and gets a free-tier dyno killed.
MAX_EDGE = 2000

# Results are disposable. Anything older than this is somebody else's
# finished download.
RESULT_TTL = 30 * 60

# How far toward the full grade to push. The measured gamma is ~0.377,
# which applyGamma raises to 1/0.377, and at full power that crushes most
# daylight photographs into mud. This is a fixed house setting, not a
# control -- the tool should have one opinion about how it looks.
GRADE_STRENGTH = 0.70

STATS_PATH = os.path.join(os.path.dirname(__file__), "movie_stats.json")

FILMS = {"fa": "Fallen Angels", "ml": "In the Mood for Love"}


def loadStats():
    """Read the precomputed grade.

    The numbers come from 198 sampled frames, but the sampling is a
    build step, not a boot step: the frames are ~200 MB of JPEG and are
    not in the repository, so analysing them at import time meant a
    fresh clone raised TypeError on the first upload. movie_stats.json
    is committed and holds the same figures.
    """
    with open(STATS_PATH, "r", encoding="utf-8") as fh:
        stats = json.load(fh)
    missing = set(FILMS) - set(stats)
    if missing:
        raise RuntimeError(f"movie_stats.json is missing: {sorted(missing)}")
    return stats


movieMap = loadStats()


def sweepOldResults():
    """Drop expired results. Cheap enough to run inline per upload."""
    cutoff = time.time() - RESULT_TTL
    for name in os.listdir(OUT_DIR):
        path = os.path.join(OUT_DIR, name)
        try:
            if os.path.getmtime(path) < cutoff:
                os.remove(path)
        except OSError:
            pass


def readUpload(storage):
    """Decode an upload into BGR, downscaled to MAX_EDGE.

    Decoding straight from the request buffer keeps the temp file the
    old version leaked out of the picture entirely.
    """
    buf = np.frombuffer(storage.read(), np.uint8)
    if buf.size == 0:
        return None
    img = cv2.imdecode(buf, cv2.IMREAD_COLOR)
    if img is None:
        return None

    h, w = img.shape[:2]
    edge = max(h, w)
    if edge > MAX_EDGE:
        scale = MAX_EDGE / edge
        img = cv2.resize(img, (round(w * scale), round(h * scale)),
                         interpolation=cv2.INTER_AREA)
    return img


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method != "POST":
        return render_template("index.html", done=False)

    film = request.form.get("movie")
    upload = request.files.get("file")

    if film not in movieMap:
        return render_template("index.html", done=False,
                               error="Pick a film to grade toward."), 400

    if upload is None or not upload.filename:
        return render_template("index.html", done=False, film=film,
                               error="Choose an image first."), 400

    img = readUpload(upload)
    if img is None:
        return render_template("index.html", done=False, film=film,
                               error="That file could not be read as an "
                                     "image. JPEG and PNG work best."), 400

    styled = stylizeImage(img, movieMap[film])

    styled = cv2.addWeighted(styled, GRADE_STRENGTH,
                             img, 1.0 - GRADE_STRENGTH, 0.0)

    sweepOldResults()
    token = uuid.uuid4().hex
    # One output file per request. The old build wrote every result to a
    # single static/styled.jpg, so two people uploading at once each got
    # whichever image finished last.
    cv2.imwrite(os.path.join(OUT_DIR, f"{token}-before.jpg"), img,
                [cv2.IMWRITE_JPEG_QUALITY, 88])
    cv2.imwrite(os.path.join(OUT_DIR, f"{token}-after.jpg"), styled,
                [cv2.IMWRITE_JPEG_QUALITY, 92])

    return render_template("index.html", done=True, film=film,
                           token=token)


@app.route("/download/<token>")
def download(token):
    if not token.isalnum() or len(token) != 32:
        abort(404)
    path = os.path.join(OUT_DIR, f"{token}-after.jpg")
    if not os.path.exists(path):
        abort(404)
    return send_file(path, as_attachment=True, download_name="wkw-ify.jpg")


@app.errorhandler(413)
def tooLarge(_):
    return render_template("index.html", done=False,
                           error="That image is over 12 MB. Try a smaller "
                                 "export."), 413


@app.route("/health")
def health():
    return {"ok": True, "films": sorted(movieMap)}


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1",
            port=int(os.environ.get("PORT", 5000)))
