import streamlit as st
from analyzer import analyze_document

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DocVerify AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Minimal styling tweaks (no external CSS) ──────────────────────────────────
st.markdown("""
<style>
    /* Centre the main block and cap its width */
    .block-container { max-width: 1100px; padding-top: 2rem; padding-bottom: 3rem; }

    /* Soften the metric boxes */
    [data-testid="metric-container"] {
        background: #f8f9fb;
        border: 1px solid #e3e6ea;
        border-radius: 10px;
        padding: 0.75rem 1rem;
    }

    /* Make the file-uploader label less bold */
    [data-testid="stFileUploaderDropzone"] { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    "<h1 style='text-align:center; margin-bottom:0'>🛡️ DocVerify AI</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align:center; color:grey; font-size:1.05rem; margin-top:0.25rem'>"
    "AI-powered document forgery detection — upload a file and get an instant verdict."
    "</p>",
    unsafe_allow_html=True,
)

st.divider()


# ── Upload section ────────────────────────────────────────────────────────────
upload_col, _ = st.columns([2, 1])          # keep uploader from stretching edge-to-edge
with upload_col:
    st.subheader("📂 Upload Document")
    uploaded_file = st.file_uploader(
        "Supported formats: PDF, JPG, PNG",
        type=["pdf", "jpg", "jpeg", "png"],
        label_visibility="visible",
    )

if not uploaded_file:
    st.info("👆 Upload a document above to get started.", icon="ℹ️")
    st.stop()                               # nothing more to render until a file arrives


# ── File ready ────────────────────────────────────────────────────────────────
st.success(f"**{uploaded_file.name}** uploaded successfully!", icon="✅")

file_bytes = uploaded_file.read()
file_type  = uploaded_file.type
is_image   = file_type.startswith("image")

st.divider()


# ── Preview + Analyze button ──────────────────────────────────────────────────
st.subheader("🖼️ Document Preview")

if is_image:
    prev_col, _ = st.columns([1, 1])
    with prev_col:
        st.image(file_bytes, caption=uploaded_file.name, use_container_width=True)
else:
    st.markdown(
        f"📄 **{uploaded_file.name}** &nbsp;·&nbsp; "
        f"`{round(len(file_bytes)/1024, 1)} KB`",
        unsafe_allow_html=True,
    )
    st.caption("PDF preview not available — text will be extracted on analysis.")

st.write("")                                # vertical breathing room

analyze_btn = st.button("🔍 Analyze Document", type="primary", use_container_width=False)

st.divider()


# ── Analysis ──────────────────────────────────────────────────────────────────
if analyze_btn:
    with st.spinner("Running forgery detection… this takes a few seconds."):
        result = analyze_document(file_bytes, file_type)

    verdict   = result["verdict"]
    score_pct = int(result["score"] * 100)
    insights  = result["insights"]
ocr_text = result.get("ocr_text", "OCR not available")
    st.subheader("📊 Analysis Results")
    st.write("")

    # Two-column results layout
    left_col, gap_col, right_col = st.columns([1, 0.08, 1.2])

    # ── Left: document preview ────────────────────────────────────────────────
    with left_col:
        st.markdown("**Document**")
        if is_image:
            st.image(file_bytes, use_container_width=True)
        else:
            st.markdown(
                f"<div style='background:#f0f2f6; border-radius:10px; padding:2rem; "
                f"text-align:center; color:#555; font-size:2.5rem;'>📄</div>",
                unsafe_allow_html=True,
            )
            st.caption(uploaded_file.name)

    # ── Right: verdict + metrics + insights ───────────────────────────────────
    with right_col:

        # Verdict banner
        if verdict == "Forged":
            st.error(f"⚠️  **Verdict: Likely Forged**", icon="🚨")
        elif verdict == "Suspicious":
            st.warning(f"🔶  **Verdict: Suspicious**", icon="⚠️")
        else:
            st.success(f"✅  **Verdict: Likely Genuine**", icon="✅")

        st.write("")

        # Score + confidence side by side
        m1, m2 = st.columns(2)
        m1.metric("Fraud Risk Score", f"{score_pct}%")
        confidence_label = (
            "High confidence" if score_pct >= 75 or score_pct <= 25
            else "Moderate confidence"
        )
        m2.metric("Confidence", confidence_label)

        st.write("")
        st.markdown("**🔎 Detection Insights**")

        if insights:
            for insight in insights:
                icon = (
                    "🔴" if insight.get("type") == "danger"
                    else "🟡" if insight.get("type") == "warning"
                    else "🔵"
                )
                with st.container():
                    st.markdown(f"{icon} **{insight['title']}**")
                    st.caption(insight["description"])
                    st.write("")
        else:
            st.caption("No specific anomalies detected.")

    st.divider()

    # ── Extracted text ────────────────────────────────────────────────────────
    st.subheader("📝 Extracted Text (OCR)")
    st.text_area(
        label="",
        value=ocr_text if ocr_text else "(No text could be extracted from this document.)",
        height=220,
        disabled=True,
        label_visibility="collapsed",
    )

    st.divider()
    st.caption(
        "DocVerify AI · Prototype · Results are indicative and should not be used as sole evidence."
    )