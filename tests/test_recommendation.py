"""Integração: trilha → prioridades → essenciais → Knapsack → recomendação."""

import json
from dataclasses import replace
from pathlib import Path

import pytest

from src.models import Category, Item, Trail, TrailConditions
from src.recommendation import recommend_backpack


@pytest.fixture
def trail():
    return Trail("Percurso de teste", 5, 2,
                 TrailConditions(20, "baixo", "baixo", "baixo", True), 4)


def test_known_optimum_after_reserving_essentials(trail):
    kit = Item("Kit", Category.SEGURANCA, 1, 10, False, True)
    water = Item("Água", Category.HIDRATACAO, 1, 100, True, False, 2)
    food = Item("Comida", Category.ALIMENTACAO, 2, 80, True, False, 3)
    result = recommend_backpack(trail, iter([food, kit, water]))
    assert [(i.nome, i.quantidade_padrao) for i in result.itens] == [
        ("Kit", 1), ("Água", 2), ("Comida", 0.5)]
    assert result.peso_total == pytest.approx(4)
    assert result.capacidade_restante == pytest.approx(0)
    assert result.valor_total == pytest.approx(250)
    assert food.quantidade_padrao == 3
    assert water.valor_base == 100


def test_context_reverses_selection_order(trail):
    water = Item("Água", Category.HIDRATACAO, 1, 100, True, False, 2)
    food = Item("Comida", Category.ALIMENTACAO, 1, 120, True, False, 2)
    small = replace(trail, capacidade=1)
    hot = replace(small, condicoes=replace(trail.condicoes, temperatura=30))
    assert recommend_backpack(small, [water, food]).itens[0].nome == "Comida"
    result = recommend_backpack(hot, [water, food])
    assert result.itens[0].nome == "Água"
    assert result.valor_total == pytest.approx(140)


def test_divisible_essential_is_counted_once(trail):
    water = Item("Água reservada", Category.HIDRATACAO, 1, 100, True, True, 2)
    result = recommend_backpack(trail, [water])
    assert len(result.itens) == 1
    assert result.peso_total == 2
    assert result.valor_total == 200


def test_infeasible_essentials_raise_without_mutating_stock(trail):
    kit = Item("Kit", Category.SEGURANCA, 5, 10, False, True)
    with pytest.raises(ValueError, match="essenciais"):
        recommend_backpack(trail, [kit])
    assert kit.peso == 5 and kit.quantidade_padrao == 1


def test_essentials_exactly_fill_capacity(trail):
    kit = Item("Kit", Category.SEGURANCA, 4, 10, False, True)
    water = Item("Água", Category.HIDRATACAO, 1, 100, True, False, 2)
    result = recommend_backpack(trail, [kit, water])
    assert [i.nome for i in result.itens] == ["Kit"]
    assert result.capacidade_restante == 0


@pytest.mark.parametrize("capacity", [0, 4])
def test_empty_stock_returns_empty_recommendation(trail, capacity):
    result = recommend_backpack(replace(trail, capacidade=capacity), [])
    assert result.itens == ()
    assert result.valor_total == 0
    assert result.peso_total == 0
    assert result.capacidade_restante == capacity
    assert result.avisos


def test_unavailable_essential_and_zero_utility_are_not_selected(trail):
    absent = Item("Kit indisponível", Category.SEGURANCA, 10, 100, False, True, 0)
    useless = Item("Recurso", Category.OUTROS, 1, 0, True, False, 3)
    result = recommend_backpack(trail, [absent, useless])
    assert result.itens == ()
    assert result.peso_total == 0


def test_group_does_not_invent_available_quantities(trail):
    item = Item("Água", Category.HIDRATACAO, 1, 100, True, False, 2)
    result = recommend_backpack(replace(trail, pessoas=4), [item])
    assert result.itens[0].quantidade_padrao == 2
    assert result.peso_total == 2
    assert result.avisos


def test_real_catalog_is_repeatable_and_respects_availability(trail):
    path = Path(__file__).resolve().parents[1] / "data/items.json"
    items = tuple(Item(**entry) for entry in json.loads(path.read_text()))
    snapshot = tuple(replace(item) for item in items)
    result = recommend_backpack(trail, items)
    assert result == recommend_backpack(trail, items)
    assert items == snapshot
    assert result.peso_total <= trail.capacidade + 1e-9
    for item in result.itens:
        original = next(i for i in items if i.nome == item.nome)
        assert 0 < item.quantidade_padrao <= original.quantidade_padrao
        if not item.divisivel:
            assert float(item.quantidade_padrao).is_integer()
    assert result.valor_total == pytest.approx(sum(i.valor_base * i.quantidade_padrao for i in result.itens))


def test_optional_equipment_reserves_capacity_only_when_requested(trail):
    map_item = Item("Mapa", Category.NAVEGACAO, 1, 20, False, False)
    water = Item("Água", Category.HIDRATACAO, 1, 100, True, False, 5)
    default = recommend_backpack(trail, [map_item, water])
    explicit = recommend_backpack(trail, [map_item, water], include_optional_equipment=True)
    assert [i.nome for i in default.itens] == ["Água"]
    assert default.itens[0].quantidade_padrao == 4
    assert [(i.nome, i.quantidade_padrao) for i in explicit.itens] == [("Mapa", 1), ("Água", 3)]
    assert explicit.valor_total == 320
    assert default.avisos and not explicit.avisos


def test_optional_equipment_overflow_is_reported(trail):
    equipment = Item("Equipamento", Category.OUTROS, 5, 10, False, False)
    with pytest.raises(ValueError, match="equipamentos selecionados"):
        recommend_backpack(trail, [equipment], include_optional_equipment=True)


def test_selected_items_have_contextual_explanations(trail):
    hot = replace(trail, duracao=7,
                  condicoes=replace(trail.condicoes, temperatura=30, agua_disponivel=False))
    water = Item("Água", Category.HIDRATACAO, 1, 100, True, False, 2)
    result = recommend_backpack(hot, [water])
    assert result.itens[0].valor_base == pytest.approx(273)
    reasons = " ".join(result.justificativas["Água"])
    assert "Temperatura alta" in reasons
    assert "Longa duração" in reasons
    assert "Sem pontos de água" in reasons
    assert set(result.justificativas) == {item.nome for item in result.itens}
