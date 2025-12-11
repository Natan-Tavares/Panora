from django.shortcuts import render,get_object_or_404,redirect
from .models import Noticia, Resposta, Historico,Noticias_salvas,Tags,Categoria
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.utils.timezone import now
from django.views import View
from django.utils import timezone
from django.http import HttpResponse, Http404
from rest_framework import viewsets
from .serializers import RespostaSerializer
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.

def criar_noticia(request):
    todas_tags = Tags.objects.all() 
    categoria = Categoria.objects.all() 
    if request.method == "POST":
        titulo=request.POST.get("titulo")
        materia=request.POST.get("materia")
        autor=request.user
        tag_escolhida = request.POST.get('tag')
        tag = Tags.objects.get(id=tag_escolhida)
        data=now()
        local=request.POST.get("local")
        fontes=request.POST.get("fontes")
        subtitulo=request.POST.get("subtitulo")
        cat_id=request.POST.get("categoria")
        cat = Categoria.objects.get(id=cat_id)if cat_id else None
        imagem = request.FILES.get("imagem")
        capa = request.FILES.get("capa")
        noticia = Noticia.objects.create(
                            titulo=titulo,
                            subtitulo=subtitulo,
                            materia=materia,
                            autor=autor,
                            data_criacao=data,
                            local=local,
                            fontes=fontes,
                            categoria=cat,
                            imagem=imagem,
                            capa=capa
                        )
        noticia.tags.add(tag)
    
    return render(request,'criar_noticia.html', {'tags': todas_tags, 'categorias':categoria})


def editar_noticia(request,id):
    noticia = get_object_or_404(Noticia, id=id)
    todas_tags = Tags.objects.all() 
    categoria = Categoria.objects.all() 
    if request.method == "POST":
        noticia.titulo = request.POST.get("titulo")
        noticia.materia = request.POST.get("materia")
        noticia.subtitulo = request.POST.get("subtitulo")
        noticia.local = request.POST.get("local")
        noticia.fontes = request.POST.get("fontes")
        tag_escolhida = request.POST.get('tag')
        tag = Tags.objects.get(id=tag_escolhida)
        cat_id=request.POST.get("categoria")
        noticia.categoria = Categoria.objects.get(id=cat_id) if cat_id else None
        if 'imagem' in request.FILES:
            noticia.imagem = request.FILES['imagem']
        if 'capa' in request.FILES:
            noticia.capa = request.FILES['capa']
        if tag_escolhida:
            tag = Tags.objects.get(id=tag_escolhida)
            noticia.tags.set([tag])
        noticia.save()
        return redirect('inicial')
    
    return render(request,'editar_noticia.html', {'noticia': noticia,'tags': todas_tags, 'categorias':categoria})

def inicial(request):
    id_tag = request.GET.get("tag")
    noticias=Noticia.objects.all()
    if id_tag:
        noticias = noticias.filter(tags__id=id_tag)
    todas_tags = Tags.objects.all() 
    return render(request, 'inicial.html', {'noticias': noticias, 'tags': todas_tags})

def ler_noticia(request,id):
    noticia_individual = get_object_or_404(Noticia, id=id)
    if request.user.is_authenticated:
        usuario=request.user
        Historico.objects.create(noticia=noticia_individual,usuario=usuario)

    return render(request,'noticia.html', {'noticia':noticia_individual})

def apagar_noticia(request,id):
    noticia_individual = get_object_or_404(Noticia, id=id)
    if request.method == 'POST':
        noticia_individual.delete()
        return redirect('/')
    return render(request, 'apagar_noticia.html', {'noticia': noticia_individual})

class InserirRespostaView(View):
    def get(self, request, noticia_id):
        if not request.user.is_authenticated:
            return redirect('login')
            
        try:
            noticia = Noticia.objects.get(pk=noticia_id)
        except Noticia.DoesNotExist:
            raise Http404("Noticia inexistente")
        
        pai_id = request.GET.get("pai")
        pai = None
        if pai_id:
            try:
                pai = Resposta.objects.get(pk=pai_id)
            except Resposta.DoesNotExist:
                pai = None

        contexto = {'noticia' : noticia,
                    'pai' : pai
                    }
        return render(request, 'inserir_resposta.html', contexto)

    def post(self, request, noticia_id):
        if not request.user.is_authenticated:
            return redirect('login')

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

        pai_id = request.GET.get("pai")
        pai = None
        if pai_id:
            try:
                pai = Resposta.objects.get(pk=pai_id)
            except Resposta.DoesNotExist:
                pai = None
        
        noticia.resposta_set.create(texto=texto, data_criacao=data_criacao, usuario=usuario, pai=pai)

        return redirect('ler_noticia', id=noticia.id)
    
def cadastro(request):
    if request.method == "GET":
        return render(request, 'cadastro.html')
    
    username = request.POST.get("username")
    email = request.POST.get("email")
    senha = request.POST.get("senha")

    user = User.objects.filter(username=username).first()

    if user:
        return render(request, 'mensagem.html', {
            'titulo': 'Usuário já existe',
            'mensagem': 'Esse nome de usuário já está sendo usado.',
            'link': '/login',
            'link_text': 'Fazer login'
        })

    user = User.objects.create_user(username=username, email=email, password=senha)
    user.save()

    return render(request, 'mensagem.html', {
        'titulo': 'Usuário criado com sucesso!',
        'mensagem': 'Sua conta foi criada. Agora você pode fazer login.',
        'link': '/login',
        'link_text': 'Fazer login'
    })


def login_view(request):
    if request.method == "GET":
        return render(request, 'login.html')
    
    username = request.POST.get("username")
    senha = request.POST.get("senha")

    user = authenticate(request, username=username, password=senha)

    if user:
        login(request, user)
        return render(request, 'mensagem.html', {
            'titulo': 'Usuário autenticado com sucesso!',
            'mensagem': 'Bem-vindo(a) de volta.',
            'link': '/',
            'link_text': 'Ir para página inicial'
        })
    else:
        return render(request, 'mensagem.html', {
            'titulo': 'Erro no login',
            'mensagem': 'Usuário ou senha inválidos.',
            'link': '/login',
            'link_text': 'Tentar novamente'
        })
    
def deslogar(request):
    logout(request)
    return redirect('login')

class RespostaViewSet(viewsets.ModelViewSet):
    queryset = Resposta.objects.all()
    serializer_class = RespostaSerializer

    def perform_create(self, serializer):
        # verifica se é pai
        parent_id = self.request.data.get("pai")
        parent = Resposta.objects.get(id=parent_id) if parent_id else None
        serializer.save(usuario=self.request.user, pai=parent)

@login_required
def salvar_noticia(request,id):
    noticia_individual = get_object_or_404(Noticia, id=id)
    if request.method=="POST":
        usuario=request.user
        Noticias_salvas.objects.get_or_create(noticia=noticia_individual,usuario=usuario)
    return redirect('ler_noticia',id=id)


@login_required
def vizualizar_noticias_salvas(request):
    usuario = request.user
    noticias=Noticias_salvas.objects.filter(usuario=usuario)
    return render(request,'noticias_salvas.html', {'noticias_salvas': noticias})



@login_required
def remover_noticias_salvas(request,id):
    usuario = request.user
    noticias=Noticias_salvas.objects.filter(id=id,usuario=usuario)
    if request.method == 'POST':
        noticias.delete()
    return redirect('vizualizar_salvos')

@login_required

def curtir_resposta(request,resposta_id):
    resposta =  get_object_or_404(Resposta, id=resposta_id)

    if request.user in resposta.curtidas.all():
        resposta.curtidas.remove(request.user)

    else:
        resposta.curtidas.add(request.user)

    
    return redirect(request.META.get('HTTP_REFERER', 'inicial'))

@login_required
def denunciar_comentario(request, resposta_id):
    resposta = get_object_or_404(Resposta, id=resposta_id)

    resposta.denuncias += 1
    resposta.save()

    messages.success(request, "Comentário denunciado com sucesso!")


    return redirect(request.META.get('HTTP_REFERER', 'inicial'))

@login_required
def conta(request):

    usuario = request.user
    noticias_salvas = Noticias_salvas.objects.filter(usuario=usuario)

    context = {
        'noticias_salvas': noticias_salvas,
        'tags': Tags.objects.all(),
        'colunistas': None   
    }

    return render(request, 'conta.html', context)

@login_required
def editar_perfil(request):
    user = request.user
    perfil = user.perfil  # vem do OneToOneField

    if request.method == "POST":
        user.username = request.POST.get("username")
        user.email = request.POST.get("email")

        if 'foto' in request.FILES:
            perfil.foto = request.FILES['foto']

        user.save()
        perfil.save()
        return redirect("conta")

    return render(request, "editar_perfil.html", {"perfil": perfil})


def criar_tag(request):
    if request.method == "POST":
        tag=request.POST.get("tag")
        Tags.objects.get_or_create(tag=tag)
    tags=Tags.objects.all()
    
    return render(request,'Criar_tag.html',{'tags':tags})

def criar_categoria(request):
    if request.method == "POST":
        cat=request.POST.get("categoria")
        Categoria.objects.get_or_create(categoria=cat)
    cats=Categoria.objects.all()
    
    return render(request,'Criar_categoria.html',{'cats':cats})

def noticias_por_categoria(request, id):
    categoria = Categoria.objects.get(id=id)
    noticias = Noticia.objects.filter(categoria=categoria)

    return render(request, 'noticias_por_categoria.html', {
        'categoria': categoria,
        'noticias': noticias
    })


