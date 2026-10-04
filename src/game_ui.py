"""Montagem manual e apresentação da comparação com a solução gulosa."""

import streamlit as st

from .game import compare_player_with_greedy
from .models import Item, Trail


def render_game(trail: Trail, items: tuple[Item, ...]) -> None:
    st.subheader("Desafio TrailPack · Jogador versus algoritmo")
    fixed_weight = sum(item.peso_total for item in items if item.essencial or not item.divisivel)
    st.write(
        f"Monte os consumíveis usando até {max(0.0, trail.capacidade - fixed_weight):.3f} kg. "
        f"Os mesmos equipamentos e essenciais ({fixed_weight:.3f} kg) são reservados nas duas mochilas."
    )
    st.caption("O desafio usa a trilha e o estoque da última montagem. As quantidades informadas abaixo são o que você deseja levar, dentro desse estoque.")
    resources = [item for item in items if item.divisivel and not item.essencial and item.quantidade_padrao > 0]
    with st.form("player_backpack"):
        quantities = {}
        for index, item in enumerate(resources):
            quantities[item.nome] = st.number_input(
                f"{item.nome} · estoque: {item.quantidade_padrao:g} · peso/un.: {item.peso:g} kg",
                min_value=0.0, max_value=float(item.quantidade_padrao), value=0.0,
                step=0.1, key=f"game_quantity_{index}",
            )
        submitted = st.form_submit_button("Comparar com o algoritmo")
    if submitted:
        st.session_state.pop("game_comparison", None)
        try:
            st.session_state.game_comparison = compare_player_with_greedy(trail, items, quantities)
        except ValueError as exc:
            st.error(f"Mochila do jogador inválida: {exc}")
    if "game_comparison" in st.session_state:
        comparison = st.session_state.game_comparison
        st.caption("Resultado da última comparação. Ao editar sua mochila, compare novamente.")
        player, greedy, efficiency = st.columns(3)
        player.metric("Score jogador", f"{comparison.score_jogador:.2f}")
        greedy.metric("Score greedy", f"{comparison.score_greedy:.2f}")
        efficiency.metric("Eficiência", f"{comparison.eficiencia_percentual:.2f}%")
        st.write(f"Peso jogador: {comparison.jogador.peso_total:.3f} kg · Peso greedy: {comparison.greedy.peso_total:.3f} kg")
        st.caption("Score = soma da utilidade contextual × quantidade selecionada, incluindo os itens reservados. Eficiência = score jogador / score greedy × 100. Se ambos os scores forem zero, o empate vale 100%.")
        st.dataframe([
            {"Item": item.nome,
             "Quantidade jogador": next((chosen.quantidade_padrao for chosen in comparison.jogador.itens if chosen.nome == item.nome), 0),
             "Quantidade greedy": next((chosen.quantidade_padrao for chosen in comparison.greedy.itens if chosen.nome == item.nome), 0)}
            for item in items if item.quantidade_padrao > 0
        ], use_container_width=True, hide_index=True)
