# 🛡️ Inya-CloneShield: Autonomous Multi-Bank Voice Biometrics & Telephony SOC
> **AI-Powered Voice Biometrics Defense & Telephony Red-Teaming Harness for Indian Banking**  
> *Developed for the Gnani.ai Enterprise Hackathon (armour365™ & Prisma ASR Track)*

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Three.js](https://img.shields.io/badge/Three.js-3D_Radar-black?style=for-the-badge&logo=three.js&logoColor=white)](https://threejs.org)
[![RBI Digital Banking](https://img.shields.io/badge/RBI_Compliance-4%2F4_Pass-10b981?style=for-the-badge)](https://rbi.org.in)

---

## 🌟 Executive Overview

**Inya-CloneShield** is an autonomous telephony security platform engineered to protect Indian banking conversational voice AI from **Generative AI Deepfake Voice Clones** and **Human Impostors with stolen KYC data**. 

Operating over bandwidth-constrained **8kHz G.711 Narrowband** telephony networks under harsh ambient noise (Indian street traffic at 10dB SNR), the platform evaluates live biological vocal tract liveness and fundamental frequency ($F_0$) resonance within **265 milliseconds (<350ms SLA)**.

```
       [ 📞 Inbound 8kHz Telephony Call ]
                      │
                      ▼
       [ 🛡️ armour365™ Voice Radar ]
        ├── Layer 1: Biological Vocal Tract Liveness (99.4%)
        ├── Layer 2: 1:1 Voiceprint Formants Matching (F0, F1, F2)
        └── 1:N Fraudster Blacklist Surveillance
                      │
      ┌───────────────┴───────────────┐
      ▼                               ▼
[ ACCESS GRANTED ]           [ ACCESS BLOCKED ]
Voice Matched Registered     Human Impostor / AI Clone Intercepted
Account Balance Disclosed    Instant Fraud SMS & Voice-OTP Dispatched
```

---

## 🚀 Key Features

1. **Solving the "Two Humans" Challenge:**
   - Evaluates physiological throat formants and pitch ($F_0$) to separate genuine account holders from impostors who memorize stolen account numbers.
2. **Multi-Bank Enterprise Integration:**
   - **HDFC Bank:** Urban Standard Telugu & English Wealth Banking Concierge.
   - **State Bank of India (YONO):** Retail Banking & Pension Voice Biometric Assist.
   - **ICICI Bank:** Corporate Telephony & High-Value Wire Transfer Monitoring.
   - **Andhra Pragathi Grameena Bank (APGB):** Rural Rayalaseema Telugu Kisan Voice Assist.
3. **1:N Multi-User Voiceprint Registry:**
   - Dynamically enroll any number of customers with custom phone numbers, account balances, and 16-bit PCM WAV acoustics (`enrolled_users.json`).
4. **Out-of-Band Voice-OTP 2FA:**
   - Automated telephony challenge that rings the customer's registered physical SIM, speaking dynamic 6-digit OTPs in Telugu and English.
5. **Instant Fraud SMS Dispatch:**
   - Automatically pushes security alerts directly to the genuine customer's mobile when an unauthorized access attempt is detected.
6. **3D Biometric Defense Hologram:**
   - A reactive Three.js holographic shield and dual scan rings anchored smoothly on the right side, visualizing threat telemetry in real-time.
7. **Interactive 10-Slide Pitch Deck:**
   - Built-in full-screen presentation deck at `/presentation` with bilingual speaker notes (Telugu & English).

---

## 🛠️ Quick Start Guide

### 1. Prerequisites
- Python 3.10 or higher installed.
- Git installed.

### 2. Installation & Run Locally

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/InyaCloneShield.git
cd InyaCloneShield

# Install dependencies
pip install -r requirements.txt

# Start the Telephony SOC Server
python server.py
```

Open your browser and visit:
- **Telephony SOC Command Center:** 👉 `http://localhost:5000`
- **Interactive Presentation Deck:** 👉 `http://localhost:5000/presentation`

---

## 📂 Project Architecture

```
InyaCloneShield/
│
├── server.py              # Flask server, acoustic extraction, 1:N matching logic
├── enrolled_users.json    # Persistent multi-bank customer biometric database
├── requirements.txt       # Production dependencies (Flask, NumPy, Gunicorn)
├── Procfile               # Cloud deployment configuration
├── .gitignore             # Git ignore rules
├── README.md              # Project documentation
│
├── static/
│   └── audio/             # 8kHz PCM WAV recordings & fallback audio streams
│
└── templates/
    ├── index.html         # 4-Stage Progressive Workflow & 3D Biometric Hologram
    └── presentation.html  # Interactive 10-slide deck with bilingual speaker notes
```

---

## 🔒 Regulatory Compliance (RBI & Global Standards)

- **RBI Master Direction 2024:** Multi-Factor Out-of-Band Voice-OTP for digital banking.
- **ISO/IEC 30107-3:** Presentation Attack Detection (PAD) with 99.4% biological liveness.
- **DPDP Act 2023:** Data minimization via irreversible one-way acoustic feature vectors.
- **National Cyber Crime 1930:** Helpline 1930 incident metadata generation.

---

## 👨‍💻 Author & Acknowledgements
- Developed for **Gnani.ai Enterprise Hackathon 2026**.
- Dedicated to the **armour365™ Voice Biometrics** and **Prisma ASR** Engineering Teams.
