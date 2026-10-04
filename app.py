"""Interface do planejador de mochila TrailPack."""

import json

import streamlit as st

from src.models import Item, Level, Trail, TrailConditions
from src.recommendation import recommend_backpack
from src.ui import ROOT, render_header

LEVEL_LABELS = {"baixo": "Baixo", "medio": "Médio", "alto": "Alto"}


def trail_form() -> Trail | None:
    st.subheader("01 · Trace sua aventura")
    st.caption("Conte como será o caminho. Nós cuidamos das contas da mochila.")
    with st.form("trail_configuration"):
        name = st.text_input("Nome da trilha", value="Minha próxima aventura", key="nome")
        left, right = st.columns(2)
        with left:
            distance = st.number_input("Distância (km)", min_value=0.0, value=12.0, step=1.0, key="distancia")
            duration = st.number_input("Duração (horas)", min_value=0.0, value=4.0, step=0.5, key="duracao")
            difficulty = st.selectbox("Dificuldade", list(LEVEL_LABELS), index=1, format_func=LEVEL_LABELS.get, key="dificuldade")
            isolation = st.selectbox("Isolamento", list(LEVEL_LABELS), format_func=LEVEL_LABELS.get, key="isolamento")
        with right:
            temperature = st.number_input("Temperatura (°C)", min_value=-50.0, max_value=60.0, value=25.0, step=1.0, key="temperatura")
            rain = st.selectbox("Possibilidade de chuva", list(LEVEL_LABELS), format_func=LEVEL_LABELS.get, key="chuva")
            people = st.number_input("Pessoas no grupo", min_value=1, value=1, step=1, key="pessoas")
            capacity = st.number_input("Capacidade total de carga (kg)", min_value=0.0, value=6.0, step=0.5, key="capacidade")
        water = st.checkbox("Há pontos de água durante o percurso", value=True, key="agua_disponivel")
        st.caption("A carga e o estoque são totais para o grupo. Mais pessoas não multiplicam os itens disponíveis.")
        submitted = st.form_submit_button("Montar minha mochila →", type="primary", use_container_width=True)
    if not submitted:
        return None
    return Trail(name, distance, duration,
                 TrailConditions(temperature, Level(difficulty), Level(rain), Level(isolation), water),
                 capacity, people)


def main() -> None:
    st.set_page_config(page_title="TrailPack · Sua próxima aventura", page_icon="🎒", layout="wide")
    render_header()
    st.caption("PLANEJADOR DE EXPEDIÇÃO · ALGORITMOS GULOSOS")
    with st.expander("🎒 O que está disponível nesta versão?"):
        st.write("Usamos o catálogo inicial do projeto. Seleção e edição de itens chegarão na próxima etapa.")
        st.write("Lanterna, apito, capa de chuva e kit de primeiros socorros são reservados primeiro. Água e alimentos usam o espaço restante.")
    try:
        trail = trail_form()
        if trail is not None:
            st.session_state.pop("recommendation", None)
            items = [Item(**entry) for entry in json.loads((ROOT / "data/items.json").read_text(encoding="utf-8"))]
            st.session_state.recommendation = recommend_backpack(trail, items)
    except (ValueError, OSError) as exc:
        st.session_state.pop("recommendation", None)
        st.error(f"Não foi possível montar a mochila: {exc}")
    if "recommendation" in st.session_state:
        result = st.session_state.recommendation
        st.success(f"Mochila calculada: {result.peso_total:.2f} kg de {result.trilha.capacidade:.2f} kg.")
    st.caption("TrailPack · Projeto de Algoritmos · Euller & Tiago")


if __name__ == "__main__":
    main()
