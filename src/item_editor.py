"""Seleção e customização dos itens disponíveis na sessão do usuário."""

from dataclasses import asdict

import streamlit as st

from .models import Category, Item


def render_custom_item_form(catalog: list[Item]) -> None:
    """Adiciona itens à sessão, preservando o catálogo em disco."""
    st.session_state.setdefault("custom_items", [])
    with st.expander("Adicionar item personalizado"):
        with st.form("custom_item", clear_on_submit=True):
            name = st.text_input("Nome do item", key="custom_name")
            category = st.selectbox("Categoria", [category.value for category in Category], key="custom_category")
            weight = st.number_input("Peso por unidade (kg)", min_value=0.001, value=0.1, step=0.01, key="custom_weight")
            value = st.number_input("Utilidade base por unidade", min_value=0.0, value=50.0, step=1.0, key="custom_value")
            quantity = st.number_input("Quantidade disponível", min_value=0.0, value=1.0, step=0.1, key="custom_quantity")
            divisible = st.checkbox("Pode ser fracionado", key="custom_divisible")
            essential = st.checkbox("Essencial", key="custom_essential")
            st.caption("Indivisíveis exigem quantidade inteira. Peso e utilidade devem corresponder à mesma unidade de quantidade.")
            added = st.form_submit_button("Adicionar item")
        if added:
            try:
                item = Item(name.strip(), category, weight, value, divisible, essential, quantity)
                existing = catalog + st.session_state.custom_items
                if any(other.nome.casefold() == item.nome.casefold() for other in existing):
                    raise ValueError("Já existe um item com esse nome.")
                st.session_state.custom_items.append(item)
                st.session_state.pop("recommendation", None)
                st.success(f"{item.nome} adicionado. Selecione-o abaixo e monte a mochila.")
            except ValueError as exc:
                st.error(f"Não foi possível adicionar o item: {exc}")


def render_item_editor(items: list[Item]) -> list[dict]:
    """Renderiza controles no formulário de montagem; validação ocorre no envio."""
    st.subheader("02 · Escolha o que você tem disponível")
    st.caption("Marque os itens que deseja levar. Equipamentos selecionados são reservados inteiros; consumíveis usam a capacidade restante. Quantidade zero indica estoque indisponível.")
    st.caption("Água e isotônico: litros. Alimentos e mistura energética: kg. Equipamentos: unidades. Ajuste o peso em kg por unidade, incluindo a embalagem quando necessário.")
    records = []
    for index, item in enumerate(items):
        prefix = f"inventory_{index}"
        with st.expander(item.nome):
            enabled = st.checkbox("Selecionar item", value=item.essencial or item.divisivel,
                                  key=f"{prefix}_selected")
            st.caption(f"{item.categoria.value} · {'Essencial' if item.essencial else 'Opcional'} · {'Divisível' if item.divisivel else 'Indivisível'}")
            left, right = st.columns(2)
            with left:
                quantity = st.number_input(
                    "Quantidade disponível", min_value=0.0 if item.divisivel else 0,
                    value=float(item.quantidade_padrao) if item.divisivel else int(item.quantidade_padrao),
                    step=0.1 if item.divisivel else 1, key=f"{prefix}_quantity",
                )
            with right:
                weight = st.number_input("Peso por unidade (kg)", min_value=0.001,
                                         value=float(item.peso), step=0.01, key=f"{prefix}_weight")
            if enabled:
                record = asdict(item)
                record.update(peso=weight, quantidade_padrao=quantity)
                records.append(record)
    return records
