"""
analyzer.py
-----------
Core fraud-detection logic.

Right now this is a simulation — it uses random scoring and rule-based
insight selection so the whole stack works end-to-end without any
heavy ML libraries.

HOW TO EXTEND LATER:
  1. Replace `simulate_fraud_score()` with a real ML model call.
  2. Replace `generate_ela_image()` with real OpenCV ELA logic.
  3. Add more detectors (metadata, font analysis, etc.) and wire them in.
"""

import random
import io
import base64

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyze_document(file_bytes: bytes, content_type: str) -> dict:
    """
    Run all detection checks on the uploaded document and return a result dict.

    Args:
        file_bytes:   Raw bytes of the uploaded file.
        content_type: MIME type, e.g. "image/png" or "application/pdf".

    Returns:
        dict with keys: verdict, score, insights, ela_image_b64
    """
    score = simulate_fraud_score(file_bytes)
    verdict = score_to_verdict(score)
    insights = pick_insights(score, content_type)
    ela_b64 = generate_ela_image(file_bytes, content_type)

    return {
        "verdict": verdict,
        "score": round(score, 4),
        "insights": insights,
        "ela_image_b64": ela_b64,
    }


# ---------------------------------------------------------------------------
# Detection helpers  (replace these with real logic as you build it out)
# ---------------------------------------------------------------------------

def simulate_fraud_score(file_bytes: bytes) -> float:
    """
    Simulate a fraud probability score between 0.0 and 1.0.

    The score is seeded from the file contents so the same file always
    produces the same result — useful for demo / testing.

    TODO: Replace with a real model:
        from model import load_model, predict
        model = load_model("model.pkl")
        return predict(model, file_bytes)
    """
    seed = sum(file_bytes[:512])  # deterministic seed from file header
    rng = random.Random(seed)
    return rng.uniform(0.0, 1.0)


def score_to_verdict(score: float) -> str:
    """Map a numeric risk score to a human-readable verdict."""
    if score >= 0.55:
        return "Forged"
    elif score >= 0.30:
        return "Suspicious"
    else:
        return "Genuine"


def pick_insights(score: float, content_type: str) -> list[dict]:
    """
    Return 2–3 contextually appropriate insights based on the risk score.

    Each insight has:
      title       – short headline
      description – 1-sentence explanation
      type        – "danger" | "warning" | "info"
      icon        – key used by the frontend SVG icon map
    """

    # --- Pool of all possible insights ---
    high_risk_insights = [
        {
            "title": "Font Inconsistency Detected",
            "description": "Multiple font families found in areas that are normally uniform, suggesting possible text replacement.",
            "type": "danger",
            "icon": "text",
        },
        {
            "title": "Image Compression Anomaly",
            "description": "Error Level Analysis reveals uneven JPEG compression artefacts near the signature and date fields.",
            "type": "danger",
            "icon": "image",
        },
        {
            "title": "Copy-Move Forgery Suspected",
            "description": "Duplicate pixel regions detected that may indicate cloning or copy-paste tampering.",
            "type": "danger",
            "icon": "copy",
        },
    ]

    medium_risk_insights = [
        {
            "title": "Layout Alignment Irregularity",
            "description": "Header and footer elements show sub-pixel misalignment compared to standard template baselines.",
            "type": "warning",
            "icon": "wave",
        },
        {
            "title": "Unusual Metadata Timestamp",
            "description": "Document creation date is inconsistent with the stated issue date.",
            "type": "warning",
            "icon": "text",
        },
    ]

    low_risk_insights = [
        {
            "title": "Document Appears Authentic",
            "description": "No significant anomalies detected. Fonts, layout, and compression patterns are consistent.",
            "type": "info",
            "icon": "check",
        },
        {
            "title": "Structural Consistency Verified",
            "description": "Page margins, line spacing, and element positions match expected document standards.",
            "type": "info",
            "icon": "wave",
        },
    ]

    # --- Select insights based on score tier ---
    if score >= 0.55:
        # Forged: pick all 3 high-risk insights
        return high_risk_insights

    elif score >= 0.30:
        # Suspicious: 1 high-risk + 1 medium-risk
        return [
            random.choice(high_risk_insights),
            random.choice(medium_risk_insights),
        ]

    else:
        # Genuine: 2 positive/info insights
        return low_risk_insights


# ---------------------------------------------------------------------------
# ELA image generator  (placeholder — returns a coloured gradient PNG)
# ---------------------------------------------------------------------------

def generate_ela_image(file_bytes: bytes, content_type: str) -> str:
    """
    Generate an Error Level Analysis (ELA) image and return it as a
    base64-encoded PNG string.

    Real ELA steps (implement when you add OpenCV / Pillow):
      1. Re-compress the image at a known JPEG quality (e.g. 90 %).
      2. Compute the pixel-level difference between original and re-compressed.
      3. Amplify the difference so it's visible.
      4. Return the amplified image.

    For now we return a simple coloured PNG so the frontend preview works.

    TODO:
        from PIL import Image, ImageChops, ImageEnhance
        import io, base64

        img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
        buffer = io.BytesIO()
        img.save(buffer, "JPEG", quality=90)
        recompressed = Image.open(buffer)
        diff = ImageChops.difference(img, recompressed)
        diff = ImageEnhance.Brightness(diff).enhance(10)
        out = io.BytesIO()
        diff.save(out, "PNG")
        return base64.b64encode(out.getvalue()).decode()
    """
    # --- Minimal 1×1 transparent PNG (placeholder) ---
    # A tiny valid PNG so the frontend doesn't break.
    TRANSPARENT_1PX_PNG = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
        b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
        b"\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    return base64.b64encode(TRANSPARENT_1PX_PNG).decode()
