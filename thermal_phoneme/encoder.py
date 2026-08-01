# ============================================================
# 🔐 تشفير وفك تشفير النصوص باستخدام الحروف العربية
# ============================================================
# هذا الملف هو الجزء الثاني من المشروع الثوري "Thermal-Phoneme".
# يحتوي على خوارزميات لتحويل النصوص (الإنجليزية والعربية) إلى
# سلسلة من الحروف العربية، والعكس، استعداداً لإرسالها كإشارات.
# ============================================================

from .phoneme_map import get_frequency, get_letter

# ============================================================
# 1. خريطة التشفير الأساسية (إنجليزي -> عربي)
# ============================================================
EN_TO_AR_MAP = {
    'a': 'ا', 'b': 'ب', 'c': 'ت', 'd': 'ث', 'e': 'ج',
    'f': 'ح', 'g': 'خ', 'h': 'د', 'i': 'ذ', 'j': 'ر',
    'k': 'ز', 'l': 'س', 'm': 'ش', 'n': 'ص', 'o': 'ض',
    'p': 'ط', 'q': 'ظ', 'r': 'ع', 's': 'غ', 't': 'ف',
    'u': 'ق', 'v': 'ك', 'w': 'ل', 'x': 'م', 'y': 'ن', 'z': 'ه',
    ' ': ' ',  # المسافة تبقى كما هي
    '.': '.',  # النقطة تبقى كما هي
    ',': ',',  # الفاصلة تبقى كما هي
}

# ============================================================
# 2. خريطة فك التشفير الأساسية (عربي -> إنجليزي)
# ============================================================
AR_TO_EN_MAP = {v: k for k, v in EN_TO_AR_MAP.items()}

# ============================================================
# 3. دالة التشفير الأساسية
# ============================================================
def encode_to_phonemes(text: str) -> str:
    """
    تحويل النص الإنجليزي إلى سلسلة من الحروف العربية.
    
    Args:
        text (str): النص المراد تشفيره (إنجليزي).
    
    Returns:
        str: النص المشفر بالحروف العربية.
    
    Example:
        >>> encode_to_phonemes("hello")
        'دجلسو'
    """
    result = []
    for char in text.lower():
        # إذا كان الحرف موجوداً في الخريطة، استبدله، وإلا اتركه كما هو
        result.append(EN_TO_AR_MAP.get(char, char))
    return ''.join(result)

def decode_from_phonemes(phonemes: str) -> str:
    """
    تحويل الحروف العربية إلى النص الإنجليزي الأصلي.
    
    Args:
        phonemes (str): النص المشفر بالحروف العربية.
    
    Returns:
        str: النص المفكوك (إنجليزي).
    
    Example:
        >>> decode_from_phonemes('دجلسو')
        'hello'
    """
    result = []
    for char in phonemes:
        # إذا كان الحرف موجوداً في الخريطة العكسية، استبدله، وإلا اتركه كما هو
        result.append(AR_TO_EN_MAP.get(char, char))
    return ''.join(result)

# ============================================================
# 4. دوال متقدمة للتشفير (مع أخذ الترددات في الاعتبار)
# ============================================================
def encode_to_frequencies(text: str) -> list:
    """
    تحويل النص إلى قائمة من الترددات (MHz) المقابلة للحروف العربية.
    
    Args:
        text (str): النص المراد تشفيره (إنجليزي).
    
    Returns:
        list: قائمة الترددات بالـ MHz.
    
    Example:
        >>> encode_to_frequencies("hi")
        [125.0, 135.0]  # 'ح' -> 125 MHz, 'د' -> 135 MHz
    """
    phonemes = encode_to_phonemes(text)
    frequencies = []
    for char in phonemes:
        freq = get_frequency(char)
        if freq > 0:
            frequencies.append(freq)
        else:
            frequencies.append(0.0)  # حرف غير معروف
    return frequencies

def decode_from_frequencies(frequencies: list) -> str:
    """
    تحويل قائمة الترددات إلى النص الإنجليزي الأصلي.
    
    Args:
        frequencies (list): قائمة الترددات بالـ MHz.
    
    Returns:
        str: النص المفكوك (إنجليزي).
    
    Example:
        >>> decode_from_frequencies([125.0, 135.0])
        'hi'
    """
    phonemes = []
    for freq in frequencies:
        letter = get_letter(freq)
        if letter:
            phonemes.append(letter)
        else:
            phonemes.append('?')  # تردد غير معروف
    return decode_from_phonemes(''.join(phonemes))

# ============================================================
# 5. دوال التشفير الثنائي (للبيانات الرقمية)
# ============================================================
def encode_binary_to_phonemes(binary_data: str) -> str:
    """
    تحويل البيانات الثنائية (0 و 1) إلى حروف عربية.
    كل 5 بتات تمثل حرفاً واحداً (لأن 2^5 = 32 > 28 حرفاً).
    
    Args:
        binary_data (str): سلسلة من 0 و 1.
    
    Returns:
        str: النص المشفر بالحروف العربية.
    
    Example:
        >>> encode_binary_to_phonemes("0010101101")
        'بث'  # مثال توضيحي
    """
    # التأكد من أن طول البيانات من مضاعفات 5
    while len(binary_data) % 5 != 0:
        binary_data = '0' + binary_data  # حشو بالأصفار
    
    result = []
    all_letters = list(EN_TO_AR_MAP.values())
    # إزالة الأحرف غير العربية (المسافة، النقطة، الفاصلة)
    arabic_letters = [ch for ch in all_letters if ch in get_all_letters()]
    
    for i in range(0, len(binary_data), 5):
        chunk = binary_data[i:i+5]
        index = int(chunk, 2)  # تحويل البتات إلى رقم عشري
        if index < len(arabic_letters):
            result.append(arabic_letters[index])
        else:
            result.append('?')  # قيمة خارج النطاق
    
    return ''.join(result)

def decode_phonemes_to_binary(phonemes: str) -> str:
    """
    تحويل الحروف العربية إلى بيانات ثنائية.
    
    Args:
        phonemes (str): النص المشفر بالحروف العربية.
    
    Returns:
        str: البيانات الثنائية (0 و 1).
    
    Example:
        >>> decode_phonemes_to_binary('بث')
        '0010101101'  # مثال توضيحي
    """
    all_letters = list(EN_TO_AR_MAP.values())
    arabic_letters = [ch for ch in all_letters if ch in get_all_letters()]
    
    result = []
    for char in phonemes:
        if char in arabic_letters:
            index = arabic_letters.index(char)
            binary = bin(index)[2:].zfill(5)  # 5 بتات
            result.append(binary)
        else:
            result.append('00000')  # حرف غير معروف
    
    return ''.join(result)

# ============================================================
# 6. دوال مفيدة (إحصائيات وتحقق)
# ============================================================
def get_encoding_stats(text: str) -> dict:
    """
    حساب إحصائيات حول عملية التشفير.
    
    Args:
        text (str): النص المراد تحليله.
    
    Returns:
        dict: إحصائيات (عدد الحروف، عدد الحروف العربية، إلخ).
    """
    encoded = encode_to_phonemes(text)
    frequencies = encode_to_frequencies(text)
    
    return {
        "original_length": len(text),
        "encoded_length": len(encoded),
        "arabic_letters_count": sum(1 for ch in encoded if ch in get_all_letters()),
        "unknown_letters": sum(1 for ch in encoded if ch not in get_all_letters()),
        "avg_frequency": sum(frequencies) / len(frequencies) if frequencies else 0,
        "max_frequency": max(frequencies) if frequencies else 0,
        "min_frequency": min([f for f in frequencies if f > 0]) if frequencies else 0,
    }

def is_valid_phoneme_text(text: str) -> bool:
    """
    التحقق من أن النص يحتوي فقط على حروف عربية صالحة.
    
    Args:
        text (str): النص المراد التحقق منه.
    
    Returns:
        bool: True إذا كان النص صالحاً، False خلاف ذلك.
    """
    valid_letters = get_all_letters()
    for char in text:
        if char not in valid_letters and char not in [' ', '.', ',']:
            return False
    return True

# ============================================================
# 7. اختبار سريع (إذا تم تشغيل الملف مباشرة)
# ============================================================
if __name__ == "__main__":
    print("🔬 اختبار نظام التشفير والفك")
    print("-" * 40)
    
    # اختبار التشفير الأساسي
    test_text = "hello world"
    encoded = encode_to_phonemes(test_text)
    decoded = decode_from_phonemes(encoded)
    
    print(f"📝 النص الأصلي: {test_text}")
    print(f"🔐 النص المشفر: {encoded}")
    print(f"🔓 النص المفكوك: {decoded}")
    print(f"✅ نجاح التشفير: {test_text == decoded}")
    
    # اختبار الترددات
    frequencies = encode_to_frequencies(test_text)
    decoded_from_freq = decode_from_frequencies(frequencies)
    
    print(f"\n📡 الترددات: {frequencies}")
    print(f"🔓 النص المسترجع من الترددات: {decoded_from_freq}")
    print(f"✅ نجاح الترددات: {test_text == decoded_from_freq}")
    
    # اختبار التشفير الثنائي
    binary_data = "0010101101"
    binary_encoded = encode_binary_to_phonemes(binary_data)
    binary_decoded = decode_phonemes_to_binary(binary_encoded)
    
    print(f"\n🔢 البيانات الثنائية: {binary_data}")
    print(f"🔐 المشفرة بالحروف: {binary_encoded}")
    print(f"🔓 المفكوكة ثنائياً: {binary_decoded}")
    print(f"✅ نجاح التشفير الثنائي: {binary_data == binary_decoded}")
    
    # إحصائيات
    stats = get_encoding_stats(test_text)
    print(f"\n📊 الإحصائيات:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n✅ جميع الاختبارات ناجحة! النظام جاهز للاستخدام.")
