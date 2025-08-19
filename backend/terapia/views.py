import os
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils.text import slugify

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .forms import PacienteForm, AtividadeSessaoForm, AtividadeModeloForm
from .models import Paciente, Sessao, AtividadeModelo, AtividadeSessao
from .serializers import (
    PacienteSerializer,
    SessaoSerializer,
    AtividadeModeloSerializer,
    AtividadeSessaoSerializer,
)


# =========================
# Páginas do Terapeuta
# =========================

@login_required
def dashboard(request):
    """Mostra sessões ativas do terapeuta (como estava no seu código original)."""
    sessoes_ativas = (
        Sessao.objects.filter(terapeuta=request.user, encerrada=False)
        .select_related("paciente")
        .order_by("-data_inicio")
    )
    return render(request, "terapia/dashboard.html", {"sessoes_ativas": sessoes_ativas})


@login_required
def lista_pacientes(request):
    pacientes = Paciente.objects.filter(terapeuta=request.user)
    return render(request, "terapia/lista_pacientes.html", {"pacientes": pacientes})


@login_required
def adicionar_paciente(request):
    if request.method == "POST":
        form = PacienteForm(request.POST)
        if form.is_valid():
            paciente = form.save(commit=False)
            paciente.terapeuta = request.user
            paciente.save()
            messages.success(request, "Paciente adicionado com sucesso.")
            return redirect("lista_pacientes")
        messages.error(request, "Formulário inválido. Verifique os campos.")
    else:
        form = PacienteForm()
    return render(request, "terapia/form_paciente.html", {"form": form})


@login_required
def historico_sessoes(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id, terapeuta=request.user)
    sessoes = Sessao.objects.filter(paciente=paciente).order_by("-data_inicio")
    return render(
        request,
        "terapia/historico_sessoes.html",
        {"paciente": paciente, "sessoes": sessoes},
    )


# =========================
# Sessões e Atividades
# =========================

@login_required
def iniciar_sessao(request, paciente_id):
    """
    Inicia uma sessão nova (se não houver ativa) e mostra a tela para selecionar
    as atividades modelo que serão usadas nesta sessão.
    """
    paciente = get_object_or_404(Paciente, id=paciente_id, terapeuta=request.user)

    # Já existe sessão ativa?
    sessao_ativa = Sessao.objects.filter(
        paciente=paciente, terapeuta=request.user, encerrada=False
    ).first()
    if sessao_ativa:
        messages.warning(request, "Já existe uma sessão ativa para este paciente.")
        return redirect("registrar_atividades_sessao", sessao_id=sessao_ativa.id)

    # Cria nova sessão e exibe seleção de atividades modelo
    sessao = Sessao.objects.create(paciente=paciente, terapeuta=request.user)
    atividades_modelo = AtividadeModelo.objects.filter(
        terapeuta=request.user
    ).order_by("descricao")

    return render(
        request,
        "terapia/selecionar_atividades_sessao.html",
        {"sessao": sessao, "atividades_modelo": atividades_modelo},
    )


@login_required
def registrar_atividades_sessao(request, sessao_id):
    """
    Página principal da sessão:
    - POST: adiciona atividades modelo selecionadas à sessão.
    - GET: lista atividades da sessão e também mostra atividades modelo disponíveis.
    Render usa 'terapia/registrar_atividade.html' como no seu projeto.
    """
    sessao = get_object_or_404(Sessao, id=sessao_id, terapeuta=request.user)

    if sessao.encerrada:
        messages.warning(request, "Sessão já encerrada.")
        return redirect("dashboard")

    if request.method == "POST":
        ids = request.POST.getlist("atividades")
        if not ids:
            messages.info(request, "Selecione ao menos uma atividade.")
        else:
            for atividade_id in ids:
                atividade_modelo = get_object_or_404(
                    AtividadeModelo, id=atividade_id, terapeuta=request.user
                )
                AtividadeSessao.objects.create(
                    sessao=sessao, atividade_modelo=atividade_modelo
                )
            messages.success(request, "Atividades adicionadas à sessão.")
        return redirect("registrar_atividades_sessao", sessao_id=sessao.id)

    atividades_sessao = AtividadeSessao.objects.filter(sessao=sessao).order_by(
        "-data_registro"
    )
    atividades_modelo = AtividadeModelo.objects.filter(
        terapeuta=request.user
    ).order_by("descricao")

    return render(
        request,
        "terapia/registrar_atividade.html",
        {
            "sessao": sessao,
            "atividades_modelo": atividades_modelo,
            "atividades_sessao": atividades_sessao,
        },
    )


@login_required
def registrar_detalhes_atividade(request, atividade_sessao_id):
    """
    Edita resposta (positiva/negativa) e detalhes da atividade da sessão.
    Corrigido o bug de sintaxe do else.
    """
    atividade_sessao = get_object_or_404(
        AtividadeSessao, id=atividade_sessao_id, sessao__terapeuta=request.user
    )

    if request.method == "POST":
        form = AtividadeSessaoForm(request.POST, instance=atividade_sessao)
        if form.is_valid():
            form.save()
            messages.success(request, "Detalhes da atividade atualizados.")

            # HTMX: devolve apenas a lista parcial
            if request.headers.get("HX-Request"):
                atividades = AtividadeSessao.objects.filter(
                    sessao=atividade_sessao.sessao
                ).order_by("-data_registro")
                return render(
                    request,
                    "terapia/_lista_atividades_sessao.html",
                    {"atividades": atividades},
                )

            return redirect(
                "registrar_atividades_sessao", sessao_id=atividade_sessao.sessao.id
            )
    else:
        form = AtividadeSessaoForm(instance=atividade_sessao)

    return render(
        request,
        "terapia/form_detalhes_atividade.html",
        {"form": form, "atividade": atividade_sessao},
    )


@login_required
def encerrar_sessao(request, sessao_id):
    """
    Encerra sessão. Se HTMX, retorna só o status parcial.
    Caso normal, gera relatório HTML em /media/reports e renderiza a página de relatório.
    """
    sessao = get_object_or_404(Sessao, id=sessao_id, terapeuta=request.user)

    if sessao.encerrada:
        messages.info(request, "Sessão já está encerrada.")
    else:
        sessao.encerrada = True
        sessao.save()
        messages.success(request, "Sessão encerrada com sucesso.")

    # HTMX: retorna somente o status
    if request.headers.get("HX-Request"):
        return render(request, "terapia/_status_sessao.html", {"sessao": sessao})

    # Relatório completo
    atividades = AtividadeSessao.objects.filter(sessao=sessao).order_by(
        "-data_registro"
    )

    # Diretório de reports
    media_root = getattr(settings, "MEDIA_ROOT", os.path.join(os.getcwd(), "media"))
    reports_dir = os.path.join(media_root, "reports")
    Path(reports_dir).mkdir(parents=True, exist_ok=True)

    paciente_nome = sessao.paciente.nome if sessao.paciente else "paciente"
    safe_nome = slugify(f"sessao-{sessao.id}-{paciente_nome}")
    filename = f"{safe_nome}.html"
    filepath = os.path.join(reports_dir, filename)

    # Renderiza HTML e salva no disco
    html_string = render_to_string(
        "terapia/relatorio_sessao.html",
        {"sessao": sessao, "atividades": atividades, "gerado_por": request.user},
    )
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_string)

    # URL pública
    media_url = getattr(settings, "MEDIA_URL", "/media/")
    report_url = os.path.join(media_url, "reports", filename)

    return render(
        request,
        "terapia/relatorio_sessao.html",
        {"sessao": sessao, "atividades": atividades, "report_url": report_url},
    )


# =========================
# Atividades Modelo
# =========================

@login_required
def lista_atividades_modelo(request):
    atividades = AtividadeModelo.objects.filter(terapeuta=request.user).order_by(
        "descricao"
    )
    return render(
        request, "terapia/lista_atividades_modelo.html", {"atividades": atividades}
    )


@login_required
def criar_atividade_modelo(request):
    if request.method == "POST":
        form = AtividadeModeloForm(request.POST)
        if form.is_valid():
            atividade = form.save(commit=False)
            atividade.terapeuta = request.user
            atividade.save()
            messages.success(request, "Atividade modelo criada com sucesso.")
            return redirect("lista_atividades_modelo")
    else:
        form = AtividadeModeloForm()
    return render(request, "terapia/form_atividade_modelo.html", {"form": form})


# =========================
# Autenticação
# =========================

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("dashboard")
        messages.error(request, "Usuário ou senha inválidos.")

    return render(request, "auth/login.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


# =========================
# API REST Framework (ViewSets)
# =========================

class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(terapeuta=self.request.user)

    def perform_create(self, serializer):
        serializer.save(terapeuta=self.request.user)


class SessaoViewSet(viewsets.ModelViewSet):
    queryset = Sessao.objects.all()
    serializer_class = SessaoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(terapeuta=self.request.user)

    def perform_create(self, serializer):
        serializer.save(terapeuta=self.request.user)


class AtividadeModeloViewSet(viewsets.ModelViewSet):
    queryset = AtividadeModelo.objects.all()
    serializer_class = AtividadeModeloSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(terapeuta=self.request.user)

    def perform_create(self, serializer):
        serializer.save(terapeuta=self.request.user)


class AtividadeSessaoViewSet(viewsets.ModelViewSet):
    queryset = AtividadeSessao.objects.all()
    serializer_class = AtividadeSessaoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(sessao__terapeuta=self.request.user)

    def perform_create(self, serializer):
        serializer.save()
 