from pathlib import Path

import streamlit as st

from application.models import ConversionRequest
from application.use_cases import process_document
from domain.models import ConversionMode
from domain.music import TONES

LABELS = {ConversionMode.CHORDS_TO_CHORDS: "Acordes para acordes",
          ConversionMode.CHORDS_TO_NASHVILLE: "Acordes para Nashville",
          ConversionMode.NASHVILLE_TO_CHORDS: "Nashville para acordes"}


def run_app():
    st.set_page_config(page_title="Transpositor de Cifras", page_icon="🎸")
    st.title("🎸 Transpositor de Cifras")
    st.caption(
        "Os ficheiros são processados em memória para gerar a cópia convertida. "
        "O documento original nunca é alterado."
    )
    uploaded = st.file_uploader("Carregar ficheiro", type=["docx", "pdf"])
    mode = st.selectbox("Modo de conversão", list(ConversionMode), format_func=LABELS.get)
    source = st.selectbox("Tom original", TONES, index=TONES.index("Ab")) if mode is not ConversionMode.NASHVILLE_TO_CHORDS else None
    target = st.selectbox("Tom de destino" if mode is ConversionMode.NASHVILLE_TO_CHORDS else "Novo tom", TONES, index=TONES.index("C")) if mode is not ConversionMode.CHORDS_TO_NASHVILLE else None
    if st.button("Processar ficheiro", type="primary", disabled=uploaded is None):
        try:
            request = ConversionRequest(mode, source, target)
            result = process_document(uploaded.getvalue(), Path(uploaded.name).suffix, request)
            suffix = "Nashville" if mode is ConversionMode.CHORDS_TO_NASHVILLE else f"Tom {target}"
            st.session_state.result = result
            st.session_state.name = f"{Path(uploaded.name).stem} - {suffix}{Path(uploaded.name).suffix}"
            st.success("Ficheiro processado com sucesso. Reveja o resultado, sobretudo se for PDF.")
        except (ValueError, ModuleNotFoundError) as exc:
            st.error(str(exc))
    if st.session_state.get("result"):
        st.download_button("Descarregar ficheiro", st.session_state.result, st.session_state.name)
