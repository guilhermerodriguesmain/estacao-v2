from django.urls import path

from . import views


urlpatterns = [

    path(
        "",
        views.home,
        name="home"
    ),
    path(
        "analises/comparacao/",
        views.comparacao,
        name="comparacao"
    ),
    path(
        "analises/investigacao/",
        views.investigacao,
        name="investigacao"
    ),
     path(
        "eda/estatisticas/",
        views.estatisticas,
        name="estatisticas"
    ),

    path(
        "eda/outliers/",
        views.outliers,
        name="outliers"
    ),

    # Dados
    path(
        "dados/registros/",
        views.registros,
        name="registros"
    ),
]
