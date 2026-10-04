"""Pontuação, restrições e igualdade de condições no desafio."""

from dataclasses import replace

import pytest

from src.game import compare_player_with_greedy
from src.models import Category, Item, Level, Trail, TrailConditions


@pytest.fixture
def trail():
    return Trail("Desafio", 5, 2,
                 TrailConditions(20, Level.BAIXO, Level.BAIXO, Level.BAIXO, True), 50)


@pytest.fixture
def items():
    return [Item(name, Category.OUTROS, weight, value, True, False)
            for name, weight, value in [("A", 10, 60), ("B", 20, 100), ("C", 30, 120)]]


def test_known_scores_and_efficiency(trail, items):
    original = tuple(replace(item) for item in items)
    result = compare_player_with_greedy(trail, iter(items), {"A": 1, "B": 0.5, "C": 1})

    assert result.score_jogador == pytest.approx(230)
    assert result.score_greedy == pytest.approx(240)
    assert result.eficiencia_percentual == pytest.approx(230 / 240 * 100)
    assert result.jogador.peso_total == pytest.approx(50)
    assert result.greedy.peso_total == pytest.approx(50)
    assert tuple(items) == original


def test_optimal_player_reaches_one_hundred_percent(trail, items):
    result = compare_player_with_greedy(trail, items, {"A": 1, "B": 1, "C": 2 / 3})
    assert result.score_jogador == pytest.approx(240)
    assert result.eficiencia_percentual == pytest.approx(100)


def test_empty_player_scores_zero_with_positive_greedy(trail, items):
    result = compare_player_with_greedy(trail, items, {})
    assert result.jogador.itens == ()
    assert result.score_jogador == 0
    assert result.eficiencia_percentual == 0


@pytest.mark.parametrize("capacity", [0, 50])
def test_zero_scores_are_a_tie_without_division_by_zero(trail, capacity):
    result = compare_player_with_greedy(replace(trail, capacidade=capacity), [], {})
    assert result.score_jogador == result.score_greedy == 0
    assert result.eficiencia_percentual == 100


@pytest.mark.parametrize("essential,divisible", [(True, False), (False, False), (True, True)])
def test_same_fixed_items_and_remaining_capacity(trail, items, essential, divisible):
    fixed = Item("Fixo", Category.OUTROS, 5, 20, divisible, essential, 2)
    result = compare_player_with_greedy(replace(trail, capacidade=60), [fixed, *items], {"A": 1, "B": 0.5, "C": 1})

    assert result.jogador.itens[0] == result.greedy.itens[0] == fixed
    assert result.score_jogador == pytest.approx(270)
    assert result.score_greedy == pytest.approx(280)
    assert result.jogador.peso_total == result.greedy.peso_total == pytest.approx(60)


def test_contextual_utility_is_used_once_for_both_players(trail):
    hot = replace(trail, duracao=7, capacidade=2,
                  condicoes=replace(trail.condicoes, temperatura=30, agua_disponivel=False))
    water = Item("Água", Category.HIDRATACAO, 1, 100, True, False, 3)
    result = compare_player_with_greedy(hot, [water], {"Água": 1})

    assert result.score_jogador == pytest.approx(273)
    assert result.score_greedy == pytest.approx(546)
    assert result.eficiencia_percentual == pytest.approx(50)
    assert water.valor_base == 100


@pytest.mark.parametrize("quantity", [-1, 1.1, float("nan"), float("inf"), True, "1"])
def test_invalid_or_unavailable_quantity_is_rejected(trail, items, quantity):
    with pytest.raises(ValueError, match="Quantidade"):
        compare_player_with_greedy(trail, items, {"A": quantity})


def test_overweight_player_is_rejected(trail, items):
    with pytest.raises(ValueError, match="excede"):
        compare_player_with_greedy(trail, items, {"A": 1, "B": 1, "C": 1})


def test_unknown_resource_is_rejected(trail, items):
    with pytest.raises(ValueError, match="não disponível"):
        compare_player_with_greedy(trail, items, {"Inexistente": 1})


def test_fixed_items_cannot_be_changed_by_player(trail):
    fixed = Item("Kit", Category.SEGURANCA, 1, 100, False, True)
    with pytest.raises(ValueError, match="não disponível"):
        compare_player_with_greedy(trail, [fixed], {"Kit": 0})


def test_duplicate_names_are_rejected(trail, items):
    with pytest.raises(ValueError, match="nomes únicos"):
        compare_player_with_greedy(trail, [items[0], replace(items[1], nome="a")], {})


def test_infeasible_fixed_items_are_rejected(trail):
    fixed = Item("Kit", Category.SEGURANCA, 51, 100, False, True)
    with pytest.raises(ValueError, match="excede"):
        compare_player_with_greedy(trail, [fixed], {})
