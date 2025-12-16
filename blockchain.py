"""
Core Engine da Blockchain.
Responsável pelo consenso (Proof of Work), gerenciamento de blocos
e orquestração da execução de contratos inteligentes (EVM simplificada).
"""
import hashlib
import json
import time
import logging
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple, Type

# Configuração de Logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("BlockchainEngine")

# ==========================================
# Estruturas de Dados (Data Transfer Objects)
# ==========================================

@dataclass(frozen=True)
class Transaction:
    """Representa uma intenção de execução imutável."""
    sender: str
    contract_address: str
    function: str
    params: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class Block:
    """Estrutura do Bloco contendo metadados e lote de transações."""
    index: int
    transactions: List[Dict[str, Any]]
    timestamp: float
    previous_hash: str
    nonce: int = 0
    hash: str = ""

    def compute_hash(self) -> str:
        """Gera o hash SHA-256 do bloco garantindo a ordenação das chaves JSON."""
        block_dict = asdict(self)
        del block_dict['hash'] # O hash não faz parte do cálculo dele mesmo
        
        block_string = json.dumps(block_dict, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

# ==========================================
# A Blockchain (The State Machine)
# ==========================================

class PythonBlockchain:
    def __init__(self, difficulty: int = 2):
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.contracts: Dict[str, Any] = {} # Registro de contratos (Address -> Instance)
        self.difficulty = difficulty # Quantos zeros o hash precisa ter no início
        self._create_genesis_block()

    def _create_genesis_block(self) -> None:
        """Cria o bloco zero da cadeia."""
        genesis_block = Block(
            index=0,
            transactions=[],
            timestamp=time.time(),
            previous_hash="0" * 64
        )
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)
        logger.info("Blockchain inicializada. Genesis Block criado.")

    @property
    def last_block(self) -> Block:
        return self.chain[-1]

    def deploy_contract(self, contract: Any) -> None:
        """Registra um contrato inteligente na rede."""
        if contract.address in self.contracts:
            logger.warning(f"Tentativa de sobrescrever contrato no endereço {contract.address}")
            return
        
        self.contracts[contract.address] = contract
        logger.info(f"Contrato Implantado: {contract.state.get('name', 'Unknown')} [{contract.address}]")

    def add_transaction(self, sender: str, contract_address: str, function: str, **params) -> int:
        """Adiciona uma transação à Mempool (fila de espera)."""
        tx = Transaction(
            sender=sender,
            contract_address=contract_address,
            function=function,
            params=params
        )
        
        self.pending_transactions.append(tx)
        return self.last_block.index + 1

    def is_chain_valid(self) -> bool:
        """Auditoria: Verifica se a integridade da blockchain está preservada."""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash != current.compute_hash():
                logger.error(f"Hash inválido no bloco {current.index}")
                return False

            if current.previous_hash != previous.hash:
                logger.error(f"Quebra de corrente entre {previous.index} e {current.index}")
                return False
        
        return True

    def _execute_transactions(self, transactions: List[Transaction]) -> List[str]:
        """
        Engine de Execução (EVM).
        Processa as transações e altera o estado dos contratos.
        """
        execution_logs = []
        
        for tx in transactions:
            contract = self.contracts.get(tx.contract_address)
            
            if not contract:
                error_msg = f"Falha: Contrato {tx.contract_address} não encontrado."
                execution_logs.append(error_msg)
                logger.error(error_msg)
                continue

            # Injeção de dependência segura: Sender entra como kwargs
            call_params = tx.params.copy()
            call_params['sender'] = tx.sender
            
            try:
                # Executa o contrato
                success, result = contract.execute(tx.function, **call_params)
                status = "SUCESSO" if success else "REVERTIDO"
                log_entry = f"Tx[{tx.function}] {status}: {result}"
                execution_logs.append(log_entry)
                
            except Exception as e:
                # Catch-all para evitar crash da blockchain por erro em contrato
                error_msg = f"CRITICAL ERROR no contrato {tx.contract_address}: {str(e)}"
                execution_logs.append(error_msg)
                logger.critical(error_msg)

        return execution_logs

    def mine(self) -> Tuple[Optional[Block], List[str]]:
        """
        Processo de Mineração (Consenso + Execução).
        1. Executa as transações (altera o estado).
        2. Encontra o Proof of Work.
        3. Sela o bloco.
        """
        if not self.pending_transactions:
            logger.info("Nenhuma transação pendente para minerar.")
            return None, []

        logger.info(f"Iniciando mineração de {len(self.pending_transactions)} transações...")

        # 1. Execução (State Transition)
        # Convertemos Transações (Objetos) para Dicts apenas para salvar no JSON do bloco
        tx_data_for_block = [tx.to_dict() for tx in self.pending_transactions]
        execution_logs = self._execute_transactions(self.pending_transactions)

        # 2. Construção do Bloco
        new_block = Block(
            index=self.last_block.index + 1,
            transactions=tx_data_for_block,
            timestamp=time.time(),
            previous_hash=self.last_block.hash
        )

        # 3. Proof of Work (Consenso)
        target = '0' * self.difficulty
        start_time = time.time()
        
        while not new_block.hash.startswith(target):
            new_block.nonce += 1
            new_block.hash = new_block.compute_hash()

        elapsed_time = time.time() - start_time
        logger.info(f"Bloco #{new_block.index} minerado em {elapsed_time:.4f}s. Hash: {new_block.hash}")

        # 4. Finalização
        self.chain.append(new_block)
        self.pending_transactions = [] # Limpa a mempool
        
        return new_block, execution_logs