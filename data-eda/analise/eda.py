# implementa classe para investigação exploratória de dados (EDA)
import pandas as pd

class EDA:
    def __init__(self, df: pd.DataFrame):
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
    def periodo_tempo(self, coluna_dados):
        if coluna_dados in self.df.columns:
            data = self.df.copy()
            data[coluna_dados] = pd.to_datetime(data[coluna_dados])
            data_min = data[coluna_dados].min()
            data_max = data[coluna_dados].max()
            return data_min, data_max
        else:
            raise ValueError(f"A coluna '{coluna_dados}' não existe no dataframe.")

    # Retorna frequencia das medicoes por hora, dia, semana, mes e ano com base na coluna de data
    def frequencia_medicoes(self, coluna_dados):
        data = self.df.copy()
        if coluna_dados in data.columns:
            data[coluna_dados] = pd.to_datetime(data[coluna_dados])
            frequencia = {
                "hora": data.set_index(coluna_dados).resample('h').size(),
                "dia": data.set_index(coluna_dados).resample('D').size(),
                "semana": data.set_index(coluna_dados).resample('W').size(),
                "mes": data.set_index(coluna_dados).resample('ME').size(),
                "ano": data.set_index(coluna_dados).resample('YE').size()
            }
            return frequencia
        else:
            raise ValueError(f"A coluna '{coluna_dados}' não existe no dataframe.")
    
    # Retorna variaveis disponiveis no dataframe
    def variaveis_disponiveis(self):
        return self.df.columns.tolist()

    # Retorna valores maximos e minimos de cada variavel do dataframe
    def valores_maximos_minimos(self, column_dados):
        if column_dados in self.df.columns:
            return self.df[column_dados].min(), self.df[column_dados].max()
        else:
            raise ValueError(f"A coluna '{column_dados}' não existe no dataframe.")
    
    # Retorna a quantidade de registros no dataframe
    def quantidade_registros(self):
        return len(self.df)

    # Retorna media, mediana e desvio padrao de cada variavel do dataframe
    def estatisticas_descritivas(self, column_dados):
        if column_dados in self.df.columns:
            return {
                "media": self.df[column_dados].mean(),
                "mediana": self.df[column_dados].median(),
                "desvio_padrao": self.df[column_dados].std()
            }
        else:
            raise ValueError(f"A coluna '{column_dados}' não existe no dataframe.")

    # Retorna possiveis anomalias ou outliers em cada variavel do dataframe usando o metodo do IQR (Interquartile Range)
    def detectar_anomalias_outliers(self, column_dados):
        if column_dados in self.df.columns:
            Q1 = self.df[column_dados].quantile(0.25)
            Q3 = self.df[column_dados].quantile(0.75)
            IQR = Q3 - Q1
            outliers = self.df[(self.df[column_dados] < (Q1 - 1.5 * IQR)) | (self.df[column_dados] > (Q3 + 1.5 * IQR))]
            return outliers
        else:
            raise ValueError(f"A coluna '{column_dados}' não existe no dataframe.")
    
