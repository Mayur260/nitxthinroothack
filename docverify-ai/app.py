import streamlit as st
from analyzer import analyze_document

st.set_page_config(page_title="DocVerify AI", layout="wide")

st.title("🛡️ DocVerify AI – Document Forgery Detection")
st.markdown("Upload a document and detect forgery using AI.")

uploaded_file = st.file_uploader("Upload Document", type=["pdf", "jpg", "png"])

if uploaded_file:
    st.success("File uploaded successfully!")

    file_bytes = uploaded_file.read()
    file_type = uploaded_file.type

    if uploaded_file.type.startswith("image"):
        st.image(uploaded_file, caption="Preview", use_container_width=True)

    if st.button("Analyze Document"):
        with st.spinner("Analyzing..."):
            result = analyze_document(file_bytes, file_type)

        st.subheader("🔍 Result")

        col1, col2 = st.columns(2)

        with col1:
            if uploaded_file.type.startswith("image"):
                st.image(uploaded_file, caption="Document")

        with col2:
            if result["verdict"] == "Forged":
                st.error("⚠️ Likely Forged")
            else:
                st.success("✅ Genuine")

            st.metric("Fraud Risk Score", f"{int(result['score']*100)}%")

            st.markdown("### Insights")
            for insight in result["insights"]:
                st.write(f"- {insight['title']}: {insight['description']}")

        st.markdown("### Extracted Text")
        st.text_area("", result["ocr_text"], height=200)