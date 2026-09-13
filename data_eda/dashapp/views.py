import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import pandas as pd
import numpy as np
from django.shortcuts import render
from analise.eda import EDA
from analise.comparacao import Comparacao
from analise.investigacao import Investigacao
from datetime import datetime



BASE_DIR = Path(__file__).resolve().parent.parent
DADOS_DIR = BASE_DIR / "dados"

def carregar_dados():
    from coleta.iot import coletar_dados_iot, salvar_dados_csv
    dados_iot = coletar_dados_iot()
    salvar_dados_csv(dados_iot, "dados_iot.csv" )


    from coleta.openmeteo import openmeteo_to_dataframe, salvar_dados_csv
    dados_openmeteo = openmeteo_to_dataframe()
    salvar_dados_csv(dados_openmeteo, "dados_openmeteo.csv")

    from processamento.processamento import Processamento
    padronizar = Processamento()
    dados_iot_padronizados = padronizar.padronizar_dataframe_iot(
    pd.read_csv(
        "dados_iot.csv", 
        sep=';', 
        encoding='utf-8',
        usecols=['temperatura', 'umidade', 'timestamp']) )

    dados_openmeteo_padronizados = padronizar.padronizar_dataframe_openmeteo(
        pd.read_csv(
            "dados_openmeteo.csv", 
            sep=';', 
            encoding='utf-8',
            ) )

    dados_mesclados = padronizar.mesclar_dataframes(dados_iot_padronizados, dados_openmeteo_padronizados)

    padronizar.salvar_dados_csv(dados_mesclados, "dados_meteorologicos.csv")

    return pd.read_csv(
        DADOS_DIR / "dados_meteorologicos.csv",
        sep=";"
    )

def home(request):

    df = carregar_dados()
    eda = EDA(df)
    comp = Comparacao(df)


    agora = datetime.now()


    # grafico com temperatura atual
    temperatura_atual = df.iloc[-1]["temperatura_iot"]

    # grafico com umidade_relativa atual
    umidade_atual = df.iloc[-1]["umidade_relativa_iot"]

    # estatisticas de umidade e temperatura
    estatistica_umidade = eda.estatisticas_descritivas("umidade_relativa_iot")
    estatistica_temperatura = eda.estatisticas_descritivas("temperatura_iot")


    #grafico com temperatuda ao longo do tempo IoT x OpenMeteo
    #grafico de duas linhas ostrando variação de hora em hora naquele dia, colunaY = temperatura, colunay= data
    fig_temperatura = go.Figure()
    fig_temperatura.add_trace(
        go.Scatter(
            x=df["data"],
            y=df["temperatura_iot"],
            mode = "lines+markers",
            name="Iot"
        )
    )
    fig_temperatura.add_trace(
        go.Scatter(
            x=df["data"],
            y=df["temperatura_openmeteo"],
            mode = "lines+markers",
            name="Open-Meteo"
        )
    )
    fig_temperatura.update_layout(
        title="Temperatura - Iot x Open-Meteo",
        xaxis_title="Data",
        yaxis_title="temperatura °C",
        hovermode="x unified",
        template="plotly_white"
    )
    grafico_temperatura =  fig_temperatura.to_html(
        full_html= False,
        include_plotlyjs= "cdn"
    )

    #drafico com umidade ao londo do tempo Iot x OpenMeteo
    # mesma logica do grafico de temperatura
    fig_umidade = go.Figure()
    fig_umidade.add_trace(
        go.Scatter(
            x=df["data"],
            y=df["umidade_relativa_iot"],
            mode = "lines+markers",
            name = "Iot"
        )
    )
    fig_umidade.add_trace(
        go.Scatter(
            x = df["data"],
            y = df["umidade_relativa_openmeteo"],
            mode = "lines+markers",
            name = "Open-Meteo"
        )
    )
    fig_umidade.update_layout(
        title = "Umidade Relativa do Ar - Iot x Open-Meteo",
        xaxis_title="Data",
        yaxis_title="Umidade Relativa em Percentual",
        hovermode="x unified",
        template="plotly_white"
    )
    grafico_umidade =  fig_umidade.to_html(
        full_html= False,
        include_plotlyjs= "cdn"
    )


    # grafico ponto de orvalho Iot x OpenMeteo
    #grafico de duas linhas mostrando variação de hora em hora naquele dia onde y= temperatura e x= data
    td_orvalho = comp.comparar_ponto_orvalho()
    dados_td = td_orvalho["dados"]

    fig_td = go.Figure()
    fig_td.add_trace(
        go.Scatter(
            x=dados_td["data"],
            y=dados_td["ponto_orvalho_iot"],
            mode = "lines+markers",
            name = "Iot"
        )
    )
    fig_td.add_trace(
        go.Scatter(
            x = dados_td["data"],
            y = dados_td["ponto_orvalho_iot"],
            mode="lines+markers",
            name = "Open-Meteo"
        )
    )
    fig_td.update_layout(
        title = "Ponto de Orvalho - IoT x Open-Meteo",
        xaxis_title = "Data",
        yaxis_title = "Ponto de Orvalho °C",
        hovermode = "x unified",
        template = "plotly_white"
    )
    grafico_td = fig_td.to_html(
        full_html = False,
        include_plotlyjs="cdn"
    )

    context = {
        "temperatura_atual": temperatura_atual,
        "umidade_atual": umidade_atual,
        "estatistica_temperatura" : estatistica_temperatura,
        "estatistica_umidade" : estatistica_umidade,
        "grafico_temperatura" : grafico_temperatura,
        "grafico_umidade" : grafico_umidade,
        "ponto_orvalho" : grafico_td
    }

    return render(
        request,
        "dashapp/home.html",
        context
    )

def comparacao(request):

    df = carregar_dados()
    comp = Comparacao(df)
    eda = EDA(df)

    # ==================================
    # TEMPERATURA
    # ==================================

    resultado_temperatura = comp.comparar_temperatura()

    dados_temperatura = resultado_temperatura["dados"]
    indicadores_temperatura = resultado_temperatura["indicadores"]

    fig_temperatura = go.Figure()

    fig_temperatura.add_trace(
        go.Scatter(
            x=dados_temperatura["data"],
            y=dados_temperatura["temperatura_iot"],
            mode="lines+markers",
            name="IoT"
        )
    )

    fig_temperatura.add_trace(
        go.Scatter(
            x=dados_temperatura["data"],
            y=dados_temperatura["temperatura_openmeteo"],
            mode="lines+markers",
            name="Open-Meteo"
        )
    )

    fig_temperatura.update_layout(
        title="Temperatura — IoT × Open-Meteo",
        xaxis_title="Data",
        yaxis_title="Temperatura °C",
        hovermode="x unified",
        template="plotly_white"
    )

    grafico_temperatura = fig_temperatura.to_html(
        full_html=False,
        include_plotlyjs="cdn"
    )


    # ==================================
    # UMIDADE
    # ==================================

    resultado_umidade = comp.comparar_umidade()

    dados_umidade = resultado_umidade["dados"]
    indicadores_umidade = resultado_umidade["indicadores"]

    fig_umidade = go.Figure()

    fig_umidade.add_trace(
        go.Scatter(
            x=dados_umidade["data"],
            y=dados_umidade["umidade_relativa_iot"],
            mode="lines+markers",
            name="IoT"
        )
    )

    fig_umidade.add_trace(
        go.Scatter(
            x=dados_umidade["data"],
            y=dados_umidade["umidade_relativa_openmeteo"],
            mode="lines+markers",
            name="Open-Meteo"
        )
    )

    fig_umidade.update_layout(
        title="Umidade relativa — IoT × Open-Meteo",
        xaxis_title="Data",
        yaxis_title="Umidade %",
        hovermode="x unified",
        template="plotly_white"
    )

    grafico_umidade = fig_umidade.to_html(
        full_html=False,
        include_plotlyjs="cdn"
    )



    resultado_td = comp.comparar_ponto_orvalho()

    dados_td = resultado_td["dados"]
    indicadores_td = resultado_td["indicadores"]

    fig_td = go.Figure()

    fig_td.add_trace(
        go.Scatter(
            x=dados_td["data"],
            y=dados_td["ponto_orvalho_iot"],
            mode="lines+markers",
            name="IoT"
        )
    )

    fig_td.add_trace(
        go.Scatter(
            x=dados_td["data"],
            y=dados_td["ponto_orvalho_openmeteo"],
            mode="lines+markers",
            name="Open-Meteo"
        )
    )

    fig_td.update_layout(
        title="Ponto de orvalho — IoT × Open-Meteo",
        xaxis_title="Data",
        yaxis_title="Ponto de orvalho °C",
        hovermode="x unified",
        template="plotly_white"
    )

    grafico_td = fig_td.to_html(
        full_html=False,
        include_plotlyjs="cdn"
    )


    # ==================================
    # CONTEXT
    # ==================================

    context = {
        "grafico_temperatura": grafico_temperatura,
        "grafico_umidade": grafico_umidade,
        "grafico_td": grafico_td,

        "indicadores_temperatura": indicadores_temperatura,
        "indicadores_umidade": indicadores_umidade,
        "indicadores_td": indicadores_td,
    }

    return render(
        request,
        "dashapp/comparacao.html",
        context
    )

def investigacao(request):


    df = carregar_dados()

    # ============================================================
    # PREPARAÇÃO DOS DADOS
    # ============================================================

    df["data"] = pd.to_datetime(df["data"])
    df = df.sort_values("data").copy()

    analise = Investigacao(df)

    # Calcula o ponto de orvalho
    df = analise.adicionar_ponto_orvalho()

    # Chuva definida pela precipitação do Open-Meteo
    df["choveu"] = df["precipitacao"] > 0

    # ============================================================
    # VARIÁVEIS DERIVADAS
    # ============================================================

    # Depressão do ponto de orvalho
    df["depressao_orvalho"] = (
        df["temperatura_iot"] -
        df["ponto_orvalho_iot"]
    )

    # Variação do ponto de orvalho
    df["variacao_tpo"] = (
        df["ponto_orvalho_iot"].diff()
    )

    # Tempo entre medições
    df["tempo_horas"] = (
        df["data"].diff().dt.total_seconds() / 3600
    )

    # Taxa de variação do ponto de orvalho
    df["taxa_variacao_tpo"] = (
        df["variacao_tpo"] /
        df["tempo_horas"]
    )

    # Remove infinitos causados por divisão por zero
    df["taxa_variacao_tpo"] = (
        df["taxa_variacao_tpo"]
        .replace([np.inf, -np.inf], np.nan)
    )

    # ============================================================
    # IDENTIFICAÇÃO DOS EVENTOS DE CHUVA
    # ============================================================

    df["mudanca_chuva"] = (
        df["choveu"] != df["choveu"].shift()
    )

    inicio_chuva = df[
        (df["mudanca_chuva"]) &
        (df["choveu"])
    ].copy()

    fim_chuva = df[
        (df["mudanca_chuva"]) &
        (~df["choveu"])
    ].copy()

    # ============================================================
    # CONFIGURAÇÃO DOS GRÁFICOS
    # ============================================================

    def configurar_tempo(fig):

        fig.update_xaxes(
            tickformat="%d/%m %Hh",
            nticks=8,
            hoverformat="%d/%m/%Y %H:%M",
            showgrid=True
        )

        fig.update_layout(
            hovermode="x unified"
        )

        return fig

    # ============================================================
    # SOMBREAMENTO DOS PERÍODOS DE CHUVA
    # ============================================================

    def adicionar_sombreamento_chuva(fig):

        inicio = None

        for i in range(len(df)):

            chovendo = df.iloc[i]["choveu"]
            data_atual = df.iloc[i]["data"]

            if chovendo and inicio is None:

                inicio = data_atual

            elif not chovendo and inicio is not None:

                fig.add_vrect(
                    x0=inicio,
                    x1=data_atual,
                    fillcolor="lightblue",
                    opacity=0.25,
                    line_width=0,
                    layer="below"
                )

                inicio = None

        # Se a chuva continuar até o último registro
        if inicio is not None:

            fig.add_vrect(
                x0=inicio,
                x1=df["data"].iloc[-1],
                fillcolor="lightblue",
                opacity=0.25,
                line_width=0,
                layer="below"
            )

        return fig

    # ============================================================
    # 1. DEPRESSÃO NO INÍCIO DA CHUVA
    # ============================================================

    fig_depressao = go.Figure()

    fig_depressao.add_trace(
        go.Scatter(
            x=df["data"],
            y=df["depressao_orvalho"],
            mode="lines",
            name="Depressão do Tpo",
            line=dict(width=2)
        )
    )

    fig_depressao.add_trace(
        go.Scatter(
            x=inicio_chuva["data"],
            y=inicio_chuva["depressao_orvalho"],
            mode="markers",
            name="Início da chuva",
            marker=dict(
                size=9,
                symbol="circle"
            )
        )
    )

    fig_depressao.add_hline(
        y=0,
        line_dash="dash",
        annotation_text="Saturação"
    )

    fig_depressao.update_layout(
        title="Depressão do ponto de orvalho no início da chuva",
        xaxis_title="Data e hora",
        yaxis_title="T − Tpo (°C)",
        height=500
    )

    adicionar_sombreamento_chuva(fig_depressao)
    configurar_tempo(fig_depressao)

    if not inicio_chuva.empty:

        indicador_inicio = {
            "media": inicio_chuva["depressao_orvalho"].mean(),
            "mediana": inicio_chuva["depressao_orvalho"].median(),
            "minimo": inicio_chuva["depressao_orvalho"].min(),
            "maximo": inicio_chuva["depressao_orvalho"].max()
        }

    else:

        indicador_inicio = {
            "media": np.nan,
            "mediana": np.nan,
            "minimo": np.nan,
            "maximo": np.nan
        }

    # ============================================================
    # 2. COMPORTAMENTO DO TPO ANTES DA CHUVA
    # ============================================================

    fig_gradiente = go.Figure()

    fig_gradiente.add_trace(
        go.Scatter(
            x=df["data"],
            y=df["taxa_variacao_tpo"],
            mode="lines",
            name="Taxa de variação do Tpo",
            line=dict(width=2)
        )
    )

    fig_gradiente.add_trace(
        go.Scatter(
            x=inicio_chuva["data"],
            y=inicio_chuva["taxa_variacao_tpo"],
            mode="markers",
            name="Início da chuva",
            marker=dict(
                size=9,
                symbol="diamond"
            )
        )
    )

    fig_gradiente.add_hline(
        y=0,
        line_dash="dash",
        annotation_text="Sem variação"
    )

    fig_gradiente.update_layout(
        title="Taxa de variação do ponto de orvalho",
        xaxis_title="Data e hora",
        yaxis_title="Taxa de variação do Tpo (°C/h)",
        height=500
    )

    adicionar_sombreamento_chuva(fig_gradiente)
    configurar_tempo(fig_gradiente)

    # Escala visual definida para facilitar a leitura
    fig_gradiente.update_yaxes(
        range=[-5, 5],
        zeroline=True,
        zerolinewidth=1
    )

    # Média da taxa nas 3 horas anteriores aos eventos
    gradientes_3h = []

    for _, evento in inicio_chuva.iterrows():

        inicio = (
            evento["data"] -
            pd.Timedelta(hours=3)
        )

        janela = df[
            (df["data"] >= inicio) &
            (df["data"] <= evento["data"])
        ]

        gradientes_3h.extend(
            janela["taxa_variacao_tpo"]
            .dropna()
            .tolist()
        )

    if gradientes_3h:

        indicador_antecedencia = {
            "media": np.mean(gradientes_3h),
            "mediana": np.median(gradientes_3h)
        }

    else:

        indicador_antecedencia = {
            "media": np.nan,
            "mediana": np.nan
        }

    # ============================================================
    # 3. TEMPERATURA E TPO DURANTE A CHUVA
    # ============================================================

    dados_chuva = df[
        df["choveu"]
    ].copy()

    fig_saturacao = go.Figure()

    fig_saturacao.add_trace(
        go.Scatter(
            x=dados_chuva["data"],
            y=dados_chuva["temperatura_iot"],
            mode="lines",
            name="Temperatura IoT"
        )
    )

    fig_saturacao.add_trace(
        go.Scatter(
            x=dados_chuva["data"],
            y=dados_chuva["ponto_orvalho_iot"],
            mode="lines",
            name="Ponto de orvalho IoT"
        )
    )

    fig_saturacao.update_layout(
        title="Temperatura e ponto de orvalho durante a chuva",
        xaxis_title="Data e hora",
        yaxis_title="Temperatura (°C)",
        height=500
    )

    adicionar_sombreamento_chuva(fig_saturacao)
    configurar_tempo(fig_saturacao)

    if not dados_chuva.empty:

        amplitude = (
            dados_chuva["temperatura_iot"] -
            dados_chuva["ponto_orvalho_iot"]
        ).abs()

        indicador_durante = {
            "media": amplitude.mean(),
            "mediana": amplitude.median(),
            "minimo": amplitude.min(),
            "maximo": amplitude.max(),
            "amplitude": (
                amplitude.max() -
                amplitude.min()
            )
        }

    else:

        indicador_durante = {
            "media": np.nan,
            "mediana": np.nan,
            "minimo": np.nan,
            "maximo": np.nan,
            "amplitude": np.nan
        }

    # ============================================================
    # 4. COMPORTAMENTO DO TPO NO FIM DA CHUVA
    # ============================================================

    fig_fim_chuva = go.Figure()

    fig_fim_chuva.add_trace(
        go.Scatter(
            x=df["data"],
            y=df["taxa_variacao_tpo"],
            mode="lines",
            name="Taxa de variação do Tpo",
            line=dict(width=2)
        )
    )

    fig_fim_chuva.add_trace(
        go.Scatter(
            x=fim_chuva["data"],
            y=fim_chuva["taxa_variacao_tpo"],
            mode="markers",
            name="Fim da chuva",
            marker=dict(
                size=10,
                symbol="x"
            )
        )
    )

    fig_fim_chuva.add_hline(
        y=0,
        line_dash="dash",
        annotation_text="Sem variação"
    )

    fig_fim_chuva.update_layout(
        title="Taxa de variação do Tpo no fim da chuva",
        xaxis_title="Data e hora",
        yaxis_title="Taxa de variação do Tpo (°C/h)",
        height=500
    )

    adicionar_sombreamento_chuva(fig_fim_chuva)
    configurar_tempo(fig_fim_chuva)

    # Escala visual definida para facilitar a leitura
    fig_fim_chuva.update_yaxes(
        range=[-3, 3],
        zeroline=True,
        zerolinewidth=1
    )

    if not fim_chuva.empty:

        indicador_fim = {
            "media": fim_chuva["taxa_variacao_tpo"].mean(),
            "mediana": fim_chuva["taxa_variacao_tpo"].median()
        }

    else:

        indicador_fim = {
            "media": np.nan,
            "mediana": np.nan
        }

    # ============================================================
    # 5. DISTRIBUIÇÃO DO PONTO DE ORVALHO
    # ============================================================

    df_distribuicao = df.copy()

    df_distribuicao["condicao"] = np.where(
        df_distribuicao["choveu"],
        "Com chuva",
        "Sem chuva"
    )

    fig_distribuicao = go.Figure()

    for condicao in ["Sem chuva", "Com chuva"]:

        dados = df_distribuicao[
            df_distribuicao["condicao"] == condicao
        ]["ponto_orvalho_iot"].dropna()

        fig_distribuicao.add_trace(
            go.Box(
                y=dados,
                name=condicao,
                boxpoints="all",
                jitter=0.25,
                pointpos=0,
                boxmean=True
            )
        )

    fig_distribuicao.update_layout(
        title="Distribuição do ponto de orvalho: chuva × sem chuva",
        xaxis_title="Condição",
        yaxis_title="Ponto de orvalho (°C)",
        height=500
    )

    # ============================================================
    # INDICADORES DA DISTRIBUIÇÃO
    # ============================================================

    td_chuva = df[
        df["choveu"]
    ]["ponto_orvalho_iot"].dropna()

    td_sem_chuva = df[
        ~df["choveu"]
    ]["ponto_orvalho_iot"].dropna()

    if not td_chuva.empty and not td_sem_chuva.empty:

        indicador_distribuicao = {
            "media_chuva": td_chuva.mean(),
            "mediana_chuva": td_chuva.median(),
            "media_sem_chuva": td_sem_chuva.mean(),
            "mediana_sem_chuva": td_sem_chuva.median(),
            "diferenca_media": (
                td_chuva.mean() -
                td_sem_chuva.mean()
            )
        }

    else:

        indicador_distribuicao = {
            "media_chuva": np.nan,
            "mediana_chuva": np.nan,
            "media_sem_chuva": np.nan,
            "mediana_sem_chuva": np.nan,
            "diferenca_media": np.nan
        }

    # ============================================================
    # CONTEXTO PARA O TEMPLATE
    # ============================================================

    context = {

        "grafico_inicio_chuva":
            fig_depressao.to_html(
                full_html=False
            ),

        "grafico_antecedencia":
            fig_gradiente.to_html(
                full_html=False
            ),

        "grafico_durante_chuva":
            fig_saturacao.to_html(
                full_html=False
            ),

        "grafico_fim_chuva":
            fig_fim_chuva.to_html(
                full_html=False
            ),

        "grafico_distribuicao":
            fig_distribuicao.to_html(
                full_html=False
            ),

        "indicador_inicio":
            indicador_inicio,

        "indicador_antecedencia":
            indicador_antecedencia,

        "indicador_durante":
            indicador_durante,

        "indicador_fim":
            indicador_fim,

        "indicador_distribuicao":
            indicador_distribuicao,

        "quantidade_inicio_chuva":
            len(inicio_chuva),

        "quantidade_fim_chuva":
            len(fim_chuva),

        "quantidade_registros_chuva":
            len(dados_chuva),

        # Mantém os resultados antigos
        "resultados": {

            "depressao_media_inicio_chuva":
                indicador_inicio["media"],

            "depressao_mediana_inicio_chuva":
                indicador_inicio["mediana"],

            "depressao_minima_inicio_chuva":
                indicador_inicio["minimo"],

            "gradiente_medio_3h_antes":
                indicador_antecedencia["media"],

            "gradiente_mediano_3h_antes":
                indicador_antecedencia["mediana"],

            "amplitude_media_durante_chuva":
                indicador_durante["media"],

            "amplitude_mediana_durante_chuva":
                indicador_durante["mediana"],

            "gradiente_medio_fim_chuva":
                indicador_fim["media"],

            "gradiente_mediano_fim_chuva":
                indicador_fim["mediana"],

            "ponto_orvalho_medio_com_chuva":
                indicador_distribuicao["media_chuva"],

            "ponto_orvalho_medio_sem_chuva":
                indicador_distribuicao["media_sem_chuva"],

            "diferenca_media_td_chuva":
                indicador_distribuicao["diferenca_media"]
        }
    }

    return render(
        request,
        "dashapp/investigacao.html",
        context
    )

def estatisticas(request):

    df = carregar_dados()

    analise = EDA(df)

    estatisticas = {}

    colunas = [
        "temperatura_iot",
        "umidade_relativa_iot",
        "temperatura_openmeteo",
        "umidade_relativa_openmeteo",
        "precipitacao",
        "pressao"
    ]

    for coluna in colunas:

        estatisticas[coluna] = (
            analise.estatisticas_descritivas(coluna)
        )

    quantidade_registros = analise.quantidade_registros()

    return render(
        request,
        "dashapp/estatisticas.html",
        {
            "estatisticas": estatisticas,
            "quantidade_registros": quantidade_registros
        }
    )

def outliers(request):

    df = carregar_dados()

    analise = EDA(df)

    colunas = [
        "temperatura_iot",
        "umidade_relativa_iot",
        "temperatura_openmeteo",
        "umidade_relativa_openmeteo",
        "precipitacao",
        "pressao"
    ]

    outliers = {}

    for coluna in colunas:

        dados = analise.detectar_anomalias_outliers(coluna)

        outliers[coluna] = dados.to_dict(
            orient="records"
        )

    return render(
        request,
        "dashapp/outliers.html",
        {
            "outliers": outliers
        }
    )

def registros(request):

    df = carregar_dados()

    colunas = df.columns.tolist()

    dados = df.values.tolist()

    return render(
        request,
        "dashapp/registros.html",
        {
            "dados": dados,
            "colunas": colunas
        }
    )
    