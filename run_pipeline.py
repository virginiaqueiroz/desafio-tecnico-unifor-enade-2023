from pathlib import Path
import subprocess
import sys


# Identifica a pasta principal do projeto

pasta_projeto = Path(__file__).resolve().parent


# Define os notebooks na ordem em que serão executados

notebooks = [
pasta_projeto / "1. Download Microdados ENADE.ipynb",
pasta_projeto / "2. Exploração Microdados ENADE.ipynb"
]


# Cria uma pasta separada para os notebooks executados

pasta_resultados = (
pasta_projeto
/ "artifacts"
/ "notebooks_executados"
)

pasta_resultados.mkdir(
parents=True,
exist_ok=True
)


# Executa cada notebook na ordem definida

for notebook in notebooks:
    if not notebook.exists():
        raise FileNotFoundError(
        f"Notebook não encontrado: {notebook}"
        )

    print(f"\nExecutando: {notebook.name}")

    subprocess.run(
    [
    sys.executable,
    "-m",
    "jupyter",
    "nbconvert",
    "--to",
    "notebook",
    "--execute",
    "--ExecutePreprocessor.timeout=-1",
    f"--output={notebook.stem}_executado",
    f"--output-dir={pasta_resultados}",
    str(notebook)
    ],
    cwd=pasta_projeto,
    check=True
    )

    print(f"Concluído: {notebook.name}")


print("\nPipeline executado com sucesso.")