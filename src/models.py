"""Contratos de domínio. Pesos em kg, distância em km e duração em horas.

Item.peso e Item.valor_base referem-se a uma unidade do recurso. A quantidade
disponível pode ser fracionária somente para itens divisíveis. As condições
climáticas e os níveis são entradas; o cálculo de prioridade pertence ao motor.
"""

from dataclasses import dataclass, field
from enum import Enum
from math import isfinite


class Level(str, Enum):
    BAIXO = "baixo"
    MEDIO = "medio"
    ALTO = "alto"


class Category(str, Enum):
    HIDRATACAO = "Hidratação"
    ALIMENTACAO = "Alimentação"
    SEGURANCA = "Segurança"
    NAVEGACAO = "Navegação"
    PROTECAO_CLIMATICA = "Proteção climática"
    ENERGIA = "Energia"
    HIGIENE = "Higiene"
    OUTROS = "Outros"


def _number(name: str, value: float, *, positive: bool = False) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} deve ser numérico.")
    if not isfinite(value) or value < 0 or (positive and value == 0):
        raise ValueError(f"{name} deve ser finito e {'positivo' if positive else 'não negativo'}.")


@dataclass(frozen=True)
class TrailConditions:
    temperatura: float
    dificuldade: Level
    chuva: Level
    isolamento: Level
    agua_disponivel: bool

    def __post_init__(self) -> None:
        if isinstance(self.temperatura, bool) or not isinstance(self.temperatura, (int, float)) or not isfinite(self.temperatura):
            raise ValueError("temperatura deve ser um número finito em °C.")
        for name in ("dificuldade", "chuva", "isolamento"):
            object.__setattr__(self, name, Level(getattr(self, name)))
        if not isinstance(self.agua_disponivel, bool):
            raise ValueError("agua_disponivel deve ser booleano.")


@dataclass(frozen=True)
class Trail:
    nome: str
    distancia: float
    duracao: float
    condicoes: TrailConditions
    capacidade: float
    pessoas: int = 1

    def __post_init__(self) -> None:
        if not isinstance(self.nome, str) or not self.nome.strip():
            raise ValueError("nome da trilha não pode ser vazio.")
        for name in ("distancia", "duracao", "capacidade"):
            _number(name, getattr(self, name))
        if isinstance(self.pessoas, bool) or not isinstance(self.pessoas, int) or self.pessoas < 1:
            raise ValueError("pessoas deve ser um inteiro positivo.")
        if not isinstance(self.condicoes, TrailConditions):
            raise ValueError("condicoes deve ser TrailConditions.")


@dataclass(frozen=True)
class Item:
    nome: str
    categoria: Category
    peso: float
    valor_base: float
    divisivel: bool
    essencial: bool
    quantidade_padrao: float = 1

    def __post_init__(self) -> None:
        if not isinstance(self.nome, str) or not self.nome.strip():
            raise ValueError("nome do item não pode ser vazio.")
        object.__setattr__(self, "categoria", Category(self.categoria))
        _number("peso", self.peso, positive=True)
        _number("valor_base", self.valor_base)
        _number("quantidade_padrao", self.quantidade_padrao)
        if not isinstance(self.divisivel, bool) or not isinstance(self.essencial, bool):
            raise ValueError("divisivel e essencial devem ser booleanos.")
        if not self.divisivel and not float(self.quantidade_padrao).is_integer():
            raise ValueError("Itens indivisíveis exigem quantidade inteira.")

    @property
    def peso_total(self) -> float:
        return self.peso * self.quantidade_padrao


@dataclass(frozen=True)
class Recommendation:
    """Resultado: itens usam quantidade_padrao como quantidade selecionada.

    Justificativas e avisos serão preenchidos pelo serviço de recomendação.
    O modelo não executa seleção nem altera a capacidade da trilha.
    """

    trilha: Trail
    itens: tuple[Item, ...] = ()
    valor_total: float = 0
    justificativas: dict[str, list[str]] = field(default_factory=dict)
    avisos: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.trilha, Trail):
            raise ValueError("trilha deve ser Trail.")
        object.__setattr__(self, "itens", tuple(self.itens))
        if not all(isinstance(item, Item) for item in self.itens):
            raise ValueError("itens deve conter apenas Item.")
        _number("valor_total", self.valor_total)
        if self.peso_total > self.trilha.capacidade + 1e-9:
            raise ValueError("Peso recomendado excede a capacidade da mochila.")

    @property
    def peso_total(self) -> float:
        return sum(item.peso_total for item in self.itens)

    @property
    def capacidade_restante(self) -> float:
        return max(0.0, self.trilha.capacidade - self.peso_total)
