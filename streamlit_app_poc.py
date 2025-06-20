import streamlit as st
import openai
import requests
import json

st.set_page_config(page_title="AI Content Creator PoC", layout="centered")
st.title("🎬 AI Content Creation Studio (Proof of Concept)")

# Load API keys from Streamlit secrets
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
replicate_api = st.secrets["REPLICATE_API_KEY"]
elevenlabs_api = st.secrets["ELEVENLABS_API_KEY"]
heygen_api = st.secrets["HEYGEN_API_KEY"]

# Sidebar menu
st.sidebar.title("Modules")
module = st.sidebar.radio(
    "Select a feature:",
    ["Script Writer", "Text to Image", "Voice Over", "Avatar Video"]
)

# ---------------- SCRIPT WRITING ----------------
if module == "Script Writer":
    st.header("📝 Script Writer")
    prompt = st.text_area(
        "Describe your video idea:",
        placeholder="A motivational video about perseverance in business"
    )
    tone = st.selectbox(
        "Select tone:",
        ["Professional", "Inspirational", "Funny", "Casual"]
    )

    if st.button("Generate Script"):
        with st.spinner("Generating script using GPT..."):
            try:
                client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                f"You are a scriptwriter creating a "
                                f"{tone.lower()} script for video narration."
                            )
                        },
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=600
                )
                script = response.choices[0].message.content
                st.text_area("Generated Script:", script, height=300)
            except Exception as e:
                st.error(f"Script generation failed: {e}")

# ---------------- TEXT TO IMAGE ----------------
if module == "Text to Image":
    st.header("🖼️ Text to Image Generator")
    prompt = st.text_area(
        "Enter image prompt:",
        placeholder="A futuristic city skyline at sunset"
    )
    if st.button("Generate Image"):
        with st.spinner("Generating image from Replicate SDXL..."):
            url = "https://api.replicate.com/v1/predictions"
            headers = {
                "Authorization": f"Token {replicate_api}",
                "Content-Type": "application/json"
            }
            data = {
                "version": "39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                "input": {"prompt": prompt}
            }
            resp = requests.post(url, headers=headers, json=data)
            try:
                prediction = resp.json()
                if prediction.get("output"):
                    st.image(prediction["output"][0], caption="Generated Image")
                else:
                    st.error(f"Image generation failed: {prediction}")
            except ValueError:
                st.error(f"Invalid response: {resp.text}")

# ---------------- VOICE OVER ----------------
if module == "Voice Over":
    st.header("🎙️ Voice Over Generator")
    script_input = st.text_area(
        "Enter narration script:",
        placeholder="This is a sample narration script."
    )
    voice_id = st.text_input(
        "Enter Voice ID (from ElevenLabs)",
        value="mICtXKBwZnUg1cC6k90B"
    )

    if st.button("Generate Voice Over"):
        if not script_input.strip():
            st.warning("Please enter some script text first.")
        else:
            with st.spinner("Generating voiceover via ElevenLabs..."):
                tts_url = (
                    f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
                )
                headers = {
                    "xi-api-key": elevenlabs_api,
                    "Content-Type": "application/json",
                    "Accept": "audio/mpeg"
                }
                payload = {
                    "text": script_input,
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75
                    }
                }
                try:
                    response = requests.post(
                        tts_url, headers=headers, json=payload
                    )
                    if response.status_code == 200:
                        with open("output.mp3", "wb") as f:
                            f.write(response.content)
                        st.audio("output.mp3")
                    else:
                        st.error(
                            f"Voice generation failed. "
                            f"Status: {response.status_code} | {response.text}"
                        )
                except requests.RequestException as e:
                    st.error(f"Network error: {e}")

# ---------------- AVATAR VIDEO ----------------
if module == "Avatar Video":
    st.header("🧑‍💼 Avatar Video Generator")
    st.markdown("This demo uses the HeyGen API to create an avatar video.")
    video_script = st.text_area("Enter script for avatar video:")
    avatar_id = st.text_input(
        "Enter Avatar ID (HeyGen)",
        placeholder="e.g. avtr_123abc"
    )

    if st.button("Generate Avatar Video"):
        if not video_script.strip() or not avatar_id.strip():
            st.warning("Both script and avatar ID are required.")
        else:
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
                try:
                    res = requests.post(url, headers=headers, json=payload)
                    if res.status_code == 200:
                        st.json(res.json())
                    else:
                        st.error(
                            f"Video generation failed. "
                            f"Status: {res.status_code} | {res.text}"
                        )
                except requests.RequestException as e:
                    st.error(f"Network error: {e}")
