from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Tags(models.Model):
    tag = models.CharField(max_length=50)

    def __str__(self):
        return f"[{self.tag}]"

class Noticia(models.Model):
    titulo = models.CharField(max_length=200, null=False)
    materia = models.TextField(null=False)
    data_criacao = models.DateTimeField("Criado em ", auto_now_add=True)
    autor = models.CharField(max_length=200, null=False)
    tag = models.ForeignKey(Tags, on_delete=models.CASCADE,null=True)
    
    def __str__(self):
        return "[" + str(self.id) + "] " + self.titulo

class Resposta(models.Model):
    noticia = models.ForeignKey(Noticia, on_delete=models.CASCADE)
    texto = models.TextField(null=False)
    data_criacao = models.DateTimeField("Criado em ", auto_now_add=True)
    usuario = models.CharField(max_length=200, null=False)

    def __str__(self):
        return "[" + str(self.id) + "] " + self.texto
    '''
class Usuario_comum(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE,null=True)
    descricao = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.usuario.username if self.usuario else "Usuário sem conta"'''
