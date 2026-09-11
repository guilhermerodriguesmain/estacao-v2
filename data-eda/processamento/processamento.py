## define classe de processamento de dados do openmeteo e IoT
import pandas as pd

class Processamento():
    
    def __init__(self):
        pass

    def padronizar_dataframe_openmeteo(self, df_openmeteo):
        # Padroniza o dataframe para ter colunas consistentes
        df = df_openmeteo.rename(columns={
            'date': 'data',
            'temperature_2m': 'temperatura',
            'relative_humidity_2m': 'umidade_relativa',
            'rain': 'chuva',
            'pressure_msl': 'pressao'
        })
        df['data'] = pd.to_datetime(df['data'], utc=True)
        return df

    def padronizar_dataframe_iot(self, df_iot):
        # Padroniza o dataframe para ter colunas consistentes
        df = df_iot.rename(columns={
            'temperatura': 'temperatura',
            'umidade': 'umidade_relativa',
            'timestamp': 'data'
        })
        df['data'] = pd.to_datetime(df['data'], utc=True)

        return df

    def mesclar_dataframes(self, df_iot, df_openmeteo):
        # Mescla os dataframes do IoT e do OpenMeteo com base na coluna de data
        df_iot = df_iot.sort_values('data')
        df_iot = df_iot.drop(columns=['fonte'], errors='ignore')

        df_openmeteo = df_openmeteo.sort_values('data')
        df_openmeteo = df_openmeteo.drop(columns=['fonte'], errors='ignore')
        df_openmeteo = df_openmeteo.drop(columns=['Unnamed: 0'],errors='ignore')

        df_merged = pd.merge_asof(
            df_iot, 
            df_openmeteo, 
            on='data', 
            direction='nearest',
            tolerance=pd.Timedelta('30min'),
            suffixes=('_iot', '_openmeteo')
            )
        return df_merged

    def salvar_dados_csv(self, df, path, sep=';', encoding='utf-8'):
        df.to_csv(path, index=True, sep=sep, encoding=encoding)
        print(f"Dados salvos em {path}")

    def salvar_dados_sql(self, df, db_path, table_name = "dados_meteorologicos"):
        import sqlite3
        path = sqlite3.connect(db_path)
        df.to_sql(table_name, path, if_exists='replace', index=True)
        path.close()
        print(f"Dados salvos na tabela '{table_name}' do banco de dados '{db_path}'")
        
padronizar = Processamento()

dados_iot_padronizados = padronizar.padronizar_dataframe_iot(
    pd.read_csv(
        "../dados/dados_iot.csv", 
        sep=';', 
        encoding='utf-8',
        usecols=['temperatura', 'umidade', 'timestamp']) )

dados_openmeteo_padronizados = padronizar.padronizar_dataframe_openmeteo(
    pd.read_csv(
        "../dados/dados_openmeteo.csv", 
        sep=';', 
        encoding='utf-8',
        ) )

dados_mesclados = padronizar.mesclar_dataframes(dados_iot_padronizados, dados_openmeteo_padronizados)

padronizar.salvar_dados_csv(dados_mesclados, "../dados/dados_meteorologicos.csv")
