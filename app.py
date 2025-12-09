from flask import Flask, render_template, request, send_file
import cv2
import numpy as np
import tempfile
import os
import analyzeData
from apply import stylizeImage

app = Flask(__name__)

# Precompute stats once
faStats = analyzeData.analyzeFrames("frameFA")
mlStats = analyzeData.analyzeFrames("frameITMFL")

movieMap = {
    "fa": faStats,
    "ml": mlStats
}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        movie = request.form.get("movie")
        file = request.files.get("file")

        if not file or movie not in movieMap:
            return "Error: Missing file or movie selection"

        # Save uploaded file temporarily
        tmp_in = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        file.save(tmp_in.name)

        img = cv2.imread(tmp_in.name)

        # Stylize
        stats = movieMap[movie]
        out = stylizeImage(img, stats)

        # Save output
        out_path = "static/styled.jpg"
        cv2.imwrite(out_path, out)

        return render_template("index.html", done=True)

    return render_template("index.html", done=False)

@app.route("/download")
def download():
    return send_file("static/styled.jpg", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
