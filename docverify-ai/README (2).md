# DocVerify AI – Backend

A FastAPI backend for the DocVerify AI document forgery detection tool.

---

## Project Structure

```
docverify-backend/
├── main.py          # FastAPI app, routes, CORS
├── analyzer.py      # Fraud detection logic (simulated → real ML later)
├── ocr.py           # OCR text extraction (placeholder → Tesseract/Cloud later)
├── requirements.txt
├── static/
│   └── index.html   # Your frontend HTML (served at "/")
└── README.md
```

---

## Run Locally

### 1. Clone / copy the files

Make sure your frontend HTML is saved as `static/index.html`.

### 2. Create a virtual environment

```bash
python -m venv venv

# Mac / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the server

```bash
uvicorn main:app --reload --port 8000
```

Open **http://localhost:8000** — you'll see your frontend.  
The API is at **http://localhost:8000/api/analyze**.

### 5. Test the API directly (optional)

```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@/path/to/your/document.jpg"
```

---

## API Reference

### `POST /api/analyze`

**Request:** `multipart/form-data` with a `file` field (PDF, JPG, or PNG).

**Response:**

```json
{
  "verdict": "Forged",
  "score": 0.782,
  "insights": [
    {
      "title": "Font Inconsistency Detected",
      "description": "Multiple font families found in areas that are normally uniform.",
      "type": "danger",
      "icon": "text"
    }
  ],
  "ocr_text": "INVOICE #INV-2024-0847 ...",
  "ela_image_b64": "<base64 PNG string>"
}
```

| Field | Type | Notes |
|---|---|---|
| `verdict` | string | `"Forged"` / `"Suspicious"` / `"Genuine"` |
| `score` | float | 0.0 (safe) → 1.0 (forged) |
| `insights` | array | 2–3 detection findings |
| `ocr_text` | string | Extracted document text |
| `ela_image_b64` | string | Base64 PNG for preview (placeholder for now) |

---

## Deploy on Render (free tier)

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial DocVerify AI backend"
git remote add origin https://github.com/YOUR_USERNAME/docverify-ai.git
git push -u origin main
```

### 2. Create a Render Web Service

1. Go to [https://render.com](https://render.com) and sign in.
2. Click **New → Web Service**.
3. Connect your GitHub repo.
4. Fill in the settings:

| Setting | Value |
|---|---|
| **Environment** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | Free |

5. Click **Create Web Service**.

Render will build and deploy automatically. Your API will be live at:
`https://your-service-name.onrender.com`

### 3. Update the frontend fetch URL

In `static/index.html`, find the fetch call and update it if needed:

```js
// If frontend and backend are on the same Render service — no change needed.
// If they're on different domains, replace with your Render URL:
const response = await fetch('https://your-service-name.onrender.com/api/analyze', { ... });
```

> **Note:** Render's free tier spins down after 15 minutes of inactivity.
> The first request after sleep takes ~30 seconds to wake up.

---

## Extending the Backend

### Add real OCR (Tesseract)

```bash
pip install pytesseract Pillow
# Also install the Tesseract binary from https://github.com/UB-Mannheim/tesseract/wiki
```

Then in `ocr.py`, replace `_extract_from_image()`:

```python
from PIL import Image
import pytesseract, io

def _extract_from_image(file_bytes, content_type):
    img = Image.open(io.BytesIO(file_bytes))
    return pytesseract.image_to_string(img)
```

### Add real ELA (OpenCV)

```bash
pip install opencv-python-headless Pillow
```

Then in `analyzer.py`, replace `generate_ela_image()`:

```python
from PIL import Image, ImageChops, ImageEnhance
import io, base64

def generate_ela_image(file_bytes, content_type):
    img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    buffer = io.BytesIO()
    img.save(buffer, "JPEG", quality=90)
    recompressed = Image.open(buffer)
    diff = ImageChops.difference(img, recompressed)
    diff = ImageEnhance.Brightness(diff).enhance(10)
    out = io.BytesIO()
    diff.save(out, "PNG")
    return base64.b64encode(out.getvalue()).decode()
```

### Add a real ML model

Replace `simulate_fraud_score()` in `analyzer.py`:

```python
import joblib  # pip install scikit-learn
_model = joblib.load("model.pkl")

def simulate_fraud_score(file_bytes):
    features = extract_features(file_bytes)   # your feature pipeline
    return float(_model.predict_proba([features])[0][1])
```
