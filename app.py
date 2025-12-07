import streamlit as st
from PIL import Image
import io

from algorithms import (
    rle_compress, rle_decompress,
    huffman_compress, huffman_decompress,
    lzw_compress, lzw_decompress,
    golomb_encode, golomb_decode,
    quantize_image
)

st.set_page_config(page_title="Data Compression App", page_icon="📦", layout="wide")
st.title("📦 Data Compression Application")

# ===============================
# Initialize Session State
# ===============================
if "compressed" not in st.session_state:
    st.session_state.compressed = None
    st.session_state.codes = None
    st.session_state.lzw = None
    st.session_state.original_text = None
    st.session_state.decompressed = None

# ===============================
# Sidebar — Mode Selection
# ===============================
st.sidebar.header("Choose Compression Mode")
mode = st.sidebar.radio("Compression Mode", ["Lossless (Text)", "Lossy (Image)"])

# ===============================
# LOSSLESS TEXT COMPRESSION
# ===============================
if mode == "Lossless (Text)":

    st.subheader("📄 Lossless Text Compression")

    # Choose Algorithm
    technique = st.radio("Select Technique", ["Run-Length Encoding", "Huffman", "LZW", "Golomb"])

    # Choose Operation
    operation = st.radio("Choose Operation", ["Compression", "Decompression"])

    # If Golomb selected → ask for parameter m BEFORE operation
    if technique == "Golomb":
        m = st.number_input("Enter Golomb Parameter (m)", min_value=1)
    else:
        m = None

    # Upload text file
    uploaded_file = st.file_uploader(
        "Upload a Text File (one number per line for Golomb, normal text for others)", 
        type=["txt"]
    )

    # Load text
    if uploaded_file:
        text = uploaded_file.read().decode("utf-8").strip()
        st.session_state.original_text = text
        st.text_area("Original Text / Numbers", text, height=200)

    # ===============================
    # OPERATION: COMPRESSION
    # ===============================
    if operation == "Compression" and st.button("🔐 Compress", type="primary"):

        if not st.session_state.original_text:
            st.warning("Please upload a text file first.")
        else:
            text = st.session_state.original_text

            if technique == "Run-Length Encoding":
                st.session_state.compressed = rle_compress(text)
                st.session_state.codes = None
                st.session_state.lzw = None

            elif technique == "Huffman":
                encoded, codes = huffman_compress(text)
                st.session_state.compressed = encoded
                st.session_state.codes = codes
                st.session_state.lzw = None

            elif technique == "LZW":
                lst = lzw_compress(text)
                st.session_state.lzw = lst
                st.session_state.compressed = lst
                st.session_state.codes = None

            elif technique == "Golomb":
                # Treat each line as integer n
                try:
                    numbers = [int(line.strip()) for line in text.splitlines() if line.strip() != ""]
                except ValueError:
                    st.error("Golomb requires numbers only, one per line.")
                    st.stop()
                encoded_list = [golomb_encode(n, m) for n in numbers]
                st.session_state.compressed = encoded_list
                st.session_state.codes = m

            # Prepare display
            compressed_display = "\n".join(st.session_state.compressed) if technique == "Golomb" else str(st.session_state.compressed)
            st.success("Compression Done Successfully!")
            st.text_area("🔒 Compressed Output", compressed_display, height=200)

            # Download compressed file
            st.download_button(
                label="💾 Download Compressed File",
                data="\n".join(st.session_state.compressed) if technique == "Golomb" else str(st.session_state.compressed),
                file_name="compressed.txt",
                mime="text/plain",
                key="download_compressed"
            )

    # ===============================
    # OPERATION: DECOMPRESSION
    # ===============================
    if operation == "Decompression" and st.button("🔓 Decompress", type="primary"):

        if not st.session_state.compressed:
            st.warning("No compressed data found. Please compress or upload compressed text.")
        else:

            if technique == "Run-Length Encoding":
                st.session_state.decompressed = rle_decompress(st.session_state.compressed)

            elif technique == "Huffman":
                st.session_state.decompressed = huffman_decompress(
                    st.session_state.compressed,
                    st.session_state.codes
                )

            elif technique == "LZW":
                st.session_state.decompressed = lzw_decompress(st.session_state.lzw)

            elif technique == "Golomb":
                m = st.session_state.codes
                encoded_list = st.session_state.compressed
                decoded_numbers = [golomb_decode(code, m) for code in encoded_list]
                st.session_state.decompressed = decoded_numbers

            # Prepare display
            decompressed_display = "\n".join(str(n) for n in st.session_state.decompressed) if technique == "Golomb" else str(st.session_state.decompressed)
            st.success("Decompression Completed Successfully!")
            st.text_area("📤 Decompressed Output", decompressed_display, height=200)

            # Download decompressed file
            st.download_button(
                label="💾 Download Decompressed File",
                data="\n".join(str(n) for n in st.session_state.decompressed) if technique == "Golomb" else str(st.session_state.decompressed),
                file_name="decompressed.txt",
                mime="text/plain",
                key="download_decompressed"
            )

# ===============================
# LOSSY IMAGE COMPRESSION
# ===============================
else:
    st.subheader("🖼️ Lossy Image Compression (Quantization)")

    uploaded_image = st.file_uploader("Upload an Image", type=["png", "jpg", "jpeg"])

    if uploaded_image:
        image = Image.open(uploaded_image)
        st.image(image, caption="Original Image", use_container_width=True)

        levels = st.slider("Select Quantization Levels", 2, 64, 16)

        if st.button("Compress Image", type="primary"):
            compressed_img = quantize_image(image, levels)
            st.image(compressed_img, caption="Compressed Image", use_container_width=True)

            buf = io.BytesIO()
            compressed_img.save(buf, format="PNG")
            byte_im = buf.getvalue()

            st.download_button(
                label="💾 Download Compressed Image",
                data=byte_im,
                file_name="compressed_image.png",
                mime="image/png",
                key="download_image"
            )
