from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'pacientes', views.PacienteViewSet, basename='paciente')
router.register(r'sessoes', views.SessaoViewSet, basename='sessao')
router.register(r'atividades-modelo', views.AtividadeModeloViewSet, basename='atividade_modelo')
router.register(r'atividades-sessao', views.AtividadeSessaoViewSet, basename='atividade_sessao')

urlpatterns = [
    # Páginas principais
    path('', views.dashboard, name='dashboard'),
    path('pacientes/', views.lista_pacientes, name='lista_pacientes'),
    path('pacientes/adicionar/', views.adicionar_paciente, name='adicionar_paciente'),
    path('pacientes/<int:paciente_id>/historico/', views.historico_sessoes, name='historico_sessoes'),

    # Sessões
    path('sessao/<int:paciente_id>/iniciar/', views.iniciar_sessao, name='iniciar_sessao'),
    path('sessao/<int:sessao_id>/atividades/', views.registrar_atividades_sessao, name='registrar_atividades_sessao'),
    path('sessao/atividade/<int:atividade_sessao_id>/detalhes/', views.registrar_detalhes_atividade, name='registrar_detalhes_atividade'),
    path('sessao/<int:sessao_id>/encerrar/', views.encerrar_sessao, name='encerrar_sessao'),
    path('sessao/<int:sessao_id>/relatorio/', views.relatorio_sessao, name='relatorio_sessao'),

    # Atividades modelo
    path('atividades-modelo/', views.lista_atividades_modelo, name='lista_atividades_modelo'),
    path('atividades-modelo/criar/', views.criar_atividade_modelo, name='criar_atividade_modelo'),
    

    # Autenticação
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # API
    path('api/', include(router.urls)),
]
