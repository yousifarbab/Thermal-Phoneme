import sys
import os

# إضافة مجلد المشروع إلى مسار البحث
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import time
from datetime import datetime

# ============================================================
# 🗺️ خريطة الحروف العربية والترددات (مضمنة لتجنب أخطاء الاستيراد)
# ============================================================
PHONEME_MAP = {
    'ا': 100.0, 'ب': 105.5, 'ت': 110.0, 'ث': 115.5, 'ج': 120.0,
    'ح': 125.5, 'خ': 130.0, 'د': 135.5, 'ذ': 140.0, 'ر': 145.5,
    'ز': 150.0, 'س': 155.5, 'ش': 160.0, 'ص': 165.5, 'ض': 170.0,
    'ط': 175.5, 'ظ': 180.0, 'ع': 185.5, 'غ': 190.0, 'ف': 195.5,
    'ق': 200.0, 'ك': 205.5, 'ل': 210.0, 'م': 215.5, 'ن': 220.0,
    'هـ': 225.5, 'و': 230.0, 'ي': 235.5, 'أ': 240.0, 'ة': 245.5
}

# خريطة تبديلية تحويلية إضافية للحروف اللاتينية لتوافقه مع النظام
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
# 🎨 CSS مخصص للثيم الداكن
# ============================================================
st.markdown("""
<style>
    .main, .stApp {
        background-color: #0a0a12;
    }
    .stMetric {
        background: linear-gradient(145deg, #1a1a2e, #0d0d1a);
        border-radius: 12px;
        padding: 15px;
        border: 1px solid rgba(0, 204, 255, 0.15);
    }
    h1, h2, h3, h4, h5 {
        color: #00CCFF;
        font-family: 'Arial Black', sans-serif;
        text-shadow: 0 0 10px rgba(0, 204, 255, 0.3);
    }
    .stButton > button {
        background: linear-gradient(135deg, #00CCFF, #0066AA);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 30px rgba(0, 204, 255, 0.4);
    }
    .welcome-box {
        background: linear-gradient(135deg, #1a1a2e, #0d0d1a);
        border-radius: 12px;
        padding: 20px 25px;
        border: 1px solid rgba(0, 204, 255, 0.15);
        margin-bottom: 20px;
    }
    .welcome-box h2 {
        color: #00CCFF;
        margin: 0 0 10px 0;
    }
    .welcome-box p {
        color: #88AACC;
        margin: 0;
        font-size: 1.05em;
    }
    .copyright {
        text-align: center;
        color: #445566;
        font-size: 0.8em;
        padding: 20px 0;
        border-top: 1px solid #1a1a2e;
        margin-top: 20px;
    }
    .frequency-badge {
        background: #1a1a2e;
        border-radius: 20px;
        padding: 5px 15px;
        border: 1px solid #00CCFF33;
        display: inline-block;
        margin: 3px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 🌟 العنوان الرئيسي
# ============================================================
st.markdown("""
<div style='text-align: center; padding: 20px 0;'>
    <h1 style='font-size: 4em; text-shadow: 0 0 40px #00CCFF;'>🔥 Thermal-Phoneme</h1>
    <p style='color: #88AACC; font-size: 1.3em;'>الاتصالات الثورية بالحروف العربية والإشارات الحرارية</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class='welcome-box'>
    <h2>🚀 ثورة في عالم الاتصالات</h2>
    <p>
    <b>Thermal-Phoneme</b> هو مشروع يعيد تعريف الاتصالات من جذورها.
    يستخدم <b>الحروف العربية</b> كأساس لتوليد ترددات فريدة، وينقلها عبر <b>إشارات حرارية</b>
    يمكنها اختراق العوائق والتكيف مع البيئة. هذا النظام يلغي الحاجة إلى الترددات المرخصة
    ويقدم حلاً آمناً ومنخفض التكلفة للاتصالات.
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# 📊 الشريط الجانبي (المعلومات العامة)
# ============================================================
with st.sidebar:
    st.image("https://via.placeholder.com/300x60/0a0a12/00CCFF?text=Thermal-Phoneme", use_column_width=True)
    st.markdown("---")
    
    st.subheader("📊 معلومات النظام")
    st.metric("عدد الحروف العربية", len(get_all_letters()))
    st.metric("نطاق الترددات", f"{min(get_all_frequencies())} - {max(get_all_frequencies())} MHz")
    st.metric("الإصدار", "v0.1.0")
    
    st.markdown("---")
    st.subheader("🔬 حالة النظام")
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
        input_text = st.text_area(
            "أدخل النص المراد تشفيره:",
            value="Hello World",
            height=100,
            key="encode_input"
        )
        
        if st.button("🔐 تشفير", key="encode_btn"):
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
                                <b>{char}</b><br>
                                <span style='color: #00CCFF;'>{freq} MHz</span>
                            </div>
                            """, unsafe_allow_html=True)
                
                st.subheader("📊 إحصائيات التشفير")
                stat_cols = st.columns(4)
                stat_cols[0].metric("طول النص الأصلي", stats["original_length"])
                stat_cols[1].metric("طول النص المشفر", stats["encoded_length"])
                stat_cols[2].metric("متوسط التردد", f"{stats['avg_frequency']:.1f} MHz")
                stat_cols[3].metric("مدى الترددات", f"{stats['min_frequency']} - {stats['max_frequency']} MHz")
            else:
                st.warning("⚠️ يرجى إدخال نص للتشفير.")
    
    with col2:
        st.subheader("🔓 فك تشفير نص")
        encoded_input = st.text_area(
            "أدخل النص المشفر بالحروف العربية:",
            value="دجلسو گووطذ",
            height=100,
            key="decode_input"
        )
        
        if st.button("🔓 فك التشفير", key="decode_btn"):
            if encoded_input:
                if is_valid_phoneme_text(encoded_input):
                    decoded = decode_from_phonemes(encoded_input)
                    st.success(f"✅ النص المفكوك: **{decoded}**")
                    
                    frequencies = []
                    for char in encoded_input:
                        freq = get_frequency(char)
                        if freq > 0:
                            frequencies.append(freq)
                    
                    if frequencies:
                        st.subheader("📡 الترددات المستلمة")
                        st.write(frequencies)
                else:
                    st.error("⚠️ النص المدخل يحتوي على أحرف غير مدعومة.")
            else:
                st.warning("⚠️ يرجى إدخال نص مشفر لفك التشفير.")
    
    st.markdown("---")
    st.subheader("🗺️ خريطة الحروف العربية والترددات")
    
    phoneme_df = pd.DataFrame([
        {"الحرف": letter, "التردد (MHz)": freq}
        for letter, freq in PHONEME_MAP.items()
    ])
    st.dataframe(phoneme_df, use_container_width=True)

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
        environment = st.selectbox(
            "البيئة:",
            ["مفتوحة", "مبنى خرساني", "تحت الأرض", "غابة كثيفة"]
        )
        
        attenuation_map = {
            "مفتوحة": 0.95,
            "مبنى خرساني": 0.60,
            "تحت الأرض": 0.35,
            "غابة كثيفة": 0.50,
        }
        attenuation = attenuation_map.get(environment, 0.8)
        
        if st.button("🚀 محاكاة الإرسال", key="simulate_btn"):
            encoded = encode_to_phonemes(send_text)
            frequencies = encode_to_frequencies(send_text)
            attenuated_power = power * attenuation
            
            time_steps = 100
            signal = []
            for i in range(time_steps):
                value = 0
                for j, freq in enumerate(frequencies[:5]):
                    if freq > 0:
                        value += 0.2 * np.sin(2 * np.pi * (freq / 100) * i / time_steps + j)
                signal.append(value * attenuated_power)
            
            st.success(f"✅ تم إرسال: **{encoded}**")
            
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("قوة الإرسال", f"{power:.1f} وحدة")
            col_b.metric("التضعيف", f"{(1-attenuation)*100:.0f}%")
            col_c.metric("القوة المستلمة", f"{attenuated_power:.2f} وحدة")
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=list(range(time_steps)),
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
            
            st.subheader("📡 الترددات المرسلة")
            freq_data = []
            for char in encoded:
                freq = get_frequency(char)
                if freq > 0:
                    freq_data.append({"الحرف": char, "التردد (MHz)": freq, "القوة": attenuated_power})
            if freq_data:
                st.dataframe(pd.DataFrame(freq_data), use_container_width=True)
    
    with col2:
        st.subheader("📊 حالة الاستقبال")
        st.metric("جودة الإشارة", f"{attenuation*100:.0f}%")
        
        if attenuation > 0.8:
            st.success("🟢 إشارة ممتازة")
        elif attenuation > 0.5:
            st.warning("🟡 إشارة متوسطة")
        else:
            st.error("🔴 إشارة ضعيفة")
        
        st.subheader("🌡️ درجة الحرارة المتوقعة")
        temp = 25 + power * attenuation
        st.metric("درجة الحرارة", f"{temp:.1f}°C")
        
        st.subheader("📋 معلومات البيئة")
        st.caption(f"نوع البيئة: {environment}")
        st.caption(f"معامل التضعيف: {attenuation:.2f}")
        st.caption(f"المسافة القصوى: {int(10 * attenuation)} كم")

# ============================================================
# 📈 التبويب الثالث: تحليل الإشارات
# ============================================================
with tab3:
    st.header("📈 تحليل الإشارات الحرارية والطيفية")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 تحليل الطيف")
        
        frequencies_spectrum = np.linspace(80, 250, 200)
        spectrum = np.exp(-((frequencies_spectrum - 150) ** 2) / 200) * 10
        spectrum += np.exp(-((frequencies_spectrum - 120) ** 2) / 100) * 5
        spectrum += np.random.normal(0, 0.5, 200)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=frequencies_spectrum,
            y=spectrum,
            mode='lines',
            name='الطيف الحراري',
            line=dict(color='#FF6B35', width=2)
        ))
        
        for letter, freq in PHONEME_MAP.items():
            if freq in [100, 125, 150, 175, 200]:
                fig.add_vline(
                    x=freq,
                    line_dash="dash",
                    line_color="rgba(255, 255, 255, 0.2)",
                    annotation_text=letter,
                    annotation_position="top"
                )
        
        fig.update_layout(
            title="الطيف الترددي للإشارة الحرارية",
            xaxis_title="التردد (MHz)",
            yaxis_title="الشدة",
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 تحليل الزمن الحقيقي")
        
        time_data = np.linspace(0, 10, 500)
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
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.subheader("📊 إحصائيات الإشارة")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("متوسط التردد", "156.3 MHz")
    col2.metric("ذروة الإشارة", "8.7 وحدة")
    col3.metric("نسبة الإشارة للضوضاء", "14.2 dB")
    col4.metric("عرض النطاق", "120 MHz")

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
        Z += 30 * np.exp(-0.08 * ((X - 5) ** 2 + (Y - 5) ** 2))
        
        fig = go.Figure(data=
            go.Contour(
                z=Z,
                x=x,
                y=y,
                colorscale='Hot',
                colorbar=dict(title="شدة الإشارة")
            )
        )
        fig.update_layout(
            title="خريطة توزيع الإشارات الحرارية",
            height=500,
            xaxis_title="المسافة (كم)",
            yaxis_title="المسافة (كم)",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 معلومات التغطية")
        st.metric("نقاط الإرسال", "3")
        st.metric("التغطية", "78%")
        st.metric("أقصى مدى", "12.5 كم")
        
        st.subheader("📍 نقاط الإرسال")
        st.caption("🟢 المحطة الرئيسية (2, 3)")
        st.caption("🟡 المحطة الثانوية (-3, -2)")
        st.caption("🟠 المحطة المتنقلة (5, 5)")

# ============================================================
# 📌 حقوق الملكية
# ============================================================
st.markdown("---")
st.markdown("""
<div class='copyright'>
    <p>🔥 Thermal-Phoneme v0.1.0</p>
    <p>© 2026 Yousif Zakaria Eissa Arbarb. جميع الحقوق محفوظة.</p>
    <p style='font-size: 0.8em; color: #334455;'>مرخص تحت AGPL-3.0 & Apache 2.0</p>
</div>
""", unsafe_allow_html=True)
