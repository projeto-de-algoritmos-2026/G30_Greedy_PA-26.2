"""Os cenários precisam carregar e produzir mochilas válidas com o catálogo."""

import json
from pathlib import Path

import pytest

from src.models import Item
from src.recommendation import recommend_backpack
from src.scenarios import load_scenarios, scenario_trail


@pytest.mark.parametrize("scenario", load_scenarios(), ids=lambda s: s["id"])
def test_scenario_produces_valid_backpack(scenario):
    path = Path(__file__).resolve().parents[1] / "data" / "items.json"
    items = tuple(Item(**entry) for entry in json.loads(path.read_text()))
    trail = scenario_trail(scenario["trilha"])
    result = recommend_backpack(trail, items)
    assert 0 < result.peso_total <= trail.capacidade + 1e-9
    assert {i.nome for i in result.itens if i.essencial} == {i.nome for i in items if i.essencial}
    assert result.valor_total > 0
    for selected in result.itens:
        original = next(i for i in items if i.nome == selected.nome)
        assert selected.quantidade_padrao <= original.quantidade_padrao
