"""Utilidade contextual por unidade, compatível com fractional_knapsack.

O catálogo original mantém valor_base. As cópias retornadas carregam nesse
campo o valor contextual, pois esse é o contrato de entrada do algoritmo.
Sempre recalcule a partir dos itens originais para não acumular fatores.
"""

from collections.abc import Iterable
from dataclasses import dataclass, replace
from math import isfinite

from .models import Item, Trail
from .trail_profile import TrailProfile, build_trail_profile


@dataclass(frozen=True)
class ItemPriority:
    item: Item
    fator: float
    valor_contextual: float

    @property
    def valor_por_peso(self) -> float:
        return self.valor_contextual / self.item.peso

    def as_knapsack_item(self) -> Item:
        """Preserva peso, quantidade e marcações; altera só a utilidade."""
        return replace(self.item, valor_base=self.valor_contextual)


def calculate_item_priority(item: Item, profile: TrailProfile) -> ItemPriority:
    factor = profile.factor_for(item.categoria)
    value = item.valor_base * factor
    if not isfinite(factor) or factor < 0 or not isfinite(value):
        raise ValueError("Fator e utilidade contextual devem ser finitos e não negativos.")
    return ItemPriority(item=item, fator=factor, valor_contextual=value)


def calculate_priorities(items: Iterable[Item], trail: Trail) -> tuple[ItemPriority, ...]:
    """Calcula prioridades sem ordenar, selecionar ou modificar os itens.

    Inclui indivisíveis para futura exibição. O chamador deve separar os
    essenciais e filtrar divisíveis antes de passar as cópias ao Knapsack.
    """
    profile = build_trail_profile(trail)
    return tuple(calculate_item_priority(item, profile) for item in items)
