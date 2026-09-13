from analise.eda import EDA
from analise.comparacao import Comparacao

import pandas as pd
import numpy as np


class Investigacao(EDA, Comparacao):

    def __init__(self, df: pd.DataFrame):

        EDA.__init__(self, df)
        Comparacao.__init__(self, df)

        self.df = df.copy()

        self.df = self.adicionar_ponto_orvalho()

        self.df = self.df.sort_values("data").reset_index(drop=True)


    # =========================================================
    # CHUVA
    # =========================================================

    def precipitacao(self):

        df = self.df.copy()

        df["choveu"] = df["precipitacao"] > 0

        return df

    def separar_com_chuva(self):

        df = self.precipitacao()

        return df[df["choveu"]].copy()

    def separar_sem_chuva(self):

        df = self.precipitacao()

        return df[~df["choveu"]].copy()

    def dados_em_torno_da_chuva(self, indice):

        df = self.precipitacao()

        inicio = max(0, indice - 3)
        fim = min(len(df), indice + 4)

        return df.iloc[inicio:fim].copy()


    # =========================================================
    # UMIDADE
    # =========================================================

    def analisar_umidade(self):

        df = self.precipitacao()

        resultados = []

        for indice in df.index:

            if df.loc[indice, "choveu"]:

                janela = self.dados_em_torno_da_chuva(indice)

                resultados.append({

                    "data_chuva":
                        df.loc[indice, "data"],

                    "umidade_iot_antes":
                        janela[janela.index < indice]
                        ["umidade_relativa_iot"].mean(),

                    "umidade_iot_durante":
                        df.loc[indice, "umidade_relativa_iot"],

                    "umidade_iot_depois":
                        janela[janela.index > indice]
                        ["umidade_relativa_iot"].mean(),

                    "umidade_openmeteo_antes":
                        janela[janela.index < indice]
                        ["umidade_relativa_openmeteo"].mean(),

                    "umidade_openmeteo_durante":
                        df.loc[indice, "umidade_relativa_openmeteo"],

                    "umidade_openmeteo_depois":
                        janela[janela.index > indice]
                        ["umidade_relativa_openmeteo"].mean()
                })

        return pd.DataFrame(resultados)


    # =========================================================
    # PONTO DE ORVALHO
    # =========================================================

    def estatisticas_ponto_orvalho(self):

        return {

            "media_iot":
                self.df["ponto_orvalho_iot"].mean(),

            "mediana_iot":
                self.df["ponto_orvalho_iot"].median(),

            "minimo_iot":
                self.df["ponto_orvalho_iot"].min(),

            "maximo_iot":
                self.df["ponto_orvalho_iot"].max(),

            "media_openmeteo":
                self.df["ponto_orvalho_openmeteo"].mean(),

            "mediana_openmeteo":
                self.df["ponto_orvalho_openmeteo"].median(),

            "minimo_openmeteo":
                self.df["ponto_orvalho_openmeteo"].min(),

            "maximo_openmeteo":
                self.df["ponto_orvalho_openmeteo"].max()
        }


    def analisar_outliers_ponto_orvalho(self):

        outliers_iot = self.detectar_anomalias_outliers(
            "ponto_orvalho_iot"
        )

        outliers_openmeteo = self.detectar_anomalias_outliers(
            "ponto_orvalho_openmeteo"
        )

        return {
            "iot": outliers_iot,
            "openmeteo": outliers_openmeteo
        }


    def analisar_distribuicao_ponto_orvalho(self):

        resultado = []

        for coluna in [
            "ponto_orvalho_iot",
            "ponto_orvalho_openmeteo"
        ]:

            outliers = self.detectar_anomalias_outliers(coluna)

            q1 = self.df[coluna].quantile(0.25)
            q3 = self.df[coluna].quantile(0.75)

            iqr = q3 - q1

            resultado.append({

                "variavel": coluna,

                "media":
                    self.df[coluna].mean(),

                "mediana":
                    self.df[coluna].median(),

                "minimo":
                    self.df[coluna].min(),

                "maximo":
                    self.df[coluna].max(),

                "q1":
                    q1,

                "q3":
                    q3,

                "iqr":
                    iqr,

                "limite_inferior":
                    q1 - 1.5 * iqr,

                "limite_superior":
                    q3 + 1.5 * iqr,

                "quantidade_outliers":
                    len(outliers)
            })

        return pd.DataFrame(resultado)


    # =========================================================
    # COMPORTAMENTO
    # =========================================================

    def calcular_variacao_ponto_orvalho(self):

        df = self.df.copy()

        df["variacao_td_iot"] = (
            df["ponto_orvalho_iot"].diff()
        )

        df["variacao_td_openmeteo"] = (
            df["ponto_orvalho_openmeteo"].diff()
        )

        return df

    def calcular_amplitude_ponto_orvalho(self):

        df = self.df.copy()

        amplitude_iot = (
            df["ponto_orvalho_iot"].max()
            - df["ponto_orvalho_iot"].min()
        )

        amplitude_openmeteo = (
            df["ponto_orvalho_openmeteo"].max()
            - df["ponto_orvalho_openmeteo"].min()
        )

        return {
            "amplitude_iot": amplitude_iot,
            "amplitude_openmeteo": amplitude_openmeteo
        }

    def calcular_velocidade_ponto_orvalho(self):

        df = self.calcular_variacao_ponto_orvalho()

        df["velocidade_td_iot"] = (
            df["variacao_td_iot"]
        )

        df["velocidade_td_openmeteo"] = (
            df["variacao_td_openmeteo"]
        )

        return df

    def comparar_td_com_chuva(self):

        com_chuva = self.separar_com_chuva()
        sem_chuva = self.separar_sem_chuva()

        return {
                "media_td_iot_com_chuva":
                    com_chuva["ponto_orvalho_iot"].mean(),

                "media_td_iot_sem_chuva":
                    sem_chuva["ponto_orvalho_iot"].mean(),

                "mediana_td_iot_com_chuva":
                    com_chuva["ponto_orvalho_iot"].median(),

                "mediana_td_iot_sem_chuva":
                    sem_chuva["ponto_orvalho_iot"].median(),

                "maximo_td_iot_com_chuva":
                    com_chuva["ponto_orvalho_iot"].max(),

                "maximo_td_iot_sem_chuva":
                    sem_chuva["ponto_orvalho_iot"].max()
            }

    def comparar_variacao_com_chuva(self):

        df = self.calcular_variacao_ponto_orvalho()
        df["choveu"] = df["precipitacao"] > 0
        com_chuva = df[df["choveu"]]
        sem_chuva = df[~df["choveu"]]

        return {
            "media_variacao_td_iot_com_chuva":
                com_chuva["variacao_td_iot"].mean(),

            "media_variacao_td_iot_sem_chuva":
                sem_chuva["variacao_td_iot"].mean(),

            "mediana_variacao_td_iot_com_chuva":
                com_chuva["variacao_td_iot"].median(),

            "mediana_variacao_td_iot_sem_chuva":
                sem_chuva["variacao_td_iot"].median(),

            "maximo_variacao_td_iot_com_chuva":
                com_chuva["variacao_td_iot"].max(),

            "maximo_variacao_td_iot_sem_chuva":
                sem_chuva["variacao_td_iot"].max()
        }
    
    def comparar_amplitude_com_chuva(self):
        com_chuva = self.separar_com_chuva()
        sem_chuva = self.separar_sem_chuva()

        amplitude_com_chuva = (
            com_chuva["ponto_orvalho_iot"].max()
            - com_chuva["ponto_orvalho_iot"].min()
        )

        amplitude_sem_chuva = (
            sem_chuva["ponto_orvalho_iot"].max()
            - sem_chuva["ponto_orvalho_iot"].min()
        )

        return {
            "amplitude_td_iot_com_chuva": amplitude_com_chuva,
            "amplitude_td_iot_sem_chuva": amplitude_sem_chuva
        }

    def comparar_velocidade_com_chuva(self):

        df = self.calcular_velocidade_ponto_orvalho()
    
        df["choveu"] = df["precipitacao"] > 0

        com_chuva = df[df["choveu"]]
        sem_chuva = df[~df["choveu"]]

        return {
            "media_velocidade_td_iot_com_chuva":
                com_chuva["velocidade_td_iot"].mean(),

            "media_velocidade_td_iot_sem_chuva":
                sem_chuva["velocidade_td_iot"].mean(),

            "mediana_velocidade_td_iot_com_chuva":
                com_chuva["velocidade_td_iot"].median(),

            "mediana_velocidade_td_iot_sem_chuva":
                sem_chuva["velocidade_td_iot"].median(),

            "maximo_velocidade_td_iot_com_chuva":
                com_chuva["velocidade_td_iot"].max(),

            "maximo_velocidade_td_iot_sem_chuva":
                sem_chuva["velocidade_td_iot"].max()
        }
    def calcular_correlacoes(self):

        df = self.calcular_velocidade_ponto_orvalho()

        colunas = [
            "ponto_orvalho_iot",
            "ponto_orvalho_openmeteo",
            "variacao_td_iot",
            "variacao_td_openmeteo",
            "precipitacao"
        ]

        return df[colunas].corr()

    def analisar_td_antes_da_chuva(self):
        df = self.separar_com_chuva()

        resultados = []

        for indice in df.index:

            janela = self.dados_em_torno_da_chuva(indice)

            resultados.append({

                "data_chuva":
                    df.loc[indice, "data"],

                "td_iot_antes":
                    janela[janela.index < indice]
                    ["ponto_orvalho_iot"].mean(),

                "td_openmeteo_antes":
                    janela[janela.index < indice]
                    ["ponto_orvalho_openmeteo"].mean()
            })

        return pd.DataFrame(resultados)

    def analisar_td_durante_chuva(self):
        df = self.separar_com_chuva()

        resultados = []

        for indice in df.index:

            resultados.append({

                "data_chuva":
                    df.loc[indice, "data"],

                "td_iot_durante":
                    df.loc[indice, "ponto_orvalho_iot"],

                "td_openmeteo_durante":
                    df.loc[indice, "ponto_orvalho_openmeteo"]
            })

        return pd.DataFrame(resultados)

    def analisar_td_depois_da_chuva(self):
        df = self.separar_com_chuva()

        resultados = []

        for indice in df.index:

            janela = self.dados_em_torno_da_chuva(indice)

            resultados.append({

                "data_chuva":
                    df.loc[indice, "data"],

                "td_iot_depois":
                    janela[janela.index > indice]
                    ["ponto_orvalho_iot"].mean(),

                "td_openmeteo_depois":
                    janela[janela.index > indice]
                    ["ponto_orvalho_openmeteo"].mean()
            })

        return pd.DataFrame(resultados)

    def distancia_outlier_chuva(self):

        df = self.precipitacao()

        outliers_iot = self.detectar_anomalias_outliers(
            "ponto_orvalho_iot"
        )

        outliers_openmeteo = self.detectar_anomalias_outliers(
            "ponto_orvalho_openmeteo"
        )

        indices_iot = set(outliers_iot.index)
        indices_openmeteo = set(outliers_openmeteo.index)

        resultados = []

        for indice in df.index:

            if df.loc[indice, "choveu"]:

                outliers_antes_iot = [
                    i for i in indices_iot
                    if i < indice
                ]

                outliers_antes_openmeteo = [
                    i for i in indices_openmeteo
                    if i < indice
                ]

                distancia_iot = (
                    indice - max(outliers_antes_iot)
                    if outliers_antes_iot
                    else None
                )

                distancia_openmeteo = (
                    indice - max(outliers_antes_openmeteo)
                    if outliers_antes_openmeteo
                    else None
                )

                resultados.append({

                    "data_chuva":
                        df.loc[indice, "data"],

                    "distancia_outlier_iot":
                        distancia_iot,

                    "distancia_outlier_openmeteo":
                        distancia_openmeteo
                })

        return pd.DataFrame(resultados)

    def encontrar_limiar_td(self):
        df = self.df.copy()

        limiar_iot = df["ponto_orvalho_iot"].quantile(0.75)
        limiar_openmeteo = df["ponto_orvalho_openmeteo"].quantile(0.75)

        return {
            "limiar_td_iot": limiar_iot,
            "limiar_td_openmeteo": limiar_openmeteo
        }
    def encontrar_limiar_variacao(self):

        df = self.calcular_variacao_ponto_orvalho()

        limiar_variacao_iot = (
            df["variacao_td_iot"].quantile(0.75)
        )

        limiar_variacao_openmeteo = (
            df["variacao_td_openmeteo"].quantile(0.75)
        )

        return {
            "limiar_variacao_iot":
                limiar_variacao_iot,

            "limiar_variacao_openmeteo":
                limiar_variacao_openmeteo
        }
    def encontrar_janela(self):
        df = self.df.copy()

        janela_iot = df["ponto_orvalho_iot"].rolling(window=3).mean()
        janela_openmeteo = df["ponto_orvalho_openmeteo"].rolling(window=3).mean()

        return {
            "janela_td_iot": janela_iot,
            "janela_td_openmeteo": janela_openmeteo
        }
    def testar_regra(self):
        df = self.df.copy()

        limiar = self.encontrar_limiar_td()

        df["regra_iot"] = df["ponto_orvalho_iot"] > limiar["limiar_td_iot"]
        df["regra_openmeteo"] = df["ponto_orvalho_openmeteo"] > limiar["limiar_td_openmeteo"]

        return df 

    def salvar_csv(self, resultado, nome_arquivo):

        if isinstance(resultado, pd.DataFrame):

            resultado.to_csv(
                nome_arquivo,
                index=False,
                encoding="utf-8-sig"
            )

        elif isinstance(resultado, dict):

            pd.DataFrame([resultado]).to_csv(
                nome_arquivo,
                index=False,
                encoding="utf-8-sig"
            )

        else:
            raise TypeError(
                "O resultado deve ser um DataFrame ou dicionário."
            )  

