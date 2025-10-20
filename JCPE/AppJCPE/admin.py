from django.contrib import admin

# Register your models here.
from .models import Noticia, Resposta, Tags, Historico#, Usuario_comum

admin.site.register(Noticia)
admin.site.register(Resposta)
admin.site.register(Tags)
admin.site.register(Historico)
'''
admin.site.register(Usuario_comum)
'''