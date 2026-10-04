"""Coerência das justificativas com as condições e os itens selecionados."""

from dataclasses import replace

import pytest

from src.explanations import explain_item
from src.models import Category, Item, Level, Trail, TrailConditions
from src.recommendation import recommend_backpack


@pytest.fixture
def trail():
    return Trail("Trilha", 5, 2,
                 TrailConditions(20, Level.BAIXO, Level.BAIXO, Level.BAIXO, True), 5)


def resource(category, name="Recurso"):
    return Item(name, category, 1, 100, True, False, 10)


def test_water_explains_hot_long_trail_without_water(trail):
    changed = replace(trail, duracao=7, distancia=18,
                      condicoes=replace(trail.condicoes, temperatura=30, agua_disponivel=False))
    result = recommend_backpack(changed, [resource(Category.HIDRATACAO, "Água")])
    reasons = result.justificativas["Água"]

    assert reasons[:3] == [
        "Temperatura alta (30 °C ou mais).",
        "Longa duração da trilha (6 horas ou mais).",
        "Sem pontos de água disponíveis no percurso.",
    ]
    assert not any("distância" in reason for reason in reasons)


@pytest.mark.parametrize("field,value,category,text", [
    ("temperatura", 30, Category.HIDRATACAO, "Temperatura alta"),
    ("temperatura", 30, Category.PROTECAO_CLIMATICA, "Temperatura alta"),
    ("temperatura", 10, Category.PROTECAO_CLIMATICA, "Temperatura baixa"),
    ("agua_disponivel", False, Category.HIDRATACAO, "Sem pontos de água"),
    ("dificuldade", Level.MEDIO, Category.ALIMENTACAO, "Dificuldade"),
    ("dificuldade", Level.ALTO, Category.SEGURANCA, "Dificuldade"),
    ("isolamento", Level.ALTO, Category.SEGURANCA, "Isolamento"),
    ("isolamento", Level.MEDIO, Category.NAVEGACAO, "Isolamento"),
    ("isolamento", Level.ALTO, Category.ENERGIA, "Isolamento"),
    ("chuva", Level.MEDIO, Category.PROTECAO_CLIMATICA, "Chuva"),
    ("chuva", Level.ALTO, Category.PROTECAO_CLIMATICA, "Chuva"),
])
def test_contextual_reasons_apply_only_to_relevant_categories(trail, field, value, category, text):
    changed = replace(trail, condicoes=replace(trail.condicoes, **{field: value}))
    assert any(text in reason for reason in explain_item(resource(category), changed))
    assert not any(text in reason for reason in explain_item(resource(Category.OUTROS), changed))


@pytest.mark.parametrize("field,below,boundary,text", [
    ("duracao", 5.99, 6, "Longa duração"),
    ("distancia", 14.99, 15, "Longa distância"),
])
def test_long_trail_boundaries(trail, field, below, boundary, text):
    water = resource(Category.HIDRATACAO)
    assert not any(text in reason for reason in explain_item(water, replace(trail, **{field: below})))
    assert any(text in reason for reason in explain_item(water, replace(trail, **{field: boundary})))


@pytest.mark.parametrize("temperature", [10.01, 29.99])
def test_neutral_temperature_does_not_claim_heat_or_cold(trail, temperature):
    changed = replace(trail, condicoes=replace(trail.condicoes, temperatura=temperature))
    reasons = explain_item(resource(Category.PROTECAO_CLIMATICA), changed)
    assert not any("Temperatura" in reason for reason in reasons)
    assert "utilidade base" in reasons[0]


def test_only_selected_items_receive_explanations_and_inputs_are_preserved(trail):
    essential = Item("Kit", Category.SEGURANCA, 1, 0, False, True)
    water = resource(Category.HIDRATACAO, "Água")
    optional = Item("Mapa", Category.NAVEGACAO, 1, 100, False, False)
    unavailable = replace(water, nome="Indisponível", quantidade_padrao=0)
    items = [essential, water, optional, unavailable]
    originals = tuple(replace(item) for item in items)

    result = recommend_backpack(trail, iter(items))

    assert set(result.justificativas) == {"Kit", "Água"}
    assert any("essencial" in reason for reason in result.justificativas["Kit"])
    assert any("utilidade por kg" in reason for reason in result.justificativas["Água"])
    assert tuple(items) == originals
    assert recommend_backpack(trail, []).justificativas == {}
