# implementa classe para comparação de dados
# Objetivo: verificar como os dados da estação local se comportam em relação aos dados meteorológicos externos.


import pandas as pd
import numpy as np


class Comparacao:

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def comparar_temperatura(self):

        df = self.df.copy()

        df["diferenca_temperatura"] = ( df["temperatura_iot"] - df["temperatura_openmeteo"])

        diferenca_media = df["diferenca_temperatura"].mean()

        mae = np.mean(np.abs(df["diferenca_temperatura"]))

        rmse = np.sqrt(np.mean(df["diferenca_temperatura"] ** 2))

        return {
            "dados": df[
                [
                    "data",
                    "temperatura_iot",
                    "temperatura_openmeteo",
                    "diferenca_temperatura"
                ]
            ],

            "indicadores": {
                "diferenca_media": diferenca_media,
                "mae": mae,
                "rmse": rmse
            }
        }

    def comparar_umidade(self):
        # Comparar a umidade das duas fontes ao longo do tempo.
        # Diferenças das medias de umidade entre as duas fontes.
        # Calcular MAE (Mean Absolute Error) e RMSE (Root Mean Square Error) entre as duas fontes.
        # retornar um dataframe com as diferenças de umidade entre as duas fontes ao longo do tempo.
        df = self.df.copy()

        df["diferenca_umidade"] = (df["umidade_iot"] - df["umidade_openmeteo"])

        diferenca_media = df["diferenca_umidade"].mean()
        mae = np.mean(np.abs(df["diferenca_umidade"]))
        rmse = np.sqrt(np.mean(df["diferenca_umidade"] ** 2))

        return {
            "dados": df[
                [
                    "data",
                    "umidade_iot",
                    "umidade_openmeteo",
                    "diferenca_umidade"
                ]
            ],
            "indicadores": {
                "diferenca_media": diferenca_media,
                "mae": mae,
                "rmse": rmse
            }
        }

    def calcular_ponto_orvalho(self, temperatura: pd.Series,umidade: pd.Series):

        # Coeficientes da fórmula de Magnus-Tetens
        a = 17.27
        b = 237.7
        
        # Passo 1: Calcular o termo intermediário alfa
        alfa = ((a * temperatura) / (b + temperatura)) + np.log(umidade / 100.0)
        
        # Passo 2: Calcular a temperatura do ponto de orvalho (Td)
        td = (b * alfa) / (a - alfa)
        
        return td
        
    def comparar_ponto_orvalho(self):
        # Comparar o ponto de orvalho das duas fontes ao longo do tempo.
        # Diferenças das medias de ponto de orvalho entre as duas fontes.
        # Calcular MAE (Mean Absolute Error) e RMSE (Root Mean Square Error) entre as duas fontes.
        # retornar um dataframe com as diferenças de ponto de orvalho entre as duas fontes ao longo do tempo.
        df = self.df.copy()

        df["ponto_orvalho_iot"] = self.calcular_ponto_orvalho(
            df["temperatura_iot"], 
            df["umidade_iot"]
            )

        df["ponto_orvalho_openmeteo"] = self.calcular_ponto_orvalho(
            df["temperatura_openmeteo"], 
            df["umidade_openmeteo"]
            )
        
        df["diferenca_ponto_orvalho"] = (df["ponto_orvalho_iot"] - df["ponto_orvalho_openmeteo"])
        diferenca_media = df["diferenca_ponto_orvalho"].mean()
        mae = np.mean(np.abs(df["diferenca_ponto_orvalho"]))
        rmse = np.sqrt(np.mean(df["diferenca_ponto_orvalho"] ** 2))

        return {
            "dados": df[
                [
                    "data",
                    "ponto_orvalho_iot",
                    "ponto_orvalho_openmeteo",
                    "diferenca_ponto_orvalho"
                ]
            ],
            "indicadores": {
                "diferenca_media": diferenca_media,
                "mae": mae,
                "rmse": rmse
            }
        }
