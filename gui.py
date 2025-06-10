import streamlit as st
from hide import HideImage, HideAudio
from unhide import UnhideImage, UnhideAudio
import os
import requests

# -------------------------------
# Configuration
# -------------------------------
st.set_page_config(page_title="Steganography Assistant", layout="wide")
st.title("🔐 Steganography Assistant")
st.caption("Securely hide and reveal messages in image or audio files using steganography.")

# -------------------------------
# Upload to GoFile.io
# -------------------------------
def upload_to_gofile(file_path):
    try:
        server_res = requests.get("https://api.gofile.io/getServer")
        server = server_res.json()['data']['server']
        with open(file_path, 'rb') as f:
            upload_res = requests.post(
                f"https://{server}.gofile.io/uploadFile",
                files={"file": f}
            )
        data = upload_res.json()
        if upload_res.status_code == 200 and data["status"] == "ok":
            return data["data"]["downloadPage"]
        else:
            raise Exception(f"Upload failed: {data}")
    except Exception as e:
        raise Exception(f"HTTP error: {e}")

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
                original_path = "temp_uploaded_image.png"
                with open(original_path, "wb") as f:
                    f.write(uploaded_img.getbuffer())
                st.session_state["original_image_path"] = original_path
                st.image(original_path, caption="Original Image", use_container_width=True)

            if "original_image_path" in st.session_state:
                with col2:
                    st.subheader("✉️ Enter Your Secret Message")
                    message = st.text_area("Type the secret message:", height=150)

                    if st.button("Hide Message in Image"):
                        if message:
                            output_path = "encoded_image.png"
                            try:
                                stego_img = HideImage(st.session_state["original_image_path"], output_path)
                                stego_img.embed_text_pvd(message)
                                st.session_state["encoded_image_path"] = output_path
                                st.success("✅ Message embedded successfully!")
                                st.image(output_path, caption="Stego Image", use_container_width=True)

                                with open(output_path, "rb") as f:
                                    st.download_button("⬇️ Download Encoded Image", f, file_name="stego_image.png")

                            except Exception as e:
                                st.error(f"❌ Encoding error: {e}")
                        else:
                            st.warning("⚠️ Please enter a message.")

            if "encoded_image_path" in st.session_state:
                with col2:
                    if st.button("📤 Share Image via GoFile & WhatsApp"):
                        try:
                            url = upload_to_gofile(st.session_state["encoded_image_path"])
                            st.success("🌐 Public URL:")
                            st.code(url)
                            whatsapp_message = f"Check out this stego image: {url}"
                            whatsapp_url = f"https://wa.me/?text={whatsapp_message.replace(' ', '%20')}"
                            st.markdown(f"[📲 Share via WhatsApp]({whatsapp_url})", unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"❌ Upload failed: {e}")

        elif media_type == "Audio":
            with col1:
                st.subheader("🎧 Upload an Audio File")
                uploaded_audio = st.file_uploader("Supported format: WAV", type=["wav"])

            if uploaded_audio:
                original_path = "temp_uploaded_audio.wav"
                with open(original_path, "wb") as f:
                    f.write(uploaded_audio.getbuffer())
                st.session_state["original_audio_path"] = original_path
                st.audio(original_path, format="audio/wav")

            if "original_audio_path" in st.session_state:
                with col2:
                    st.subheader("✉️ Enter Your Secret Message")
                    message = st.text_area("Type the secret message:", height=150)

                    if st.button("Hide Message in Audio"):
                        if message:
                            output_path = "encoded_audio.wav"
                            try:
                                stego_audio = HideAudio(st.session_state["original_audio_path"], output_path)
                                stego_audio.embed_text_lsb(message)
                                st.session_state["encoded_audio_path"] = output_path
                                st.success("✅ Message embedded in audio!")
                                st.audio(output_path, format="audio/wav")

                            except Exception as e:
                                st.error(f"❌ Encoding error: {e}")
                        else:
                            st.warning("⚠️ Please enter a message.")

            if "encoded_audio_path" in st.session_state:
                with col2:
                    if st.button("📤 Share Audio via GoFile & WhatsApp"):
                        try:
                            url = upload_to_gofile(st.session_state["encoded_audio_path"])
                            st.success("🌐 Public URL:")
                            st.code(url)
                            whatsapp_message = f"Check out this stego audio: {url}"
                            whatsapp_url = f"https://wa.me/?text={whatsapp_message.replace(' ', '%20')}"
                            st.markdown(f"[📲 Share via WhatsApp]({whatsapp_url})", unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"❌ Upload failed: {e}")

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
