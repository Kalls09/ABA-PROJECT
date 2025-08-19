from django.db import models
from django.contrib.auth.models import User

class Paciente(models.Model):
    nome = models.CharField(max_length=100)
    data_nascimento = models.DateField(null=True, blank=True)
    terapeuta = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome


class Sessao(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    terapeuta = models.ForeignKey(User, on_delete=models.CASCADE)
    data_inicio = models.DateTimeField(auto_now_add=True)
    encerrada = models.BooleanField(default=False)

    def __str__(self):
        return f"Sessão de {self.paciente.nome} em {self.data_inicio.strftime('%d/%m/%Y')}"


class AtividadeModelo(models.Model):
    """Atividades que o terapeuta cadastra para selecionar nas sessões."""
    descricao = models.CharField(max_length=200)
    terapeuta = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.descricao


class AtividadeSessao(models.Model):
    """Atividades selecionadas para uma sessão específica."""
    sessao = models.ForeignKey(Sessao, on_delete=models.CASCADE)
    atividade_modelo = models.ForeignKey(AtividadeModelo, on_delete=models.CASCADE)
    detalhes = models.TextField(blank=True, null=True)  # Observações específicas da sessão
    data_registro = models.DateTimeField(auto_now_add=True)

    RESPOSTAS_CHOICES = [
        ('positiva', 'Positiva'),
        ('negativa', 'Negativa'),
    ]
    resposta = models.CharField(max_length=10, choices=RESPOSTAS_CHOICES, default='positiva')

    def __str__(self):
        return f"{self.sessao.paciente.nome} - {self.atividade_modelo.descricao} ({self.resposta})"
