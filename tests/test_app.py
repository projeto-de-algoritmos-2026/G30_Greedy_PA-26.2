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


def optimization_table(app):
    return next(frame.value for frame in app.dataframe if "Valor/Peso" in frame.value.columns)


def test_optimization_table_preserves_selection_order_and_contextual_values():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=15).run()
    app.button(key="scenario_travessia").click().run()
    submit(app)

    result = app.session_state.recommendation
    table = optimization_table(app)
    assert list(table.columns) == ["Item", "Valor", "Peso", "Valor/Peso", "Quantidade selecionada"]
    assert list(table["Item"]) == [item.nome for item in result.itens]
    assert list(table["Valor"]) == pytest.approx([item.valor_base for item in result.itens])
    assert list(table["Peso"]) == pytest.approx([item.peso for item in result.itens])
    assert list(table["Valor/Peso"]) == pytest.approx([item.valor_base / item.peso for item in result.itens])
    assert list(table["Quantidade selecionada"]) == pytest.approx([item.quantidade_padrao for item in result.itens])
    resources = table[[not item.essencial and item.divisivel for item in result.itens]]
    assert list(resources["Valor/Peso"]) == sorted(resources["Valor/Peso"], reverse=True)


def test_optimization_table_distinguishes_unit_weight_from_fractional_quantity():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=15).run()
    for checkbox in app.checkbox:
        if checkbox.key and checkbox.key.startswith("inventory_") and checkbox.key.endswith("_selected"):
            checkbox.set_value(checkbox.key == "inventory_0_selected")
    app.number_input(key="inventory_0_weight").set_value(2.0)
    app.number_input(key="capacidade").set_value(1.25)
    app.number_input(key="temperatura").set_value(30.0)
    app.number_input(key="duracao").set_value(7.0)
    app.checkbox(key="agua_disponivel").set_value(False)
    submit(app)

    table = optimization_table(app)
    row = table.iloc[0]
    assert row["Item"] == "Água"
    assert row["Valor"] == pytest.approx(273)
    assert row["Peso"] == 2
    assert row["Valor/Peso"] == pytest.approx(136.5)
    assert row["Quantidade selecionada"] == pytest.approx(0.625)
    assert row["Peso"] * row["Quantidade selecionada"] == pytest.approx(1.25)

    app.number_input(key="inventory_0_weight").set_value(1.0).run()
    assert optimization_table(app).equals(table)


def test_empty_backpack_has_no_optimization_table():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=15).run()
    for checkbox in app.checkbox:
        if checkbox.key and checkbox.key.startswith("inventory_") and checkbox.key.endswith("_selected"):
            checkbox.set_value(False)
    submit(app)

    assert not app.dataframe
    assert any("tabela de otimização" in message.value for message in app.info)


def compare_game(app):
    next(button for button in app.button if button.label == "Comparar com o algoritmo").click().run()
    assert not app.exception


def test_player_challenge_displays_scores_and_resets_after_new_planning():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=15).run()
    submit(app)
    app.number_input(key="game_quantity_0").set_value(1.0)
    compare_game(app)

    assert not app.error
    assert {metric.label for metric in app.metric} >= {"Score jogador", "Score greedy", "Eficiência"}
    comparison = app.session_state.game_comparison
    assert comparison.score_jogador > 0
    assert 0 < comparison.eficiencia_percentual <= 100
    table = next(frame.value for frame in app.dataframe if "Quantidade jogador" in frame.value.columns)
    assert table.loc[table["Item"] == "Água", "Quantidade jogador"].iloc[0] == 1
    submit(app)
    assert len(app.metric) == 3
    assert app.number_input(key="game_quantity_0").value == 0


def test_invalid_player_backpack_clears_previous_comparison():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=15).run()
    app.button(key="scenario_sol").click().run()
    submit(app)
    compare_game(app)
    assert len(app.metric) == 6
    for control in app.number_input:
        if control.key and control.key.startswith("game_quantity_"):
            control.set_value(control.max)
    compare_game(app)

    assert len(app.error) == 1
    assert "Mochila do jogador inválida" in app.error[0].value
    assert len(app.metric) == 3
