# Este script é um exemplo de como usar a biblioteca openmeteo_requests
# fonte: https://open-meteo.com/en/docs

import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": -22,9194,
	"longitude": -42,8186,
	"daily": [
        "temperature_2m_max",
         "temperature_2m_min", 
         "apparent_temperature_max", 
         "apparent_temperature_min",
          "precipitation_probability_max", 
          "precipitation_hours",
          "precipitation_sum", 
           "rain_sum", 
           "temperature_2m_mean", 
           "relative_humidity_2m_mean", 
           "relative_humidity_2m_max", 
           "relative_humidity_2m_min", 
           "pressure_msl_mean"],

	"hourly": [
        "temperature_2m", 
        "relative_humidity_2m", 
        "rain", "pressure_msl", 
        "wind_speed_10m"],

	"current": [
        "rain", 
        "relative_humidity_2m", 
        "temperature_2m"],
}
responses = openmeteo.weather_api(url, params = params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]

# Process current data. The order of variables needs to be the same as requested.
current = response.Current()
current_rain = current.Variables(0).Value()
current_relative_humidity_2m = current.Variables(1).Value()
current_temperature_2m = current.Variables(2).Value()

print(f"\nCurrent time: {current.Time()}")
print(f"Current rain: {current_rain}")
print(f"Current relative_humidity_2m: {current_relative_humidity_2m}")
print(f"Current temperature_2m: {current_temperature_2m}")

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
hourly_rain = hourly.Variables(2).ValuesAsNumpy()
hourly_pressure_msl = hourly.Variables(3).ValuesAsNumpy()
hourly_wind_speed_10m = hourly.Variables(4).ValuesAsNumpy()

hourly_data = {
	"date": pd.date_range(
		start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
		end =  pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
		freq = pd.Timedelta(seconds = hourly.Interval()),
		inclusive = "left"
	)
}

hourly_data["temperature_2m"] = hourly_temperature_2m
hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
hourly_data["rain"] = hourly_rain
hourly_data["pressure_msl"] = hourly_pressure_msl
hourly_data["wind_speed_10m"] = hourly_wind_speed_10m

hourly_dataframe = pd.DataFrame(data = hourly_data)
print("\nHourly data\n", hourly_dataframe)


def montar_dataframe_openmeteo():
        ##monta dataframe com dados de interesse do openmeteo
        hourly_data = {
        "date": pd.date_range(
		start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
		end =  pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
		freq = pd.Timedelta(seconds = hourly.Interval()),
		inclusive = "left"
	)}

        hourly_data["temperature_2m"] = hourly_temperature_2m
        hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
        hourly_data["rain"] = hourly_rain
        hourly_data["pressure_msl"] = hourly_pressure_msl

        hourly_dataframe = pd.DataFrame(data = hourly_data)

    return hourly_dataframe

def salvar_dados_csv(df, path, sep=';', encoding='utf-8'):
    df.to_csv(path, index=True, sep=sep, encoding=encoding)
    print(f"Dados salvos em {path}")

def salvar_dados_sql(df, db_path, table_name):
        import sqlite3
        path = sqlite3.connect(db_path)
        df.to_sql(table_name, path, if_exists='replace', index=True)
        path.close()
        print(f"Dados salvos na tabela '{table_name}' do banco de dados '{db_path}'")

