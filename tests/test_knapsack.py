import pytest

from src.knapsack import fractional_knapsack
from src.models import Category, Item


def resource(name, weight, value, quantity=1):
    return Item(
        nome=name,
        categoria=Category.ALIMENTACAO,
        peso=weight,
        valor_base=value,
        divisivel=True,
        essencial=False,
        quantidade_padrao=quantity,
    )


@pytest.mark.parametrize("capacity", [0, 10])
def test_empty_backpack(capacity):
    assert fractional_knapsack([], capacity) == ()


def test_zero_capacity_selects_nothing():
    items = [resource("Alimentos", 1, 80, 2)]

    assert fractional_knapsack(items, 0) == ()
    assert items[0].quantidade_padrao == 2


@pytest.mark.parametrize("capacity", [4, 10])
def test_all_items_fit(capacity):
    items = [
        resource("Alimentos", 2, 80, 1.5),
        resource("Mistura energética", 0.5, 30, 2),
    ]

    selected = fractional_knapsack(items, capacity)

    assert {item.nome: item.quantidade_padrao for item in selected} == {
        "Alimentos": 1.5,
        "Mistura energética": 2,
    }
    assert sum(item.peso_total for item in selected) == pytest.approx(4)
    assert sum(item.valor_base * item.quantidade_padrao for item in selected) == pytest.approx(180)


def test_item_is_partially_selected_without_changing_input():
    items = [
        resource("Alimentos", 2, 100, 3),
        resource("Mistura energética", 1, 20, 1),
    ]

    selected = fractional_knapsack(items, 2.5)

    assert len(selected) == 1
    assert selected[0].nome == "Alimentos"
    assert selected[0].quantidade_padrao == pytest.approx(1.25)
    assert selected[0].peso_total == pytest.approx(2.5)
    assert selected[0].valor_base * selected[0].quantidade_padrao == pytest.approx(125)
    assert selected[0] is not items[0]
    assert items[0].quantidade_padrao == 3
    assert items[1].quantidade_padrao == 1


def test_selection_uses_value_per_weight_order():
    # Razões 8, 4 e 10: nem o maior valor absoluto nem o menor peso vem primeiro.
    items = [
        resource("Maior valor absoluto", 10, 80),
        resource("Mais leve", 1, 4),
        resource("Maior utilidade por kg", 2, 20),
    ]

    selected = fractional_knapsack(items, 3)

    assert [item.nome for item in selected] == [
        "Maior utilidade por kg",
        "Maior valor absoluto",
    ]
    assert [item.quantidade_padrao for item in selected] == pytest.approx([1, 0.1])
    assert sum(item.peso_total for item in selected) == pytest.approx(3)
    assert sum(item.valor_base * item.quantidade_padrao for item in selected) == pytest.approx(28)


def test_known_optimal_result():
    # Caso clássico: 10 kg/60 pontos, 20 kg/100 pontos e 30 kg/120 pontos.
    # Em 50 kg, o ótimo é 60 + 100 + (2/3 × 120) = 240 pontos.
    items = [
        resource("C", 30, 120),
        resource("A", 10, 60),
        resource("B", 20, 100),
    ]

    selected = fractional_knapsack(items, 50)

    assert [item.nome for item in selected] == ["A", "B", "C"]
    assert [item.quantidade_padrao for item in selected] == pytest.approx([1, 1, 2 / 3])
    assert sum(item.peso_total for item in selected) == pytest.approx(50)
    assert sum(item.valor_base * item.quantidade_padrao for item in selected) == pytest.approx(240)
