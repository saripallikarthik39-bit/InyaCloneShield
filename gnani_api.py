"""
Gnani.ai Proprietary Stack Integration Module
Using Single Unified Master API Key for:
1. Gnani Prisma v2.5 (STT - Speech-to-Text)
2. Gnani Timbre v2.0 (TTS - Text-to-Speech)
3. Voice Cloning / armour365
"""

import requests
import json
import os

# ======================================================================
# PASTE YOUR SINGLE GNANI API KEY HERE:
# ======================================================================
GNANI_API_KEY = os.getenv("GNANI_API_KEY", "vach_1ytE2CY5X2DzFv56YKIzWPVm9KtNsloPF5wJYx4Hm4CycmISrHq1V7GecijArYv2twqavFkUgzjYP3I6CyNhTjQzANNZDPwO_f65d52cb483a704258aa124f140b156d")
# ======================================================================

class GnaniEngine:
    def __init__(self, api_key=GNANI_API_KEY):
        self.api_key = api_key
        # Gnani API Endpoints
        self.stt_endpoint = "https://api.gnani.ai/v1/stt"
        self.tts_endpoint = "https://api.gnani.ai/v1/tts"
        self.clone_endpoint = "https://api.gnani.ai/v1/voice-clone"

    def is_configured(self):
        return bool(self.api_key and self.api_key != "YOUR_GNANI_API_KEY_HERE")

    def transcribe(self, audio_path, language="te-IN"):
        """
        Uses Gnani Prisma v2.5 STT to transcribe noisy audio.
        """
        if not self.is_configured():
            print("[Gnani STT] Using built-in simulation fallback.")
            return None

        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            with open(audio_path, "rb") as f:
                files = {"audio": f}
                data = {"language": language, "model": "prisma-v2.5"}
                response = requests.post(self.stt_endpoint, headers=headers, files=files, data=data, timeout=5)
                if response.status_code == 200:
                    return response.json().get("transcript", "")
                else:
                    print(f"[Gnani STT Warning] Status {response.status_code}: {response.text}")
                    return None
        except Exception as e:
            print(f"[Gnani STT Error] {e}")
            return None

    def synthesize(self, text, language="te-IN", voice="female-agent"):
        """
        Uses Gnani Timbre v2.0 TTS to speak the target bot's response.
        """
        if not self.is_configured():
            print("[Gnani TTS] Using built-in simulation fallback.")
            return None

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "language": language,
            "voice": voice,
            "sample_rate": 8000
        }
        try:
            response = requests.post(self.tts_endpoint, headers=headers, json=payload, timeout=5)
            if response.status_code == 200:
                output_path = "static/audio/live_bot_reply.wav"
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return output_path
            else:
                print(f"[Gnani TTS Warning] Status {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"[Gnani TTS Error] {e}")
            return None

    def clone_voice(self, sample_audio_path, text_to_speak):
        """
        Uses Gnani Voice Cloning with your master key.
        If your tier does not have Voice Cloning activated yet, 
        it automatically falls back to the simulated attacker voice safely!
        """
        if not self.is_configured():
            return None

        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            with open(sample_audio_path, "rb") as f:
                files = {"reference_audio": f}
                data = {"text": text_to_speak, "lang": "te-IN"}
                response = requests.post(self.clone_endpoint, headers=headers, files=files, data=data, timeout=8)
                if response.status_code == 200:
                    output_path = "static/audio/live_cloned_voice.wav"
                    with open(output_path, "wb") as out:
                        out.write(response.content)
                    return output_path
                else:
                    # Graceful fallback so your demo never fails
                    print(f"[Gnani Clone API Note] Server returned {response.status_code}, using realistic fallback.")
                    return None
        except Exception as e:
            print(f"[Gnani Clone Error] {e}")
            return None
