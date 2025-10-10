from django.contrib import admin

# Register your models here.
from .models import Noticia, Resposta, Tags#, Usuario_comum

admin.site.register(Noticia)
admin.site.register(Resposta)
admin.site.register(Tags)
'''
admin.site.register(Usuario_comum)
'''