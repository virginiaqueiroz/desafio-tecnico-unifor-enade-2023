# Imagem base enxuta com Python 3.11
FROM python:3.11-slim

WORKDIR /app

# Dependências de sistema:
# - build-essential: compila wheels nativos usados por algumas libs Python
# - curl: o notebook "1. Download Microdados ENADE.ipynb" chama o comando
#   `curl` diretamente (via subprocess) para baixar os microdados do INEP.
#   No Windows o curl já vem instalado por padrão; na imagem slim do Docker
#   precisa ser instalado explicitamente.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Instala as dependências Python primeiro (aproveita cache do Docker em rebuilds)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Registra o kernel Jupyter "python3", exigido pelo run_pipeline.py
# (jupyter nbconvert --execute procura esse kernel pelo nome definido
# no metadata dos notebooks: kernelspec.name == "python3")
RUN python -m ipykernel install --name python3 --display-name "Python 3 (ipykernel)" --sys-prefix

# Copia o restante do projeto (respeitando o .dockerignore)
COPY . .

RUN chmod +x docker-entrypoint.sh

# Configuração padrão para execução dentro do container:
# - não tenta abrir navegador local (não existe display no container)
# - escuta em todas as interfaces para ser acessível fora do container
ENV DASHBOARD_NAO_ABRIR=1 \
    DASHBOARD_HOST=0.0.0.0 \
    DASHBOARD_PORTA=8050

EXPOSE 8050

ENTRYPOINT ["./docker-entrypoint.sh"]
