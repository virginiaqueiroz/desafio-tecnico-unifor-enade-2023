#!/bin/sh
set -e

BANCO="/app/data/database/enade.duckdb"

if [ -f "$BANCO" ]; then
    echo "=========================================="
    echo "Banco de dados encontrado em data/database/enade.duckdb"
    echo "Pulando a execução do pipeline."
    echo "=========================================="
else
    echo "=========================================="
    echo "Banco de dados não encontrado."
    echo "Executando o pipeline (download + tratamento dos microdados)."
    echo "Isso pode levar alguns minutos na primeira execução."
    echo "=========================================="
    python run_pipeline.py
fi

echo ""
echo "=========================================="
echo "Iniciando o dashboard em http://localhost:${DASHBOARD_PORTA:-8050}"
echo "=========================================="
exec python dashboard/app.py
