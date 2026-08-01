import sys
import os
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime

# ============================================================
# 🗺️ خريطة الحروف العربية والترددات
# ============================================================
PHONEME_MAP = {
    'ا': 100.0, 'ب': 105.5, 'ت': 110.0, 'ث': 115.5, 'ج': 120.0,
    'ح': 125.5, 'خ': 130.0, 'د': 135.5, 'ذ': 140.0, 'ر': 145.5,
    'ز': 150.0, 'س': 155.5, 'ش': 160.0, 'ص': 165.5, 'ض': 170.0,
    'ط': 175.5, 'ظ': 180.0, 'ع': 185.5, 'غ': 190.0, 'ف': 195.5,
    'ق': 200.0, 'ك': 205.5, 'ل': 210.0, 'م': 215.5, 'ن': 220.0,
    'هـ': 225.5, 'و': 230.0, 'ي': 235.5, 'أ': 240.0, 'ة': 245.5
}

LATIN_TO_ARABIC_MAP = {
    'a': 'ا', 'b': 'ب', 'c': 'ث', 'd': 'د', 'e': 'ع', 'f': 'ف',
    'g': 'ج', 'h': 'ح', 'i': 'ي', 'j': 'ج', 'k': 'ك', 'l': 'ل',
    'm': 'م', 'n': 'ن', 'o': 'و', 'p': 'ب', 'q': 'ق', 'r': 'ر',
    's': 'س', 't': 'ت', 'u': 'و', 'v': 'ف', 'w': 'و', 'x': 'ش',
    'y': 'ي', 'z': 'ز', ' ': 'هـ'
}

ARABIC_TO_LATIN_MAP = {v: k for k, v in LATIN_TO_ARABIC_MAP.items()}

def get_frequency(char: str) -> float:
    return PHONEME_MAP.get(char, 0.0)

def get_letter(freq: float) -> str:
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
    for char in text.lower():
        if char in LATIN_TO_ARABIC_MAP:
            encoded.append(LATIN_TO_ARABIC_MAP[char])
        elif char in PHONEME_MAP:
            encoded.append(char)
        else:
            encoded.append('ا')
    return "".join(encoded)

def decode_from_phonemes(phonemes: str) -> str:
    decoded = []
    for char in phonemes:
        if char in ARABIC_TO_LATIN_MAP:
            decoded.append(ARABIC_TO_LATIN_MAP[char])
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
    valid_freqs = [f for f in freqs if f > 0]
    return {
        "original_length": len(text),
        "encoded_length": len(encoded),
        "avg_frequency": np.mean(valid_freqs) if valid_freqs else 0.0,
        "min_frequency": min(valid_freqs) if valid_freqs else 0.0,
        "max_frequency": max(valid_freqs) if valid_freqs else 0.0
    }

def is_valid_phoneme_text(text: str) -> bool:
    return all(c in PHONEME_MAP or c in ARABIC_TO_LATIN_MAP for c in text)

# ============================================================
# 🎛️ إعداد الصفحة
# ============================================================
st.set_page_config(
    page_title="Thermal-Phoneme - الاتصالات الثورية",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 🎨 CSS مخصص
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
</style>
""", unsafe_allow_html=True)

# ============================================================
# 🌟 العنوان
# ============================================================
st.markdown("""
<div style='text-align: center; padding: 20px 0;'>
    <h1 style='font-size: 3.5em; text-shadow: 0 0 40px #00CCFF;'>🔥 Thermal-Phoneme</h1>
    <p style='color: #88AACC; font-size: 1.2em;'>الاتصالات الثورية بالحروف العربية والإشارات الحرارية</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# 📊 الشريط الجانبي
# ============================================================
with st.sidebar:
    st.subheader("📊 معلومات النظام")
    st.metric("عدد الحروف العربية", len(get_all_letters()))
    st.metric("نطاق الترددات", f"{min(get_all_frequencies())} - {max(get_all_frequencies())} MHz")
    st.metric("الإصدار", "v0.1.0")
    st.markdown("---")
    st.success("✅ النظام يعمل بنجاح")
    st.caption("© 2026 Yousif Zakaria Eissa Arbarb")

# ============================================================
# 📋 علامات التبويب الرئيسية
# ============================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🔐 التشفير بالحروف العربية",
    "📡 المحاكاة الحرارية",
    "📈 تحليل الإشارات",
    "🌍 خريطة التوزيع"
])

# ============================================================
# 🔐 التبويب الأول: التشفير
# ============================================================
with tab1:
    st.header("🔐 تشفير وفك تشفير النصوص")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 تشفير نص")
        input_text = st.text_area("أدخل النص المراد تشفيره:", value="Hello World", key="enc_in")
        if st.button("🔐 تشفير", key="btn_enc"):
            if input_text:
                encoded = encode_to_phonemes(input_text)
                frequencies = encode_to_frequencies(input_text)
                stats = get_encoding_stats(input_text)
                st.success(f"✅ النص المشفر: **{encoded}**")
                
                st.subheader("📡 الترددات المولدة")
                freq_cols = st.columns(5)
                for i, (char, freq) in enumerate(zip(encoded, frequencies)):
                    if freq > 0:
                        with freq_cols[i % 5]:
                            st.markdown(f"""
                            <div class='frequency-badge'>
                                <b>{char}</b><br><span style='color: #00CCFF;'>{freq} MHz</span>
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ أدخل نصاً للتشفير.")
                
    with col2:
        st.subheader("🔓 فك تشفير نص")
        encoded_input = st.text_area("أدخل النص المشفر:", value="دجلسو گووطذ", key="dec_in")
        if st.button("🔓 فك التشفير", key="btn_dec"):
            if encoded_input:
                if is_valid_phoneme_text(encoded_input):
                    decoded = decode_from_phonemes(encoded_input)
                    st.success(f"✅ النص المفكوك: **{decoded}**")
                else:
                    st.error("⚠️ النص يحتوي على أحرف غير مدعومة.")
            else:
                st.warning("⚠️ أدخل نصاً مشفراً.")

# ============================================================
# 📡 التبويب الثاني: المحاكاة الحرارية
# ============================================================
with tab2:
    st.header("📡 محاكاة الإرسال والاستقبال الحراري")
    send_text = st.text_input("النص للإرسال:", value="سلام")
    power = st.slider("قوة الإشارة", 1.0, 10.0, 5.0)
    
    if st.button("🚀 بدء المحاكاة"):
        encoded = encode_to_phonemes(send_text)
        st.success(f"✅ تم الإرسال بنجاح لنص: {encoded}")

# ============================================================
# 📈 التبويب الثالث: تحليل الإشارات
# ============================================================
with tab3:
    st.header("📈 تحليل الإشارات الحرارية والطيفية")
    
    # تحليل الزمن الحقيقي (يبدأ من 1)
    time_data = np.linspace(1, 10, 500)
    signal_data = np.sin(time_data * 2) + 0.5 * np.sin(time_data * 4) + 0.2 * np.random.normal(0, 1, 500)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=time_data,
        y=signal_data,
        mode='lines',
        name='الإشارة الحية',
        line=dict(color='#00CCFF', width=2)
    ))
    fig.update_layout(
        title="تذبذب الإشارة الحرارية في الزمن",
        xaxis_title="الزمن (ثانية)",
        yaxis_title="الشدة",
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', dtick=1),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
    )
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 🌍 التبويب الرابع: الخريطة
# ============================================================
with tab4:
    st.header("🌍 خريطة توزيع الإشارات الحرارية")
    x = np.linspace(-10, 10, 50)
    y = np.linspace(-10, 10, 50)
    X, Y = np.meshgrid(x, y)
    Z = 100 * np.exp(-0.1 * (X**2 + Y**2))
    
    fig_map = go.Figure(data=go.Contour(z=Z, x=x, y=y, colorscale='Hot'))
    fig_map.update_layout(
        title="توزيع الإشارات الكهرومغناطيسية الحرارية",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=450
    )
    st.plotly_chart(fig_map, use_container_width=True)
