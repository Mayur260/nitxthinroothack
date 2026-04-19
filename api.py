"""
DocAuth — FastAPI Backend
Serves the frontend and exposes REST endpoints for ML pipelines.

Run with:
    uvicorn api:app --reload --port 8000
"""

from __future__ import annotations

import base64
import io
import tempfile
from pathlib import Path

import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image

# ── App setup ────────────────────────────────────────────────────────────────
app = FastAPI(title="DocAuth API", version="1.0.0")

# Serve static files (CSS, JS, images, etc.)
STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ── Helpers ──────────────────────────────────────────────────────────────────

async def _save_upload(upload: UploadFile) -> Path:
    """Save an uploaded file to a temp location and return the path."""
    suffix = Path(upload.filename or "image.png").suffix or ".png"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    content = await upload.read()
    tmp.write(content)
    tmp.close()
    return Path(tmp.name)


def _numpy_to_b64png(arr: np.ndarray) -> str:
    """Convert a numpy array (RGB uint8) to a base64-encoded PNG string."""
    img = Image.fromarray(arr.astype(np.uint8))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def _pil_to_b64png(img: Image.Image) -> str:
    """Convert a PIL Image to a base64-encoded PNG string."""
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def _compute_verdict(score: float) -> str:
    """Map a 0-1 score to a verdict string."""
    if score < 0.10:
        return "Authentic"
    elif score < 0.55:
        return "Suspicious"
    else:
        return "Forged"


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the main frontend page."""
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Frontend not found")
    return index_path.read_text(encoding="utf-8")


@app.post("/api/analyze")
async def analyze_document(file: UploadFile = File(...)):
    """Run full document analysis: ELA + Edge Detection + OCR + Wavelet.

    Returns a comprehensive JSON result with scores, insights, and images.
    """
    try:
        file_path = await _save_upload(file)
        
        # Load image or convert first page of PDF
        if file_path.suffix.lower() == ".pdf":
            import fitz
            doc = fitz.open(file_path)
            if len(doc) == 0:
                raise ValueError("PDF is empty")
            page = doc.load_page(0)
            pix = page.get_pixmap()
            pil_image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            doc.close()
            
            # Since ML code expects an image path sometimes, replace file_path
            # with a temp image path
            img_path = file_path.with_suffix(".png")
            pil_image.save(img_path)
            file_path = img_path
        else:
            pil_image = Image.open(file_path).convert("RGB")

        # ── ELA ──────────────────────────────────────────────────────────
        from src.analysis.ela import generate_ela, ela_score

        ela_img = generate_ela(pil_image, quality=95, scale=15)
        ela_sc = ela_score(ela_img)
        ela_image_b64 = _pil_to_b64png(ela_img)

        # ── Edge Detection ───────────────────────────────────────────────
        from src.analysis.edge_detection import detect_all

        edges = detect_all(pil_image)
        edge_images_b64 = {
            name: _numpy_to_b64png(arr) for name, arr in edges.items()
        }

        # ── OCR ──────────────────────────────────────────────────────────
        ocr_result = {"full_text": "", "avg_confidence": 0.0, "engine": "none", "words": []}
        try:
            from src.analysis.ocr import extract_text
            ocr_result = extract_text(file_path, handwritten=False)
        except Exception:
            pass  # OCR is optional — may fail if easyocr/trocr not installed

        # ── Wavelet ──────────────────────────────────────────────────────
        from src.analysis.wavelet import decompose

        wav_result = decompose(pil_image, wavelet="db1", level=3)
        wavelet_heatmap_b64 = _numpy_to_b64png(wav_result["heatmap"])

        # ── Copy-Move (included in full analysis) ────────────────────────
        cm_score = 0.0
        cm_method = "none"
        try:
            from src.copy_move.detector import detect_copy_move
            cm_result = detect_copy_move(file_path)
            cm_score = cm_result["score"]
            cm_method = cm_result["method"]
        except Exception:
            pass

        # ── Composite Score ──────────────────────────────────────────────
        # Weight: ELA 40%, Copy-Move 30%, OCR confidence inverse 15%, Wavelet 15%
        wavelet_intensity = float(np.mean(wav_result["reconstructed"]) / 255.0)

        # Low OCR confidence is suspicious
        ocr_suspicion = max(0.0, 1.0 - ocr_result["avg_confidence"]) if ocr_result["avg_confidence"] > 0 else 0.0

        composite_score = (
            ela_sc * 5.0 * 0.40 +           # ELA scores are typically small, scale up
            cm_score * 0.30 +
            ocr_suspicion * 0.15 +
            wavelet_intensity * 0.15
        )
        composite_score = min(1.0, max(0.0, composite_score))

        verdict = _compute_verdict(composite_score)

        # ── Build Insights ───────────────────────────────────────────────
        insights = []

        if ela_sc > 0.05:
            insights.append({
                "type": "danger",
                "title": "Image Manipulation Evidence",
                "description": f"ELA analysis reveals compression artifacts (score: {ela_sc:.4f}) suggesting possible image editing.",
                "icon": "image"
            })
        elif ela_sc > 0.02:
            insights.append({
                "type": "warning",
                "title": "Minor Compression Anomalies",
                "description": f"ELA detected slight compression inconsistencies (score: {ela_sc:.4f}). May be due to re-saving.",
                "icon": "image"
            })
        else:
            insights.append({
                "type": "info",
                "title": "Consistent Compression Levels",
                "description": f"ELA score ({ela_sc:.4f}) is within normal range. No obvious manipulation detected.",
                "icon": "image"
            })

        if cm_score > 0.10:
            insights.append({
                "type": "danger" if cm_score > 0.55 else "warning",
                "title": "Copy-Move Regions Detected",
                "description": f"Duplicate regions identified ({cm_method}, score: {cm_score:.1%}). Possible copy-paste forgery.",
                "icon": "copy"
            })

        if ocr_result["avg_confidence"] > 0 and ocr_result["avg_confidence"] < 0.7:
            insights.append({
                "type": "warning",
                "title": "Low Text Confidence",
                "description": f"OCR confidence is {ocr_result['avg_confidence']:.1%} — text may be blurry, altered, or generated.",
                "icon": "text"
            })

        if wavelet_intensity > 0.3:
            insights.append({
                "type": "warning",
                "title": "High-Frequency Anomalies",
                "description": "Wavelet decomposition reveals unusual high-frequency patterns that may indicate tampering.",
                "icon": "wave"
            })

        if not insights:
            insights.append({
                "type": "info",
                "title": "No Anomalies Detected",
                "description": "All analyses returned results within normal parameters.",
                "icon": "check"
            })

        return {
            "verdict": verdict,
            "score": round(composite_score, 4),
            "ela_score": round(ela_sc, 4),
            "ela_image_b64": ela_image_b64,
            "edge_images_b64": edge_images_b64,
            "wavelet_heatmap_b64": wavelet_heatmap_b64,
            "copy_move_score": round(cm_score, 4),
            "ocr_text": ocr_result["full_text"],
            "ocr_confidence": round(ocr_result["avg_confidence"], 4),
            "ocr_engine": ocr_result["engine"],
            "insights": insights,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/copy-move")
async def detect_copy_move_endpoint(file: UploadFile = File(...)):
    """Run copy-move forgery detection on an uploaded image."""
    try:
        file_path = await _save_upload(file)

        from src.copy_move.detector import detect_copy_move
        from src.copy_move.visualizer import overlay_heatmap

        result = detect_copy_move(file_path)

        # Generate heatmap overlay
        pil_image = Image.open(file_path).convert("RGB")
        heatmap_b64 = None
        if result["mask"].any():
            overlay = overlay_heatmap(np.array(pil_image), result["mask"], alpha=0.4)
            heatmap_b64 = _numpy_to_b64png(overlay)

        return {
            "verdict": result["verdict"],
            "score": result["score"],
            "method": result["method"],
            "heatmap_b64": heatmap_b64,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Copy-move detection failed: {str(e)}")


@app.post("/api/signature")
async def verify_signature(
    reference: UploadFile = File(...),
    query: UploadFile = File(...),
):
    """Compare two signature images and return verification result."""
    try:
        ref_path = await _save_upload(reference)
        qry_path = await _save_upload(query)

        weights_path = Path("weights/siamese_best.pt")
        if not weights_path.exists():
            raise HTTPException(
                status_code=400,
                detail="Model weights not found. Train the model first with: python -m src.signature.train"
            )

        from src.signature.inference import verify
        result = verify(ref_path, qry_path, weights=weights_path)

        return {
            "match": result["match"],
            "confidence": result["confidence"],
            "distance": result["distance"],
            "verdict": result["verdict"],
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signature verification failed: {str(e)}")
