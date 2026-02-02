# Wongkarwaify

A web application that applies cinematic color grading from Wong Kar-wai films to your photos.

## What it does

Upload a photo and apply the distinctive color palette and visual style from iconic Wong Kar-wai movies. The app analyzes frames from films like "Fallen Angels" and "In the Mood for Love" to extract their color characteristics, then applies that same look to your images.

## Features

- Apply color grading from multiple Wong Kar-wai films
- Automated white balance, saturation, and gamma adjustments
- Three-way color grading (shadows, midtones, highlights)
- Web-based interface for easy use
- Download your styled images

## Installation

```bash
# Clone the repository
git clone https://github.com/grmpyktn11/wongkarwaify.git
cd wongkarwaify

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Running the web app

```bash
python app.py
```

Then open your browser to `http://localhost:5000`

### Extracting frames from a video

If you want to analyze a different movie:

```bash
python getFrames.py
```

Edit the video path in the script to point to your video file. Frames will be extracted every 60 seconds by default.

### Analyzing frames

After extracting frames, analyze them to get color statistics:

```bash
python getStats.py
```

This creates a JSON file with the color grading parameters.

## How it works

1. **Frame extraction**: Sample frames are taken from the source movies at regular intervals
2. **Statistical analysis**: Each frame is analyzed for color balance, saturation, and gamma
3. **Style transfer**: Your uploaded image is adjusted to match the computed statistics using various color grading techniques

The color grading process includes:
- White balance adjustment using Gray World algorithm
- Saturation matching
- Three-way color grading for shadows, midtones, and highlights
- Per-channel curve adjustments
- Gamma correction

## Requirements

- Python 3.7+
- OpenCV (cv2)
- Flask
- NumPy

## Project Structure

```
wongkarwaify/
├── app.py              # Flask web application
├── apply.py            # Image stylization functions
├── analyzeData.py      # Frame analysis tools
├── getFrames.py        # Video frame extraction
├── getStats.py         # Statistics computation
├── templates/          # HTML templates
└── static/             # Static files and outputs
```

## License

MIT License

## Acknowledgments

Inspired by the cinematography of Christopher Doyle and the visual aesthetics of Wong Kar-wai's films.
