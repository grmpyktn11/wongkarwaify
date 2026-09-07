# python:3.12-slim to match runtime.txt. The full image is 700 MB heavier and
# nothing here needs a compiler - every wheel in requirements.txt is prebuilt
# for manylinux, opencv-python-headless included.
FROM python:3.12-slim

# PYTHONUNBUFFERED so gunicorn's stdout reaches `docker logs` as it happens
# rather than in 8 KB bursts.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Requirements first: this layer only rebuilds when the pins change, so editing
# app.py does not re-download opencv.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# movie_stats.json is the whole grade, and app.py reads it at import. The frame
# folders are ~200 MB and deliberately not here - see .dockerignore.
COPY app.py apply.py analyzeData.py movie_stats.json ./
COPY templates/ templates/
COPY static/ static/

# Results are written here per request and swept after 30 minutes. Nothing in
# it needs to survive a restart.
RUN mkdir -p static/out && \
    useradd --create-home --uid 10001 wkw && \
    chown -R wkw:wkw /app
USER wkw

EXPOSE 8000

# Same command as the Procfile. Two workers because each holds its own float32
# copies of the image being graded; four threads because the work is in numpy,
# which drops the GIL.
CMD ["sh", "-c", "gunicorn app:app --workers 2 --threads 4 --timeout 60 --bind 0.0.0.0:${PORT}"]
