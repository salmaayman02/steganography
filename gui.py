# -*- coding: utf-8 -*-
import streamlit as st
from hide import HideImage, HideAudio
from unhide import UnhideImage, UnhideAudio
import os

# -------------------------------
# Configuration
# -------------------------------
st.set_page_config(page_title="Steganography Assistant", layout="wide")

# -------------------------------
# Title and Branding
# -------------------------------
st.title("🔐 Steganography Assistant".encode("utf-8", "ignore").decode("utf-8"))
st.caption("Securely hide and reveal messages in image or audio files using steganography.")

# -------------------------------
# Chat Start
# -------------------------------
with st.chat_message("assistant"):
    st.write("Hi there! 👋 How can I assist you today?".encode("utf-8", "ignore").decode("utf-8"))
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
            st.subheader("📁 Select Data Type")
            media_type = st.radio("Choose where to hide the message:", ["Image", "Audio"], index=None)

        if media_type == "Image":
            with col1:
                st.subheader("🖼️ Upload an Image File")
                uploaded_img = st.file_uploader("Supported formats: PNG, JPG, JPEG", type=["png", "jpg", "jpeg"])

            if uploaded_img:
                original_path = "temp_uploaded_image.png"
                with open(original_path, "wb") as f:
                    f.write(uploaded_img.getbuffer())

                with col2:
                    message = st.text_area("Type the secret message:", height=120)
                    output_path = "encoded_image.png"
                    if st.button("Hide Message in Image"):
                        try:
                            stego_img = HideImage(original_path, output_path)
                            stego_img.embed_text_pvd(message)
                            st.success("✅ Message embedded successfully.")
                            img_col1, img_col2 = st.columns(2)
                            with img_col1:
                                st.image(original_path, caption="Original Image", use_column_width=True)
                            with img_col2:
                                st.image(output_path, caption="Stego Image", use_column_width=True)
                            with open(output_path, "rb") as f:
                                st.download_button("⬇️ Download Encoded Image", f, file_name="stego_image.png")
                            st.caption("💾 The file will be saved to your **Downloads** folder.")
                            st.subheader("📤 Share with Friends")
                            col_share1, col_share2 = st.columns(2)
                            with col_share1:
                                st.markdown(
                                    "[📱 WhatsApp](https://wa.me/?text=Check%20out%20this%20encoded%20image%20file!)",
                                    unsafe_allow_html=True
                                )
                            with col_share2:
                                st.markdown(
                                    "[📧 Gmail](https://mail.google.com/mail/?view=cm&fs=1&tf=1&su=Encoded%20Image&body=Download%20it%20from%20the%20tool.)",
                                    unsafe_allow_html=True
                                )
                        except Exception as e:
                            st.error(f"❌ Error during encoding: {e}")

        elif media_type == "Audio":
            with col1:
                st.subheader("🎧 Upload an Audio File")
                uploaded_audio = st.file_uploader("Supported formats: WAV", type=["wav"])

            if uploaded_audio:
                original_audio_path = "temp_uploaded_audio.wav"
                with open(original_audio_path, "wb") as f:
                    f.write(uploaded_audio.getbuffer())

                with col2:
                    st.subheader("✉️ Enter Your Secret Message")
                    message = st.text_area("Type the secret message:", height=120)
                    output_path = "encoded_audio.wav"
                    if st.button("Hide Message in Audio"):
                        try:
                            stego_audio = HideAudio(original_audio_path, output_path)
                            stego_audio.embed_text_lsb(message)
                            st.success("✅ Message successfully embedded into the audio.")
                            st.audio(output_path, format="audio/wav")
                            with open(output_path, "rb") as f:
                                st.download_button("⬇️ Download Encoded Audio", f, file_name="stego_audio.wav")
                            st.caption("💾 File saved as `stego_audio.wav`.")
                            st.subheader("📤 Share with Friends")
                            col_share1, col_share2 = st.columns(2)
                            with col_share1:
                                st.markdown(
                                    "[📱 WhatsApp](https://wa.me/?text=Check%20out%20this%20encoded%20audio%20file!)",
                                    unsafe_allow_html=True
                                )
                            with col_share2:
                                st.markdown(
                                    "[📧 Gmail](https://mail.google.com/mail/?view=cm&fs=1&tf=1&su=Encoded%20Audio&body=Download%20it%20from%20the%20tool.)",
                                    unsafe_allow_html=True
                                )
                        except Exception as e:
                            st.error(f"❌ Error during encoding: {e}")

    elif process == "Unhide a Message":
        with col1:
            st.subheader("📁 Select Data Type")
            media_type = st.radio("Choose file type to extract message from:", ["Image", "Audio"], index=None)

        if media_type == "Image":
            with col2:
                st.subheader("🖼️ Upload Image File")
                uploaded_img = st.file_uploader("Supported formats: PNG, JPG, JPEG", type=["png", "jpg", "jpeg"])

                if uploaded_img:
                    st.success("✅ Image uploaded successfully.")
                    st.image(uploaded_img, caption="Uploaded Image", use_column_width=True)
                    if st.button("Reveal Message from Image"):
                        try:
                            extract_img = UnhideImage(uploaded_img)
                            hidden_message = extract_img.extract_text_pvd()
                            with st.chat_message("assistant"):
                                st.subheader("🕵️ Extracted Message")
                                lines = hidden_message.count('\n') + 1
                                st.text_area("Hidden message:", value=hidden_message, height=min(500, max(100, lines * 20)), disabled=True)
                        except Exception as e:
                            st.error(f"❌ Failed to extract message: {e}")

        elif media_type == "Audio":
            with col2:
                st.subheader("🎧 Upload Audio File")
                uploaded_audio = st.file_uploader("Supported formats: WAV", type=["wav"])

                if uploaded_audio:
                    st.success("✅ Audio uploaded successfully.")
                    st.audio(uploaded_audio, format="audio/wav")
                    if st.button("Reveal Message from Audio"):
                        try:
                            extract_audio = UnhideAudio(uploaded_audio)
                            hidden_message = extract_audio.extract_text_lsb()
                            with st.chat_message("assistant"):
                                st.subheader("🕵️ Extracted Message")
                                lines = hidden_message.count('\n') + 1
                                st.text_area("Hidden message:", value=hidden_message, height=min(500, max(100, lines * 20)), disabled=True)
                        except Exception as e:
                            st.error(f"❌ Failed to extract message: {e}")

# -------------------------------
# Footer and Notes
# -------------------------------
st.info(
    "💡 **Note**: File resolution and size affect how much data can be hidden. "
    "Use larger images or higher-quality audio for better results."
)
