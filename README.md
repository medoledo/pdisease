# Plant Disease Detector

AI-powered crop health analysis using deep learning.

**Built by:** Mohammed Essam · Malak Ahmed · Abdelrahman Noaman

---

## Overview

A Django web application that uses a trained TensorFlow MobileNetV2 model to identify plant diseases from leaf images. The model can classify **38 different plant disease classes** across multiple crop types with approximately **96% accuracy**.

Users upload a leaf photo through a clean web interface, and the AI returns the predicted disease name along with a confidence score.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 5.2 + Django REST Framework |
| AI/ML | TensorFlow 2.21 + MobileNetV2 |
| Image Processing | Pillow + NumPy |
| Frontend | Bootstrap 5, vanilla JavaScript |
| Database | SQLite (default) |
| Fonts | Inter, Playfair Display, Bootstrap Icons |

---

## Project Structure

```
pdisease/
├── manage.py
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── pdisease/              # Django project settings
│   ├── settings.py        # Dual dev/prod mode
│   ├── urls.py
│   └── wsgi.py
├── core/                  # Main Django app
│   ├── views.py           # Model loading + predict/index views
│   ├── urls.py            # URL routes
│   ├── apps.py            # App configuration
│   └── ml/                # Place model files here (see Setup)
│       ├── plant_disease_model.h5
│       └── class_names.json
└── templates/
    └── index.html         # Single-page detector UI
```

---

## Server Deployment Instructions (For the AI)

### 1. Clone the Repository

```bash
git clone https://github.com/medoledo/pdisease.git
cd pdisease
```

### 2. Create & Activate Virtual Environment

```bash
# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note:** `requirements.txt` includes: Django, djangorestframework, tensorflow, pillow, numpy, python-dotenv, gunicorn.

### 4. Create .env File

Copy the example environment file and fill in your values:

```bash
cp .env.example .env
```

Then edit `.env`:

```bash
# Generate a NEW secret key (NEVER use the default in production)
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Paste that output into your `.env` file:

```env
SECRET_KEY=paste-your-new-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

#### Environment Variables Explained

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key. **Must be regenerated for production.** | `abc123...` |
| `DEBUG` | `True` = development mode, `False` = production mode | `False` |
| `ALLOWED_HOSTS` | Comma-separated list of allowed domains | `localhost,127.0.0.1` |

#### Dual Mode Behavior

| Setting | DEBUG=True (Development) | DEBUG=False (Production) |
|---------|-------------------------|--------------------------|
| `ALLOWED_HOSTS` | `['*']` (any host) | Uses `.env` value |
| Static files | Served by Django dev server | Must run `collectstatic` |
| Error pages | Detailed debug tracebacks | Generic 404/500 pages |
| SECRET_KEY | Falls back to insecure default | **Must be set in `.env`** |

### 5. Place Model Files

**CRITICAL:** Manually copy these two files into `core/ml/` before starting the server:

```
core/ml/plant_disease_model.h5    # Trained MobileNetV2 model (224x224x3, 38 classes)
core/ml/class_names.json          # JSON array of 38 class name strings
```

Example `class_names.json` format:
```json
["Apple___Apple_scab", "Apple___Black_rot", "Apple___healthy", "Tomato___healthy", ...]
```

> **Note:** The `.h5` model file is too large for GitHub. It must be uploaded to the server separately.

### 6. Run Migrations (Optional)

Only needed if you plan to use the Django admin panel:

```bash
python manage.py migrate
```

### 7. Development Mode (Local Testing)

```bash
# Set DEBUG=True in .env
python manage.py runserver
```

Then open: **http://127.0.0.1:8000/**

### 8. Production Deployment

#### Step A: Set Production Environment

Edit `.env`:
```env
SECRET_KEY=your-new-generated-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

#### Step B: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

#### Step C: Run with Gunicorn

```bash
gunicorn pdisease.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120
```

#### Step D: Configure Nginx (Reverse Proxy)

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/pdisease/staticfiles/;
    }
}
```

#### Step E: (Optional) HTTPS with Certbot

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

---

## Quick Reference

### Generate New Secret Key
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Development Server
```bash
python manage.py runserver
```

### Run Production Server
```bash
python manage.py collectstatic --noinput
gunicorn pdisease.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120
```

### System Check
```bash
python manage.py check
```

---

## Key Features

- **Single-page upload interface** — drag & drop or click to select an image
- **Real-time preview** — image thumbnail shown before analysis
- **AI prediction** — returns disease name + confidence percentage
- **Visual results** — color-coded badges (green for healthy, red for disease) + animated progress bar
- **Disease reference guide** — collapsible accordion showing all 38 detectable classes grouped by plant
- **Fully mobile responsive** — works smoothly on phones, tablets, and desktops
- **CSRF-exempt API** — fetch-based frontend for seamless AJAX predictions
- **No caching** — all responses include no-cache headers for fresh predictions every time

---

## API Endpoint

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Renders the detector homepage |
| `/api/predict/` | POST | Accepts `image` file, returns JSON prediction |

### Example API Response

```json
{
  "status": "success",
  "disease": "Tomato: Early Blight",
  "confidence": "97.3%"
}
```

---

## Important Notes for Deployment

- **Model Loading:** The TensorFlow model is loaded **once at server startup** (module-level in `core/views.py`) for efficiency. The first request after starting the server may take a few seconds as the model initializes.
- **Input Requirements:** The model expects **leaf images** (not fruits or whole plants) with a resolution of **224×224 pixels**. The app automatically resizes uploaded images.
- **Preprocessing:** Images are normalized by dividing pixel values by `255.0` (range [0, 1]) before being fed into the model.
- **No Database Required:** This app uses SQLite by default and does not require external database setup for the demo.
- **CSRF Exempt:** The `/api/predict/` endpoint is decorated with `csrf_exempt` to allow direct `fetch()` calls from the frontend without CSRF tokens.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'tensorflow'` | Run `pip install -r requirements.txt` with venv activated |
| `FileNotFoundError: plant_disease_model.h5` | Verify both `.h5` and `.json` files are inside `core/ml/` |
| `DisallowedHost at /` | Add your domain to `ALLOWED_HOSTS` in `.env` |
| `CommandError: You must set settings.ALLOWED_HOSTS` | Set `DEBUG=True` for dev, or add hosts to `.env` |
| TensorFlow oneDNN warnings | Normal on CPU-only installs; set `TF_ENABLE_ONEDNN_OPTS=0` to suppress |
| Port 8000 already in use | Kill existing process: `lsof -t -i:8000 | xargs kill -9` then restart |
| Nginx 502 Bad Gateway | Check Gunicorn is running: `ps aux \| grep gunicorn` |
| Static files not loading | Run `python manage.py collectstatic --noinput` |

---

## System Requirements

| Component | Minimum |
|-----------|---------|
| Python | 3.11+ |
| RAM | 4 GB (8 GB recommended for TensorFlow) |
| CPU | 2 cores (x86_64 with AVX support) |
| Disk | 2 GB free (model file + dependencies) |
| OS | Linux (Ubuntu 22.04+), Windows 10/11, macOS |

---

## License

University project — educational use only.
