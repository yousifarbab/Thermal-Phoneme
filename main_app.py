import sys
import os
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime
import random

# ============================================================
# 🌍 خريطة الحروف العربية والترددات (مع فجوة 3 MHz)
# ============================================================
PHONEME_MAP = {
    'ا': 100.0, 'ب': 103.0, 'ت': 106.0, 'ث': 109.0, 'ج': 112.0,
    'ح': 115.0, 'خ': 118.0, 'د': 121.0, 'ذ': 124.0, 'ر': 127.0,
    'ز': 130.0, 'س': 133.0, 'ش': 136.0, 'ص': 139.0, 'ض': 142.0,
    'ط': 145.0, 'ظ': 148.0, 'ع': 151.0, 'غ': 154.0, 'ف': 157.0,
    'ق': 160.0, 'ك': 163.0, 'ل': 166.0, 'م': 169.0, 'ن': 172.0,
    'هـ': 175.0, 'و': 178.0, 'ي': 181.0, 'أ': 184.0, 'ة': 187.0,
}

# ============================================================
# 🔄 خريطة التشفير (إنجليزي -> عربي)
# ============================================================
LATIN_TO_ARABIC = {
    'a': 'ا', 'b': 'ب', 'c': 'ث', 'd': 'د', 'e': 'ع', 'f': 'ف',
    'g': 'ج', 'h': 'ح', 'i': 'ي', 'j': 'ج', 'k': 'ك', 'l': 'ل',
    'm': 'م', 'n': 'ن', 'o': 'و', 'p': 'ب', 'q': 'ق', 'r': 'ر',
    's': 'س', 't': 'ت', 'u': 'و', 'v': 'ف', 'w': 'و', 'x': 'ش',
    'y': 'ي', 'z': 'ز', ' ': 'هـ'  # المسافة تتحول إلى 'هـ' (تردد 175 MHz)
}

ARABIC_TO_LATIN = {v: k for k, v in LATIN_TO_ARABIC.items()}

# ============================================================
# 🛠️ دوال التشفير وفك التشفير
# ============================================================
def get_frequency(char: str) -> float:
    """تُعيد التردد المطابق للحرف (مع معالجة المسافة)."""
    if char == ' ':
        return 250.0  # تردد خاص للمسافة
    return PHONEME_MAP.get(char, 0.0)

def get_letter(freq: float) -> str:
    """تُعيد الحرف المطابق للتردد."""
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
    """تحويل النص الإنجليزي إلى حروف عربية."""
    encoded = []
    for char in text:
        if char in LATIN_TO_ARABIC:
            encoded.append(LATIN_TO_ARABIC[char])
        elif char in PHONEME_MAP:
            encoded.append(char)
        else:
            encoded.append('ا')  # حرف افتراضي
    return "".join(encoded)

def decode_from_phonemes(phonemes: str) -> str:
    """تحويل الحروف العربية إلى نص إنجليزي."""
    decoded = []
    for char in phonemes:
        if char in ARABIC_TO_LATIN:
            decoded.append(ARABIC_TO_LATIN[char])
        else:
            decoded.append(char)
    return "".join(decoded)

def encode_to_frequencies(text: str) -> list:
    """تحويل النص إلى قائمة ترددات."""
    phonemes = encode_to_phonemes(text)
    return [get_frequency(c) for c in phonemes]

def decode_from_frequencies(frequencies: list) -> str:
    """تحويل قائمة الترددات إلى نص."""
    phonemes = "".join([get_letter(f) for f in frequencies])
    return decode_from_phonemes(phonemes)

def get_encoding_stats(text: str) -> dict:
    """إحصائيات التشفير."""
    encoded = encode_to_phonemes(text)
    freqs = encode_to_frequencies(text)
    valid_freqs = [f for f in freqs if f > 0 and f != 250.0]
    return {
        "original_length": len(text),
        "encoded_length": len(encoded),
        "avg_frequency": np.mean(valid_freqs) if valid_freqs else 0.0,
        "min_frequency": min(valid_freqs) if valid_freqs else 0.0,
        "max_frequency": max(valid_freqs) if valid_freqs else 0.0,
        "space_count": text.count(' ')
    }

def is_valid_phoneme_text(text: str) -> bool:
    """التحقق من صحة النص المشفر."""
    return all(c in PHONEME_MAP or c in ARABIC_TO_LATIN or c == ' ' for c in text)

# ============================================================
# 📡 دوال المحاكاة الحرارية
# ============================================================
def simulate_environment(frequencies: list, environment: str) -> tuple:
    """
    محاكاة تأثير البيئة على الإشارات الحرارية.
    تُعيد (الترددات المُضعَّفة، معامل التضعيف، جودة الإشارة)
    """
    attenuation_map = {
        "مفتوحة": (0.95, "🟢 ممتازة"),
        "مبنى خرساني": (0.60, "🟡 متوسطة"),
        "تحت الأرض": (0.35, "🔴 ضعيفة"),
        "غابة كثيفة": (0.50, "🟠 منخفضة"),
    }
    attenuation, quality = attenuation_map.get(environment, (0.80, "🟢 ممتازة"))
    attenuated = [freq * attenuation for freq in frequencies]
    return attenuated, attenuation, quality

def generate_signal(frequencies: list, time_steps: int = 100) -> list:
    """توليد إشارة حرارية مركبة من الترددات."""
    signal = []
    for i in range(1, time_steps + 1):
        value = 0
        for j, freq in enumerate(frequencies[:5]):
            if freq > 0:
                value += 0.2 * np.sin(2 * np.pi * (freq / 100) * i / time_steps + j)
        signal.append(value)
    return signal

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
</style>
""", unsafe_allow_html=True)

# ============================================================
# 🌟 العنوان الرئيسي
# ============================================================
st.markdown("""
<div style='text-align: center; padding: 20px 0;'>
    <h1 style='font-size: 3.5em; text-shadow: 0 0 40px #00CCFF;'>🔥 Thermal-Phoneme</h1>
    <p style='color: #88AACC; font-size: 1.2em;'>الاتصالات الثورية بالحروف العربية والإشارات الحرارية</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class='welcome-box'>
    <h2>🚀 ثورة في عالم الاتصالات</h2>
    <p>
    <b>Thermal-Phoneme</b> هو مشروع يعيد تعريف الاتصالات من جذورها.
    يستخدم <b>30 حرفاً عربياً</b> كأساس لتوليد ترددات فريدة، وينقلها عبر <b>إشارات حرارية</b>
    يمكنها اختراق العوائق والتكيف مع البيئة. هذا النظام يلغي الحاجة إلى الترددات المرخصة
    ويقدم حلاً آمناً ومنخفض التكلفة للاتصالات.
    </p>
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
    st.metric("الإصدار", "v0.2.0")
    st.markdown("---")
    st.success("✅ النظام جاهز")
    st.info(f"🕐 {datetime.now().strftime('%H:%M:%S')}")
    st.markdown("---")
    st.caption("""
    **Thermal-Phoneme** © 2026 Yousif Zakaria Eissa Arbarb  
    مرخص تحت AGPL-3.0 & Apache 2.0
    """)

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
    st.header("🔐 تشفير وفك تشفير النصوص بالحروف العربية")
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
                
                st.subheader("📊 إحصائيات التشفير")
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
# 📡 التبويب الثاني: المحاكاة الحرارية
# ============================================================
with tab2:
    st.header("📡 محاكاة الإرسال والاستقبال الحراري")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📝 إعدادات الإرسال")
        send_text = st.text_input("النص المراد إرساله:", value="سلام")
        power = st.slider("قوة الإشارة (وحدات)", 1.0, 10.0, 5.0, 0.5)
        environment = st.selectbox("البيئة:", ["مفتوحة", "مبنى خرساني", "تحت الأرض", "غابة كثيفة"])
        
        if st.button("🚀 بدء المحاكاة", key="sim_btn"):
            encoded = encode_to_phonemes(send_text)
            frequencies = encode_to_frequencies(send_text)
            
            attenuated_freqs, attenuation, quality = simulate_environment(frequencies, environment)
            attenuated_power = power * attenuation
            
            signal = generate_signal(attenuated_freqs, 100)
            
            st.success(f"✅ تم إرسال النص: **{encoded}**")
            
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("قوة الإرسال", f"{power:.1f} وحدة")
            col_b.metric("جودة الإشارة", quality)
            col_c.metric("القوة المستلمة", f"{attenuated_power:.2f} وحدة")
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=list(range(1, 101)),
                y=signal,
                mode='lines',
                name='الإشارة الحرارية',
                line=dict(color='#00CCFF', width=2)
            ))
            fig.update_layout(
                title=f"الإشارة الحرارية المرسلة ({environment})",
                xaxis_title="الزمن (وحدة)",
                yaxis_title="الشدة الحرارية",
                height=300,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("📡 الترددات المرسلة (بعد التضعيف)")
            freq_df = pd.DataFrame([
                {"الحرف": char, "التردد (MHz)": freq, "التردد المستلم (MHz)": round(freq * attenuation, 2)}
                for char, freq in zip(encoded, frequencies)
            ])
            st.dataframe(freq_df, use_container_width=True)
    
    with col2:
        st.subheader("📊 حالة الاستقبال")
        st.metric("جودة الإشارة", "ممتازة")
        st.success("🟢 إشارة ممتازة")
        
        st.subheader("🌡️ درجة الحرارة المتوقعة")
        temp = 25 + power * 0.8
        st.metric("درجة الحرارة", f"{temp:.1f}°C")

# ============================================================
# 📈 التبويب الثالث: تحليل الإشارات
# ============================================================
with tab3:
    st.header("📈 تحليل الإشارات الحرارية والطيفية")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 تحليل الطيف")
        freqs = np.linspace(80, 250, 200)
        spectrum = np.exp(-((freqs - 150) ** 2) / 200) * 10
        spectrum += np.exp(-((freqs - 120) ** 2) / 100) * 5
        spectrum += np.random.normal(0, 0.5, 200)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=freqs,
            y=spectrum,
            mode='lines',
            name='الطيف الحراري',
            line=dict(color='#FF6B35', width=2)
        ))
        fig.update_layout(
            title="الطيف الترددي للإشارة الحرارية",
            xaxis_title="التردد (MHz)",
            yaxis_title="الشدة",
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 تحليل الزمن")
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
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 🌍 التبويب الرابع: الخريطة
# ============================================================
with tab4:
    st.header("🌍 خريطة توزيع الإشارات الحرارية")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("🗺️ خريطة شدة الإشارة")
        x = np.linspace(-10, 10, 100)
        y = np.linspace(-10, 10, 100)
        X, Y = np.meshgrid(x, y)
        
        Z = 100 * np.exp(-0.1 * ((X - 2) ** 2 + (Y - 3) ** 2))
        Z += 50 * np.exp(-0.05 * ((X + 3) ** 2 + (Y + 2) ** 2))
        
        fig = go.Figure(data=go.Contour(
            z=Z, x=x, y=y,
            colorscale='Hot',
            colorbar=dict(title="شدة الإشارة")
        ))
        fig.update_layout(
            title="توزيع الإشارات الحرارية (محطات الإرسال)",
            height=500,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 التغطية")
        st.metric("نقاط الإرسال", "3")
        st.metric("التغطية", "78%")

# ============================================================
# 📌 حقوق الملكية
# ============================================================
st.markdown("---")
st.markdown("""
<div class='copyright'>
    <p>🔥 Thermal-Phoneme v0.2.0 | © 2026 Yousif Zakaria Eissa Arbarb</p>
    <p style='font-size: 0.8em; color: #334455;'>مرخص تحت AGPL-3.0 & Apache 2.0</p>
</div>
""", unsafe_allow_html=True)
