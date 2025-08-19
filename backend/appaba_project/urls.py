from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from terapia.views import PacienteViewSet, SessaoViewSet, AtividadeModeloViewSet, AtividadeSessaoViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'pacientes', PacienteViewSet)
router.register(r'sessoes', SessaoViewSet)
router.register(r'atividades_modelo', AtividadeModeloViewSet)
router.register(r'atividades_sessao', AtividadeSessaoViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('terapia.urls')),
    path('api/', include(router.urls)),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path("accounts/", include("django.contrib.auth.urls")),

]
