"""Cenários simulados para explorar prioridades e o futuro modo desafio."""

import json
from pathlib import Path

from .models import Trail, TrailConditions

SCENARIOS_PATH = Path(__file__).resolve().parents[1] / "data" / "scenarios.json"


def scenario_trail(data: dict) -> Trail:
    return Trail(
        nome=data["nome"], distancia=data["distancia"], duracao=data["duracao"],
        condicoes=TrailConditions(data["temperatura"], data["dificuldade"],
                                  data["chuva"], data["isolamento"], data["agua_disponivel"]),
        capacidade=data["capacidade"], pessoas=data["pessoas"],
    )


def load_scenarios() -> list[dict]:
    scenarios = json.loads(SCENARIOS_PATH.read_text(encoding="utf-8"))
    ids = set()
    for scenario in scenarios:
        if scenario["id"] in ids:
            raise ValueError("Os cenários devem ter identificadores únicos.")
        ids.add(scenario["id"])
        scenario_trail(scenario["trilha"])
    return scenarios
