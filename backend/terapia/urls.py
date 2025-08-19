from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.lista_pacientes, name='lista_pacientes'),
    path('adicionar/', views.adicionar_paciente, name='adicionar_paciente'),

    # Sessões
    path('iniciar_sessao/<int:paciente_id>/', views.iniciar_sessao, name='iniciar_sessao'),
    path('sessao/<int:sessao_id>/registrar/', views.registrar_atividades_sessao, name='registrar_atividades_sessao'),
    path('sessao/<int:sessao_id>/encerrar/', views.encerrar_sessao, name='encerrar_sessao'),
    path('paciente/<int:paciente_id>/historico/', views.historico_sessoes, name='historico_sessoes'),

    # Detalhes de atividade (por atividade da sessão)
    path('atividade_sessao/<int:atividade_sessao_id>/detalhes/', views.registrar_detalhes_atividade, name='registrar_detalhes_atividade'),

    # Atividades Modelo
    path('atividades_modelo/', views.lista_atividades_modelo, name='lista_atividades_modelo'),
    path('atividades_modelo/novo/', views.criar_atividade_modelo, name='criar_atividade_modelo'),
    path("atividade_modelo/", views.criar_atividade_modelo, name="form_atividade_modelo"),

]
