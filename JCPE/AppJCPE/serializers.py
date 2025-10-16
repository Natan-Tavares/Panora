# forum/serializers.py
from rest_framework import serializers
from .models import Resposta

class RespostaSerializer(serializers.ModelSerializer):
    comentarios_filho = serializers.SerializerMethodField()

    class Meta:
        model = Resposta
        fields = ["id", "noticia", "texto", "pai", "data_criacao", "usuario", "comentarios_filho"]

    def get_comentarios_filho(self, obj):
        return RespostaSerializer(obj.comentarios_filho.all(), many=True).data