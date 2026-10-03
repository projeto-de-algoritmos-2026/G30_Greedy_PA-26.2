"""Ponto de entrada da interface do TrailPack."""

import streamlit as st


def main() -> None:
    st.set_page_config(page_title="TrailPack", page_icon="🎒")
    st.title("🎒 TrailPack")
    st.write("Planejador inteligente de mochila para trilhas.")
    st.info("Projeto em desenvolvimento: configuração e otimização serão adicionadas nas próximas etapas.")


if __name__ == "__main__":
    main()
