"""Integra prioridades contextuais, reserva de essenciais e otimização."""

from collections.abc import Iterable

from .essential_items import select_essential_items
from .explanations import explain_item
from .knapsack import fractional_knapsack
from .models import Item, Recommendation, Trail
from .priority_engine import calculate_priorities


def recommend_backpack(trail: Trail, items: Iterable[Item]) -> Recommendation:
    """Calcula a mochila sem alterar o catálogo ou multiplicar disponibilidades.

    A capacidade é a carga total informada para o grupo; pessoas não duplicam
    os recursos disponíveis. Indivisíveis opcionais aguardam seleção explícita
    na etapa de customização e são indicados nos avisos.
    """
    priorities = calculate_priorities(items, trail)
    selection = select_essential_items(
        (priority.as_knapsack_item() for priority in priorities), trail.capacidade
    )
    optimized = fractional_knapsack(
        selection.recursos_otimizaveis, selection.capacidade_restante
    )
    selected = selection.essenciais + optimized
    warnings = []
    if selection.itens_opcionais:
        names = ", ".join(item.nome for item in selection.itens_opcionais)
        warnings.append(f"Equipamentos opcionais não incluídos automaticamente: {names}.")
    if not selected:
        warnings.append("Nenhum item disponível foi selecionado para esta mochila.")
    if trail.pessoas > 1:
        warnings.append(
            "A capacidade e as quantidades disponíveis são totais para o grupo; "
            "não foram multiplicadas pelo número de pessoas."
        )
    return Recommendation(
        trilha=trail,
        itens=selected,
        valor_total=sum(item.valor_base * item.quantidade_padrao for item in selected),
        justificativas={item.nome: explain_item(item, trail) for item in selected},
        avisos=tuple(warnings),
    )
