"""
language_config.py
Clean configuration for supported languages (NLLB-200)
"""

LANGUAGES = {
    "Arabic": "arb_Arab",
    "English": "eng_Latn",
    "Spanish": "spa_Latn",
    "French": "fra_Latn",
    "German": "deu_Latn",
    "Italian": "ita_Latn",
    "Portuguese": "por_Latn",
    "Russian": "rus_Cyrl",

    "Chinese (Simplified)": "zho_Hans",
    "Chinese (Traditional)": "zho_Hant",
    "Japanese": "jpn_Jpan",
    "Korean": "kor_Hang",
    "Hindi": "hin_Deva",
    "Bengali": "ben_Beng",
    "Urdu": "urd_Arab",
    "Vietnamese": "vie_Latn",
    "Thai": "tha_Thai",
    "Indonesian": "ind_Latn",
    "Malay": "zsm_Latn",
    "Tamil": "tam_Taml",
    "Telugu": "tel_Telu",

    "Turkish": "tur_Latn",
    "Dutch": "nld_Latn",
    "Polish": "pol_Latn",
    "Swedish": "swe_Latn",
    "Greek": "ell_Grek",
    "Czech": "ces_Latn",
    "Romanian": "ron_Latn",
    "Hungarian": "hun_Latn",
    "Ukrainian": "ukr_Cyrl",
    "Danish": "dan_Latn",
    "Finnish": "fin_Latn",
    "Norwegian": "nob_Latn",

    "Persian": "pes_Arab",
    "Hebrew": "heb_Hebr",

    "Swahili": "swh_Latn",
    "Amharic": "amh_Ethi",
    "Hausa": "hau_Latn",
    "Yoruba": "yor_Latn",
    "Somali": "som_Latn",

    "Catalan": "cat_Latn",
    "Slovak": "slk_Latn",
    "Bulgarian": "bul_Cyrl",
    "Croatian": "hrv_Latn",
    "Serbian": "srp_Cyrl",
    "Lithuanian": "lit_Latn",
    "Latvian": "lvs_Latn",
    "Estonian": "est_Latn",
    "Slovenian": "slv_Latn",
}

CODE_TO_LANGUAGE = {code: name for name, code in LANGUAGES.items()}


def get_language_code(language_name: str):
    return LANGUAGES.get(language_name)


def get_language_name_from_code(code: str):
    return CODE_TO_LANGUAGE.get(code, code)


def get_all_language_names():
    return sorted(LANGUAGES.keys())
