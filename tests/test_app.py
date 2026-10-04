"""Fluxos de formulário, presets e recuperação de erros da interface."""

from pathlib import Path

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
