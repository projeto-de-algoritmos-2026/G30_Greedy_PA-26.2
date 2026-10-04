from collections.abc import Iterable
from dataclasses import dataclass
from math import isfinite

from .knapsack import fractional_knapsack
from .models import Item


@dataclass(frozen=True)
class EssentialSelection:
    essenciais: tuple[Item, ...]
    recursos_otimizaveis: tuple[Item, ...]
    itens_opcionais: tuple[Item, ...]
    peso_essenciais: float
    capacidade_restante: float


def select_essential_items(items: Iterable[Item], capacidade: float) -> EssentialSelection:
    """Reserva a quantidade disponível de cada essencial sem alterar os itens.

    A entrada deve conter somente os itens disponíveis escolhidos pelo usuário.
    Essencialidade tem precedência sobre divisibilidade: um essencial divisível
    também é reservado integralmente e não entra novamente no Knapsack.
    Indivisíveis não essenciais ficam em ``itens_opcionais`` para seleção futura;
    não são incluídos automaticamente nem enviados ao algoritmo fracionário.
    Quantidades zero representam itens indisponíveis e são ignoradas.
    """
    if (
        isinstance(capacidade, bool)
        or not isinstance(capacidade, (int, float))
        or not isfinite(capacidade)
        or capacidade < 0
    ):
        raise ValueError("capacidade deve ser um número finito e não negativo em kg.")

    essenciais: list[Item] = []
    recursos: list[Item] = []
    opcionais: list[Item] = []
    for item in items:
        if not isinstance(item, Item):
            raise ValueError("items deve conter apenas Item.")
        if item.quantidade_padrao == 0:
            continue
        if item.essencial:
            essenciais.append(item)
        elif item.divisivel:
            recursos.append(item)
        else:
            opcionais.append(item)

    peso_essenciais = sum(item.peso_total for item in essenciais)
    if peso_essenciais > capacidade:
        raise ValueError("Peso dos itens essenciais excede a capacidade da mochila.")

    return EssentialSelection(
        essenciais=tuple(essenciais),
        recursos_otimizaveis=tuple(recursos),
        itens_opcionais=tuple(opcionais),
        peso_essenciais=peso_essenciais,
        capacidade_restante=capacidade - peso_essenciais,
    )


def optimize_with_essentials(items: Iterable[Item], capacidade: float) -> tuple[Item, ...]:
    """Reúne essenciais e recursos otimizados usando somente o peso restante.

    Usa os valores de utilidade fornecidos nos itens, sem calcular prioridades
    da trilha. Essenciais inviáveis geram erro, sem remoção ou fracionamento.
    """
    selection = select_essential_items(items, capacidade)
    optimized = fractional_knapsack(
        selection.recursos_otimizaveis, selection.capacidade_restante
    )
    return selection.essenciais + optimized
