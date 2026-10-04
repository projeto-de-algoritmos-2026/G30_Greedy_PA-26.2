"""Fatores heurísticos de necessidade; não representam avaliação médica de risco.

Uma trilha é longa a partir de 6 h OU 15 km (sem contar duas vezes).
Calor começa em 30 °C e frio em 10 °C ou menos. Fatores independentes
se multiplicam; os níveis baixo/médio/alto usam fatores crescentes.
"""

from dataclasses import dataclass

from .models import Category, Level, Trail


@dataclass(frozen=True)
class TrailProfile:
    hidratacao: float = 1.0
    alimentacao: float = 1.0
    seguranca: float = 1.0
    navegacao: float = 1.0
    protecao_climatica: float = 1.0
    energia: float = 1.0

    def factor_for(self, category: Category) -> float:
        """Categorias sem regra contextual mantêm o valor base."""
        fields = {
            Category.HIDRATACAO: self.hidratacao,
            Category.ALIMENTACAO: self.alimentacao,
            Category.SEGURANCA: self.seguranca,
            Category.NAVEGACAO: self.navegacao,
            Category.PROTECAO_CLIMATICA: self.protecao_climatica,
            Category.ENERGIA: self.energia,
        }
        return fields.get(Category(category), 1.0)


def build_trail_profile(trail: Trail) -> TrailProfile:
    """Converte condições em multiplicadores por categoria.

    Capacidade e pessoas não alteram a utilidade por unidade. Quantidades e
    reserva de essenciais serão tratadas pelo serviço de recomendação.
    """
    conditions = trail.condicoes
    long_trail = trail.duracao >= 6 or trail.distancia >= 15
    hydration = 1.3 if long_trail else 1.0
    food = 1.3 if long_trail else 1.0
    protection = 1.0
    if conditions.temperatura >= 30:
        hydration *= 1.4
        protection *= 1.2
    elif conditions.temperatura <= 10:
        protection *= 1.3
    if not conditions.agua_disponivel:
        hydration *= 1.5

    difficulty = {Level.BAIXO: 1.0, Level.MEDIO: 1.15, Level.ALTO: 1.3}
    isolation = {Level.BAIXO: 1.0, Level.MEDIO: 1.2, Level.ALTO: 1.5}
    rain = {Level.BAIXO: 1.0, Level.MEDIO: 1.25, Level.ALTO: 1.5}
    difficulty_factor = difficulty[conditions.dificuldade]
    isolation_factor = isolation[conditions.isolamento]
    return TrailProfile(
        hidratacao=hydration,
        alimentacao=food * difficulty_factor,
        seguranca=difficulty_factor * isolation_factor,
        navegacao=isolation_factor,
        protecao_climatica=protection * rain[conditions.chuva],
        energia=isolation_factor,
    )
