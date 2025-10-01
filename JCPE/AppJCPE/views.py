from django.shortcuts import render
from .models import Noticia, Resposta
from django.contrib.auth.models import User
from django.utils.timezone import now
# Create your views here.

def criar_noticia(request):
    if request.method == "POST":
        titulo=request.POST.get("titulo")
        materia=request.POST.get("materia")
        autor=request.user
        data=now()
        Noticia.objects.create(titulo=titulo,materia=materia,autor=autor,data_criacao=data)
    
    return render(request,'criar_noticia.html')

def inicial(request):
    noticias=Noticia.objects.all()
    return render(request,'inicial.html', {'noticias':noticias})

