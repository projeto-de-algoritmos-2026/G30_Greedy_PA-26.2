"""Interface do planejador de mochila TrailPack."""

import json

import streamlit as st

from src.models import Item, Level, Trail, TrailConditions
from src.item_editor import render_custom_item_form, render_item_editor
from src.game_ui import render_game
from src.recommendation import recommend_backpack
from src.scenarios import load_scenarios
from src.ui import ROOT, render_header, render_recommendation

LEVEL_LABELS = {"baixo": "Baixo", "medio": "Médio", "alto": "Alto"}


def select_scenario(scenario: dict) -> None:
    for field, value in scenario["trilha"].items():
        st.session_state[field] = value
    st.session_state["active_scenario"] = scenario["titulo"]
    st.session_state.pop("recommendation", None)


def render_scenarios() -> None:
    st.subheader("Escolha sua próxima expedição")
    st.caption("Quatro cenários simulados para explorar. Escolha um ou crie seu próprio percurso abaixo.")
    for column, scenario in zip(st.columns(4), load_scenarios()):
        with column, st.container(border=True):
            st.markdown(f"### {scenario['icone']} {scenario['titulo']}")
            st.caption(scenario["nivel"].upper())
            st.write(scenario["descricao"])
            data = scenario["trilha"]
            st.caption(f"{data['distancia']:g} km · {data['duracao']:g} h · {data['temperatura']:g} °C")
            st.button("Explorar rota →", key=f"scenario_{scenario['id']}",
                      on_click=select_scenario, args=(scenario,), use_container_width=True)
    if "active_scenario" in st.session_state:
        st.info(f"Rota carregada: {st.session_state.active_scenario}. Ajuste os dados e monte sua mochila.")


def trail_form(items: list[Item]) -> tuple[Trail, tuple[Item, ...]] | None:
    defaults = {"nome": "Minha próxima aventura", "distancia": 12.0, "duracao": 4.0,
                "dificuldade": "medio", "isolamento": "baixo", "temperatura": 25.0,
                "chuva": "baixo", "pessoas": 1, "capacidade": 6.0, "agua_disponivel": True}
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)
    st.subheader("01 · Trace sua aventura")
    st.caption("Conte como será o caminho. Nós cuidamos das contas da mochila.")
    with st.form("trail_configuration"):
        name = st.text_input("Nome da trilha", key="nome")
        left, right = st.columns(2)
        with left:
            distance = st.number_input("Distância (km)", min_value=0.0, value=None, step=1.0, key="distancia")
            duration = st.number_input("Duração (horas)", min_value=0.0, value=None, step=0.5, key="duracao")
            difficulty = st.selectbox("Dificuldade", list(LEVEL_LABELS), format_func=LEVEL_LABELS.get, key="dificuldade")
            isolation = st.selectbox("Isolamento", list(LEVEL_LABELS), format_func=LEVEL_LABELS.get, key="isolamento")
        with right:
            temperature = st.number_input("Temperatura (°C)", min_value=-50.0, max_value=60.0, value=None, step=1.0, key="temperatura")
            rain = st.selectbox("Possibilidade de chuva", list(LEVEL_LABELS), format_func=LEVEL_LABELS.get, key="chuva")
            people = st.number_input("Pessoas no grupo", min_value=None, value=None, step=1, key="pessoas")
            capacity = st.number_input("Capacidade total de carga (kg)", min_value=0.0, value=None, step=0.5, key="capacidade")
        water = st.checkbox("Há pontos de água durante o percurso", key="agua_disponivel")
        st.caption("A carga e o estoque são totais para o grupo. Mais pessoas não multiplicam os itens disponíveis.")
        selected_records = render_item_editor(items)
        submitted = st.form_submit_button("Montar minha mochila →", type="primary", use_container_width=True)
    if not submitted:
        return None
    trail = Trail(name, distance, duration,
                 TrailConditions(temperature, Level(difficulty), Level(rain), Level(isolation), water),
                 capacity, people)
    return trail, tuple(Item(**record) for record in selected_records)


def main() -> None:
    st.set_page_config(page_title="TrailPack · Sua próxima aventura", page_icon="🎒", layout="wide")
    render_header()
    st.caption("PLANEJADOR DE EXPEDIÇÃO · ALGORITMOS GULOSOS")
    render_scenarios()
    try:
        catalog = [Item(**entry) for entry in json.loads((ROOT / "data/items.json").read_text(encoding="utf-8"))]
        render_custom_item_form(catalog)
        submission = trail_form(catalog + st.session_state.custom_items)
        if submission is not None:
            st.session_state.pop("recommendation", None)
            st.session_state.pop("game_comparison", None)
            for key in list(st.session_state):
                if key.startswith("game_quantity_"):
                    del st.session_state[key]
            trail, items = submission
            st.session_state.recommendation = recommend_backpack(trail, items, include_optional_equipment=True)
            st.session_state.recommendation_inventory = items
    except (ValueError, OSError) as exc:
        st.session_state.pop("recommendation", None)
        st.error(f"Não foi possível montar a mochila: {exc}")
    if "recommendation" in st.session_state:
        render_recommendation(st.session_state.recommendation)
        render_game(st.session_state.recommendation.trilha, st.session_state.recommendation_inventory)
    st.caption("TrailPack · Projeto de Algoritmos · Euller & Tiago")


if __name__ == "__main__":
    main()
