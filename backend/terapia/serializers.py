from rest_framework import serializers
from .models import Paciente, Sessao, AtividadeModelo, AtividadeSessao

class PacienteSerializer(serializers.ModelSerializer):
    terapeuta = serializers.ReadOnlyField(source='terapeuta.username')
    class Meta:
        model = Paciente
        fields = ['id', 'nome', 'data_nascimento', 'terapeuta']

class SessaoSerializer(serializers.ModelSerializer):
    terapeuta = serializers.ReadOnlyField(source='terapeuta.username')
    paciente_nome = serializers.ReadOnlyField(source='paciente.nome')
    class Meta:
        model = Sessao
        fields = ['id', 'paciente', 'paciente_nome', 'terapeuta', 'data_inicio', 'encerrada']

class AtividadeModeloSerializer(serializers.ModelSerializer):
    class Meta:
        model = AtividadeModelo
        fields = ['id', 'descricao', 'terapeuta']

class AtividadeSessaoSerializer(serializers.ModelSerializer):
    atividade_nome = serializers.ReadOnlyField(source='atividade_modelo.descricao')
    class Meta:
        model = AtividadeSessao
        fields = ['id', 'sessao', 'atividade_modelo', 'atividade_nome', 'detalhes', 'resposta', 'data_registro']
