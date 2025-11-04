from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Tags(models.Model):
    tag = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.tag}"

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
    # "pai" seria o comentario original e "filho" seriam as respostas a ele
    pai = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="comentarios_filho")
    data_criacao = models.DateTimeField("Criado em ", auto_now_add=True)
    usuario = models.CharField(max_length=200, null=False)

    def __str__(self):
        return "[" + str(self.id) + "] " + self.texto

class Historico(models.Model):
    noticia = models.ForeignKey(Noticia, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return f"usuario: {self.usuario.username} acessou {self.noticia}"
    
    
class Noticias_salvas(models.Model):
    noticia = models.ForeignKey(Noticia, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return f"usuario: {self.usuario.username} salvou {self.noticia}"
    
class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    foto = models.ImageField(upload_to='fotos_perfil/', blank=True, null=True)

    def __str__(self):
        return f"Perfil de {self.usuario.username}"


@receiver(post_save, sender=User)
def criar_ou_atualizar_perfil(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(usuario=instance)
    else:
        instance.perfil.save()


    
    '''
class Usuario_comum(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE,null=True)
    descricao = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.usuario.username
    '''
