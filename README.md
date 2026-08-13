# Joscam

Real-time virtual camera enhancement app for Linux.

Joscam processes your physical webcam in real time and exposes the result as a virtual camera that can be used in apps such as Google Meet, Zoom, Discord, OBS, and other webcam-compatible applications.

## Features

* Real-time webcam preview
* Virtual camera output
* Basic adjustments

  * Brightness
  * Contrast
  * Gamma
* Light adjustments

  * Exposure
  * Highlights
  * Shadows
* Color adjustments

  * Saturation
  * Temperature
  * Tint
* Detail effects

  * Skin smoothing
  * Blur
  * Clarity
  * Sharpness
* Film effects

  * Fade
  * Vignette
  * Film grain
* Camera presets

  * Neutral
  * Natural
  * Soft
  * Cinematic
  * Moody
  * Film
  * Warm
  * Cool
  * Portrait
  * Youth
* Filters / Looks

  * Social-style looks
  * Cinematic looks
  * Adjustable intensity
* Frame effects

  * Circle
  * Oval
  * Rounded rectangle
  * Retro 70s
  * Retro 90s
  * Custom colors

Joscam currently uses traditional image processing with OpenCV and NumPy. No AI model is required for the core effects.

## Tech Stack

* Python
* OpenCV
* NumPy
* PySide6
* pyvirtualcam
* v4l2loopback
* uv

## Requirements

* Linux
* Python 3
* Webcam
* `v4l2loopback`

Joscam is currently developed and tested primarily for Linux Mint.

## Installation

Install system dependencies:

```bash
sudo apt update

sudo apt install \
  v4l2loopback-dkms \
  v4l-utils \
  libxcb-cursor0
```

Clone the project and install Python dependencies:

```bash
git clone https://github.com/omkz/joscam.git
cd joscam

uv sync
```

## Virtual Camera Setup

Load `v4l2loopback`:

```bash
sudo modprobe v4l2loopback \
  devices=1 \
  exclusive_caps=1 \
  card_label="Joscam"
```

Check available video devices:

```bash
v4l2-ctl --list-devices
```

You should see a virtual camera named `Joscam`.

## Running Joscam

```bash
uv run python -m joscam.main
```

Then select **Joscam** as the camera source in your video application.

## Project Structure

```text
joscam/
├── joscam/
│   ├── effects/
│   ├── filters/
│   ├── frames/
│   ├── ui/
│   ├── camera.py
│   ├── pipeline.py
│   ├── presets.py
│   ├── settings.py
│   └── main.py
├── pyproject.toml
├── uv.lock
└── README.md
```

## Processing Pipeline

```text
Physical Camera
      ↓
Basic / Light / Color
      ↓
Detail Effects
      ↓
Filter / Look
      ↓
Film Effects
      ↓
Frame
      ↓
Joscam Virtual Camera
```

## Development

Run Joscam:

```bash
uv run python -m joscam.main
```

Add a dependency:

```bash
uv add <package>
```

## Status

Joscam is under active development.

Current focus:

* smooth real-time 30 FPS processing
* webcam enhancement
* configurable presets
* social and cinematic filters
* customizable frame styles
