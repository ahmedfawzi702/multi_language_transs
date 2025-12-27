"""
language_detector.py
Improved Mixed Language Detection (word-by-word)

Fixes:
✅ Script detection first (very accurate)
✅ langdetect only for long latin words
✅ Avoid langdetect on very short tokens (my, is, it...)
✅ Uses context language for short tokens
"""

import re
from collections import Counter

try:
    from langdetect import detect
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False


class LanguageDetector:
    MAP = {
        "ar": "arb_Arab",
        "en": "eng_Latn",
        "fr": "fra_Latn",
        "es": "spa_Latn",
        "de": "deu_Latn",
        "it": "ita_Latn",
        "pt": "por_Latn",
        "ru": "rus_Cyrl",
        "tr": "tur_Latn",
        "nl": "nld_Latn",
        "pl": "pol_Latn",
        "sv": "swe_Latn",
        "id": "ind_Latn",
        "vi": "vie_Latn",
    }

    SCRIPT_PATTERNS = {
        "arabic": re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+"),
        "cyrillic": re.compile(r"[\u0400-\u04FF]+"),
        "greek": re.compile(r"[\u0370-\u03FF]+"),
        "hebrew": re.compile(r"[\u0590-\u05FF]+"),
        "thai": re.compile(r"[\u0E00-\u0E7F]+"),
        "devanagari": re.compile(r"[\u0900-\u097F]+"),
        "korean": re.compile(r"[\uAC00-\uD7AF]+"),
        "japanese": re.compile(r"[\u3040-\u30FF]+"),
        "chinese": re.compile(r"[\u4E00-\u9FFF]+"),
    }

    SCRIPT_DEFAULT = {
        "arabic": "arb_Arab",
        "cyrillic": "rus_Cyrl",
        "greek": "ell_Grek",
        "hebrew": "heb_Hebr",
        "thai": "tha_Thai",
        "devanagari": "hin_Deva",
        "korean": "kor_Hang",
        "japanese": "jpn_Jpan",
        "chinese": "zho_Hans",
    }

    def detect_by_script(self, token: str):
        for script, pat in self.SCRIPT_PATTERNS.items():
            if pat.search(token):
                return self.SCRIPT_DEFAULT[script]
        return None

    def detect_language(self, token: str, fallback="eng_Latn") -> str:
        token = token.strip()
        if not token:
            return fallback

        # script first
        script_lang = self.detect_by_script(token)
        if script_lang:
            return script_lang

        # short latin words are unstable
        if re.fullmatch(r"[A-Za-z]+", token) and len(token) <= 3:
            return fallback

        # use langdetect for longer latin tokens
        if LANGDETECT_AVAILABLE and len(token) >= 4:
            try:
                code = detect(token)
                return self.MAP.get(code, fallback)
            except:
                return fallback

        return fallback

    def analyze_words(self, text: str):
        if not text or not text.strip():
            return {"words": [], "languages_detected": [], "languages_count": 0}

        tokens = re.findall(r"\w+|[^\w\s]+|\s+", text, flags=re.UNICODE)

        words = []
        context_lang = "eng_Latn"

        for tok in tokens:
            if tok.isspace():
                continue

            # punctuation
            if re.fullmatch(r"[^\w\s]+", tok):
                words.append((tok, "punct"))
                continue

            lang = self.detect_language(tok, fallback=context_lang)
            words.append((tok, lang))
            context_lang = lang

        langs = [lang for _, lang in words if lang != "punct"]
        counts = Counter(langs)

        return {
            "words": words,
            "languages_detected": list(counts.keys()),
            "languages_count": len(counts),
        }
