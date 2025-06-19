import streamlit as st
import openai
import requests
import json

st.set_page_config(page_title="AI Content Creator PoC", layout="centered")
st.title("🎬 AI Content Creation Studio (Proof of Concept)")

# Load API keys from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]
replicate_api = st.secrets["REPLICATE_API_KEY"]
elevenlabs_api = st.secrets["ELEVENLABS_API_KEY"]
heygen_api = st.secrets["HEYGEN_API_KEY"]

# Sidebar menu
st.sidebar.title("Modules")
module = st.sidebar.radio("Select a feature:", ["Script Writer", "Text to Image", "Voice Over", "Avatar Video"])

# ---------------- SCRIPT WRITING ----------------
if module == "Script Writer":
    st.header("📝 Script Writer")
    prompt = st.text_area("Describe your video idea:", placeholder="A motivational video about perseverance in business")
    tone = st.selectbox("Select tone:", ["Professional", "Inspirational", "Funny", "Casual"])
    if st.button("Generate Script"):
        with st.spinner("Generating script using GPT..."):
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": f"You are a scriptwriter creating a {tone.lower()} script for video narration."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=600
            )
            script = response.choices[0].message.content
            st.text_area("Generated Script:", script, height=300)

# ---------------- TEXT TO IMAGE ----------------
elif module == "Text to Image":
    st.header("🖼️ Text to Image Generator")
    prompt = st.text_area("Enter image prompt:", placeholder="A futuristic city skyline at sunset")
    model = "stability-ai/sdxl"
    if st.button("Generate Image"):
        with st.spinner("Generating image from Replicate SDXL..."):
            url = f"https://api.replicate.com/v1/predictions"
            headers = {
                "Authorization": f"Token {replicate_api}",
                "Content-Type": "application/json"
            }
            data = {
                "version": "a9758cb7b05c5795cd0a78a2e0c04ec303b6367fbb9c8f4efbcd687bdfb02e55",
                "input": {"prompt": prompt}
            }
            response = requests.post(url, headers=headers, data=json.dumps(data))
            prediction = response.json()
            if prediction.get("output"):
                st.image(prediction["output"][0], caption="Generated Image")
            else:
                st.error("Image generation failed. Try a different prompt.")

# ---------------- VOICE OVER ----------------
elif module == "Voice Over":
    st.header("🎙️ Voice Over Generator")
    script_input = st.text_area("Enter narration script:", placeholder="This is a sample narration script.")
    voice_id = st.text_input("Enter Voice ID (from ElevenLabs)", value="EXAVITQu4vr4xnSDxMaL")
    if st.button("Generate Voice Over"):
        with st.spinner("Generating voiceover via ElevenLabs..."):
            tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {
                "xi-api-key": elevenlabs_api,
                "Content-Type": "application/json"
            }
            payload = {
                "text": script_input,
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
            response = requests.post(tts_url, headers=headers, json=payload)
            if response.status_code == 200:
                with open("output.mp3", "wb") as f:
                    f.write(response.content)
                st.audio("output.mp3")
            else:
                st.error("Voice generation failed. Check voice ID and script.")

# ---------------- AVATAR VIDEO ----------------
elif module == "Avatar Video":
    st.header("🧑‍💼 Avatar Video Generator")
    st.markdown("This demo uses the HeyGen API to create an avatar video.")
    video_script = st.text_area("Enter script for avatar video:")
    avatar_id = st.text_input("Enter Avatar ID (HeyGen)", value="Default")
    if st.button("Generate Avatar Video"):
        with st.spinner("Submitting to HeyGen..."):
            url = "https://api.heygen.com/v1/video/generate"
            headers = {
                "Authorization": f"Bearer {heygen_api}",
                "Content-Type": "application/json"
            }
            payload = {
                "avatar_id": avatar_id,
                "script": video_script,
                "voice": "en_us_001"
            }
            res = requests.post(url, headers=headers, json=payload)
            if res.status_code == 200:
                video_info = res.json()
                st.json(video_info)
            else:
                st.error("Video generation failed. Check avatar ID and script.")
