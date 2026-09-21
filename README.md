# Desafio Técnico — ENADE 2023

Pipeline local para análise dos Microdados do ENADE 2023, com arquitetura
Bronze, Silver e Gold em DuckDB e um relatório web interativo sobre a
Universidade de Fortaleza (Unifor).

## O que o projeto entrega

- download e extração automatizados dos arquivos oficiais do INEP;
- tratamento e validação dos dados em notebooks reproduzíveis;
- banco local DuckDB organizado nas camadas Bronze, Silver e Gold;
- dashboard web responsivo, desenvolvido com Flask, HTML, CSS e Plotly;
- execução simplificada por arquivos `.bat` no Windows.

O dashboard responde às seguintes perguntas:

1. A Unifor está no ENADE 2023? Quais cursos, áreas e modalidades aparecem?
2. A nota média difere entre cursos presenciais e EaD?
3. Quais são os dez cursos da Unifor com maior nota média?
4. Qual é a melhor IES comparável nas áreas em que a Unifor atua e qual é a diferença?

## Como executar no Windows

### 1. Baixar o projeto

No GitHub, clique em **Code > Download ZIP** e extraia a pasta. Também é
possível clonar o repositório com GitHub Desktop.

### 2. Configurar o ambiente

Dê dois cliques em:

```text
configurar_ambiente.bat
```

Esse arquivo cria a pasta `.venv` e instala as bibliotecas listadas em
`requirements.txt`. Essa etapa é necessária apenas na primeira execução.

### 3. Executar a pipeline

Dê dois cliques em:

```text
executar_pipeline.bat
```

A pipeline executa os notebooks na ordem correta e gera o banco:

```text
data/database/enade.duckdb
```

### 4. Abrir o dashboard

Dê dois cliques em:

```text
executar_dashboard.bat
```

O navegador será aberto automaticamente em:

```text
http://127.0.0.1:8050
```

Para encerrar o dashboard, feche a janela preta que foi aberta pelo arquivo
`.bat` ou pressione `Ctrl + C` nela.

## Fluxo do projeto

```text
Microdados INEP
      ↓
Notebook 1 — download e extração
      ↓
Notebook 2 — Bronze, Silver e Gold
      ↓
data/database/enade.duckdb
      ↓
Flask + Plotly
      ↓
Dashboard no navegador
```

## Regras analíticas

- somente estudantes presentes (`TP_PRES = 555`) e com `NT_GER` válida entram
  no cálculo;
- a tabela fato possui uma linha por curso;
- a média institucional é ponderada por `QT_AVALIADOS`;
- o dashboard consulta exclusivamente tabelas da camada Gold;
- a comparação nacional considera IES presentes em pelo menos 16 das 17 áreas
  avaliadas da Unifor, evitando instituições com cobertura muito diferente.

## Estrutura principal

```text
dashboard/
├── app.py
├── static/
│   ├── fonts/
│   ├── images/
│   └── style.css
└── templates/
    └── index.html

1. Download Microdados ENADE.ipynb
2. Exploração Microdados ENADE.ipynb
configurar_ambiente.bat
executar_pipeline.bat
executar_dashboard.bat
requirements.txt
```

## Identidade visual

O relatório usa o logotipo, a tipografia Satoshi e referências cromáticas
disponibilizadas publicamente na
[Central de Marca da Unifor](https://unifor.br/central-de-marca). O material é
apresentado como análise independente produzida para o desafio técnico.

## Tecnologias

Python, Pandas, DuckDB, Jupyter, Flask, Plotly, HTML e CSS.
