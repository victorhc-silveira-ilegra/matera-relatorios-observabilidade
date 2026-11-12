# Regra de Engenharia: Qualidade, Testes e CI/CD

Esta regra padroniza as praticas de desenvolvimento orientado a testes (TDD), analises estaticas, convencoes de codigo e matriz de automacao.

---

## 1. Test-Driven Development e Cobertura 100%

1. **Metodologia TDD**:
   - Para alteracoes em regras de status (`status.py`), formatadores (`formatter.py`) ou calculos de tempo (`time_window.py`), escreva primeiro os casos de teste que reproduzem o cenario desejado.
   - Aplique as mudancas no dominio ate a suite passar com 100% de cobertura.
2. **Cobertura Estrita de 100% com Branch Coverage**:
   - Todas as camadas em `app/` exigem **100% de cobertura de linhas e ramos** (`--cov-branch --cov-fail-under=100`).
   - Nenhum desvio condicional (`if/else`, `try/except`) pode ser adicionado sem teste unitario correspondente.
3. **Isolamento de Testes**:
   - A suite de testes unitarios nunca deve depender de configuracoes reais ou conectividade com a rede de producao/VPN.
   - Adaptadores externos em testes devem utilizar mocks deterministas baseados em `unittest.mock` ou `httpx.MockTransport`.

---

## 2. A Matriz de 5 Estagios

A validacao local e de CI executa estritamente os 5 estagios abaixo na ordem exata:

```text
1. Lint      -> Verificacao de estilo (Ruff) e tipos estritos (Mypy --strict)
2. Security  -> Varredura de vulnerabilidades (Bandit)
3. Test      -> Suite automatizada com meta de 100% de cobertura de branches
4. Validate  -> Validacao de estrutura de arquivos, presenca de harness e limite de 300 linhas
5. Build     -> Compilacao e empacotamento de distribuicao wheel
```

- **Orquestrador Central**: O script `scripts/quality_gate.py` centraliza a execucao desses 5 estagios e pode ser invocado via `make quality`.

---

## 3. Padrao de Estilo e Nomenclatura

- **Linter & Formatador**: `Ruff` com limite de 120 caracteres por linha e regras modernas de tipagem.
- **Tipagem Estrita**: `mypy --strict` em todas as camadas (`app/` e `tests/`).
- **Zero Comentarios**: O codigo-fonte Python nao deve conter comentarios nem docstrings nao essenciais. O codigo expressa suas intencoes por meio de tipagem estrita e nomes semanticos.
- **Tamanho Maximo de Arquivos**: Maximo de 300 linhas de codigo por arquivo em `app/`.

---

## 4. Conventional Commits

- Todas as mensagens de commit devem seguir rigorosamente a especificacao Conventional Commits em portugues com **escopo obrigatorio**:
  ```text
  <tipo>(<escopo>): <descricao em letras minusculas>
  ```
- **Escopos Permitidos**: `app`, `application`, `ci`, `deps`, `docs`, `domain`, `flagship`, `harness`, `hooks`, `infra`, `linters`, `makefile`, `presentation`, `release`, `reports`, `revolut`, `scripts`, `tests`.
- **Exemplos Canônicos**:
  ```text
  feat(flagship): ajusta limiar de integracoes saga para ambiente estavel
  fix(revolut): corrige consulta progressiva de metricas nos servicos spi
  refactor(domain): simplifica formatacao de latencias pix
  test(infra): adiciona cobertura para timeout de scraper rds
  docs(docs): atualiza diagrama de camadas e fluxo hexagonal
  chore(release): 0.2.0 [skip ci]
  ```
