"""
Definição do GoldPy (GLD).
Token lastreado sinteticamente, com baixa oferta para simular escassez digital.
"""
from typing import Final
from contratos import TokenContract

# Configurações de Escassez
TOKEN_NAME: Final[str] = "GoldPy"
TOKEN_SYMBOL: Final[str] = "GLD"
# Apenas 100 unidades, simulando "ouro digital"
INITIAL_SUPPLY: Final[int] = 100 
VAULT_ADDRESS: Final[str] = "0x333"

class GoldPy(TokenContract):
    """
    Token que representa reserva de valor.
    """
    def __init__(self):
        super().__init__(
            address=VAULT_ADDRESS,
            name=TOKEN_NAME,
            symbol=TOKEN_SYMBOL,
            total_supply=INITIAL_SUPPLY
        )

# Instância exportada
moeda = GoldPy()