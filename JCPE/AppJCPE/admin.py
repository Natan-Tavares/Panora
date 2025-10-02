from django.contrib import admin

# Register your models here.
from .models import Noticia, Resposta #, Usuario

admin.site.register(Noticia)
admin.site.register(Resposta)
#admin.site.register(Usuario)