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
st.title("🔐 Steganography Assistant")
st.caption("Securely hide and reveal messages in image or audio files using steganography.")

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
            st.subheader("📁 Select Data Type")
            media_type = st.radio("Choose where to hide the message:", ["Image", "Audio"], index=None)

        if media_type == "Image":
            with col1:
                st.subheader("🖼️ Upload an Image File")
                uploaded_img = st.file_uploader("Supported formats: PNG, JPG, JPEG", type=["png", "jpg", "jpeg"])

            if uploaded_img:
                # Save the uploaded image temporarily to disk for capacity calculation and processing
                original_path = "temp_uploaded_image.png"
                with open(original_path, "wb") as f:
                    f.write(uploaded_img.getbuffer())
                with col2:
                    message = st.text_area(f"Type the secret message:", height=120)
                    output_path = "encoded_image.png"
                    if st.button("Hide Message in Image"):

                        try:
                            stego_img = HideImage(original_path, output_path)
                            stego_img.embed_text_pvd(message)
                            st.success("✅ Message embedded successfully.")
                            # Show original and stego images side by side
                            img_col1, img_col2 = st.columns(2)
                            with img_col1:
                                st.image(original_path, caption="Original Image", use_column_width=True)
                            with img_col2:
                                st.image(output_path, caption="Stego Image", use_column_width=True)
                            with open(output_path, "rb") as f:
                                st.download_button("⬇️ Download Encoded Image", f, file_name="stego_image.png")
                            st.caption("💾 The file will be saved to your **Downloads** folder as `stego_image.png` after clicking the button.")
                            # Sharing section
                            st.subheader("📤 Share with Friends")
                            col_share1, col_share2 = st.columns(2)
                            with col_share1:
                                st.markdown(
                                    "[📱 Share via WhatsApp](https://wa.me/?text=Hey!%20Check%20out%20this%20encoded%20audio%20file%20I%20created.%20You'll%20find%20it%20in%20the%20Downloads%20folder!)",
                                    unsafe_allow_html=True
                                )
                            with col_share2:
                                st.markdown(
                                    "[📧 Share via Gmail](https://mail.google.com/mail/?view=cm&fs=1&tf=1&su=Encoded%20Audio%20File&body=Hey!%20I'm%20sharing%20an%20encoded%20audio%20file.%20You%20can%20find%20it%20in%20the%20Downloads%20folder%20after%20downloading%20from%20the%20tool.)",
                                    unsafe_allow_html=True
                                )

                        except Exception as e:
                            st.error(f"❌ An error occurred during encoding: {e}")

        elif media_type == "Audio":
            with col1:
                st.subheader("🎧 Upload an Audio File")
                uploaded_audio = st.file_uploader("Supported formats: WAV (recommended)", type=["wav", "mp3", "ogg"])

            if uploaded_audio:
                # Save the uploaded audio temporarily to disk for capacity calculation and processing
                original_audio_path = "temp_uploaded_audio.wav"
                with open(original_audio_path, "wb") as f:
                    f.write(uploaded_audio.getbuffer())



                with col2:
                    st.subheader("✉️ Enter Your Secret Message")
                    message = st.text_area(f"Type the secret message:", height=120)

                    output_path = "encoded_audio.wav"
                    if st.button("Hide Message in Audio"):

                        try:
                            stego_audio = HideAudio(original_audio_path, output_path)
                            stego_audio.embed_text_lsb(message)
                            st.success("✅ Message successfully embedded into the audio.")
                            st.audio(output_path, format="audio/wav")
                            with open(output_path, "rb") as f:
                                st.download_button("⬇️ Download Encoded Audio", f, file_name="stego_audio.wav")
                            st.caption("💾 The file will be saved to your **Downloads** folder as `stego_audio.wav` after clicking the button.")
                        except Exception as e:
                            st.error(f"❌ An error occurred during encoding: {e}")
                        # Sharing section
                        st.subheader("📤 Share with Friends")
                        col_share1, col_share2 = st.columns(2)
                        with col_share1:
                            st.markdown(
                                "[📱 Share via WhatsApp](https://wa.me/?text=Hey!%20Check%20out%20this%20encoded%20audio%20file%20I%20created.%20You'll%20find%20it%20in%20the%20Downloads%20folder!)",
                                unsafe_allow_html=True
                            )
                        with col_share2:
                            st.markdown(
                                "[📧 Share via Gmail](https://mail.google.com/mail/?view=cm&fs=1&tf=1&su=Encoded%20Audio%20File&body=Hey!%20I'm%20sharing%20an%20encoded%20audio%20file.%20You%20can%20find%20it%20in%20the%20Downloads%20folder%20after%20downloading%20from%20the%20tool.)",
                                unsafe_allow_html=True
                            )

    # Unhide message code stays the same
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
                                num_lines = hidden_message.count('\n') + 1
                                dynamic_height = min(500, max(100, num_lines * 20))
                                st.text_area("Hidden message:", value=hidden_message, height=dynamic_height, disabled=True)
                        except Exception as e:
                            st.error(f"❌ Failed to extract message: {e}")

        elif media_type == "Audio":
            with col2:
                st.subheader("🎧 Upload Audio File")
                uploaded_audio = st.file_uploader("Supported formats: MP3, WAV, OGG", type=["mp3", "wav", "ogg"])

                if uploaded_audio:
                    st.success("✅ Audio uploaded successfully.")
                    st.audio(uploaded_audio, format="audio/wav")
                    if st.button("Reveal Message from Audio"):


                        try:
                            extract_audio = UnhideAudio(uploaded_audio)
                            hidden_message = extract_audio.extract_text_lsb()

                            with st.chat_message("assistant"):
                                st.subheader("🕵️ Extracted Message")
                                num_lines = hidden_message.count('\n') + 1
                                dynamic_height = min(500, max(100, num_lines * 20))
                                st.text_area("Hidden message:", value=hidden_message, height=dynamic_height, disabled=True)
                        except Exception as e:
                            st.error(f"❌ Failed to extract message: {e}")

# -------------------------------
# Footer and Notes
# -------------------------------
st.info(
    "💡 **Note**: The size and resolution of your file significantly affect how much data can be hidden. "
    "For **very small images**, the encoder might not be able to embed the entire message properly, "
    "and the decoder may fail to extract it accurately. Consider using higher-resolution images for better results."
)
