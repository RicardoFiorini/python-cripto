"""
Definição da Criptomoeda de Governança: FioCoin (FIO).
Este token serve como a moeda principal do ecossistema e token de governança.
"""
from typing import Final
from contratos import TokenContract

# Configurações Imutáveis (Constants)
TOKEN_NAME: Final[str] = "FioCoin"
TOKEN_SYMBOL: Final[str] = "FIO"
INITIAL_SUPPLY: Final[int] = 1_000_000  # 1 Milhão
GENESIS_ADDRESS: Final[str] = "0x111"

class FioCoin(TokenContract):
    """
    Implementação específica do FioCoin.
    Herda de TokenContract para garantir compatibilidade com a EVM (Blockchain).
    """
    def __init__(self):
        # Inicializa o contrato pai com as configurações específicas desta moeda
        super().__init__(
            address=GENESIS_ADDRESS,
            name=TOKEN_NAME,
            symbol=TOKEN_SYMBOL,
            total_supply=INITIAL_SUPPLY
        )

    def get_description(self) -> str:
        return "Token nativo para governança e taxas da rede."

# Instância Singleton (Padrão para importação no main.py)
# Isso permite importar 'moeda' como se fosse um módulo de configuração
moeda = FioCoin()