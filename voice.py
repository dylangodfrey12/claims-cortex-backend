import os
import uuid
import cloudinary
import config
from cloudinary.uploader import upload
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

client = ElevenLabs(api_key=config.ELEVENLABS_API_KEY)

# Set Cloudinary configuration
cloudinary.config(
    cloud_name='dzfz5d8a2',
    api_key=config.CLOUDINARY_API_KEY,
    api_secret=config.CLOUDINARY_API_KEY_SECRET
)

def generate_audio(text: str) -> str:
    response = client.text_to_speech.convert(
        voice_id="pNInz6obpgDQGcFmaJgB",
        optimize_streaming_latency="0",
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_turbo_v2",
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
        ),
    )

    save_file_path = f"{uuid.uuid4()}.mp3"
    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)

    print(f"{save_file_path}: A new audio file was saved successfully!")

    # Upload to Cloudinary
    result = upload(save_file_path, resource_type="video")
    audio_url = result.get('url')

    # Delete local file after upload
    os.remove(save_file_path)

    return audio_url
