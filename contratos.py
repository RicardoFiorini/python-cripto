"""
Core Logic para Contratos Inteligentes.
Este módulo define a interface base e implementações padrão (como ERC20)
utilizando práticas modernas de Python: Type Hinting, Tratamento de Exceções e Design Patterns.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional, Final

# ==========================================
# Type Aliases (Para legibilidade do código)
# ==========================================
Address = str
Amount = int
ContractResponse = Tuple[bool, str] # (Sucesso, Mensagem/Dados)

# ==========================================
# Exceções Customizadas (Error Handling)
# ==========================================
class ContractError(Exception):
    """Classe base para erros de contrato."""
    pass

class InsufficientFundsError(ContractError):
    """Lançado quando o remetente não tem saldo suficiente."""
    pass

class InvalidAmountError(ContractError):
    """Lançado quando o valor da transação é inválido (ex: negativo)."""
    pass

# ==========================================
# Interface Abstrata (Base Contract)
# ==========================================
class SmartContract(ABC):
    """
    Interface base para todos os contratos inteligentes na rede.
    Define o padrão que a Blockchain espera encontrar.
    """
    def __init__(self, address: Address) -> None:
        self.address: Final[Address] = address
        self.state: Dict[str, Any] = {}
        self._events: list = [] # Log interno de eventos (Event Sourcing simplificado)

    @abstractmethod
    def execute(self, function_name: str, **kwargs: Any) -> ContractResponse:
        """
        Método 'Gateway'. A Blockchain chama este método, que atua como um roteador
        para as funções internas do contrato.
        """
        pass

    def _emit_event(self, event_name: str, data: Dict[str, Any]) -> None:
        """Registra um evento interno (similar aos 'Events' do Solidity)."""
        log = f"[{event_name}] {data}"
        self._events.append(log)

# ==========================================
# Implementação Padrão de Token (ERC20 Style)
# ==========================================
class TokenContract(SmartContract):
    """
    Implementação robusta de um token fungível.
    Gerencia saldos, transferências e validações de integridade.
    """
    def __init__(self, address: Address, name: str, symbol: str, total_supply: Amount) -> None:
        super().__init__(address)
        
        # Inicialização do Estado (State Initialization)
        self.state = {
            "name": name,
            "symbol": symbol,
            "total_supply": total_supply,
            "balances": {
                "system_genesis": total_supply
            }
        }

    def balance_of(self, owner: Address) -> Amount:
        """Retorna o saldo de um endereço específico."""
        return self.state["balances"].get(owner, 0)

    def _validate_transfer(self, sender: Address, amount: Amount) -> None:
        """
        Validação lógica privada.
        Lança exceções se a transferência for inválida.
        """
        if amount <= 0:
            raise InvalidAmountError(f"O valor da transferência deve ser positivo. Recebido: {amount}")
        
        current_balance = self.balance_of(sender)
        if current_balance < amount:
            raise InsufficientFundsError(
                f"Saldo insuficiente. Requerido: {amount}, Disponível: {current_balance}"
            )

    def transfer(self, sender: Address, recipient: Address, amount: Amount) -> ContractResponse:
        """
        Executa a transferência de ativos entre dois endereços.
        """
        try:
            # 1. Validação (Fail Fast)
            self._validate_transfer(sender, amount)

            # 2. Execução (State Mutation)
            # Inicializa o saldo do recipient se não existir
            if recipient not in self.state["balances"]:
                self.state["balances"][recipient] = 0

            self.state["balances"][sender] -= amount
            self.state["balances"][recipient] += amount

            # 3. Emissão de Evento
            self._emit_event("Transfer", {
                "from": sender,
                "to": recipient,
                "amount": amount,
                "token": self.state["symbol"]
            })

            return True, f"Transferência de {amount} {self.state['symbol']} realizada com sucesso."

        except ContractError as e:
            # Captura erros de lógica de negócio e retorna falha controlada
            return False, str(e)
        except Exception as e:
            # Captura erros inesperados (segurança)
            return False, f"Erro crítico no contrato: {str(e)}"

    def execute(self, function_name: str, **kwargs: Any) -> ContractResponse:
        """
        Roteador de chamadas da Virtual Machine.
        """
        # Mapeamento de funções (Pattern Matching simulado)
        if function_name == "transfer":
            # Extração segura de parâmetros
            sender = kwargs.get('sender')
            recipient = kwargs.get('recipient')
            amount = kwargs.get('amount')
            
            # Verificação básica de parâmetros obrigatórios
            if not all([sender, recipient, amount is not None]):
                return False, "Parâmetros inválidos para 'transfer'"
                
            return self.transfer(sender, recipient, int(amount))

        elif function_name == "balance_of":
            owner = kwargs.get('owner')
            if not owner:
                return False, "Parâmetro 'owner' necessário"
            
            balance = self.balance_of(owner)
            return True, f"Saldo: {balance} {self.state['symbol']}"

        return False, f"Função '{function_name}' não encontrada no contrato."