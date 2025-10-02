from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class Noticia(models.Model):
    titulo = models.CharField(max_length=200, null=False)
    materia = models.TextField(null=False)
    data_criacao = models.DateTimeField("Criado em ", auto_now_add=True)
    autor = models.CharField(max_length=200, null=False)
    
    def __str__(self):
        return "[" + str(self.id) + "] " + self.titulo

class Resposta(models.Model):
    noticia = models.ForeignKey(Noticia, on_delete=models.CASCADE)
    texto = models.TextField(null=False)
    data_criacao = models.DateTimeField("Criado em ", auto_now_add=True)
    usuario = models.CharField(max_length=200, null=False)

    def __str__(self):
        return "[" + str(self.id) + "] " + self.texto
    
'''class Usuario(AbstractUser):
    pass

    def __str__(self):
        return self.username
        '''