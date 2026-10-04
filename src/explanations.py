"""Justificativas das regras contextuais e da seleção de cada item."""

from .models import Category, Item, Level, Trail


def explain_item(item: Item, trail: Trail) -> list[str]:
    """Explica somente condições que aumentam o valor da categoria do item.

    Os limites seguem build_trail_profile. Os motivos descrevem a pontuação
    heurística, sem atribuir uma escala de prioridade ou garantir suficiência.
    """
    category = item.categoria
    conditions = trail.condicoes
    reasons = []
    if conditions.temperatura >= 30 and category in (
        Category.HIDRATACAO, Category.PROTECAO_CLIMATICA
    ):
        reasons.append("Temperatura alta (30 °C ou mais).")
    elif conditions.temperatura <= 10 and category == Category.PROTECAO_CLIMATICA:
        reasons.append("Temperatura baixa (10 °C ou menos).")

    if category in (Category.HIDRATACAO, Category.ALIMENTACAO):
        if trail.duracao >= 6:
            reasons.append("Longa duração da trilha (6 horas ou mais).")
        elif trail.distancia >= 15:
            reasons.append("Longa distância da trilha (15 km ou mais).")
    if category == Category.HIDRATACAO and not conditions.agua_disponivel:
        reasons.append("Sem pontos de água disponíveis no percurso.")

    labels = {Level.MEDIO: "médio", Level.ALTO: "alto"}
    if category in (Category.ALIMENTACAO, Category.SEGURANCA) and conditions.dificuldade != Level.BAIXO:
        reasons.append(f"Dificuldade da trilha em nível {labels[conditions.dificuldade]}.")
    if category in (Category.SEGURANCA, Category.NAVEGACAO, Category.ENERGIA) and conditions.isolamento != Level.BAIXO:
        reasons.append(f"Isolamento em nível {labels[conditions.isolamento]}.")
    if category == Category.PROTECAO_CLIMATICA and conditions.chuva != Level.BAIXO:
        reasons.append(f"Chuva em nível {labels[conditions.chuva]}.")

    if not reasons:
        reasons.append("As condições informadas mantêm a utilidade base desta categoria.")
    if item.essencial:
        reasons.append("Item marcado como essencial: peso reservado antes da otimização.")
    elif not item.divisivel:
        reasons.append("Equipamento selecionado pelo usuário: peso reservado antes da otimização.")
    else:
        reasons.append("Recurso selecionado pela utilidade por kg na capacidade restante.")
    return reasons
