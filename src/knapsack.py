from collections.abc import Iterable
from dataclasses import replace
from math import isfinite

from .models import Item


def fractional_knapsack(itens: Iterable[Item], capacidade: float) -> tuple[Item, ...]:
    if (
        isinstance(capacidade, bool)
        or not isinstance(capacidade, (int, float))
        or not isfinite(capacidade)
        or capacidade < 0
    ):
        raise ValueError("capacidade deve ser um número finito e não negativo em kg.")

    recursos = list(itens)
    for item in recursos:
        if not isinstance(item, Item):
            raise ValueError("itens deve conter apenas Item.")
        if not item.divisivel:
            raise ValueError(f"Item indivisível não pode ser otimizado: {item.nome}.")

    recursos = sorted(
        (item for item in recursos if item.quantidade_padrao > 0 and item.valor_base > 0),
        key=lambda item: item.valor_base / item.peso,
        reverse=True,
    )

    selecionados: list[Item] = []
    restante = capacidade
    for item in recursos:
        if restante <= 0:
            break

        if item.peso_total <= restante:
            selecionados.append(replace(item))
            restante -= item.peso_total
        else:
            quantidade = restante / item.peso
            selecionados.append(replace(item, quantidade_padrao=quantidade))
            break

    return tuple(selecionados)
