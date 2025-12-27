"""
app_simple.py
Clean UI + high-quality translation + word-level language analysis
✅ No footer
✅ No examples
"""

import gradio as gr
from model_handler import TranslationModel
from language_config import get_language_code, get_all_language_names, get_language_name_from_code

translator = TranslationModel()
translator.load_model()

SIMPLE_CSS = """
* {font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;}
.main-container {max-width: 900px; margin: 0 auto; padding: 20px;}

.label-text {
    color: #64748b;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 10px;
}

.simple-input textarea {
    border: 1px solid #e0e0e0 !important;
    border-radius: 8px !important;
    background: #ffffff !important;
    color: #000000 !important;
    caret-color: #000000 !important;
    font-size: 16px !important;
    line-height: 1.6 !important;
}

.output-text textarea {
    background: #1e293b !important;
    color: white !important;
    border-radius: 8px !important;
    font-size: 18px !important;
    line-height: 1.8 !important;
}

.translate-button {
    background: #3b82f6 !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 10px 24px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
}
.translate-button:hover {background: #2563eb !important;}

footer {display: none !important;}
.gradio-container footer {display:none !important;}
"""


def format_analysis(analysis):
    if not analysis:
        return ""

    langs = [get_language_name_from_code(code) for code in analysis["languages_detected"]]
    md = f"✅ **Detected Languages ({analysis['languages_count']}):** " + ", ".join(langs) + "\n\n"

    md += "✅ **Word-by-word:**\n"
    for word, lang in analysis["words"]:
        if lang == "punct":
            md += f"- `{word}` → punctuation\n"
        else:
            md += f"- **{word}** → `{get_language_name_from_code(lang)}`\n"

    return md


def translate_ui(text, target_lang):
    if not text or not text.strip():
        return "", "⚠️ Please enter some text.", ""

    target_code = get_language_code(target_lang)
    result = translator.translate(text, target_code)

    translation = result["translation"]
    analysis = result["analysis"]

    status = f"✅ Done | Languages: {analysis['languages_count'] if analysis else 0}"
    analysis_md = format_analysis(analysis)

    return translation, status, analysis_md


def create_app():
    with gr.Blocks(css=SIMPLE_CSS, title="Translation") as app:
        with gr.Column(elem_classes="main-container"):
            gr.Markdown("# Translation")
            gr.Markdown("Translate mixed-language text + show analysis (word-by-word)")

            gr.Markdown("**SOURCE TEXT (MIXED LANGUAGES)**", elem_classes="label-text")
            source_text = gr.Textbox(
                placeholder="Type or paste mixed text here...",
                lines=6,
                show_label=False,
                elem_classes="simple-input"
            )

            with gr.Row():
                gr.Markdown("**Target Language:**")
                target_lang = gr.Dropdown(
                    choices=get_all_language_names(),
                    value="Arabic",
                    show_label=False
                )

            translate_btn = gr.Button("🚀 Translate", elem_classes="translate-button", variant="primary")

            gr.Markdown("**TRANSLATION OUTPUT**", elem_classes="label-text")
            translation_output = gr.Textbox(
                lines=6,
                show_label=False,
                interactive=False,
                elem_classes="output-text"
            )

            status = gr.Markdown("")
            analysis_box = gr.Markdown("")

            translate_btn.click(
                fn=translate_ui,
                inputs=[source_text, target_lang],
                outputs=[translation_output, status, analysis_box]
            )

            source_text.submit(
                fn=translate_ui,
                inputs=[source_text, target_lang],
                outputs=[translation_output, status, analysis_box]
            )

    try:
        app.queue(max_size=20)
    except TypeError:
        app.queue()

    return app


if __name__ == "__main__":
    app = create_app()
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        inbrowser=True,
        debug=True,
        show_error=True
    )
