# implementa classe para investigação exploratória de dados (EDA)
import pandas as pd

class EDA:
    def __init__(self, df):
        self.df = df

    # Retorna um resumo estatístico do dataframe
    def resumo_estatistico(self):
        return self.df.describe()

    # Retorna a quantidade de valores nulos por coluna
    def verificar_valores_nulos(self):
        return self.df.isnull().sum()

    # Retorna a quantidade de valores duplicados no dataframe
    def verificar_valores_duplicados(self):
        return self.df.duplicated().sum()
    
    # Retorna os tipos de dados das colunas do dataframe
    def verificar_tipos_dados(self):
        return self.df.dtypes

    # retorna periodos de tempo analisado com base na coluna de data
    def periodo_tempo(self, coluna_data):
        if coluna_data in self.df.columns:
            data_min = self.df[coluna_data].min()
            data_max = self.df[coluna_data].max()
            return data_min, data_max
        else:
            raise ValueError(f"A coluna '{coluna_data}' não existe no dataframe.")

    # Retorna frequencia das medicoes por hora, dia, semana, mes e ano com base na coluna de data
    def frequencia_medicoes(self, coluna_data):
        if coluna_data in self.df.columns:
            self.df[coluna_data] = pd.to_datetime(self.df[coluna_data])
            frequencia = {
                "hora": self.df.set_index(coluna_data).resample('H').size(),
                "dia": self.df.set_index(coluna_data).resample('D').size(),
                "semana": self.df.set_index(coluna_data).resample('W').size(),
                "mes": self.df.set_index(coluna_data).resample('M').size(),
                "ano": self.df.set_index(coluna_data).resample('Y').size()
            }
            return frequencia
        else:
            raise ValueError(f"A coluna '{coluna_data}' não existe no dataframe.")
    
    # Retorna variaveis disponiveis no dataframe
    def variaveis_disponiveis(self):
        return self.df.columns.tolist()

    # Retorna valores maximos e minimos de cada variavel do dataframe
    def valores_maximos_minimos(self, column_data):
        if column_data in self.df.columns:
            return self.df[column_data].min(), self.df[column_data].max()
        else:
            raise ValueError(f"A coluna '{column_data}' não existe no dataframe.")
    
    # Retorna a quantidade de registros no dataframe
    def quantidade_registros(self):
        return len(self.df)

    # Retorna media, mediana e desvio padrao de cada variavel do dataframe
    def estatisticas_descritivas(self, column_data):
        if column_data in self.df.columns:
            return {
                "media": self.df[column_data].mean(),
                "mediana": self.df[column_data].median(),
                "desvio_padrao": self.df[column_data].std()
            }
        else:
            raise ValueError(f"A coluna '{column_data}' não existe no dataframe.")

    # Retorna possiveis anomalias ou outliers em cada variavel do dataframe usando o metodo do IQR (Interquartile Range)
    def detectar_anomalias_outliers(self, column_data):
        if column_data in self.df.columns:
            Q1 = self.df[column_data].quantile(0.25)
            Q3 = self.df[column_data].quantile(0.75)
            IQR = Q3 - Q1
            outliers = self.df[(self.df[column_data] < (Q1 - 1.5 * IQR)) | (self.df[column_data] > (Q3 + 1.5 * IQR))]
            return outliers
        else:
            raise ValueError(f"A coluna '{column_data}' não existe no dataframe.")
    
