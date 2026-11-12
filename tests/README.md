# Suite de Testes (tests/)

Suite de testes automatizados do sistema de relatorios de observabilidade (Flagship DTW / Revolut MIP), mantendo a meta inegociavel de 100% de cobertura com verificacao estrita de desvios (`branch coverage`).

## Estrutura da Suite

- [unit/](unit/): Testes unitarios rapidos e isolados por camada (`domain`, `application`, `presentation`).
- [integration/](integration/): Testes de integracao de adaptadores e infraestrutura com rede emulada e I/O.

## Execucao

```bash
# Executa a suite com medicao estrita de cobertura
make test
```
