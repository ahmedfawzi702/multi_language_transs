"""
model_handler.py
✅ High Quality + Full coverage for mixed text
✅ Chooses best translation based on:
    1) completeness (length / punctuation)
    2) minimal leftover foreign scripts (Latin/Arabic/etc.)
✅ No chunk splitting
✅ No placeholders
"""

import re
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from language_detector import LanguageDetector


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip() if text else ""


# --- script detection helpers ---
ARABIC_RE = re.compile(r"[\u0600-\u06FF]")
LATIN_RE = re.compile(r"[A-Za-z]")
CYRILLIC_RE = re.compile(r"[\u0400-\u04FF]")
CJK_RE = re.compile(r"[\u4E00-\u9FFF]")


def count_leftover_scripts(text: str, target_lang_code: str) -> int:
    """
    Penalize foreign scripts that should NOT appear in output.
    Example:
        target=Arabic -> penalize Latin, Cyrillic, CJK
        target=English -> penalize Arabic, Cyrillic, CJK
    """
    if not text:
        return 999

    arabic = len(ARABIC_RE.findall(text))
    latin = len(LATIN_RE.findall(text))
    cyr = len(CYRILLIC_RE.findall(text))
    cjk = len(CJK_RE.findall(text))

    # Target script expectation
    if target_lang_code in ["arb_Arab", "pes_Arab", "urd_Arab"]:
        # Arabic-script languages => Latin/Cyrillic/CJK are leftovers
        return latin + cyr + cjk

    if target_lang_code in ["eng_Latn", "fra_Latn", "spa_Latn", "deu_Latn", "ita_Latn", "por_Latn", "tur_Latn", "nld_Latn"]:
        # Latin-script languages => Arabic/Cyrillic/CJK leftovers
        return arabic + cyr + cjk

    if target_lang_code in ["rus_Cyrl", "ukr_Cyrl", "bul_Cyrl"]:
        # Cyrillic => Latin/Arabic/CJK leftovers
        return latin + arabic + cjk

    if target_lang_code in ["zho_Hans", "zho_Hant", "jpn_Jpan", "kor_Hang"]:
        # CJK => leftover Latin/Arabic/Cyrillic
        return latin + arabic + cyr

    # default: penalize latin + arabic leftovers
    return latin + arabic


def score_translation(source: str, translation: str, target_lang_code: str) -> float:
    """
    Higher score = better.
    ✅ reward completeness
    ✅ penalize leftover foreign scripts
    """
    if not translation:
        return -999

    source = normalize(source)
    translation = normalize(translation)

    ratio = len(translation) / max(len(source), 1)
    end_bonus = 0.25 if translation[-1] in ".!?؟" else 0.0

    leftover = count_leftover_scripts(translation, target_lang_code)
    leftover_penalty = leftover * 0.02   # ✅ strong penalty

    # if translation is too short
    short_penalty = 0.7 if ratio < 0.55 else 0.0

    return (ratio + end_bonus) - (leftover_penalty + short_penalty)


class TranslationModel:
    def __init__(self, model_name="facebook/nllb-200-distilled-600M"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.detector = LanguageDetector()
        print(f"🖥️ Device: {self.device.upper()}")

    def load_model(self):
        if self.model is not None:
            return

        print("📥 Loading translation model...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, use_fast=True)

        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
        ).to(self.device)

        self.model.eval()
        print("✅ Model loaded successfully!")

    def _translate_with_src(self, text: str, src_lang: str, tgt_lang: str) -> str:
        self.tokenizer.src_lang = src_lang

        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.inference_mode():
            tokens = self.model.generate(
                **inputs,
                forced_bos_token_id=self.tokenizer.convert_tokens_to_ids(tgt_lang),
                max_new_tokens=450,          # ✅ allow full output
                num_beams=12,                # ✅ higher quality
                do_sample=False,
                use_cache=True,
                no_repeat_ngram_size=3,
                repetition_penalty=1.18,
                length_penalty=1.05,
                early_stopping=True,
            )

        return self.tokenizer.batch_decode(tokens, skip_special_tokens=True)[0].strip()

    def translate(self, text: str, target_lang_code: str):
        text = normalize(text)
        if not text:
            return {"translation": "", "analysis": None}

        if self.model is None:
            self.load_model()

        analysis = self.detector.analyze_words(text)
        detected = analysis["languages_detected"]

        # ✅ Try 3 possible source languages (best coverage)
        candidates = []

        # Arabic candidate (if Arabic detected)
        if "arb_Arab" in detected:
            candidates.append("arb_Arab")

        # English candidate always
        candidates.append("eng_Latn")

        # French/Spanish candidate if present
        if "fra_Latn" in detected:
            candidates.append("fra_Latn")
        elif "spa_Latn" in detected:
            candidates.append("spa_Latn")

        # Translate with all candidates
        outputs = []
        for src in list(dict.fromkeys(candidates)):  # unique keep order
            out = self._translate_with_src(text, src, target_lang_code)
            outputs.append((out, score_translation(text, out, target_lang_code), src))

        # Choose best
        best_translation, best_score, best_src = max(outputs, key=lambda x: x[1])

        return {
            "translation": best_translation,
            "analysis": analysis,
            "best_src": best_src,
            "best_score": round(best_score, 3)
        }
