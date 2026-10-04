"""Fluxos de formulário, presets e recuperação de erros da interface."""

from pathlib import Path
import json

import pytest

from streamlit.testing.v1 import AppTest


def submit(app):
    next(button for button in app.button if "Montar" in button.label).click().run()
    assert not app.exception


def test_presets_populate_form_and_clear_previous_results():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=15).run()
    assert not app.exception
    for scenario in ("sol", "travessia", "frio", "chuva"):
        app.button(key=f"scenario_{scenario}").click().run()
        assert not app.exception
        assert not app.warning
        assert len(app.metric) == 0
        submit(app)
        assert len(app.metric) == 3
        assert app.session_state.recommendation.trilha.nome == app.text_input(key="nome").value


def test_invalid_capacity_clears_old_result_and_recovers():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=15).run()
    submit(app)
    assert len(app.metric) == 3
    app.number_input(key="capacidade").set_value(0.0)
    submit(app)
    assert len(app.error) == 1
    assert len(app.metric) == 0
    app.number_input(key="capacidade").set_value(4.0)
    submit(app)
    assert not app.error
    assert len(app.metric) == 3


def test_blank_name_is_reported_without_crashing():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=15).run()
    app.text_input(key="nome").set_value(" ")
    submit(app)
    assert len(app.error) == 1
    assert len(app.metric) == 0


def test_selection_weight_and_quantity_reach_recommendation():
    root = Path(__file__).resolve().parents[1]
    catalog_path = root / "data" / "items.json"
    original = catalog_path.read_bytes()
    catalog = json.loads(original)
    app = AppTest.from_file(root / "app.py", default_timeout=15).run()
    for index, entry in enumerate(catalog):
        app.checkbox(key=f"inventory_{index}_selected").set_value(entry["nome"] == "Água")
    app.number_input(key="inventory_0_quantity").set_value(2.5)
    app.number_input(key="inventory_0_weight").set_value(1.2)
    submit(app)

    result = app.session_state.recommendation
    assert [item.nome for item in result.itens] == ["Água"]
    assert result.itens[0].quantidade_padrao == 2.5
    assert result.itens[0].peso == 1.2
    assert result.peso_total == pytest.approx(3)
    assert catalog_path.read_bytes() == original
    app.button(key="scenario_sol").click().run()
    assert app.number_input(key="inventory_0_quantity").value == 2.5
    assert app.number_input(key="inventory_0_weight").value == 1.2


def test_optional_equipment_is_included_only_when_selected():
    root = Path(__file__).resolve().parents[1]
    catalog = json.loads((root / "data" / "items.json").read_text())
    app = AppTest.from_file(root / "app.py", default_timeout=15).run()
    index = next(index for index, entry in enumerate(catalog) if entry["nome"] == "Power bank")
    submit(app)
    assert "Power bank" not in {item.nome for item in app.session_state.recommendation.itens}
    app.checkbox(key=f"inventory_{index}_selected").set_value(True)
    submit(app)
    result = app.session_state.recommendation
    assert "Power bank" in {item.nome for item in result.itens}
    assert result.peso_total <= result.trilha.capacidade + 1e-9
    assert any("selecionado pelo usuário" in reason for reason in result.justificativas["Power bank"])


def test_custom_item_is_available_for_editing_and_recommendation():
    root = Path(__file__).resolve().parents[1]
    catalog_size = len(json.loads((root / "data" / "items.json").read_text()))
    app = AppTest.from_file(root / "app.py", default_timeout=15).run()
    app.text_input(key="custom_name").set_value("Bússola")
    app.selectbox(key="custom_category").set_value("Navegação")
    app.number_input(key="custom_weight").set_value(0.15)
    app.checkbox(key="custom_essential").set_value(True)
    next(button for button in app.button if button.label == "Adicionar item").click().run()
    assert not app.exception
    assert not app.error
    assert app.checkbox(key=f"inventory_{catalog_size}_selected").value
    submit(app)
    compass = next(item for item in app.session_state.recommendation.itens if item.nome == "Bússola")
    assert compass.peso == 0.15
    assert compass.quantidade_padrao == 1


@pytest.mark.parametrize("name,quantity", [(" ", 1.0), (" água ", 1.0), ("Bússola", 1.5)])
def test_invalid_custom_item_does_not_enter_inventory(name, quantity):
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=15).run()
    app.text_input(key="custom_name").set_value(name)
    app.number_input(key="custom_quantity").set_value(quantity)
    next(button for button in app.button if button.label == "Adicionar item").click().run()
    assert not app.exception
    assert len(app.error) == 1
    assert app.session_state.custom_items == []


def test_empty_selection_produces_empty_backpack():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=15).run()
    for checkbox in app.checkbox:
        if checkbox.key and checkbox.key.startswith("inventory_") and checkbox.key.endswith("_selected"):
            checkbox.set_value(False)
    submit(app)
    assert not app.error
    assert app.session_state.recommendation.itens == ()


def test_selected_equipment_over_capacity_clears_previous_result():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=15).run()
    submit(app)
    app.checkbox(key="inventory_8_selected").set_value(True)
    app.number_input(key="inventory_8_weight").set_value(10.0)
    submit(app)

    assert len(app.error) == 1
    assert "equipamentos selecionados" in app.error[0].value
    assert len(app.metric) == 0


def test_zero_quantity_excludes_selected_resource():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=15).run()
    app.number_input(key="inventory_0_quantity").set_value(0.0)
    submit(app)

    assert not app.error
    assert "Água" not in {item.nome for item in app.session_state.recommendation.itens}
