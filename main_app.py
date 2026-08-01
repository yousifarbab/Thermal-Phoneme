import sys
import os
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime
import random
import functools
import json

# ============================================================
# 🌍 خريطة الحروف العربية والترددات
# ============================================================
PHONEME_MAP = {
    'ا': 100.0, 'ب': 103.0, 'ت': 106.0, 'ث': 109.0, 'ج': 112.0,
    'ح': 115.0, 'خ': 118.0, 'د': 121.0, 'ذ': 124.0, 'ر': 127.0,
    'ز': 130.0, 'س': 133.0, 'ش': 136.0, 'ص': 139.0, 'ض': 142.0,
    'ط': 145.0, 'ظ': 148.0, 'ع': 151.0, 'غ': 154.0, 'ف': 157.0,
    'ق': 160.0, 'ك': 163.0, 'ل': 166.0, 'م': 169.0, 'ن': 172.0,
    'هـ': 175.0, 'و': 178.0, 'ي': 181.0, 'أ': 184.0, 'ة': 187.0,
}

LATIN_TO_ARABIC = {
    'a': 'ا', 'b': 'ب', 'c': 'ث', 'd': 'د', 'e': 'ع', 'f': 'ف',
    'g': 'ج', 'h': 'ح', 'i': 'ي', 'j': 'ج', 'k': 'ك', 'l': 'ل',
    'm': 'م', 'n': 'ن', 'o': 'و', 'p': 'ب', 'q': 'ق', 'r': 'ر',
    's': 'س', 't': 'ت', 'u': 'و', 'v': 'ف', 'w': 'و', 'x': 'ش',
    'y': 'ي', 'z': 'ز', ' ': 'هـ'
}

ARABIC_TO_LATIN = {v: k for k, v in LATIN_TO_ARABIC.items()}

# ============================================================
# 🛠️ دوال التشفير الأساسية
# ============================================================
def get_frequency(char: str) -> float:
    if char == ' ':
        return 250.0
    return PHONEME_MAP.get(char, 0.0)

def get_letter(freq: float) -> str:
    if abs(freq - 250.0) < 1.0:
        return ' '
    for letter, f in PHONEME_MAP.items():
        if abs(f - freq) < 1.0:
            return letter
    return 'ا'

def get_all_letters():
    return list(PHONEME_MAP.keys())

def get_all_frequencies():
    return list(PHONEME_MAP.values())

def encode_to_phonemes(text: str) -> str:
    encoded = []
    for char in text:
        if char in LATIN_TO_ARABIC:
            encoded.append(LATIN_TO_ARABIC[char])
        elif char in PHONEME_MAP:
            encoded.append(char)
        else:
            encoded.append('ا')
    return "".join(encoded)

def decode_from_phonemes(phonemes: str) -> str:
    decoded = []
    for char in phonemes:
        if char in ARABIC_TO_LATIN:
            decoded.append(ARABIC_TO_LATIN[char])
        else:
            decoded.append(char)
    return "".join(decoded)

def encode_to_frequencies(text: str) -> list:
    phonemes = encode_to_phonemes(text)
    return [get_frequency(c) for c in phonemes]

def decode_from_frequencies(frequencies: list) -> str:
    phonemes = "".join([get_letter(f) for f in frequencies])
    return decode_from_phonemes(phonemes)

def get_encoding_stats(text: str) -> dict:
    encoded = encode_to_phonemes(text)
    freqs = encode_to_frequencies(text)
    valid_freqs = [f for f in freqs if f > 0 and f != 250.0]
    return {
        "original_length": len(text),
        "encoded_length": len(encoded),
        "avg_frequency": float(np.mean(valid_freqs)) if valid_freqs else 0.0,
        "min_frequency": float(min(valid_freqs)) if valid_freqs else 0.0,
        "max_frequency": float(max(valid_freqs)) if valid_freqs else 0.0,
        "space_count": text.count(' ')
    }

def is_valid_phoneme_text(text: str) -> bool:
    return all(c in PHONEME_MAP or c in ARABIC_TO_LATIN or c == ' ' for c in text)

# ============================================================
# 💾 التخزين المؤقت (Caching) - بعد تعريف الدوال
# ============================================================
@st.cache_data(ttl=3600)
def cached_encode(text: str) -> str:
    return encode_to_phonemes(text)

@st.cache_data(ttl=3600)
def cached_frequencies(text: str) -> list:
    return encode_to_frequencies(text)

@st.cache_data(ttl=3600)
def cached_stats(text: str) -> dict:
    return get_encoding_stats(text)

# ============================================================
# 🏙️ محاكاة البيئات المتقدمة
# ============================================================
ENVIRONMENTS = {
    "مدينة مزدحمة": {"attenuation": 0.45, "noise": 0.3, "desc": "مباني مرتفعة، تداخل إشارات."},
    "صحراء مفتوحة": {"attenuation": 0.90, "noise": 0.05, "desc": "رؤية واضحة، تضاريس ملساء."},
    "منطقة جبلية": {"attenuation": 0.60, "noise": 0.15, "desc": "تضاريس وعرة، انعكاسات متعددة."},
    "غابة كثيفة": {"attenuation": 0.40, "noise": 0.35, "desc": "أشجار كثيفة، امتصاص عالٍ."},
    "تحت الأرض": {"attenuation": 0.25, "noise": 0.50, "desc": "أنفاق، جدران سميكة، عزل عالٍ."}
}

def simulate_environment_advanced(frequencies: list, environment: str) -> dict:
    env = ENVIRONMENTS.get(environment, ENVIRONMENTS["مدينة مزدحمة"])
    attenuation = env["attenuation"]
    noise_level = env["noise"]
    attenuated = [f * attenuation for f in frequencies]
    noisy = [float(f + np.random.normal(0, noise_level * 10)) for f in attenuated]
    signal_strength = float(np.mean(noisy)) if noisy else 0.0
    if signal_strength > 50:
        quality = "🟢 ممتازة"
    elif signal_strength > 30:
        quality = "🟡 متوسطة"
    elif signal_strength > 15:
        quality = "🟠 منخفضة"
    else:
        quality = "🔴 ضعيفة جداً"
    return {
        "attenuated": attenuated,
        "noisy": noisy,
        "quality": quality,
        "signal_strength": round(signal_strength, 2),
        "attenuation": attenuation,
        "description": env["desc"]
    }

def generate_signal(frequencies: list, time_steps: int = 100) -> list:
    signal = []
    for i in range(1, time_steps + 1):
        value = 0.0
        for j, freq in enumerate(frequencies[:5]):
            if freq > 0:
                value += 0.2 * np.sin(2 * np.pi * (freq / 100) * i / time_steps + j)
        signal.append(float(value))
    return signal

# ============================================================
# 🌐 دعم اللغات المتعددة
# ============================================================
LANGUAGES = {
    "ar": {
        "title": "🔥 Thermal-Phoneme",
        "subtitle": "الاتصالات الثورية بالحروف العربية والإشارات الحرارية",
        "encrypt": "🔐 تشفير النصوص",
        "decrypt": "🔓 فك التشفير",
        "simulate": "📡 محاكاة الإرسال",
        "analyze": "📈 تحليل الإشارات",
        "map": "🌍 خريطة التوزيع",
        "stats": "📊 إحصائيات التشفير",
        "freqs": "📡 الترددات المولدة"
    },
    "en": {
        "title": "🔥 Thermal-Phoneme",
        "subtitle": "Revolutionary Communications with Arabic Letters & Thermal Signals",
        "encrypt": "🔐 Encrypt Text",
        "decrypt": "🔓 Decrypt",
        "simulate": "📡 Simulate Transmission",
        "analyze": "📈 Signal Analysis",
        "map": "🌍 Distribution Map",
        "stats": "📊 Encryption Stats",
        "freqs": "📡 Generated Frequencies"
    },
    "fr": {
        "title": "🔥 Thermal-Phoneme",
        "subtitle": "Communications révolutionnaires avec lettres arabes et signaux thermiques",
        "encrypt": "🔐 Chiffrer le texte",
        "decrypt": "🔓 Déchiffrer",
        "simulate": "📡 Simuler la transmission",
        "analyze": "📈 Analyse du signal",
        "map": "🌍 Carte de distribution",
        "stats": "📊 Statistiques de chiffrement",
        "freqs": "📡 Fréquences générées"
    }
}

def get_text(key: str, lang: str = "ar") -> str:
    return LANGUAGES.get(lang, LANGUAGES["ar"]).get(key, key)

# ============================================================
# 🎛️ إعداد الصفحة
# ============================================================
st.set_page_config(
    page_title="Thermal-Phoneme - الاتصالات الثورية",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# اختيار اللغة
lang = st.sidebar.selectbox("🌐 Language / اللغة", ["ar", "en", "fr"], index=0)

# ============================================================
# 🎨 CSS مخصص مع رسوم متحركة
# ============================================================
st.markdown("""
<style>
    .main, .stApp { background-color: #0a0a12; }
    .stMetric {
        background: linear-gradient(145deg, #1a1a2e, #0d0d1a);
        border-radius: 12px; padding: 15px;
        border: 1px solid rgba(0, 204, 255, 0.15);
    }
    h1, h2, h3, h4, h5 {
        color: #00CCFF; font-family: 'Arial Black', sans-serif;
        text-shadow: 0 0 10px rgba(0, 204, 255, 0.3);
    }
    .stButton > button {
        background: linear-gradient(135deg, #00CCFF, #0066AA);
        color: white; border: none; border-radius: 8px;
        padding: 0.5rem 1rem; font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 30px rgba(0, 204, 255, 0.4);
    }
    .welcome-box {
        background: linear-gradient(135deg, #1a1a2e, #0d0d1a);
        border-radius: 12px; padding: 20px 25px;
        border: 1px solid rgba(0, 204, 255, 0.15); margin-bottom: 20px;
    }
    .welcome-box p { color: #88AACC; margin: 0; font-size: 1.05em; }
    .frequency-badge {
        background: #1a1a2e; border-radius: 20px; padding: 5px 15px;
        border: 1px solid #00CCFF33; display: inline-block; margin: 3px;
    }
    .copyright { text-align: center; color: #445566; font-size: 0.8em; padding: 20px 0; }
    @keyframes pulse {
        0% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(1.05); }
        100% { opacity: 1; transform: scale(1); }
    }
    .pulse { animation: pulse 2s infinite; }
    .glow-text { text-shadow: 0 0 20px #00CCFF; }
    .fade-in { animation: fadeIn 1s ease-in; }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 🌟 العنوان
# ============================================================
st.markdown(f"""
<div style='text-align: center; padding: 20px 0;'>
    <h1 style='font-size: 3.5em; text-shadow: 0 0 40px #00CCFF;' class='pulse'>{get_text('title', lang)}</h1>
    <p style='color: #88AACC; font-size: 1.2em;'>{get_text('subtitle', lang)}</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# 📊 الشريط الجانبي
# ============================================================
with st.sidebar:
    st.image("https://via.placeholder.com/300x60/0a0a12/00CCFF?text=Thermal-Phoneme", use_column_width=True)
    st.markdown("---")
    st.subheader("📊 معلومات النظام")
    st.metric("عدد الحروف العربية", len(get_all_letters()))
    st.metric("نطاق الترددات", f"{min(get_all_frequencies())} - {max(get_all_frequencies())} MHz")
    st.metric("الإصدار", "v0.3.0")
    st.markdown("---")
    st.success("✅ النظام جاهز")
    st.info(f"🕐 {datetime.now().strftime('%H:%M:%S')}")
    st.markdown("---")
    st.caption("""
    **Thermal-Phoneme** © 2026 Yousif Zakaria Eissa Arbarb  
    مرخص تحت AGPL-3.0 & Apache 2.0
    """)

# ============================================================
# 📋 علامات التبويب
# ============================================================
tab1, tab2, tab3, tab4 = st.tabs([
    get_text('encrypt', lang),
    get_text('simulate', lang),
    get_text('analyze', lang),
    get_text('map', lang)
])

# ============================================================
# 🔐 التبويب الأول: التشفير
# ============================================================
with tab1:
    st.header(get_text('encrypt', lang))
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 تشفير نص")
        input_text = st.text_area("أدخل النص:", value="Hello World", key="enc_in")
        if st.button("🔐 تشفير", key="btn_enc"):
            if input_text:
                encoded = cached_encode(input_text)
                frequencies = cached_frequencies(input_text)
                stats = cached_stats(input_text)
                st.success(f"✅ النص المشفر: **{encoded}**")
                
                st.subheader(get_text('freqs', lang))
                freq_cols = st.columns(5)
                for i, (char, freq) in enumerate(zip(encoded, frequencies)):
                    if freq > 0:
                        with freq_cols[i % 5]:
                            st.markdown(f"""
                            <div class='frequency-badge'>
                                <b>{char}</b><br><span style='color: #00CCFF;'>{freq} MHz</span>
                            </div>
                            """, unsafe_allow_html=True)
                
                st.subheader(get_text('stats', lang))
                col_a, col_b, col_c, col_d = st.columns(4)
                col_a.metric("طول النص الأصلي", stats["original_length"])
                col_b.metric("طول النص المشفر", stats["encoded_length"])
                col_c.metric("متوسط التردد", f"{stats['avg_frequency']:.1f} MHz")
                col_d.metric("عدد المسافات", stats["space_count"])
            else:
                st.warning("⚠️ أدخل نصاً للتشفير.")
    
    with col2:
        st.subheader("🔓 فك تشفير نص")
        encoded_input = st.text_area("أدخل النص المشفر:", value="حعجسو هـووطذ", key="dec_in")
        if st.button("🔓 فك التشفير", key="btn_dec"):
            if encoded_input:
                if is_valid_phoneme_text(encoded_input):
                    decoded = decode_from_phonemes(encoded_input)
                    st.success(f"✅ النص المفكوك: **{decoded}**")
                    freqs = [get_frequency(c) for c in encoded_input]
                    st.subheader("📡 الترددات المستلمة")
                    st.write(freqs)
                else:
                    st.error("⚠️ النص يحتوي على أحرف غير مدعومة.")
            else:
                st.warning("⚠️ أدخل نصاً مشفراً.")

# ============================================================
# 📡 التبويب الثاني: المحاكاة
# ============================================================
with tab2:
    st.header(get_text('simulate', lang))
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        send_text = st.text_input("النص للإرسال:", value="سلام")
        power = st.slider("قوة الإشارة", 1.0, 10.0, 5.0, 0.5)
        environment = st.selectbox("البيئة:", list(ENVIRONMENTS.keys()))
        
        if st.button("🚀 بدء المحاكاة", key="sim_btn"):
            encoded = encode_to_phonemes(send_text)
            frequencies = encode_to_frequencies(send_text)
            result = simulate_environment_advanced(frequencies, environment)
            
            st.success(f"✅ تم إرسال النص: **{encoded}**")
            st.metric("جودة الإشارة", result["quality"])
            st.metric("شدة الإشارة", f"{result['signal_strength']:.2f} وحدة")
            st.caption(f"📝 {result['description']}")
            
            signal = generate_signal(result["noisy"], 100)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=list(range(1, 101)),
                y=signal,
                mode='lines',
                name='الإشارة الحرارية',
                line=dict(color='#00CCFF', width=2)
            ))
            fig.update_layout(
                title=f"الإشارة الحرارية ({environment})",
                xaxis_title="الزمن (وحدة)",
                yaxis_title="الشدة الحرارية",
                height=300,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 حالة الاستقبال")
        env_info = ENVIRONMENTS.get(environment, ENVIRONMENTS["مدينة مزدحمة"])
        st.metric("معامل التضعيف", f"{env_info['attenuation']:.2f}")
        st.metric("مستوى الضوضاء", f"{env_info['noise']:.2f}")

# ============================================================
# 📈 التبويب الثالث: التحليل
# ============================================================
with tab3:
    st.header(get_text('analyze', lang))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 تحليل الطيف")
        freqs = np.linspace(80, 250, 200)
        spectrum = np.exp(-((freqs - 150) ** 2) / 200) * 10
        spectrum += np.exp(-((freqs - 120) ** 2) / 100) * 5
        spectrum += np.random.normal(0, 0.5, 200)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=freqs, y=spectrum, mode='lines', name='الطيف الحراري', line=dict(color='#FF6B35', width=2)))
        for letter, freq in PHONEME_MAP.items():
            if freq in [100, 130, 160, 190]:
                fig.add_vline(x=freq, line_dash="dash", line_color="rgba(255,255,255,0.2)", annotation_text=letter)
        fig.update_layout(title="الطيف الترددي", xaxis_title="التردد (MHz)", yaxis_title="الشدة", height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 تحليل الزمن")
        time_data = np.linspace(1, 10, 500)
        signal_data = np.sin(time_data * 2) + 0.5 * np.sin(time_data * 4) + 0.2 * np.random.normal(0, 1, 500)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=time_data, y=signal_data, mode='lines', name='الإشارة الحية', line=dict(color='#00CCFF', width=2)))
        fig.update_layout(title="تذبذب الإشارة", xaxis_title="الزمن (ثانية)", yaxis_title="الشدة", height=400)
        st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 🌍 التبويب الرابع: الخريطة
# ============================================================
with tab4:
    st.header(get_text('map', lang))
    x = np.linspace(-10, 10, 100)
    y = np.linspace(-10, 10, 100)
    X, Y = np.meshgrid(x, y)
    Z = 100 * np.exp(-0.1 * ((X - 2) ** 2 + (Y - 3) ** 2))
    Z += 50 * np.exp(-0.05 * ((X + 3) ** 2 + (Y + 2) ** 2))
    Z += 30 * np.exp(-0.08 * ((X - 5) ** 2 + (Y - 5) ** 2))
    fig = go.Figure(data=go.Contour(z=Z, x=x, y=y, colorscale='Hot', colorbar=dict(title="شدة الإشارة")))
    fig.update_layout(title="توزيع الإشارات الحرارية", height=500, xaxis_title="المسافة (كم)", yaxis_title="المسافة (كم)")
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 📌 حقوق الملكية
# ============================================================
st.markdown("---")
st.markdown("""
<div class='copyright'>
    <p>🔥 Thermal-Phoneme v0.3.0 | © 2026 Yousif Zakaria Eissa Arbarb</p>
    <p style='font-size: 0.8em; color: #334455;'>مرخص تحت AGPL-3.0 & Apache 2.0</p>
</div>
""", unsafe_allow_html=True)
