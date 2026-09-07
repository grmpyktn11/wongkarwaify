# WKW-ify

Measures the colour grade of two Wong Kar-wai films and applies it to your photo.

A computational photography project. Nothing here is a hand-tuned preset. Every
parameter comes from the films, by sampling 99 frames from each and averaging
four numbers.

Films: *In the Mood for Love* (花樣年華, 2000) and *Fallen Angels* (墮落天使, 1995).

## What the films measure

One frame every 60 seconds of runtime. For each frame we compute the channel
means, the mean HSV saturation, and a gamma estimate, then average all 99.

| Statistic | 花樣年華 | 墮落天使 | What it means |
|---|---|---|---|
| `avgRoverGray` | 1.4046 | 1.2717 | Red runs heavy |
| `avgBoverGray` | 0.5462 | 0.7127 | Blue runs light |
| `meanSaturation` | 165.2 | 127.2 | 65% and 50% of maximum |
| `estimatedGamma` | 0.3772 | 0.3769 | Both films sit at 15.9% brightness |

These live in `movie_stats.json`, which the app reads at startup. Rebuild them
with `getFrames.py` then `getStats.py`.

## The pipeline

`stylizeImage()` in `apply.py`, five stages in order.

**1. White balance.** Average a whole film and you get its colour cast. We
multiply your red and blue channels by the film's numbers.

```
R ← R × 1.4046      B ← B × 0.5462
```

Caveat: this adds the film's cast on top of yours. It assumes your photo starts
neutral.

**2. Saturation.** Measure how saturated your photo is, then scale it to match
the film.

```
S ← S × (S_film / S_photo)
```

This stage reads your image first, so a vivid photo gets toned down.

**3. Colour grade.** Split the image into dark, mid and bright areas by
luminance, then tint each one at 0.4 strength.

| Mask | Formula | Peaks at | Tint (RGB) |
|---|---|---|---|
| Shadows | `clip(1 − 2L)` | black | `(20, 120, 40)` green |
| Midtones | `1 − \|L − 0.5\| × 2` | middle gray | `(120, 20, 120)` magenta |
| Highlights | `clip(2L − 1)` | white | `(200, 200, 40)` yellow |

Caveat: both films use the same tints right now.

**4. Contrast curve.** An S-curve per channel, fixing 0, 0.5 and 1 in place.

```
f(x) = x^p / (x^p + (1−x)^p)
```

`p = 1` is no change. Red is 1.2, green is 1.0, blue is 1.4. Blue bends most, so
blue shadows go darker and blue highlights go brighter.

**5. Brightness.** Solve for the exponent that maps the film's mean luminance
onto middle gray, then apply its inverse.

```
γ = log(0.5) / log(L̄)        out = in^(1/γ)
```

Both films sit at 15.9% brightness. They are shot at night, in corridors,
through doorways. That gives `γ = 0.377` and an exponent of 2.65, which does
most of the work.

Caveat: also the harshest step. It turns 0.50 into 0.159, so a daylight photo
goes to mud.

**Then mix it back.** The result is blended with your original, 70 to 30.

```python
cv2.addWeighted(styled, 0.70, original, 0.30, 0.0)
```

That brings the brightness back without losing the colour. `GRADE_STRENGTH` in
`app.py` is the only constant here chosen by eye.

## Known limitations

- **The tints are shared.** Both films use the same three-way tints and curve
  powers, so only white balance, saturation and gamma actually differ. The two
  gammas match to three decimals. Deriving tints per film would fix this.
- **Stages 1 and 5 ignore your image.** They apply the film's absolute numbers
  instead of the ratio between the film's and yours. For gamma the fix is
  `γ = log(L̄_film) / log(L̄_photo)`.
- **Gray-world is a weak illuminant estimator.** It fails on images dominated by
  one hue. Shades-of-gray would be more robust.

## Run it

```bash
git clone https://github.com/grmpyktn11/wongkarwaify.git
cd wongkarwaify
python -m venv .venv && .venv/bin/pip install -r requirements.txt
python app.py
```

Open `http://localhost:5000`. No API keys, no network calls, fully offline.
Startup is instant because the app reads `movie_stats.json` instead of
re-analysing frames, so a fresh clone works without the frame folders (which are
gitignored, about 200 MB).

`FLASK_DEBUG=1` enables the reloader. `PORT` changes the port. `GET /health`
reports liveness.

To add a film: `python getFrames.py` then `python getStats.py`.

## Deploy

`requirements.txt` pins `opencv-python-headless`. The normal `opencv-python`
wheel links `libGL.so.1`, which minimal container images do not ship.

Behind nginx, set `client_max_body_size 12M;` to match `MAX_CONTENT_LENGTH` in
`app.py`, or uploads fail at the proxy before Flask sees them.

Uploads are capped at 12 MB and downscaled to a 2000px long edge before any
float conversion, since `stylizeImage` holds several `float32` copies at once.
Results are written per request under `static/out/` and swept after 30 minutes.

## Layout

```
wongkarwaify/
├── app.py            # routes, uploads, result lifecycle
├── apply.py          # the five grading stages
├── analyzeData.py    # frame statistics and gamma estimation
├── getFrames.py      # video to frames
├── getStats.py       # frames to movie_stats.json
├── movie_stats.json  # the committed grade
├── templates/        # the interface
└── static/out/       # generated results (gitignored)
```

## License

MIT.

## Acknowledgments

The cinematography of Christopher Doyle, and Wong Kar-wai.
