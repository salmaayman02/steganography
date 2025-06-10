import streamlit as st
from hide import HideImage, HideAudio
from unhide import UnhideImage, UnhideAudio
import os
from pathlib import Path
import uuid

# -------------------------------
# Configuration
# -------------------------------
st.set_page_config(page_title="Steganography Assistant", layout="wide")
st.title("🔐 Steganography Assistant")
st.caption("Securely hide and reveal messages in image or audio files using steganography.")

# Simulated Downloads folder on server/host
DOWNLOADS_DIR = Path.cwd() / "Downloads"
DOWNLOADS_DIR.mkdir(exist_ok=True)

# -------------------------------
# Chat Start
# -------------------------------
with st.chat_message("assistant"):
    st.write("Hi there! 👋 How can I assist you today?")
    process = st.radio("Choose an operation:", ["Hide a Message", "Unhide a Message"], index=None)

# -------------------------------
# Process Handler
# -------------------------------
if process:
    with st.chat_message("user"):
        st.write(f"You selected: **{process}**")

    col1, col2 = st.columns([2, 3])

    if process == "Hide a Message":
        with col1:
            st.subheader("📁 Select Media Type")
            media_type = st.radio("Choose where to hide the message:", ["Image", "Audio"], index=None)

        if media_type == "Image":
            with col1:
                st.subheader("🖼️ Upload an Image File")
                uploaded_img = st.file_uploader("Supported formats: PNG (recommended), JPG", type=["png", "jpg", "jpeg"])

            if uploaded_img:
                original_path = DOWNLOADS_DIR / f"temp_uploaded_{uuid.uuid4().hex}.png"
                with open(original_path, "wb") as f:
                    f.write(uploaded_img.getbuffer())
                st.session_state["original_image_path"] = original_path
                st.image(original_path, caption="Original Image", use_container_width=True)

            if "original_image_path" in st.session_state:
                with col2:
                    st.subheader("✉️ Enter Your Secret Message")
                    message = st.text_area("Type the secret message:", height=150)

                    if st.button("🔒 Hide Message in Image"):
                        if not message:
                            st.warning("⚠️ Please enter a message.")
                        else:
                            filename = f"stego_image_{uuid.uuid4().hex}.png"
                            output_path = DOWNLOADS_DIR / filename
                            try:
                                stego = HideImage(str(st.session_state["original_image_path"]), str(output_path))
                                stego.embed_text_pvd(message)

                                st.success("✅ Message embedded successfully!")
                                st.image(str(output_path), caption="Stego Image", use_container_width=True)
                                with open(output_path, "rb") as f:
                                    st.download_button("⬇️ Download Encoded Image", f, file_name=filename)

                                st.info(f"📁 Encoded image has been saved to: `{output_path}`")

                                st.subheader("📲 Share Manually")
                                st.markdown(
                                    "After downloading the file, you can manually share it via WhatsApp.\n\n"
                                    "[🔗 Open WhatsApp](https://wa.me/) and attach the saved image manually from your Downloads folder.",
                                    unsafe_allow_html=True
                                )
                            except Exception as e:
                                st.error(f"❌ Encoding failed: {e}")

        elif media_type == "Audio":
            with col1:
                st.subheader("🎧 Upload an Audio File")
                uploaded_audio = st.file_uploader("Supported format: WAV", type=["wav"])

            if uploaded_audio:
                original_path = DOWNLOADS_DIR / f"temp_uploaded_{uuid.uuid4().hex}.wav"
                with open(original_path, "wb") as f:
                    f.write(uploaded_audio.getbuffer())
                st.session_state["original_audio_path"] = original_path
                st.audio(str(original_path), format="audio/wav")

            if "original_audio_path" in st.session_state:
                with col2:
                    st.subheader("✉️ Enter Your Secret Message")
                    message = st.text_area("Type the secret message:", height=150)

                    if st.button("🔒 Hide Message in Audio"):
                        if not message:
                            st.warning("⚠️ Please enter a message.")
                        else:
                            filename = f"encoded_audio_{uuid.uuid4().hex}.wav"
                            output_path = DOWNLOADS_DIR / filename
                            try:
                                stego = HideAudio(str(st.session_state["original_audio_path"]), str(output_path))
                                stego.embed_text_lsb(message)

                                st.success("✅ Message embedded successfully!")
                                st.audio(str(output_path), format="audio/wav")
                                with open(output_path, "rb") as f:
                                    st.download_button("⬇️ Download Encoded Audio", f, file_name=filename)

                                st.info(f"📁 Encoded audio has been saved to: `{output_path}`")

                                st.subheader("📲 Share Manually")
                                st.markdown(
                                    "After downloading the file, you can manually share it via WhatsApp.\n\n"
                                    "[🔗 Open WhatsApp](https://wa.me/) and attach the saved audio manually from your Downloads folder.",
                                    unsafe_allow_html=True
                                )
                            except Exception as e:
                                st.error(f"❌ Encoding failed: {e}")

    elif process == "Unhide a Message":
        with col1:
            st.subheader("📁 Select Media Type")
            media_type = st.radio("Choose file type to extract from:", ["Image", "Audio"], index=None)

        if media_type == "Image":
            with col2:
                st.subheader("🖼️ Upload Stego Image")
                uploaded_img = st.file_uploader("Upload the stego image", type=["png", "jpg", "jpeg"])

                if uploaded_img:
                    st.image(uploaded_img, caption="Uploaded Image", use_container_width=True)

                    if st.button("Reveal Message from Image"):
                        try:
                            extract_img = UnhideImage(uploaded_img)
                            hidden_message = extract_img.extract_text_pvd()
                            with st.chat_message("assistant"):
                                st.subheader("🕵️ Extracted Message")
                                st.code(hidden_message)
                        except Exception as e:
                            st.error(f"❌ Extraction failed: {e}")

        elif media_type == "Audio":
            with col2:
                st.subheader("🎧 Upload Stego Audio")
                uploaded_audio = st.file_uploader("Upload the stego audio", type=["wav"])

                if uploaded_audio:
                    st.audio(uploaded_audio)

                    if st.button("Reveal Message from Audio"):
                        try:
                            extract_audio = UnhideAudio(uploaded_audio)
                            hidden_message = extract_audio.extract_text_lsb()
                            with st.chat_message("assistant"):
                                st.subheader("🕵️ Extracted Message")
                                st.text_area("Hidden message:", value=hidden_message, height=100, disabled=True)
                        except Exception as e:
                            st.error(f"❌ Extraction failed: {e}")
