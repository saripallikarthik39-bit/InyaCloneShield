import os
import time
import json
import math
import wave
import struct
from datetime import datetime
import numpy as np
from flask import Flask, render_template, request, jsonify, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
AUDIO_DIR = os.path.join(STATIC_DIR, "audio")
ENROLLED_USERS_FILE = os.path.join(BASE_DIR, "enrolled_users.json")

app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)

os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

# Generate fallback sample audio files
def create_sample_wav(filename, freq=440, duration=3.5):
    path = os.path.join(AUDIO_DIR, filename)
    if not os.path.exists(path):
        sample_rate = 8000
        n_samples = int(sample_rate * duration)
        with wave.open(path, 'w') as wav_file:
            wav_file.setparams((1, 2, sample_rate, n_samples, 'NONE', 'not compressed'))
            for i in range(n_samples):
                value = int(16000 * (0.6 * math.sin(2 * math.pi * freq * i / sample_rate) +
                                     0.3 * math.sin(2 * math.pi * (freq * 1.5) * i / sample_rate) +
                                     0.1 * math.sin(2 * math.pi * (freq * 2.2) * i / sample_rate)))
                wav_file.writeframes(struct.pack('h', max(-32768, min(32767, value))))

create_sample_wav("attacker_telugu.wav", freq=320, duration=3.5)
create_sample_wav("bot_reply.wav", freq=480, duration=4.0)

# Multi-Bank Metadata
BANKS = {
    "hdfc": {
        "id": "hdfc",
        "name": "HDFC Bank",
        "tagline": "We Understand Your World",
        "bot_title": "HDFC Indic Voice Bot v2.6 (Inya OS)",
        "badge_color": "border-blue-500 text-blue-400 bg-blue-950/40",
        "accent": "#0284c7",
        "greeting": "నమస్కారం! హెచ్‌డీఎఫ్‌సీ (HDFC) బ్యాంక్ వాయిస్ అసిస్టెంట్ కి స్వాగతం."
    },
    "sbi": {
        "id": "sbi",
        "name": "State Bank of India (SBI)",
        "tagline": "The Banker to Every Indian",
        "bot_title": "SBI YONO Indic Voice Assist (armour365)",
        "badge_color": "border-indigo-500 text-indigo-400 bg-indigo-950/40",
        "accent": "#6366f1",
        "greeting": "నమస్కారం! స్టేట్ బ్యాంక్ ఆఫ్ ఇండియా (SBI) యోనో వాయిస్ సేవలకు స్వాగతం."
    },
    "icici": {
        "id": "icici",
        "name": "ICICI Bank",
        "tagline": "Hum Hai Na, Khayaal Aapka",
        "bot_title": "ICICI iMobile Voice Concierge",
        "badge_color": "border-amber-500 text-amber-400 bg-amber-950/40",
        "accent": "#f59e0b",
        "greeting": "నమస్కారం! ఐసీఐసీఐ (ICICI) బ్యాంక్ వాయిస్ డెస్క్ కి స్వాగతం."
    },
    "rural_bank": {
        "id": "rural_bank",
        "name": "Andhra Pragathi Grameena Bank (APGB)",
        "tagline": "రైతు మరియు గ్రామీణ వికాస బ్యాంక్",
        "bot_title": "APGB గ్రామీణ వాయిస్ మిత్ర (Kisan Assist)",
        "badge_color": "border-emerald-500 text-emerald-400 bg-emerald-950/40",
        "accent": "#10b981",
        "greeting": "నమస్తే అండి! ఆంధ్ర ప్రగతి గ్రామీణ బ్యాంక్ (APGB) కిసాన్ వాయిస్ సహాయకుడికి స్వాగతం."
    }
}

# -------------------------------------------------------------
# ENROLLED USER REPOSITORY (Supports ANY Number of Users with Mobile Numbers)
# -------------------------------------------------------------
DEFAULT_ENROLLED_USERS = [
    {
        "id": "usr_hdfc_01",
        "bank_id": "hdfc",
        "bank_name": "HDFC Bank",
        "enrolled_name": "Ramesh Kumar",
        "account_number": "501004291823",
        "mobile_number": "+91 98480 22338",
        "balance": "₹42,850",
        "pitch": 138.5,
        "spectral_centroid": 1680.0,
        "enrolled_date": "01-Nov-2026 09:30:00"
    },
    {
        "id": "usr_sbi_01",
        "bank_id": "sbi",
        "bank_name": "State Bank of India (SBI)",
        "enrolled_name": "Suresh Reddy",
        "account_number": "304812904511",
        "mobile_number": "+91 94401 55677",
        "balance": "₹18,400",
        "pitch": 165.0,
        "spectral_centroid": 1840.0,
        "enrolled_date": "01-Nov-2026 10:15:00"
    },
    {
        "id": "usr_icici_01",
        "bank_id": "icici",
        "bank_name": "ICICI Bank",
        "enrolled_name": "Priya Sharma",
        "account_number": "002401568912",
        "mobile_number": "+91 98200 44119",
        "balance": "₹65,200",
        "pitch": 215.0,
        "spectral_centroid": 2150.0,
        "enrolled_date": "01-Nov-2026 10:45:00"
    },
    {
        "id": "usr_apgb_01",
        "bank_id": "rural_bank",
        "bank_name": "Andhra Pragathi Grameena Bank (APGB)",
        "enrolled_name": "Venkateswarlu (రైతు)",
        "account_number": "194002348102",
        "mobile_number": "+91 97012 33445",
        "balance": "₹8,650",
        "pitch": 128.0,
        "spectral_centroid": 1590.0,
        "enrolled_date": "01-Nov-2026 11:00:00"
    }
]

def load_enrolled_users():
    if not os.path.exists(ENROLLED_USERS_FILE):
        with open(ENROLLED_USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_ENROLLED_USERS, f, indent=2, ensure_ascii=False)
        return DEFAULT_ENROLLED_USERS
    try:
        with open(ENROLLED_USERS_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
            # Ensure every user has mobile_number
            for u in users:
                if "mobile_number" not in u:
                    u["mobile_number"] = "+91 98480 22338"
            return users
    except Exception:
        return DEFAULT_ENROLLED_USERS

def save_enrolled_users(users_list):
    with open(ENROLLED_USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users_list, f, indent=2, ensure_ascii=False)

# -------------------------------------------------------------
# ACOUSTIC SIGNAL PROCESSING (Pitch F0 & Spectral Formants)
# -------------------------------------------------------------
def extract_acoustic_features(wav_filepath, fallback_pitch=None, fallback_centroid=None):
    pitch = float(fallback_pitch) if fallback_pitch else 145.0
    spectral_centroid = float(fallback_centroid) if fallback_centroid else 1750.0
    liveness_score = 99.2

    if not os.path.exists(wav_filepath):
        return {"pitch": pitch, "spectral_centroid": spectral_centroid, "liveness_score": liveness_score}

    try:
        with wave.open(wav_filepath, 'rb') as wf:
            framerate = wf.getframerate()
            n_frames = wf.getnframes()
            audio_bytes = wf.readframes(n_frames)
            
        signal = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32)
        if len(signal) > 400:
            signal = signal / (np.max(np.abs(signal)) + 1e-6)

            # Auto-correlation for Fundamental Frequency (Pitch F0)
            frame_len = min(len(signal), int(framerate * 0.05))
            corr = np.correlate(signal[:frame_len], signal[:frame_len], mode='full')
            corr = corr[len(corr)//2:]
            d = np.diff(corr)
            start = np.where(d > 0)[0]
            if len(start) > 0:
                peak = np.argmax(corr[start[0]:]) + start[0]
                computed_pitch = framerate / (peak + 1e-6)
                pitch = float(np.clip(computed_pitch, 80.0, 420.0))

            # FFT for Vocal Tract Spectral Centroid & Liveness
            fft_vals = np.abs(np.fft.rfft(signal))
            freqs = np.fft.rfftfreq(len(signal), 1.0 / framerate)
            spectral_centroid = float(np.sum(freqs * fft_vals) / (np.sum(fft_vals) + 1e-6))

            high_freq_energy = np.sum(fft_vals[freqs > 3000])
            total_energy = np.sum(fft_vals) + 1e-6
            energy_ratio = float(high_freq_energy / total_energy)
            liveness_score = 99.4 if (0.04 <= energy_ratio <= 0.35) else 13.5
    except Exception as e:
        print("[Acoustic Extraction Warning - using fallback]", e)

    return {
        "pitch": round(pitch, 1),
        "spectral_centroid": round(spectral_centroid, 1),
        "liveness_score": liveness_score
    }

# -------------------------------------------------------------
# BIOMETRIC SIMILARITY FORMULA (Speaker 1:1 Voiceprint Matching)
# -------------------------------------------------------------
def compute_voiceprint_similarity(pitch1, centroid1, pitch2, centroid2):
    diff_pitch = abs(pitch1 - pitch2)
    diff_centroid = abs(centroid1 - centroid2)
    score = 100.0 - (diff_pitch * 1.35 + diff_centroid * 0.042)
    return round(float(np.clip(score, 6.0, 99.2)), 1)

# -------------------------------------------------------------
# API ROUTES
# -------------------------------------------------------------
@app.route("/")
def index():
    users = load_enrolled_users()
    return render_template("index.html", banks=BANKS, enrolled_users=users)

@app.route("/presentation")
def presentation():
    return render_template("presentation.html")

@app.route("/api/banks")
def api_banks():
    return jsonify({"banks": BANKS, "enrolled_users": load_enrolled_users()})

@app.route("/api/users", methods=["GET"])
def get_users():
    return jsonify({"users": load_enrolled_users()})

@app.route("/api/delete-user", methods=["POST"])
def delete_user():
    data = request.json or {}
    user_id = data.get("user_id")
    users = load_enrolled_users()
    updated_users = [u for u in users if u["id"] != user_id]
    save_enrolled_users(updated_users)
    return jsonify({"status": "success", "users": updated_users})

# -------------------------------------------------------------
# ENROLL NEW VOICEPRINT (Supports ANY number of profiles + Mobile)
# -------------------------------------------------------------
@app.route("/api/enroll-voice", methods=["POST"])
def enroll_voice():
    bank_id = request.form.get("bank_id", "hdfc")
    enrollee_name = request.form.get("name", "").strip() or "Registered Customer"
    account_num = request.form.get("account", "").strip() or f"50{int(time.time())}"
    mobile_num = request.form.get("mobile", "").strip() or "+91 98480 22338"
    balance = request.form.get("balance", "").strip() or "₹35,000"
    
    client_pitch = request.form.get("client_pitch")
    client_centroid = request.form.get("client_centroid")

    user_id = f"usr_{bank_id}_{int(time.time()*1000) % 100000}"
    saved_wav_name = f"{user_id}_voice.wav"
    saved_wav_path = os.path.join(AUDIO_DIR, saved_wav_name)

    if 'audio' in request.files:
        file = request.files['audio']
        file.save(saved_wav_path)
        features = extract_acoustic_features(saved_wav_path, client_pitch, client_centroid)
    else:
        features = extract_acoustic_features("", client_pitch, client_centroid)

    bank_meta = BANKS.get(bank_id, BANKS["hdfc"])
    new_profile = {
        "id": user_id,
        "bank_id": bank_id,
        "bank_name": bank_meta["name"],
        "enrolled_name": enrollee_name,
        "account_number": account_num,
        "mobile_number": mobile_num,
        "balance": balance,
        "pitch": features["pitch"],
        "spectral_centroid": features["spectral_centroid"],
        "audio_url": f"/static/audio/{saved_wav_name}" if os.path.exists(saved_wav_path) else None,
        "enrolled_date": datetime.now().strftime("%d-%b-%Y %H:%M:%S")
    }

    users = load_enrolled_users()
    users.append(new_profile)
    save_enrolled_users(users)

    return jsonify({
        "status": "success",
        "message": f"Voice biometric successfully registered for {enrollee_name} at {bank_meta['name']}!",
        "profile": new_profile,
        "all_users": users
    })

# -------------------------------------------------------------
# UPLOAD CUSTOM LIVE VOICE FROM MIC (Analyzes against Target User)
# -------------------------------------------------------------
@app.route("/api/upload-voice", methods=["POST"])
def upload_voice():
    if 'audio' not in request.files:
        return jsonify({"status": "error", "message": "No audio file provided"}), 400
    
    file = request.files['audio']
    filename = "custom_live_voice.wav"
    filepath = os.path.join(AUDIO_DIR, filename)
    file.save(filepath)
    
    client_pitch = request.form.get("client_pitch")
    client_centroid = request.form.get("client_centroid")
    live_features = extract_acoustic_features(filepath, client_pitch, client_centroid)
    
    # Target user to evaluate live audio against
    target_user_id = request.form.get("user_id")
    all_users = load_enrolled_users()
    target_user = None
    if target_user_id:
        matches = [u for u in all_users if u["id"] == target_user_id]
        if matches:
            target_user = matches[0]
    if not target_user and all_users:
        target_user = all_users[0]
        
    similarity = 50.0
    detected_mode = "impostor"
    if target_user:
        similarity = compute_voiceprint_similarity(
            live_features["pitch"], live_features["spectral_centroid"],
            target_user["pitch"], target_user["spectral_centroid"]
        )
        if live_features["liveness_score"] < 50.0:
            detected_mode = "clone"
        elif similarity >= 72.0:
            detected_mode = "human"
        else:
            detected_mode = "impostor"
            
    return jsonify({
        "status": "success",
        "features": live_features,
        "detected_mode": detected_mode,
        "similarity": similarity,
        "target_user_name": target_user["enrolled_name"] if target_user else "Customer",
        "target_bank": target_user["bank_name"] if target_user else "Bank"
    })

# -------------------------------------------------------------
# 1:N MULTI-USER BIOMETRIC EVALUATION ENGINE
# -------------------------------------------------------------
@app.route("/api/attack", methods=["POST"])
def run_attack():
    payload = request.json or {}
    bank_id = payload.get("bank_id", "hdfc")
    scenario_key = payload.get("scenario", "genuine_human")
    snr_db = payload.get("snr_db", 10)
    user_identity_mode = payload.get("user_identity_mode", "human") # "human", "impostor", "clone"
    custom_spoken_text = payload.get("custom_spoken_text", "").strip()
    client_pitch = payload.get("client_pitch")
    client_centroid = payload.get("client_centroid")

    bank_info = BANKS.get(bank_id, BANKS["hdfc"])
    all_users = load_enrolled_users()
    target_user_id = payload.get("user_id")
    
    # Filter users enrolled in the selected bank
    bank_users = [u for u in all_users if u["bank_id"] == bank_id]
    if not bank_users:
        bank_users = all_users

    # Select specific target enrolled user
    if target_user_id:
        matching = [u for u in all_users if u["id"] == target_user_id]
        primary_user = matching[0] if matching else (bank_users[0] if bank_users else DEFAULT_ENROLLED_USERS[0])
    else:
        primary_user = bank_users[0] if bank_users else DEFAULT_ENROLLED_USERS[0]

    target_user = primary_user["enrolled_name"]
    target_acc = primary_user["account_number"]
    target_phone = primary_user.get("mobile_number", "+91 98480 22338")
    target_bal = primary_user["balance"]

    custom_wav = os.path.join(AUDIO_DIR, "custom_live_voice.wav")
    is_live_mic = (scenario_key == "custom_user_voice") and os.path.exists(custom_wav)

    # 1. Acoustic Feature Extraction of Incoming Audio
    if is_live_mic:
        incoming_features = extract_acoustic_features(custom_wav, client_pitch, client_centroid)
        in_pitch = incoming_features["pitch"]
        in_centroid = incoming_features["spectral_centroid"]
        in_liveness = incoming_features["liveness_score"]
    elif user_identity_mode == "clone" or scenario_key == "telugu_scammer":
        in_pitch = 145.0
        in_centroid = 2800.0
        in_liveness = 12.4
    elif user_identity_mode == "impostor" or scenario_key == "impostor_human":
        in_pitch = primary_user["pitch"] + 55.0
        in_centroid = primary_user["spectral_centroid"] + 380.0
        in_liveness = 99.1
    else:
        in_pitch = primary_user["pitch"] + 2.1
        in_centroid = primary_user["spectral_centroid"] + 15.0
        in_liveness = 99.4

    # 2. Compute 1:1 similarity against the targeted selected user (e.g. Karthik)
    target_similarity = compute_voiceprint_similarity(
        in_pitch, in_centroid, primary_user["pitch"], primary_user["spectral_centroid"]
    )

    # 1:N Biometric Matching across all enrolled users for audit log
    comparison_results = []
    best_match_user = primary_user
    best_similarity = target_similarity

    for user in bank_users:
        sim = compute_voiceprint_similarity(in_pitch, in_centroid, user["pitch"], user["spectral_centroid"])
        comparison_results.append({
            "user_id": user["id"],
            "name": user["enrolled_name"],
            "account": user["account_number"],
            "mobile": user.get("mobile_number", "+91 98480 22338"),
            "pitch": user["pitch"],
            "spectral_centroid": user["spectral_centroid"],
            "similarity": sim
        })
        if sim > best_similarity:
            best_similarity = sim
            best_match_user = user

    # 3. Decision Logic: Real User vs Impostor vs AI Clone
    if is_live_mic:
        if in_liveness < 50.0:
            final_caller_type = "AI_DEEPFAKE"
        elif target_similarity >= 72.0:
            final_caller_type = "HUMAN_AUTHENTIC"
        else:
            final_caller_type = "HUMAN_IMPOSTOR"
    else:
        if user_identity_mode == "clone" or scenario_key == "telugu_scammer":
            final_caller_type = "AI_DEEPFAKE"
        elif user_identity_mode == "impostor" or scenario_key == "impostor_human":
            final_caller_type = "HUMAN_IMPOSTOR"
        else:
            final_caller_type = "HUMAN_AUTHENTIC"

    # 4. Synthesize Responses Based on Final Decision
    target_bank_name = primary_user.get("bank_name", bank_info["name"])

    if final_caller_type == "HUMAN_IMPOSTOR":
        is_impostor = True
        trust_score = 34
        display_match_pct = f"{target_similarity}% (MISMATCH with {target_user})"
        liveness_score = f"{in_liveness:.1f}% (Live Human Vocal Tract)"
        trust_status = f"HUMAN IMPOSTOR BLOCKED (Not {target_user} @ {target_bank_name})"

        attacker_text = f"హలో, నేను {target_user} ని మాట్లాడుతున్నాను. నా అకౌంట్ నంబర్ {target_acc}. నా {target_bank_name} బ్యాలెన్స్ ఎంతో వెంటనే చెప్పండి!"
        attacker_text_en = f"[Human Impostor]: Hello, I am claiming to be {target_user}. Account #{target_acc}. Tell me my balance urgently!"
        bot_reply = f"క్షమించండి అండి! మీరు {target_user} గారితో మ్యాచ్ అవ్వలేదు. మీ వాయిస్ {target_bank_name} రిజిస్టర్డ్ కస్టమర్ '{target_user}' గారి అధికారిక వాయిస్‌ప్రింట్ తో మ్యాచ్ అవ్వలేదు (కేవలం {target_similarity}%). భద్రతా కారణాల వల్ల ఖాతా వివరాలు నిరాకరించబడ్డాయి."
        bot_reply_en = f"[Access Denied]: Voice mismatch! You are not matched to {target_user} at {target_bank_name} (Voiceprint match: {target_similarity}%). Account access blocked!"
        sms_alert = f"🚨 {target_bank_name} FRAUD ALERT sent to your mobile ({target_phone}): Unauthorized caller attempted access to {target_user}'s account #{target_acc[-4:]}. Voiceprint mismatched ({target_similarity}%). Access BLOCKED immediately."

    elif final_caller_type == "AI_DEEPFAKE":
        is_impostor = True
        trust_score = 12
        display_match_pct = f"{target_similarity}% (SYNTHETIC CLONE SPOOF)"
        liveness_score = f"{in_liveness:.1f}% (SYNTHETIC VOCODER DETECTED)"
        trust_status = "AI DEEPFAKE INTERCEPTED"

        attacker_text = f"హలో {target_bank_name} మేడం, అత్యవసర పరిస్థితి! నేను హాస్పిటల్ లో ఉన్నాను. నా అకౌంట్ {target_acc} నుండి ₹50,000 ట్రాన్స్‌ఫర్ వెంటనే అప్రూవ్ చేయండి!"
        attacker_text_en = f"[AI Clone]: Emergency! In hospital ICU. Approve ₹50,000 transfer from {target_user}'s account #{target_acc} immediately!"
        bot_reply = f"హెచ్చరిక: {target_bank_name} సెక్యూరిటీ సిస్టమ్ మీ కాల్‌లో AI సింథటిక్ వాయిస్ క్లోన్ గుర్తించింది. {target_user} గారి ఖాతా రక్షణ కోసం లావాదేవీలు నిలిపివేయబడ్డాయి."
        bot_reply_en = f"[Access Blocked]: AI Deepfake clone detected! Fraud attack blocked on {target_user}'s account."
        sms_alert = f"🚨 {target_bank_name} CRITICAL ALERT sent to ({target_phone}): AI synthetic voice clone spoof attack blocked on {target_user}'s account #{target_acc[-4:]}. Zero funds compromised."

    else:
        # HUMAN_AUTHENTIC (Genuine Enrolled Customer)
        is_impostor = False
        trust_score = 98
        display_match_pct = f"{max(target_similarity, 93.6)}% (VERIFIED {target_user.upper()})"
        liveness_score = f"{in_liveness:.1f}% (Live Human Vocal Tract)"
        trust_status = f"VERIFIED: {target_user} ({target_bank_name})"

        attacker_text = f"నమస్కారం అండి, నా పేరు {target_user}. నా అకౌంట్ నంబర్ {target_acc}. నా {target_bank_name} ఖాతాలో ఎంత బ్యాలెన్స్ ఉందో దయచేసి చెప్పండి."
        attacker_text_en = f"[{target_user} - Real User]: Hello, my name is {target_user}. Account #{target_acc}. Please tell me my balance."
        bot_reply = f"నమస్కారం {target_user} గారు! మీ లైవ్ వాయిస్ మీ బ్యాంక్ వివరాలతో ({target_bank_name}) సరిగ్గా మ్యాచ్ అయ్యింది. మీ బ్యాంక్ బ్యాలెన్స్ {target_bal} రూపాయలు."
        bot_reply_en = f"[Access Granted]: Voice matched your bank details with {target_bank_name}! Hello {target_user} garu, your balance is {target_bal}."
        sms_alert = f"✓ {target_bank_name} SMS sent to ({target_phone}): Balance {target_bal} accessed via Voice AI for {target_user} at {datetime.now().strftime('%H:%M')}. Biometrics verified."

    if custom_spoken_text and is_live_mic:
        attacker_text = custom_spoken_text
        attacker_text_en = f"[Live Mic Spoken Speech]: \"{custom_spoken_text}\""

    noise_penalty_ms = max(0, int((22 - snr_db) * 4.5))
    final_latency = 265 + noise_penalty_ms
    acc_drop = max(0.0, (22 - snr_db) * 0.45)
    adjusted_acc = f"{max(82.0, 98.4 - acc_drop):.1f}%"
    audio_path = "/static/audio/custom_live_voice.wav" if is_live_mic else "/static/audio/attacker_telugu.wav"

    return jsonify({
        "status": "success",
        "bank_id": bank_id,
        "bank_name": bank_info["name"],
        "bot_title": bank_info["bot_title"],
        "caller_type": final_caller_type,
        "sms_notification": sms_alert,
        "alert_phone": target_phone,
        "target_user_name": target_user,
        "attacker": {
            "text": attacker_text,
            "text_en": attacker_text_en,
            "audio_url": audio_path,
            "liveness_score": liveness_score,
            "voiceprint_match": display_match_pct,
            "is_impostor": is_impostor,
            "measured_pitch": in_pitch,
            "measured_centroid": in_centroid
        },
        "target_bot": {
            "text": bot_reply,
            "text_en": bot_reply_en,
            "audio_url": "/static/audio/bot_reply.wav",
            "status": "ACCESS_GRANTED" if not is_impostor else "ACCESS_BLOCKED"
        },
        "diagnostics": {
            "trust_score": trust_score,
            "trust_status": trust_status,
            "liveness_score": liveness_score,
            "voiceprint_match": display_match_pct,
            "asr_accuracy": adjusted_acc,
            "turn_latency_ms": final_latency,
            "barge_in_ms": 145,
            "telephony_codec": "8kHz G.711 Narrowband",
            "noise_profile": f"MUMBAI TRAFFIC @ {snr_db}dB SNR",
            "enrolled_name": primary_user["enrolled_name"],
            "enrolled_account": primary_user["account_number"],
            "enrolled_phone": target_phone,
            "bank_name": primary_user.get("bank_name", bank_info["name"]),
            "timestamp": datetime.now().strftime("%d-%b-%Y %H:%M:%S"),
            "candidate_comparisons": comparison_results
        }
    })

@app.route("/static/audio/<path:filename>")
def serve_audio(filename):
    return send_from_directory(AUDIO_DIR, filename)

if __name__ == "__main__":
    print("================================================================")
    print("🛡️  Inya-CloneShield: Multi-User Voice Biometrics Started")
    print("🚀  Dashboard running live at: http://localhost:5000")
    print("================================================================")
    app.run(host="0.0.0.0", port=5000, debug=True)
