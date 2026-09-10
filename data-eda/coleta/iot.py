# módulo responsavel por coletar dados da api do iot e transformar em um dataframe pandas

import requests
import pandas as pd

def coletar_dados_iot():
    url = "https://minimeteorolia-1.onrender.com/medicoes"
    response = requests.get(url)
    
    if response.status_code == 200:
        dados_json = response.json()
        df = pd.DataFrame(dados_json)
        return df
    else:
        print(f"Erro ao coletar dados da API: {response.status_code}")
        return pd.DataFrame()  


def salvar_dados_csv(df, path, sep=';', encoding='utf-8'):
    df.to_csv(path, index=True, sep=sep, encoding=encoding)
    print(f"Dados salvos em {path}")

