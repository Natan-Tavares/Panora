from django.shortcuts import render,get_object_or_404,redirect
from .models import Noticia, Resposta
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.views import View
from django.utils import timezone
from django.http import HttpResponse, Http404
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

def ler_noticia(request,id):
    noticia_individual = get_object_or_404(Noticia, id=id)
    return render(request,'noticia.html', {'noticia':noticia_individual})

def apagar_noticia(request,id):
    noticia_individual = get_object_or_404(Noticia, id=id)
    if request.method == 'POST':
        noticia_individual.delete()
        return redirect('/')
    return render(request, 'apagar_noticia.html', {'noticia': noticia_individual})

class InserirRespostaView(View):
    def get(self, request, noticia_id):
        try:
            noticia = Noticia.objects.get(pk=noticia_id)
        except Noticia.DoesNotExist:
            raise Http404("Noticia inexistente")
        contexto = {'noticia' : noticia}
        return render(request, 'inserir_resposta.html', contexto)

    def post(self, request, noticia_id):
        try:
            noticia = Noticia.objects.get(pk=noticia_id)
        except Noticia.DoesNotExist:
            raise Http404("Noticia inexistente")

        if request.user.is_authenticated:
            usuario = request.user.username
        else:
            usuario = 'anônimo'
        texto = request.POST.get('texto')
        data_criacao = timezone.now()
        
        noticia.resposta_set.create(texto=texto, data_criacao=data_criacao, usuario=usuario)

        return redirect('ler_noticia', id=noticia.id)