from gtts import gTTS
import os

def generate_audio(text, output_path):
    try:
        # 'slow=False' makes it speak at a normal conversational speed
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(output_path)
        return output_path
    except Exception as e:
        print(f"TTS Error: {e}")
        return None