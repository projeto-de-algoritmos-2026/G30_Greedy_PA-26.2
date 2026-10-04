"""Cenários de prioridade e contrato com o catálogo e o Knapsack."""

import json
from dataclasses import replace
from pathlib import Path

import pytest

from src.knapsack import fractional_knapsack
from src.models import Category, Item, Level, Trail, TrailConditions
from src.priority_engine import calculate_item_priority, calculate_priorities
from src.trail_profile import TrailProfile, build_trail_profile


@pytest.fixture
def trail():
    return Trail("Trilha curta", 5, 2,
                 TrailConditions(20, Level.BAIXO, Level.BAIXO, Level.BAIXO, True), 8)


def resource(category, value=100):
    return Item("Recurso", category, 1, value, True, False, 3)


def test_neutral_profile_preserves_all_categories(trail):
    items = tuple(resource(category) for category in Category)
    priorities = calculate_priorities(items, trail)
    assert all(p.valor_contextual == 100 for p in priorities)
    assert [p.item for p in priorities] == list(items)


@pytest.mark.parametrize("conditions,category", [
    ({"temperatura": 30}, Category.HIDRATACAO),
    ({"temperatura": 30}, Category.PROTECAO_CLIMATICA),
    ({"temperatura": 10}, Category.PROTECAO_CLIMATICA),
    ({"chuva": Level.ALTO}, Category.PROTECAO_CLIMATICA),
    ({"isolamento": Level.ALTO}, Category.SEGURANCA),
    ({"isolamento": Level.ALTO}, Category.NAVEGACAO),
    ({"isolamento": Level.ALTO}, Category.ENERGIA),
    ({"dificuldade": Level.ALTO}, Category.SEGURANCA),
    ({"dificuldade": Level.ALTO}, Category.ALIMENTACAO),
    ({"agua_disponivel": False}, Category.HIDRATACAO),
])
def test_conditions_raise_relevant_priority(trail, conditions, category):
    changed = replace(trail, condicoes=replace(trail.condicoes, **conditions))
    item = resource(category)
    assert calculate_priorities([item], changed)[0].valor_contextual > 100
    assert calculate_priorities([resource(Category.OUTROS)], changed)[0].valor_contextual == 100


@pytest.mark.parametrize("field,below,boundary", [("duracao", 5.99, 6), ("distancia", 14.99, 15)])
def test_long_trail_thresholds(trail, field, below, boundary):
    items = [resource(Category.HIDRATACAO), resource(Category.ALIMENTACAO)]
    assert [p.valor_contextual for p in calculate_priorities(items, replace(trail, **{field: below}))] == [100, 100]
    assert [p.valor_contextual for p in calculate_priorities(items, replace(trail, **{field: boundary}))] == [130, 130]


def test_long_distance_and_duration_do_not_double_count(trail):
    profile = build_trail_profile(replace(trail, duracao=7, distancia=18))
    assert profile.hidratacao == pytest.approx(1.3)
    assert profile.alimentacao == pytest.approx(1.3)


@pytest.mark.parametrize("temperature,expected", [(29.99, 1), (30, 1.4), (35, 1.4)])
def test_heat_threshold(trail, temperature, expected):
    changed = replace(trail, condicoes=replace(trail.condicoes, temperatura=temperature))
    assert build_trail_profile(changed).hidratacao == expected


@pytest.mark.parametrize("field,category", [
    ("chuva", Category.PROTECAO_CLIMATICA),
    ("isolamento", Category.SEGURANCA),
    ("dificuldade", Category.ALIMENTACAO),
])
def test_levels_increase_monotonically(trail, field, category):
    values = [build_trail_profile(replace(trail, condicoes=replace(trail.condicoes, **{field: level}))).factor_for(category)
              for level in (Level.BAIXO, Level.MEDIO, Level.ALTO)]
    assert values[0] < values[1] < values[2]


def test_combined_hot_long_dry_trail(trail):
    changed = replace(trail, distancia=18, duracao=7,
                      condicoes=replace(trail.condicoes, temperatura=30, agua_disponivel=False))
    priority = calculate_priorities([resource(Category.HIDRATACAO)], changed)[0]
    assert priority.valor_contextual == pytest.approx(273)
    assert priority.valor_por_peso == pytest.approx(273)


def test_catalog_is_preserved_and_recalculation_is_stable(trail):
    path = Path(__file__).resolve().parents[1] / "data" / "items.json"
    items = tuple(Item(**entry) for entry in json.loads(path.read_text()))
    original = tuple(replace(item) for item in items)
    changed = replace(trail, condicoes=replace(trail.condicoes, temperatura=30))
    priorities = calculate_priorities(iter(items), changed)
    assert priorities == calculate_priorities(items, changed)
    assert items == original
    for priority in priorities:
        adjusted = priority.as_knapsack_item()
        assert adjusted is not priority.item
        assert replace(adjusted, valor_base=priority.item.valor_base) == priority.item
    assert any(not p.item.divisivel for p in priorities)


def test_context_changes_knapsack_choice_without_mutating_inputs(trail):
    water = resource(Category.HIDRATACAO)
    food = replace(resource(Category.ALIMENTACAO, 120), nome="Comida")
    assert fractional_knapsack([water, food], 1)[0].nome == "Comida"
    hot = replace(trail, condicoes=replace(trail.condicoes, temperatura=30))
    priorities = calculate_priorities([water, food], hot)
    chosen = fractional_knapsack([p.as_knapsack_item() for p in priorities], 1)
    assert chosen[0].categoria == Category.HIDRATACAO
    assert chosen[0].quantidade_padrao == 1
    assert chosen[0].valor_base == pytest.approx(140)
    assert water.valor_base == 100
    assert water.quantidade_padrao == 3


def test_empty_zero_value_and_zero_availability(trail):
    assert calculate_priorities([], trail) == ()
    item = replace(resource(Category.HIDRATACAO, 0), quantidade_padrao=0)
    priority = calculate_priorities([item], trail)[0]
    assert priority.valor_contextual == 0
    assert priority.as_knapsack_item().quantidade_padrao == 0


def test_people_and_capacity_do_not_change_per_unit_value(trail):
    items = [resource(Category.HIDRATACAO)]
    assert calculate_priorities(items, trail) == calculate_priorities(items, replace(trail, pessoas=4, capacidade=0))


@pytest.mark.parametrize("factor", [float("inf"), float("nan"), -1])
def test_invalid_profile_factor_is_rejected(factor):
    with pytest.raises(ValueError):
        calculate_item_priority(resource(Category.HIDRATACAO), TrailProfile(hidratacao=factor))


def test_contextual_value_overflow_is_rejected():
    with pytest.raises(ValueError):
        calculate_item_priority(resource(Category.HIDRATACAO, 1e308), TrailProfile(hidratacao=3))

