# Estacao IoT: analise de dados e dashboard

Este projeto coleta dados meteorologicos de uma estacao IoT e da API Open-Meteo, padroniza e combina as series temporais e disponibiliza analises em um dashboard Django.

## Visao geral

O fluxo principal do projeto e:

1. Consultar as medicoes da API da estacao IoT.
2. Consultar dados horarios de temperatura, umidade, precipitacao e pressao na Open-Meteo.
3. Padronizar nomes, datas e formatos dos DataFrames.
4. Combinar as fontes por proximidade temporal.
5. Gerar os arquivos CSV consolidados.
6. Exibir estatisticas, comparacoes, investigacoes, outliers e registros no dashboard.

Os modulos principais sao:

- `coleta/`: integra as fontes IoT e Open-Meteo.
- `processamento/`: padroniza e mescla os dados.
- `analise/`: implementa EDA, comparacoes e investigacoes meteorologicas.
- `dashapp/`: views, rotas e templates do dashboard.
- `dashboard/`: configuracao do projeto Django.
- `dados/`: arquivos CSV usados e gerados pelo fluxo de dados.

## Requisitos

- Python 3.10 ou superior.
- Acesso a internet para consultar as APIs IoT e Open-Meteo.
- PowerShell no Windows ou um terminal equivalente no Linux/macOS.

As dependencias Python estao listadas em `requirements.txt`.

## Como executar

### 1. Acesse o diretorio do projeto

A partir da raiz do repositorio:

```powershell
cd data_eda
```

Execute os comandos seguintes dentro desse diretorio. O projeto usa caminhos relativos para alguns arquivos CSV.

### 2. Crie um ambiente virtual

No Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

No Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Se o PowerShell bloquear a ativacao do ambiente, ajuste a politica apenas para o usuario atual:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### 3. Instale as dependencias

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Inicialize o banco do Django

O projeto usa SQLite por padrao. Execute as migracoes:

```powershell
python manage.py migrate
```

Esse comando cria o arquivo `db.sqlite3`, que e ignorado pelo Git.

### 5. Inicie o servidor

```powershell
python manage.py runserver
```

Abra no navegador:

<http://127.0.0.1:8000/>

O dashboard consulta as fontes externas e atualiza os CSVs quando as views carregam os dados. Por isso, a primeira abertura pode levar alguns segundos e requer conectividade com a internet.

## Paginas disponíveis

- `/`: pagina inicial com indicadores e graficos gerais.
- `/analises/comparacao/`: comparacao entre dados da estacao e da Open-Meteo.
- `/analises/investigacao/`: investigacoes relacionadas a chuva e ponto de orvalho.
- `/eda/estatisticas/`: estatisticas descritivas das variaveis meteorologicas.
- `/eda/outliers/`: deteccao de valores atipicos.
- `/dados/registros/`: visualizacao dos registros consolidados.
- `/admin/`: area administrativa do Django.

## Arquivos de dados

Durante a execucao, o fluxo pode gerar ou atualizar:

- `dados_iot.csv`
- `dados_openmeteo.csv`
- `dados_meteorologicos.csv`

Esses arquivos sao escritos no diretorio de execucao conforme a implementacao atual. Para evitar erros de caminho, inicie o servidor a partir de `data_eda/`.

## Executar verificacoes

Para validar a configuracao do Django:

```powershell
python manage.py check
```

Para executar os testes do app:

```powershell
python manage.py test
```

## Observacoes

- A API IoT utilizada e `https://minimeteorolia-1.onrender.com/medicoes`.
- Os dados meteorologicos da Open-Meteo estao configurados para latitude `-22.9194` e longitude `-42.8186`.
- O projeto esta configurado para desenvolvimento (`DEBUG = True`). Nao use essa configuracao diretamente em producao.
- Se uma API externa estiver indisponivel, a coleta ou a exibicao do dashboard pode falhar. Verifique a conectividade e os logs do servidor Django.
