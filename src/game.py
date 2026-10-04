"""Comparação de mochilas com o mesmo estoque e os mesmos itens reservados."""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, replace
from math import isfinite

from .models import Item, Recommendation, Trail
from .priority_engine import calculate_priorities
from .recommendation import recommend_backpack


@dataclass(frozen=True)
class GameComparison:
    jogador: Recommendation
    greedy: Recommendation
    eficiencia_percentual: float

    @property
    def score_jogador(self) -> float:
        return self.jogador.valor_total

    @property
    def score_greedy(self) -> float:
        return self.greedy.valor_total


def compare_player_with_greedy(
    trail: Trail, items: Iterable[Item], player_quantities: Mapping[str, float]
) -> GameComparison:
    """Pontua quantidades manuais usando a utilidade contextual por unidade.

    Essenciais e equipamentos indivisíveis do estoque selecionado são fixos
    para os dois participantes. O jogador escolhe somente recursos divisíveis
    não essenciais; recursos omitidos recebem quantidade zero. Não é permitido
    exceder o estoque ou a capacidade. Os itens originais não são alterados.

    A eficiência usa a pontuação total, incluindo os itens fixos. Se ambas as
    pontuações forem zero, a eficiência é 100% (empate sem utilidade disponível).
    """
    available = tuple(items)
    if not all(isinstance(item, Item) for item in available):
        raise ValueError("items deve conter apenas Item.")
    names = [item.nome.casefold() for item in available]
    if len(set(names)) != len(names):
        raise ValueError("Os itens do desafio devem ter nomes únicos.")
    resources = {
        item.nome: item for item in available if item.divisivel and not item.essencial
    }
    for name, quantity in player_quantities.items():
        if name not in resources:
            raise ValueError(f"Recurso não disponível para escolha no desafio: {name}.")
        if (
            isinstance(quantity, bool)
            or not isinstance(quantity, (int, float))
            or not isfinite(quantity)
            or quantity < 0
            or quantity > resources[name].quantidade_padrao
        ):
            raise ValueError(f"Quantidade inválida ou superior ao estoque para {name}.")

    greedy = recommend_backpack(trail, available, include_optional_equipment=True)
    fixed = tuple(item for item in greedy.itens if item.essencial or not item.divisivel)
    chosen = []
    for priority in calculate_priorities(available, trail):
        if priority.item.nome not in resources:
            continue
        quantity = player_quantities.get(priority.item.nome, 0)
        if quantity > 0:
            chosen.append(replace(priority.as_knapsack_item(), quantidade_padrao=quantity))
    selected = fixed + tuple(chosen)
    player = Recommendation(
        trilha=trail,
        itens=selected,
        valor_total=sum(item.valor_base * item.quantidade_padrao for item in selected),
    )
    efficiency = min(100.0, player.valor_total / greedy.valor_total * 100) if greedy.valor_total else 100.0
    return GameComparison(player, greedy, efficiency)
