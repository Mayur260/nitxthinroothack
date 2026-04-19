# DocVerify AI – Document Forgery Detection System

## Overview

DocVerify AI is an AI-based system that detects forged or tampered documents using OCR and image forensics techniques. It provides explainable outputs by highlighting suspicious regions and generating a fraud risk score.

---

## Problem Statement

Forgery and fake document submissions are major challenges in domains like banking, education, and identity verification.
Manual verification is slow, inconsistent, and prone to human error, making it difficult to detect sophisticated document tampering.

---

## Solution

DocVerify AI automates document verification using a hybrid approach of OCR and computer vision.

The system:

* Extracts text from documents
* Analyzes layout and structure
* Detects image manipulation
* Generates a fraud risk score
* Provides explainable insights

---

## How It Works

```
Upload → OCR → Analysis → Detection → Result
```

* **OCR:** Extracts text from the document
* **Analysis:** Checks inconsistencies in text and layout
* **Detection:** Identifies tampering using image forensics
* **Result:** Displays fraud score and explanation

---

## System Architecture

```
Frontend → Backend API → OCR + Image Analysis → Result
```

---

## Features

* OCR-based text extraction
* Image tampering detection (ELA)
* Fraud risk scoring system
* Explainable AI output
* Highlighted suspicious regions

---

## Tech Stack

* **Frontend:** HTML, CSS, JavaScript
* **Backend:** Python (FastAPI / Streamlit)
* **OCR:** EasyOCR / Tesseract
* **Image Processing:** OpenCV

---


## Use Cases

* Banking document verification
* College admission validation
* HR document screening
* Government identity verification

---



## How to Run Locally

### 1. Clone the repository

```
git clone <your-repo-link>
cd DocVerify-AI
```

### 2. Install dependencies

```
pip install -r requirements.txt
```

### 3. Run the app

#### If using Streamlit:

```
streamlit run app.py
```

#### If using FastAPI:

```
uvicorn main:app --reload
```

---

## Key Highlight

Our system focuses on **Explainable AI**, ensuring users understand exactly why a document is flagged as forged, rather than just providing a binary result.

---

## Future Improvements

* Support for more document types
* Improved detection accuracy
* Integration with real-world verification systems

---

## Team

Mayur S
Deepak K
Akshay N Kumar
Manya Umesh

---
