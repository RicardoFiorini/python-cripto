# Python Cripto
Uma simulação robusta de **Blockchain** e ecossistema de criptoativos desenvolvida em Python.[1] Este projeto explora a fundo a estrutura de blocos, segurança por hashing e a lógica de contratos digitais.
## Principais Componentes

- **Blockchain Core:** Implementação da lógica de encadeamento e integridade dos dados.
- **Ecossistema de Tokens:** Módulos específicos para moedas como *FioCoin*, *GoldPy* e *TechToken*.
- **Contratos Inteligentes:** Sistema para definição e execução de regras de negócio entre carteiras.
  
## Estrutura de Arquivos
| Componente | Função |
| --- | --- |
| blockchain.py | Motor principal da rede e validação de blocos. |
| contratos.py | Lógica para automação de transações. |
| tokens/*.py | Implementações individuais de ativos digitais. |
## Status do Projeto
- [x] Estrutura de blocos e hashing SHA-256
- [x] Criação de tokens personalizados
- [x] Lógica de persistência básica
- [ ] Implementação de Proof of Work (Mineração)
## Exemplo de Uso
```python

from blockchain import Blockchain[1]
Inicializando a rede
minha_cripto = Blockchain()
minha_cripto.adicionar_bloco(transacoes=["Ricardo -> Joao: 10 FioCoin"])

```[1]
> [!TIP]
> Este projeto é uma excelente base para entender como os dados são imutabilizados em uma rede distribuída antes de avançar para redes reais como Ethereum ou Bitcoin.
