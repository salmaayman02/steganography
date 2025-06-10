import streamlit as st
from hide import HideImage, HideAudio
from unhide import UnhideImage, UnhideAudio
from operations import *
import os
import cv2
import wave
import numpy as np
import matplotlib.pyplot as plt
import requests

# -------------------------------
# Configuration
# -------------------------------
st.set_page_config(page_title="Steganography Assistant", layout="wide")

# -------------------------------
# Title and Branding
# -------------------------------
st.title("🔐 Steganography Assistant")
st.caption("Securely hide and reveal messages in image or audio files using steganography.")

# -------------------------------
# Chat Start
# -------------------------------
with st.chat_message("assistant"):
    st.write("Hi there! 👋 How can I assist you today?")
    process = st.radio("Choose an operation:", ["Hide a Message", "Unhide a Message"], index=None, key="main_op")

# -------------------------------
# Upload to Transfer.sh
# -------------------------------
def upload_to_transfersh(file_path):
    with open(file_path, 'rb') as f:
        response = requests.put(f"https://transfer.sh/{os.path.basename(file_path)}", data=f)
    if response.status_code == 200:
        return response.text.strip()
    else:
        raise Exception(f"Upload failed: {response.text}")

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
            media_type = st.radio("Choose where to hide the message:", ["Image", "Audio"], index=None, key="media_type_hide")

        if media_type == "Image":
            with col1:
                st.subheader("🖼️ Upload an Image File")
                uploaded_img = st.file_uploader("Supported formats: PNG (recommended), JPG", type=["png", "jpg", "jpeg"], key="img_uploader_hide")

            if uploaded_img:
                original_path = "temp_uploaded_image.png"
                with open(original_path, "wb") as f:
                    f.write(uploaded_img.getbuffer())

                st.session_state.original_img_path = original_path
                with col1:
                    st.image(original_path, caption="Original Image", use_container_width=True)

                with col2:
                    st.subheader("✉️ Enter Your Secret Message")
                    message = st.text_area("Type the secret message:", height=150, key="msg_hide_img")

                    if st.button("Hide Message in Image"):
                        if message:
                            output_path = "encoded_image.png"
                            try:
                                stego_img = HideImage(original_path, output_path)
                                stego_img.embed_text_pvd(message)
                                st.session_state.stego_img_path = output_path

                                st.success("✅ Message embedded successfully!")
                                st.image(output_path, caption="Stego Image (with hidden message)", use_container_width=True)

                                with open(output_path, "rb") as f:
                                    st.download_button("⬇️ Download Encoded Image", f, file_name="stego_image.png")

                            except Exception as e:
                                st.error(f"❌ An error occurred during encoding: {e}")
                        else:
                            st.warning("⚠️ Please enter a message to hide.")

                if "stego_img_path" in st.session_state and os.path.exists(st.session_state.stego_img_path):
                    if st.button("📤 Generate Shareable Image URL"):
                        try:
                            url = upload_to_transfersh(st.session_state.stego_img_path)
                            st.success("🌐 Public URL:")
                            st.code(url, language=None)

                            whatsapp_message = f"Check out this image with a hidden message: {url}"
                            whatsapp_url = f"https://wa.me/?text={whatsapp_message.replace(' ', '%20')}"
                            st.markdown(f"[📲 Share via WhatsApp]({whatsapp_url})", unsafe_allow_html=True)

                        except Exception as e:
                            st.error(f"❌ Failed to generate URL: {e}")

        elif media_type == "Audio":
            with col1:
                st.subheader("🎧 Upload an Audio File")
                uploaded_audio = st.file_uploader("Supported formats: WAV (recommended)", type=["wav"], key="audio_uploader_hide")

            if uploaded_audio:
                original_audio_path = "temp_uploaded_audio.wav"
                with open(original_audio_path, "wb") as f:
                    f.write(uploaded_audio.getbuffer())

                st.audio(original_audio_path, format="audio/wav")

                with col2:
                    st.subheader("✉️ Enter Your Secret Message")

                    def update_audio_count():
                        st.session_state.char_count_audio = len(st.session_state.msg_hide_audio)

                    message = st.text_area("Type the secret message:", height=150, key="msg_hide_audio", on_change=update_audio_count)

                    if st.button("Hide Message in Audio"):
                        if message:
                            output_path = "encoded_audio.wav"
                            try:
                                stego_audio = HideAudio(original_audio_path, output_path)
                                stego_audio.embed_text_lsb(message)
                                st.success("✅ Message successfully embedded into the audio.")

                                st.audio(output_path, format="audio/wav")

                                if st.button("📤 Generate Shareable Audio URL"):
                                    try:
                                        url = upload_to_transfersh(output_path)
                                        st.success("🌐 Public URL:")
                                        st.code(url, language=None)

                                        whatsapp_message = f"Listen to the audio with hidden message: {url}"
                                        whatsapp_url = f"https://wa.me/?text={whatsapp_message.replace(' ', '%20')}"
                                        st.markdown(f"[📲 Share via WhatsApp]({whatsapp_url})", unsafe_allow_html=True)

                                    except Exception as e:
                                        st.error(f"❌ Failed to generate URL: {e}")

                            except Exception as e:
                                st.error(f"❌ An error occurred during encoding: {e}")
                        else:
                            st.warning("⚠️ Please enter a message to hide.")

    elif process == "Unhide a Message":
        with col1:
            st.subheader("📁 Select Media Type")
            media_type = st.radio("Choose file type to extract message from:", ["Image", "Audio"], index=None, key="media_type_unhide")

        if media_type == "Image":
            with col2:
                st.subheader("🖼️ Upload Stego Image File")
                uploaded_img = st.file_uploader("Upload the image containing a hidden message", type=["png", "jpg", "jpeg"], key="img_uploader_unhide")

                if uploaded_img:
                    st.image(uploaded_img, caption="Uploaded Image", use_container_width=True)

                    if st.button("Reveal Message from Image"):
                        try:
                            extract_img = UnhideImage(uploaded_img)
                            hidden_message = extract_img.extract_text_pvd()
                            with st.chat_message("assistant"):
                                st.subheader("🕵️ Extracted Message")
                                st.code(hidden_message, language=None)
                        except Exception as e:
                            st.error(f"❌ Failed to extract message: {e}")

        elif media_type == "Audio":
            with col2:
                st.subheader("🎧 Upload Stego Audio File")
                uploaded_audio = st.file_uploader("Upload the audio file containing a hidden message", type=["wav"], key="audio_uploader_unhide")

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
                            st.error(f"❌ Failed to extract message: {e}")
