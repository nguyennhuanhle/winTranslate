"""
Translation module using deep-translator (Google Translate).
Supports auto-detect source language for any language input.
"""

from deep_translator import GoogleTranslator


# Supported target languages with display names
TARGET_LANGUAGES = {
    "vi": "Tiếng Việt",
    "en": "English",
    "zh-CN": "中文 (简体)",
    "zh-TW": "中文 (繁體)",
    "ja": "日本語",
    "ko": "한국어",
    "fr": "Français",
    "de": "Deutsch",
    "es": "Español",
    "th": "ภาษาไทย",
    "ru": "Русский",
}

DEFAULT_TARGET = "vi"


def translate_text(text: str, target_lang: str = DEFAULT_TARGET) -> dict:
    """
    Translate text with auto-detected source language.
    
    Args:
        text: Text to translate
        target_lang: Target language code (default: 'vi')
    
    Returns:
        dict with keys: 'original', 'translated', 'source_lang', 'target_lang', 'error'
    """
    result = {
        "original": text,
        "translated": "",
        "source_lang": "auto",
        "target_lang": target_lang,
        "error": None,
    }

    if not text or not text.strip():
        result["error"] = "No text to translate"
        return result

    try:
        translator = GoogleTranslator(source="auto", target=target_lang)
        translated = translator.translate(text.strip())
        result["translated"] = translated if translated else ""
    except Exception as e:
        result["error"] = str(e)

    return result


if __name__ == "__main__":
    # Quick test
    tests = [
        "Hello, how are you?",
        "こんにちは、元気ですか？",
        "你好，你好吗？",
        "안녕하세요, 잘 지내세요?",
        "Bonjour, comment allez-vous?",
    ]
    for t in tests:
        r = translate_text(t)
        print(f"[{r['source_lang']}→{r['target_lang']}] {t}  →  {r['translated']}")
