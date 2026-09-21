from pathlib import Path
import os
import threading
import webbrowser

import duckdb
import plotly.graph_objects as go
import plotly.io as pio
from flask import Flask, render_template
from markupsafe import Markup


app = Flask(__name__)

# Localiza a pasta principal do projeto e o banco criado pela pipeline.
pasta_projeto = Path(__file__).resolve().parent.parent
arquivo_banco = pasta_projeto / "data" / "database" / "enade.duckdb"
porta_dashboard = int(os.environ.get("DASHBOARD_PORTA", "8050"))
host_dashboard = os.environ.get("DASHBOARD_HOST", "127.0.0.1")

AZUL_UNIFOR = "#044CF4"
AZUL_CLARO = "#E4F1FA"
LARANJA = "#FBA234"
TEXTO = "#17213A"


def numero_pt(valor, casas=0):
    """Formata números no padrão brasileiro para exibição."""
    if valor is None:
        return "—"
    texto = f"{float(valor):,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def grafico_html(figura, incluir_plotly=False):
    """Converte uma figura Plotly em HTML responsivo e autocontido."""
    return Markup(
        pio.to_html(
            figura,
            full_html=False,
            include_plotlyjs="inline" if incluir_plotly else False,
            config={"displayModeBar": False, "responsive": True, "locale": "pt-BR"},
        )
    )


def estilizar_figura(figura, altura):
    """Aplica o padrão visual do dashboard aos gráficos."""
    figura.update_layout(
        height=altura,
        margin=dict(l=12, r=24, t=24, b=28),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Satoshi, Arial, sans-serif", color=TEXTO, size=13),
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            bordercolor=AZUL_CLARO,
            font=dict(family="Satoshi, Arial, sans-serif", color=TEXTO),
        ),
        showlegend=False,
    )
    return figura


def consultar_dados_dashboard():
    """Consulta somente as tabelas Gold e prepara os dados do relatório."""
    if not arquivo_banco.exists():
        raise FileNotFoundError(
            "Banco não encontrado. Execute primeiro o arquivo executar_pipeline.bat."
        )

    conexao = duckdb.connect(str(arquivo_banco), read_only=True)

    try:
        resumo_linha = conexao.execute(
            """
            SELECT
                dc.CO_IES,
                di.NO_IES,
                di.SG_IES,
                COUNT(DISTINCT dc.CO_CURSO) AS QT_CURSOS,
                COUNT(DISTINCT dc.CO_GRUPO) AS QT_AREAS,
                SUM(f.QT_AVALIADOS) AS QT_AVALIADOS,
                SUM(f.NT_GER_MEDIA * f.QT_AVALIADOS)
                    / NULLIF(SUM(f.QT_AVALIADOS), 0) AS NT_GER_MEDIA
            FROM gold.dim_cursos AS dc
            INNER JOIN gold.dim_ies AS di ON dc.CO_IES = di.CO_IES
            INNER JOIN gold.fato_desempenho_curso AS f
                ON dc.CO_CURSO = f.CO_CURSO
            WHERE dc.CO_IES = 555
            GROUP BY dc.CO_IES, di.NO_IES, di.SG_IES
            """
        ).fetchone()

        if resumo_linha is None:
            raise RuntimeError("A Unifor não foi encontrada na camada Gold.")

        areas_df = conexao.execute(
            """
            SELECT
                dc.CO_GRUPO,
                dg.NO_GRUPO,
                dc.CO_CURSO,
                dc.NO_CURSO,
                dm.DS_MODALIDADE,
                f.NT_GER_MEDIA,
                f.QT_AVALIADOS
            FROM gold.dim_cursos AS dc
            INNER JOIN gold.dim_grupo AS dg ON dc.CO_GRUPO = dg.CO_GRUPO
            INNER JOIN gold.dim_modalidade AS dm
                ON dc.CO_MODALIDADE = dm.CO_MODALIDADE
            INNER JOIN gold.fato_desempenho_curso AS f
                ON dc.CO_CURSO = f.CO_CURSO
            WHERE dc.CO_IES = 555
            ORDER BY f.NT_GER_MEDIA DESC, dc.NO_CURSO
            """
        ).df()

        modalidades_df = conexao.execute(
            """
            SELECT
                dm.DS_MODALIDADE,
                COUNT(DISTINCT dc.CO_CURSO) AS QT_CURSOS,
                SUM(f.QT_AVALIADOS) AS QT_AVALIADOS,
                SUM(f.NT_GER_MEDIA * f.QT_AVALIADOS)
                    / NULLIF(SUM(f.QT_AVALIADOS), 0) AS NT_GER_MEDIA
            FROM gold.dim_cursos AS dc
            INNER JOIN gold.dim_modalidade AS dm
                ON dc.CO_MODALIDADE = dm.CO_MODALIDADE
            INNER JOIN gold.fato_desempenho_curso AS f
                ON dc.CO_CURSO = f.CO_CURSO
            WHERE dc.CO_IES = 555
            GROUP BY dm.DS_MODALIDADE
            ORDER BY dm.DS_MODALIDADE
            """
        ).df()

        nacional_modalidade_df = conexao.execute(
            """
            SELECT
                dm.DS_MODALIDADE,
                COUNT(DISTINCT dc.CO_CURSO) AS QT_CURSOS,
                SUM(f.QT_AVALIADOS) AS QT_AVALIADOS,
                SUM(f.NT_GER_MEDIA * f.QT_AVALIADOS)
                    / NULLIF(SUM(f.QT_AVALIADOS), 0) AS NT_GER_MEDIA
            FROM gold.dim_cursos AS dc
            INNER JOIN gold.dim_modalidade AS dm
                ON dc.CO_MODALIDADE = dm.CO_MODALIDADE
            INNER JOIN gold.fato_desempenho_curso AS f
                ON dc.CO_CURSO = f.CO_CURSO
            GROUP BY dm.DS_MODALIDADE
            ORDER BY dm.DS_MODALIDADE
            """
        ).df()

        censo_modalidade_df = conexao.execute(
            """
            SELECT
                CASE TP_MODALIDADE_ENSINO
                    WHEN \'1\' THEN \'Presencial\'
                    WHEN \'2\' THEN \'EaD\'
                    ELSE TP_MODALIDADE_ENSINO
                END AS DS_MODALIDADE,
                COUNT(*) AS QT_CURSOS
            FROM bronze.censo_cursos_raw
            WHERE CO_IES = \'555\'
            GROUP BY 1
            """
        ).df()

        comparaveis_df = conexao.execute(
            """
            WITH areas_unifor AS (
                SELECT DISTINCT CO_GRUPO
                FROM gold.dim_cursos
                WHERE CO_IES = 555
            ),
            total_areas AS (
                SELECT COUNT(*) AS QT_TOTAL FROM areas_unifor
            ),
            desempenho AS (
                SELECT
                    dc.CO_IES,
                    di.NO_IES,
                    di.SG_IES,
                    COUNT(DISTINCT dc.CO_GRUPO) AS QT_AREAS_COBERTAS,
                    COUNT(DISTINCT dc.CO_CURSO) AS QT_CURSOS,
                    SUM(f.QT_AVALIADOS) AS QT_AVALIADOS,
                    SUM(f.NT_GER_MEDIA * f.QT_AVALIADOS)
                        / NULLIF(SUM(f.QT_AVALIADOS), 0) AS NT_GER_MEDIA
                FROM gold.dim_cursos AS dc
                INNER JOIN gold.dim_ies AS di ON dc.CO_IES = di.CO_IES
                INNER JOIN gold.fato_desempenho_curso AS f
                    ON dc.CO_CURSO = f.CO_CURSO
                WHERE dc.CO_GRUPO IN (SELECT CO_GRUPO FROM areas_unifor)
                GROUP BY dc.CO_IES, di.NO_IES, di.SG_IES
            )
            SELECT desempenho.*
            FROM desempenho
            CROSS JOIN total_areas
            WHERE QT_AREAS_COBERTAS >= QT_TOTAL - 1
            ORDER BY NT_GER_MEDIA DESC
            """
        ).df()
    finally:
        conexao.close()

    resumo = {
        "codigo_ies": int(resumo_linha[0]),
        "nome_ies": resumo_linha[1],
        "sigla_ies": resumo_linha[2],
        "quantidade_cursos": int(resumo_linha[3]),
        "quantidade_areas": int(resumo_linha[4]),
        "quantidade_avaliados": int(resumo_linha[5]),
        "nota_media": float(resumo_linha[6]),
    }

    areas = areas_df.to_dict(orient="records")
    top_10 = areas[:10]

    # Inclui as duas modalidades esperadas, mesmo quando uma não existe no recorte.
    encontradas = {
        linha["DS_MODALIDADE"]: linha
        for linha in modalidades_df.to_dict(orient="records")
    }
    modalidades = []
    for nome in ("Presencial", "EaD"):
        linha = encontradas.get(nome)
        modalidades.append(
            {
                "nome": nome,
                "quantidade_cursos": int(linha["QT_CURSOS"]) if linha else 0,
                "quantidade_avaliados": int(linha["QT_AVALIADOS"]) if linha else 0,
                "nota_media": float(linha["NT_GER_MEDIA"]) if linha else None,
            }
        )

    encontradas_brasil = {
        linha["DS_MODALIDADE"]: linha
        for linha in nacional_modalidade_df.to_dict(orient="records")
    }
    nacional_modalidades = []
    for nome in ("Presencial", "EaD"):
        linha = encontradas_brasil.get(nome)
        nacional_modalidades.append(
            {
                "nome": nome,
                "quantidade_cursos": int(linha["QT_CURSOS"]) if linha else 0,
                "quantidade_avaliados": int(linha["QT_AVALIADOS"]) if linha else 0,
                "nota_media": float(linha["NT_GER_MEDIA"]) if linha else None,
            }
        )

    diferenca_nacional = (
        nacional_modalidades[0]["nota_media"] - nacional_modalidades[1]["nota_media"]
        if all(item["nota_media"] is not None for item in nacional_modalidades)
        else None
    )

    censo_encontradas = {
        linha["DS_MODALIDADE"]: int(linha["QT_CURSOS"])
        for linha in censo_modalidade_df.to_dict(orient="records")
    }
    censo_modalidades = {
        "presencial": censo_encontradas.get("Presencial", 0),
        "ead": censo_encontradas.get("EaD", 0),
    }

    melhores = comparaveis_df.to_dict(orient="records")
    melhor_brasil = next(
        (linha for linha in melhores if int(linha["CO_IES"]) != 555), None
    )
    posicao_unifor = next(
        (
            posicao
            for posicao, linha in enumerate(melhores, start=1)
            if int(linha["CO_IES"]) == 555
        ),
        None,
    )

    benchmark = None
    if melhor_brasil:
        benchmark = {
            "codigo_ies": int(melhor_brasil["CO_IES"]),
            "nome_ies": melhor_brasil["NO_IES"],
            "sigla_ies": melhor_brasil["SG_IES"],
            "areas_cobertas": int(melhor_brasil["QT_AREAS_COBERTAS"]),
            "quantidade_avaliados": int(melhor_brasil["QT_AVALIADOS"]),
            "nota_media": float(melhor_brasil["NT_GER_MEDIA"]),
            "diferenca": float(melhor_brasil["NT_GER_MEDIA"])
            - resumo["nota_media"],
            "posicao_unifor": posicao_unifor,
            "total_comparaveis": len(melhores),
        }

    melhor_curso = top_10[0]
    destaque = {
        "nome_curso": melhor_curso["NO_CURSO"],
        "nome_grupo": melhor_curso["NO_GRUPO"],
        "nota_media": float(melhor_curso["NT_GER_MEDIA"]),
        "quantidade_avaliados": int(melhor_curso["QT_AVALIADOS"]),
        "acima_media_unifor": float(melhor_curso["NT_GER_MEDIA"])
        - resumo["nota_media"],
    }

    return {
        "resumo": resumo,
        "areas": areas,
        "top_10": top_10,
        "modalidades": modalidades,
        "comparacao_modalidade_disponivel": all(
            item["quantidade_cursos"] > 0 for item in modalidades
        ),
        "nacional_modalidades": nacional_modalidades,
        "diferenca_nacional": diferenca_nacional,
        "censo_modalidades": censo_modalidades,
        "benchmark": benchmark,
        "destaque": destaque,
    }


def criar_graficos(dados):
    """Cria os gráficos centrais do relatório."""
    top_10 = list(reversed(dados["top_10"]))
    cores_top = [AZUL_UNIFOR] * len(top_10)
    cores_top[-1] = LARANJA

    grafico_top = go.Figure(
        go.Bar(
            x=[linha["NT_GER_MEDIA"] for linha in top_10],
            y=[linha["NO_CURSO"] for linha in top_10],
            orientation="h",
            marker=dict(color=cores_top, line=dict(width=0)),
            text=[numero_pt(linha["NT_GER_MEDIA"], 2) for linha in top_10],
            textposition="outside",
            cliponaxis=False,
            customdata=[linha["QT_AVALIADOS"] for linha in top_10],
            hovertemplate=(
                "<b>%{y}</b><br>Nota média: %{x:.2f}"
                "<br>Avaliados: %{customdata}<extra></extra>"
            ),
        )
    )
    estilizar_figura(grafico_top, 500)
    grafico_top.update_layout(margin=dict(l=185, r=48, t=18, b=42))
    grafico_top.update_xaxes(
        title="Nota geral média",
        range=[0, max(linha["NT_GER_MEDIA"] for linha in top_10) * 1.16],
        gridcolor="#E7ECF3",
        zeroline=False,
        tickformat=".0f",
    )
    grafico_top.update_yaxes(title=None, automargin=True)

    nacional_modalidades = dados["nacional_modalidades"]
    grafico_nacional = go.Figure(
        go.Bar(
            x=[item["nome"] for item in nacional_modalidades],
            y=[item["nota_media"] for item in nacional_modalidades],
            marker=dict(color=[AZUL_UNIFOR, LARANJA]),
            text=[numero_pt(item["nota_media"], 2) for item in nacional_modalidades],
            textposition="outside",
            cliponaxis=False,
            customdata=[item["quantidade_avaliados"] for item in nacional_modalidades],
            hovertemplate=(
                "<b>%{x}</b><br>Nota média ponderada: %{y:.2f}"
                "<br>Alunos avaliados: %{customdata:,}<extra></extra>"
            ),
        )
    )
    estilizar_figura(grafico_nacional, 300)
    grafico_nacional.update_layout(margin=dict(l=48, r=28, t=18, b=38))
    grafico_nacional.update_yaxes(
        title="Nota geral média ponderada",
        range=[0, max(item["nota_media"] for item in nacional_modalidades) * 1.2],
        gridcolor="#E7ECF3",
        zeroline=False,
    )
    grafico_nacional.update_xaxes(title=None)

    benchmark = dados["benchmark"]
    grafico_benchmark = None
    if benchmark:
        nomes = ["Unifor", benchmark["sigla_ies"] or "Melhor comparável"]
        notas = [dados["resumo"]["nota_media"], benchmark["nota_media"]]
        grafico_benchmark = go.Figure(
            go.Bar(
                x=nomes,
                y=notas,
                marker=dict(color=[AZUL_UNIFOR, LARANJA]),
                text=[numero_pt(nota, 2) for nota in notas],
                textposition="outside",
                cliponaxis=False,
                customdata=[
                    dados["resumo"]["quantidade_avaliados"],
                    benchmark["quantidade_avaliados"],
                ],
                hovertemplate=(
                    "<b>%{x}</b><br>Nota média ponderada: %{y:.2f}"
                    "<br>Avaliados: %{customdata}<extra></extra>"
                ),
            )
        )
        estilizar_figura(grafico_benchmark, 310)
        grafico_benchmark.update_layout(margin=dict(l=48, r=28, t=18, b=38))
        grafico_benchmark.update_yaxes(
            title="Nota média ponderada",
            range=[0, max(notas) * 1.18],
            gridcolor="#E7ECF3",
            zeroline=False,
        )
        grafico_benchmark.update_xaxes(title=None)

    return {
        "top_10": grafico_html(grafico_top),
        "nacional_modalidade": grafico_html(grafico_nacional, incluir_plotly=True),
        "benchmark": grafico_html(grafico_benchmark) if grafico_benchmark else None,
    }


@app.route("/")
def pagina_inicial():
    try:
        dados = consultar_dados_dashboard()
        graficos = criar_graficos(dados)
        return render_template(
            "index.html",
            dados=dados,
            graficos=graficos,
            numero_pt=numero_pt,
            erro=None,
        )
    except Exception as erro:
        return render_template(
            "index.html",
            dados=None,
            graficos=None,
            numero_pt=numero_pt,
            erro=str(erro),
        ), 500


def abrir_navegador():
    webbrowser.open(f"http://127.0.0.1:{porta_dashboard}")


if __name__ == "__main__":
    if os.environ.get("DASHBOARD_NAO_ABRIR") != "1":
        threading.Timer(1.5, abrir_navegador).start()
    app.run(
        host=host_dashboard,
        port=porta_dashboard,
        debug=False,
        use_reloader=False,
    )
