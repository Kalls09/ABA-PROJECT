from django import forms
from .models import Paciente, Sessao, AtividadeModelo, AtividadeSessao

# =========================
# Pacientes e Sessões
# =========================
class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['nome', 'data_nascimento']


class SessaoForm(forms.ModelForm):
    class Meta:
        model = Sessao
        fields = []  # Ajuste se quiser campos editáveis


# =========================
# Atividades Modelo
# =========================
class AtividadeModeloForm(forms.ModelForm):
    class Meta:
        model = AtividadeModelo
        fields = ['descricao']  # O positivo/negativo é decidido na sessão


# =========================
# Atividades da Sessão
# =========================
class AtividadeSessaoForm(forms.ModelForm):
    class Meta:
        model = AtividadeSessao
        fields = ['resposta', 'detalhes']  # Resposta da sessão + observações
