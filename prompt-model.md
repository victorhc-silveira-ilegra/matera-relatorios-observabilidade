# Prompt-Modelo de Engenharia

Contrato reutilizavel derivado da arquitetura deste repositorio (Relatorios de Observabilidade). Utilize este arquivo como diretriz canonica para orientar agentes autonomos ou equipes na concepcao, geracao ou refatoracao de sistemas corporativos com o mais alto padrao de engenharia: Domain-Driven Design (DDD), Arquitetura Hexagonal (Ports & Adapters), Test-Driven Development (TDD), observabilidade semantica, automacao de testes continuos e documentacao viva.

O dominio de observabilidade multi-cliente (Flagship DTW / Revolut MIP) serve como exemplo pratico de implementacao; os principios aqui consolidados aplicam-se a qualquer dominio de negocio e ecossistema tecnologico.

## 1. Papel e Responsabilidade do Agente

Ao atuar sobre um novo dominio e linguagem, o agente deve:

- Projetar a topologia e a implementacao aderindo rigorosamente aos contratos invariantes.
- Organizar a estrutura de pacotes e ferramentas nativas sem comprometer as fronteiras arquiteturais.
- Manter documentacao tecnica, Makefile, git hooks e quality gates perfeitamente sincronizados com o codigo.
- Priorizar a disciplina de TDD: testes unitarios primeiro para regras de dominio e casos de uso; testes de integracao para adaptadores de entrada/saida (I/O).
- Garantir que a base de codigo seja autoexplicativa, tipada estritamente e sem comentarios desnecessarios.

## 2. Contrato Invariante (Agnostico a Linguagem)

### Camadas da Arquitetura Hexagonal

| Camada | Conteudo e Responsabilidade | Dependencia Permitida |
| :--- | :--- | :--- |
| **domain** | Entidades, Value Objects, Domain Services, Regras e Politicas de Negocio puras | Nenhuma dependencia externa ao dominio |
| **application** | Casos de uso (Use Cases) e Portas (Ports - interfaces/protocolos de IO) | Exclusivamente `domain` |
| **infrastructure** | Adaptadores (Adapters) de IO, clientes HTTP/DB/Broker, persistencia e configuracoes | `application` e `domain` |
| **presentation** | Pontos de entrada (CLI, Workers, APIs), composition root e orquestracao de runtime | `application`, `domain` e `infrastructure` |

### Regras Arquiteturais Absolutas

1. As camadas `domain` e `application` nunca importam nem referenciam detalhes das camadas `infrastructure` ou `presentation`.
2. As Portas (Ports) sao contratos abstratos (interfaces puras ou protocolos tipados). Os Adaptadores (Adapters) implementam esses contratos na camada de `infrastructure`.
3. Validacoes semanticas, invariantes de estado, calculo de janelas e regras temporais pertencem exclusivamente ao dominio.
4. Formatacao de dados de saida e modelos de apresentacao canonica pertencem ao dominio ou aplicacao, nunca a interface externa de CLI/Controller.
5. Nem o `domain` nem o `application` realizam chamadas de logging ou acessam ferramentas de telemetria; o log e uma preocupacao de infraestrutura e apresentacao.
6. O Composition Root (injecao de dependencias e amarracao Settings -> Adapters -> Use Cases) vive estritamente na camada de `presentation`.

### Qualidade e Estilo

- **Zero Comentarios**: Ausencia de comentarios explicativos no codigo de aplicacao. A legibilidade e garantida por nomes semanticos, funcoes coesas e contratos explicitos.
- **Documentacao Formal em PT-BR**: Redacao tecnica clara e precisa.
- **Conventional Commits com Escopo Obrigatorio**: Mensagens de commit padronizadas no formato `<tipo>(<escopo>): <descricao>` escritas em portugues brasileiro (ex.: `feat(flagship): ...`, `fix(revolut): ...`).
- **Isolamento de Segredos**: Parametros de runtime injetados exclusivamente por variaveis de ambiente via `.env` / `.env.example`. Nenhum segredo ou credencial real e versionado.
- **Cobertura Continua**: Meta inegociavel de 100% de cobertura de codigo com analise de desvios (`branch coverage`).
- **Dimensao Coesa de Arquivos**: Limite maximo de 300 linhas por arquivo de codigo.
- **Tipagem Estrita**: Verificacao estatica maxima suportada (`mypy --strict`).

## 3. Matriz de Qualidade Unificada (5 Estagios)

A validacao continua opera sobre 5 estagios deterministicos:

| Ordem | Estagio | Finalidade |
| :---: | :--- | :--- |
| **1** | `Lint` | Analise estatica de formatacao, sintaxe e tipos (`ruff`, `mypy --strict`) |
| **2** | `Security` | Varredura de vulnerabilidades e segredos (`bandit`) |
| **3** | `Test` | Execucao automatizada da suite com 100% de cobertura de linhas e branches |
| **4** | `Validate` | Validacao estrutural de manifestos, presenca de harness e limites de dimensao |
| **5** | `Build` | Validacao de empacotamento e build de distribucao wheel |

O orquestrador unificado (`scripts/quality_gate.py`) centraliza a execucao desses estagios para o desenvolvedor e pipelines automatizados.

## 4. Observabilidade e Logging Semantico

- API padronizada de eventos estruturados: `log_event(logger, level, event, **fields)`.
- Catalogo de eventos estaveis com padrao `<contexto>.<entidade>.<acao>` (ex.: `report.generation.started`, `report.generation.completed`).
- Nivel `INFO` reservado para marcos relevantes do fluxo operacional.
- Sanitizacao obrigatoria: redacao de credenciais e mascaras em URLs corporativas.

## 5. Harness de Agentes Autonomos

O repositorio expoe um harness universal em `.agents/` para consumo por qualquer LLM ou agente inteligente:
- `.agents/rules/`: Regras de conduta, arquitetura, testes, logging e politicas de clientes.
- `.agents/skills/`: Guias operacionais e manuais passo a passo para execucao de rotinas complexas.

## 6. Prompt para Bootstrap de Novos Clientes

Copie o template abaixo para integrar novos clientes de observabilidade ao ecossistema:

```text
Voce e um Engenheiro de Software Senior. Integre o novo cliente de observabilidade ao sistema seguindo o Contrato Invariante de Engenharia (DDD + Hexagonal + TDD + 100% Branch Coverage).

DADOS DO CLIENTE:
- Nome do Cliente: <<<NOME_DO_CLIENTE>>>
- Fontes de Dados: <<<OpenSearch|Grafana|Prometheus|CloudWatch|Banco>>>
- Metricas Obrigatorias: <<<LISTA_DE_METRICAS>>>
- Janelas Horarias Oficiais: <<<08:30-10:30|10:30-13:30|13:30-16:30>>>
- Criterios de Saude (Estavel / Atencao / Instavel): <<<REGRAS_DE_NEGOCIO>>>

CONTRATO ARQUITETURAL:
1. Modelos e formatador em app/domain/<<<cliente>>>/
2. Porta abstrata em app/application/ports.py e caso de uso em app/application/use_cases.py
3. Adaptadores em app/infrastructure/adapters/<<<cliente>>>_reader.py
4. Entrypoint CLI estendido em app/presentation/cli.py
5. Testes unitarios com 100% de branch coverage em tests/
6. Politica em .agents/rules/<<<cliente>>>-policy.md e skill em .agents/skills/generate-<<<cliente>>>-report/SKILL.md
```
