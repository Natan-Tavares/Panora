from django.shortcuts import render,get_object_or_404,redirect
<<<<<<< HEAD
from .models import Noticia, Resposta, Historico,Noticias_salvas,Tag,Categoria
=======
from .models import Noticia, Resposta, Historico,Noticias_salvas,Tags,Categoria
from django.db.models import Q
>>>>>>> e249a81 (busca)
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
    todas_tags = Tag.objects.all() 
    categoria = Categoria.objects.all() 
    if request.method == "POST":
        titulo=request.POST.get("titulo")
        materia=request.POST.get("materia")
        autor=request.user
        tag_escolhida = request.POST.get('tag')
        tag = Tag.objects.get(id=tag_escolhida)
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
    todas_tags = Tag.objects.all() 
    categoria = Categoria.objects.all() 
    if request.method == "POST":
        noticia.titulo = request.POST.get("titulo")
        noticia.materia = request.POST.get("materia")
        noticia.subtitulo = request.POST.get("subtitulo")
        noticia.local = request.POST.get("local")
        noticia.fontes = request.POST.get("fontes")
        tag_escolhida = request.POST.get('tag')
        tag = Tag.objects.get(id=tag_escolhida)
        cat_id=request.POST.get("categoria")
        noticia.categoria = Categoria.objects.get(id=cat_id) if cat_id else None
        if 'imagem' in request.FILES:
            noticia.imagem = request.FILES['imagem']
        if 'capa' in request.FILES:
            noticia.capa = request.FILES['capa']
        if tag_escolhida:
            tag = Tag.objects.get(id=tag_escolhida)
            noticia.tags.set([tag])
        noticia.save()
        return redirect('inicial')
    
    return render(request,'editar_noticia.html', {'noticia': noticia,'tags': todas_tags, 'categorias':categoria})

def inicial(request):
    id_tag = request.GET.get("tag")
    q = request.GET.get("q", "").strip()
    noticias=Noticia.objects.all().order_by('-data_criacao')
    if id_tag:
        noticias = noticias.filter(tags__id=id_tag)
<<<<<<< HEAD
    todas_tags = Tag.objects.all() 
=======
    if q:
        noticias = noticias.filter(
            Q(titulo__icontains=q) |
            Q(subtitulo__icontains=q) |
            Q(materia__icontains=q) |
            Q(tags__tag__icontains=q)
        ).distinct()
        # guarda historico simples de buscas recentes em sessao
        recent = request.session.get("recent_searches", [])
        recent = [q] + [term for term in recent if term.lower() != q.lower()]
        request.session["recent_searches"] = recent[:5]
    recent_searches = request.session.get("recent_searches", [])
    todas_tags = Tags.objects.all() 
>>>>>>> e249a81 (busca)
    noticias_salvas_ids = []
    if request.user.is_authenticated:
        noticias_salvas_ids = Noticias_salvas.objects.filter(usuario=request.user).values_list('noticia_id', flat=True)
    return render(
        request,
        'inicial.html',
        {
            'noticias': noticias,
            'tags': todas_tags,
            'noticias_salvas_ids': noticias_salvas_ids,
            'recent_searches': recent_searches,
            'q': q,
        }
    )

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
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("inicial")
        else:
            messages.error(request, "Usuário ou senha incorretos.")

    return render(request, "login.html")


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

@login_required(login_url='login')
def salvar_noticia(request,id):
    noticia_individual = get_object_or_404(Noticia, id=id)
    if request.method=="POST":
        usuario=request.user
        Noticias_salvas.objects.get_or_create(noticia=noticia_individual,usuario=usuario)
    return redirect('ler_noticia',id=id)


@login_required(login_url='login')
def vizualizar_noticias_salvas(request):
    usuario = request.user
    noticias=Noticias_salvas.objects.filter(usuario=usuario)
    return render(request,'noticias_salvas.html', {'noticias_salvas': noticias})



@login_required(login_url='login')
def remover_noticias_salvas(request,id):
    usuario = request.user
    noticias=Noticias_salvas.objects.filter(id=id,usuario=usuario)
    if request.method == 'POST':
        noticias.delete()
    return redirect('vizualizar_salvos')

@login_required(login_url='login')

def curtir_resposta(request,resposta_id):
    resposta =  get_object_or_404(Resposta, id=resposta_id)

    if request.user in resposta.curtidas.all():
        resposta.curtidas.remove(request.user)

    else:
        resposta.curtidas.add(request.user)

    
    return redirect(request.META.get('HTTP_REFERER', 'inicial'))

@login_required(login_url='login')
def denunciar_comentario(request, resposta_id):
    resposta = get_object_or_404(Resposta, id=resposta_id)

    resposta.denuncias += 1
    resposta.save()

    messages.success(request, "Comentário denunciado com sucesso!")


    return redirect(request.META.get('HTTP_REFERER', 'inicial'))



def conta(request):
    return render(request, 'conta.html')

@login_required(login_url='login')
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
        Tag.objects.get_or_create(tag=tag)
    tags=Tag.objects.all()
    
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

# views.py
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import json

@login_required
@require_POST
def update_profile(request):
    """Atualiza informações do perfil do usuário."""
    try:
        data = json.loads(request.body)
        field = data.get('field')
        value = data.get('value')
        
        user = request.user
        
        if field == 'username':
            if value != user.username:
                # Verificar se o username já existe
                from django.contrib.auth.models import User
                if User.objects.filter(username=value).exclude(id=user.id).exists():
                    return JsonResponse({
                        'success': False, 
                        'error': 'Este nome de usuário já está em uso.'
                    })
                user.username = value
        
        elif field == 'email':
            if value != user.email:
                # Verificar se o email já existe
                from django.contrib.auth.models import User
                if User.objects.filter(email=value).exclude(id=user.id).exists():
                    return JsonResponse({
                        'success': False, 
                        'error': 'Este e-mail já está em uso.'
                    })
                user.email = value
        
        elif field == 'password':
            user.set_password(value)
        
        user.save()
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
def update_profile_photo(request):
    """Atualiza a foto de perfil do usuário."""
    try:
        avatar = request.FILES.get('avatar')
        if avatar:
            # Verificar se o arquivo é uma imagem
            if not avatar.content_type.startswith('image/'):
                return JsonResponse({
                    'success': False, 
                    'error': 'O arquivo deve ser uma imagem.'
                })
            
            # Verificar tamanho do arquivo (máximo 5MB)
            if avatar.size > 5 * 1024 * 1024:
                return JsonResponse({
                    'success': False, 
                    'error': 'A imagem deve ter no máximo 5MB.'
                })
            
            # Aqui você precisaria ter um modelo Profile com campo avatar
            # Exemplo:
            # profile, created = Profile.objects.get_or_create(user=request.user)
            # profile.avatar = avatar
            # profile.save()
            
            # Por enquanto, apenas simular sucesso
            return JsonResponse({
                'success': True,
                'avatar_url': '/media/avatars/default.png'  # URL da imagem padrão
            })
        
        return JsonResponse({
            'success': False, 
            'error': 'Nenhuma imagem enviada.'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
def update_user_tags(request):
    """Atualiza as tags de interesse do usuário."""
    try:
        data = json.loads(request.body)
        tag_id = data.get('tag_id')
        action = data.get('action')  # 'add' ou 'remove'
        
        # Aqui você implementaria a lógica para adicionar/remover tags
        # Exemplo com modelo Tag:
        # 
        # from .models import Tag
        # try:
        #     tag = Tag.objects.get(id=tag_id)
        #     if action == 'add':
        #         request.user.tags.add(tag)
        #     else:
        #         request.user.tags.remove(tag)
        #     return JsonResponse({'success': True})
        # except Tag.DoesNotExist:
        #     return JsonResponse({'success': False, 'error': 'Tag não encontrada.'})
        
        # Por enquanto, apenas simular sucesso
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})