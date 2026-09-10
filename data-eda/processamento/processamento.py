## define classe de processamento de dados do openmeteo e IoT

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
        return df

    def padronizar_dataframe_iot(self, df_iot):
        # Padroniza o dataframe para ter colunas consistentes
        df = df.rename(columns={
            'temperatura': 'temperatura',
            'umidade': 'umidade_relativa',
            'timestamp': 'data'
        })


        return df

    def mesclar_dataframes(self, df_iot, df_openmeteo):
        # Mescla os dataframes do IoT e do OpenMeteo com base na coluna de data
        df_merged = pd.merge(df_iot, df_openmeteo, on='date', how='outer')
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
        