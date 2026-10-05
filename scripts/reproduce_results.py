"""Execute da raiz: python -m scripts.reproduce_results."""

import json
from pathlib import Path

from src.game import compare_player_with_greedy
from src.models import Item
from src.recommendation import recommend_backpack
from src.scenarios import load_scenarios, scenario_trail


def main():
    root = Path(__file__).resolve().parents[1]
    catalog = [Item(**record) for record in json.loads((root / "data/items.json").read_text())]
    # Exatamente a seleção inicial da interface: essenciais e divisíveis.
    stock = tuple(item for item in catalog if item.essencial or item.divisivel)
    for scenario in load_scenarios():
        trail = scenario_trail(scenario["trilha"])
        result = recommend_backpack(trail, stock, include_optional_equipment=True)
        print(f"\n{trail.nome}: {result.peso_total:.3f} kg | sobra {result.capacidade_restante:.3f} kg | {result.valor_total:.2f} pontos")
        for item in result.itens:
            print(f"  {item.nome}: {item.quantidade_padrao:.6f} | {item.peso_total:.6f} kg | {item.valor_base:.2f} pontos/un.")
        if scenario["id"] == "travessia":
            player = {"Água": 2, "Alimentos fracionáveis": 1, "Isotônico": 0.5, "Mistura energética": 0.3}
            comparison = compare_player_with_greedy(trail, stock, player)
            print(f"  Jogador: {comparison.score_jogador:.2f} | Greedy: {comparison.score_greedy:.2f} | Eficiência: {comparison.eficiencia_percentual:.2f}% | Peso jogador: {comparison.jogador.peso_total:.3f} kg")


if __name__ == "__main__":
    main()
