from dataclasses import replace

import pytest

from src.essential_items import optimize_with_essentials, select_essential_items
from src.models import Category, Item


def item(name, weight=1, quantity=1, *, essential=False, divisible=False):
    return Item(name, Category.OUTROS, weight, 100, divisible, essential, quantity)


def test_separates_essentials_resources_and_optional_equipment():
    lantern = item("Lanterna", 0.2, essential=True)
    water = item("Água", quantity=3, divisible=True)
    power_bank = item("Power bank", 0.25)

    selection = select_essential_items(iter([lantern, water, power_bank]), 5)

    assert selection.essenciais == (lantern,)
    assert selection.recursos_otimizaveis == (water,)
    assert selection.itens_opcionais == (power_bank,)
    assert selection.peso_essenciais == pytest.approx(0.2)
    assert selection.capacidade_restante == pytest.approx(4.8)


def test_essential_weight_includes_all_units():
    selection = select_essential_items([item("Lanterna", 0.2, 3, essential=True)], 2)

    assert selection.peso_essenciais == pytest.approx(0.6)
    assert selection.capacidade_restante == pytest.approx(1.4)
    assert selection.essenciais[0].quantidade_padrao == 3


def test_knapsack_uses_remaining_capacity_and_preserves_inputs():
    essentials = item("Kit", 1.3, essential=True)
    water = item("Água", quantity=10, divisible=True)
    original = (replace(essentials), replace(water))

    selected = optimize_with_essentials(iter([essentials, water]), 8)

    assert selected[0] == essentials
    assert selected[1].quantidade_padrao == pytest.approx(6.7)
    assert sum(entry.peso_total for entry in selected) == pytest.approx(8)
    assert (essentials, water) == original


def test_divisible_essential_is_reserved_once():
    essential = item("Recurso obrigatório", quantity=1.5, essential=True, divisible=True)
    optional = item("Consumível", quantity=3, divisible=True)

    selection = select_essential_items([essential, optional], 2)
    selected = optimize_with_essentials([essential, optional], 2)

    assert selection.essenciais == (essential,)
    assert selection.recursos_otimizaveis == (optional,)
    assert [entry.nome for entry in selected] == [essential.nome, optional.nome]
    assert selected[0].quantidade_padrao == 1.5
    assert selected[1].quantidade_padrao == pytest.approx(0.5)


def test_essentials_fill_capacity_without_additional_resources():
    essential = item("Kit", 2, essential=True)
    water = item("Água", divisible=True)

    assert optimize_with_essentials([essential, water], 2) == (essential,)


def test_infeasible_essentials_are_not_removed_or_fractioned():
    essential = item("Kit", 2, essential=True)

    with pytest.raises(ValueError, match="essenciais excede"):
        optimize_with_essentials([essential], 1)
    assert essential.quantidade_padrao == 1


def test_optional_indivisible_is_not_automatically_selected():
    optional = item("Power bank", 0.25)

    assert optimize_with_essentials([optional], 5) == ()


def test_unavailable_items_are_not_selected_or_reserved():
    unavailable = item("Kit indisponível", quantity=0, essential=True)
    selection = select_essential_items([unavailable], 0)

    assert selection.essenciais == ()
    assert selection.peso_essenciais == 0
    assert selection.capacidade_restante == 0
    assert optimize_with_essentials([unavailable], 0) == ()


@pytest.mark.parametrize("capacity", [0, 5])
def test_empty_input(capacity):
    selection = select_essential_items([], capacity)

    assert selection.essenciais == ()
    assert selection.recursos_otimizaveis == ()
    assert selection.itens_opcionais == ()
    assert selection.capacidade_restante == capacity
    assert optimize_with_essentials([], capacity) == ()


@pytest.mark.parametrize("capacity", [-1, float("nan"), float("inf"), True, "5"])
def test_invalid_capacity_is_rejected(capacity):
    with pytest.raises(ValueError, match="capacidade"):
        select_essential_items([], capacity)


def test_invalid_item_is_rejected():
    with pytest.raises(ValueError, match="apenas Item"):
        select_essential_items([object()], 5)
