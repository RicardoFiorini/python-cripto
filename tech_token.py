"""
Definição do TechToken (TCH).
Token utilitário focado em microtransações para desenvolvedores.
"""
from typing import Final
from contratos import TokenContract

# Configurações do Token
TOKEN_NAME: Final[str] = "TechToken"
TOKEN_SYMBOL: Final[str] = "TCH"
INITIAL_SUPPLY: Final[int] = 50_000 
CONTRACT_ADDRESS: Final[str] = "0x222"

class TechToken(TokenContract):
    """
    Token de alta circulação para recompensas de devs.
    """
    def __init__(self):
        super().__init__(
            address=CONTRACT_ADDRESS,
            name=TOKEN_NAME,
            symbol=TOKEN_SYMBOL,
            total_supply=INITIAL_SUPPLY
        )
        
    # No futuro, aqui poderiam entrar métodos exclusivos, 
    # como 'burn()' (queimar tokens) ou 'mint()' (criar novos).

# Instância exportada para uso na Blockchain
moeda = TechToken()