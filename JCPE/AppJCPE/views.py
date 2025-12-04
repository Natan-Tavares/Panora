from django.shortcuts import render, get_object_or_404, redirect
from .models import Noticia, Resposta, Historico, Noticias_salvas, Tag, Categoria
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.utils.timezone import now
from django.views import View
from django.utils import timezone
from django.http import HttpResponse, Http404, JsonResponse
from rest_framework import viewsets
from .serializers import RespostaSerializer
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
import json
from datetime import datetime, timedelta

# ---------------------------
# CRIAR NOTICIA
# ---------------------------
def criar_noticia(request):
    todas_tags = Tag.objects.all()
    categoria = Categoria.objects.all()

    if request.method == "POST":
        titulo = request.POST.get("titulo")
        materia = request.POST.get("materia")
        autor = request.user
        tag_escolhida = request.POST.get('tag')
        tag = Tag.objects.get(id=tag_escolhida)
        data = now()
        local = request.POST.get("local")
        fontes = request.POST.get("fontes")
        subtitulo = request.POST.get("subtitulo")
        cat_id = request.POST.get("categoria")
        cat = Categoria.objects.get(id=cat_id) if cat_id else None
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

    return render(request, 'criar_noticia.html', {'tags': todas_tags, 'categorias': categoria})


# ---------------------------
# EDITAR NOTÍCIA
# ---------------------------
def editar_noticia(request, id):
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
        if tag_escolhida:
            tag = Tag.objects.get(id=tag_escolhida)
            noticia.tags.set([tag])

        cat_id = request.POST.get("categoria")
        noticia.categoria = Categoria.objects.get(id=cat_id) if cat_id else None

        if 'imagem' in request.FILES:
            noticia.imagem = request.FILES['imagem']

        if 'capa' in request.FILES:
            noticia.capa = request.FILES['capa']

        noticia.save()
        return redirect('inicial')

    return render(request, 'editar_noticia.html', {'noticia': noticia, 'tags': todas_tags, 'categorias': categoria})


# ---------------------------
# INICIAL / FEED
# ---------------------------
# ---------------------------
# INICIAL / FEED
# ---------------------------
def inicial(request):
    id_tag = request.GET.get("tag")
    q = request.GET.get("q", "").strip()

    noticias = Noticia.objects.all().order_by('-data_criacao')

    # filtra por tag
    if id_tag:
        noticias = noticias.filter(tags__id=id_tag)

    # filtra por busca
    if q:
        noticias = noticias.filter(
            Q(titulo__icontains=q) |
            Q(subtitulo__icontains=q) |
            Q(materia__icontains=q) |
            Q(tags__tag__icontains=q)
        ).distinct()

        # salva histórico de busca na sessão
        recent = request.session.get("recent_searches", [])
        recent = [q] + [term for term in recent if term.lower() != q.lower()]
        request.session["recent_searches"] = recent[:5]

    recent_searches = request.session.get("recent_searches", [])
    todas_tags = Tag.objects.all()
    categorias = Categoria.objects.all()  # NOVA LINHA ADICIONADA

    noticias_salvas_ids = []
    if request.user.is_authenticated:
        noticias_salvas_ids = Noticias_salvas.objects.filter(
            usuario=request.user
        ).values_list('noticia_id', flat=True)

    return render(
        request,
        'inicial.html',
        {
            'noticias': noticias,
            'tags': todas_tags,
            'categorias': categorias,  # NOVA LINHA ADICIONADA
            'noticias_salvas_ids': noticias_salvas_ids,
            'recent_searches': recent_searches,
            'q': q,
        }
    )

# ---------------------------
# ÚLTIMAS NOTÍCIAS COM FILTRO DE DATA
# ---------------------------
def ultimas_noticias(request):
    from datetime import datetime, timedelta
    
    # Obter parâmetros de data da URL
    data_inicio_str = request.GET.get('data_inicio', '')
    data_fim_str = request.GET.get('data_fim', '')
    
    # Começar com todas as notícias ordenadas por data (mais recentes primeiro)
    noticias = Noticia.objects.all().order_by('-data_criacao')
    
    # Converter strings de data para objetos date se existirem
    data_inicio = None
    data_fim = None
    
    if data_inicio_str:
        try:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
            # Filtrar notícias a partir da data de início
            noticias = noticias.filter(data_criacao__date__gte=data_inicio)
        except ValueError:
            pass
    
    if data_fim_str:
        try:
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
            # Adicionar 1 dia para incluir todo o dia final
            data_fim_plus_one = data_fim + timedelta(days=1)
            # Filtrar notícias até a data final
            noticias = noticias.filter(data_criacao__date__lt=data_fim_plus_one)
        except ValueError:
            pass
    
    # IDs das notícias salvas (se usuário logado)
    noticias_salvas_ids = []
    if request.user.is_authenticated:
        noticias_salvas_ids = Noticias_salvas.objects.filter(
            usuario=request.user
        ).values_list('noticia_id', flat=True)
    
    return render(request, 'ultimas_noticias.html', {
        'noticias': noticias,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'noticias_salvas_ids': noticias_salvas_ids,
    })

# ---------------------------
# LER NOTÍCIA
# ---------------------------
# views.py - ATUALIZAR a função ler_noticia

def ler_noticia(request, id):
    noticia_individual = get_object_or_404(Noticia, id=id)
    
    # Salvar no histórico se usuário autenticado
    if request.user.is_authenticated:
        Historico.objects.create(noticia=noticia_individual, usuario=request.user)
    
    # Buscar comentários principais (sem pai)
    comentarios = Resposta.objects.filter(noticia=noticia_individual, pai__isnull=True).order_by('-data_criacao')
    
    # Contar total de comentários
    total_comentarios = Resposta.objects.filter(noticia=noticia_individual).count()
    
    # Verificar se notícia está salva pelo usuário
    salva = False
    if request.user.is_authenticated:
        salva = Noticias_salvas.objects.filter(noticia=noticia_individual, usuario=request.user).exists()
    
    # Buscar tags da notícia
    tags_noticia = noticia_individual.tags.all()
    
    # Notícias relacionadas (mesma categoria ou tags)
    noticias_relacionadas = Noticia.objects.filter(
        Q(categoria=noticia_individual.categoria) |
        Q(tags__in=tags_noticia)
    ).exclude(id=noticia_individual.id).distinct()[:5]
    
    # Buscar tags para o menu lateral
    todas_tags = Tag.objects.all()
    
    return render(request, 'noticia.html', {  # <- MUDADO para 'noticia.html'
        'noticia': noticia_individual,
        'comentarios': comentarios,
        'total_comentarios': total_comentarios,
        'salva': salva,
        'tags_noticia': tags_noticia,
        'noticias_relacionadas': noticias_relacionadas,
        'tags': todas_tags  # Para o menu lateral
    })


# ---------------------------
# APAGAR NOTÍCIA
# ---------------------------
def apagar_noticia(request, id):
    noticia_individual = get_object_or_404(Noticia, id=id)
    if request.method == 'POST':
        noticia_individual.delete()
        return redirect('/')
    return render(request, 'apagar_noticia.html', {'noticia': noticia_individual})


# ---------------------------
# INSERIR RESPOSTA (COMENTÁRIO)
# ---------------------------
class InserirRespostaView(View):
    def get(self, request, noticia_id):
        if not request.user.is_authenticated:
            return redirect('login')

        noticia = get_object_or_404(Noticia, pk=noticia_id)

        pai_id = request.GET.get("pai")
        pai = Resposta.objects.filter(pk=pai_id).first() if pai_id else None

        return render(request, 'inserir_resposta.html', {'noticia': noticia, 'pai': pai})

    def post(self, request, noticia_id):
        if not request.user.is_authenticated:
            return redirect('login')

        noticia = get_object_or_404(Noticia, pk=noticia_id)

        usuario = request.user.username
        texto = request.POST.get('texto')
        data_criacao = timezone.now()

        pai_id = request.GET.get("pai")
        pai = Resposta.objects.filter(pk=pai_id).first() if pai_id else None

        noticia.resposta_set.create(
            texto=texto,
            data_criacao=data_criacao,
            usuario=usuario,
            pai=pai
        )

        return redirect('ler_noticia', id=noticia.id)


# ---------------------------
# CADASTRO
# ---------------------------
def cadastro(request):
    if request.method == "GET":
        return render(request, 'cadastro.html')

    username = request.POST.get("username")
    email = request.POST.get("email")
    senha = request.POST.get("senha")

    if User.objects.filter(username=username).exists():
        return render(request, 'mensagem.html', {
            'titulo': 'Usuário já existe',
            'mensagem': 'Esse nome de usuário já está sendo usado.',
            'link': '/login',
            'link_text': 'Fazer login'
        })

    User.objects.create_user(username=username, email=email, password=senha)

    return render(request, 'mensagem.html', {
        'titulo': 'Usuário criado com sucesso!',
        'mensagem': 'Sua conta foi criada. Agora você pode fazer login.',
        'link': '/login',
        'link_text': 'Fazer login'
    })


# ---------------------------
# LOGIN / LOGOUT
# ---------------------------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("inicial")

        messages.error(request, "Usuário ou senha incorretos.")

    return render(request, "login.html")


def deslogar(request):
    logout(request)
    return redirect('login')


# ---------------------------
# API RESPOSTAS
# ---------------------------
class RespostaViewSet(viewsets.ModelViewSet):
    queryset = Resposta.objects.all()
    serializer_class = RespostaSerializer

    def perform_create(self, serializer):
        parent_id = self.request.data.get("pai")
        parent = Resposta.objects.filter(id=parent_id).first() if parent_id else None
        serializer.save(usuario=self.request.user, pai=parent)


# ---------------------------
# SALVAR NOTÍCIA
# ---------------------------
@login_required(login_url='login')
def salvar_noticia(request, id):
    noticia_individual = get_object_or_404(Noticia, id=id)

    if request.method == "POST":
        Noticias_salvas.objects.get_or_create(
            noticia=noticia_individual,
            usuario=request.user
        )

    return redirect('ler_noticia', id=id)


# ---------------------------
# VISUALIZAR NOTÍCIAS SALVAS
# ---------------------------
@login_required(login_url='login')
def vizualizar_noticias_salvas(request):
    noticias = Noticias_salvas.objects.filter(usuario=request.user)
    return render(request, 'noticias_salvas.html', {'noticias_salvas': noticias})


@login_required(login_url='login')
def remover_noticias_salvas(request, id):
    noticias = Noticias_salvas.objects.filter(id=id, usuario=request.user)

    if request.method == 'POST':
        noticias.delete()

    return redirect('vizualizar_salvos')


# ---------------------------
# CURTIR RESPOSTA
# ---------------------------
@login_required(login_url='login')
def curtir_resposta(request, resposta_id):
    resposta = get_object_or_404(Resposta, id=resposta_id)

    if request.user in resposta.curtidas.all():
        resposta.curtidas.remove(request.user)
    else:
        resposta.curtidas.add(request.user)

    return redirect(request.META.get('HTTP_REFERER', 'inicial'))


# ---------------------------
# DENUNCIAR COMENTÁRIO
# ---------------------------
@login_required(login_url='login')
def denunciar_comentario(request, resposta_id):
    resposta = get_object_or_404(Resposta, id=resposta_id)

    resposta.denuncias += 1
    resposta.save()

    messages.success(request, "Comentário denunciado com sucesso!")
    return redirect(request.META.get('HTTP_REFERER', 'inicial'))


# ---------------------------
# CONTA / EDITAR PERFIL
# ---------------------------
def conta(request):
    return render(request, 'conta.html')


@login_required(login_url='login')
def editar_perfil(request):
    user = request.user
    perfil = user.perfil

    if request.method == "POST":
        user.username = request.POST.get("username")
        user.email = request.POST.get("email")

        if 'foto' in request.FILES:
            perfil.foto = request.FILES['foto']

        user.save()
        perfil.save()
        return redirect("conta")

    return render(request, "editar_perfil.html", {"perfil": perfil})


# ---------------------------
# CRIAR TAG
# ---------------------------
def criar_tag(request):
    if request.method == "POST":
        tag = request.POST.get("tag")
        Tag.objects.get_or_create(tag=tag)

    tags = Tag.objects.all()
    return render(request, 'Criar_tag.html', {'tags': tags})


# ---------------------------
# CRIAR CATEGORIA
# ---------------------------
def criar_categoria(request):
    if request.method == "POST":
        cat = request.POST.get("categoria")
        Categoria.objects.get_or_create(categoria=cat)

    cats = Categoria.objects.all()
    return render(request, 'Criar_categoria.html', {'cats': cats})


# ---------------------------
# NOTÍCIAS POR CATEGORIA
# ---------------------------
def noticias_por_categoria(request, id):
    categoria = Categoria.objects.get(id=id)
    noticias = Noticia.objects.filter(categoria=categoria)

    return render(request, 'noticias_por_categoria.html', {
        'categoria': categoria,
        'noticias': noticias
    })


# ---------------------------
# UPDATE PROFILE (AJAX)
# ---------------------------
@login_required
@require_POST
def update_profile(request):
    try:
        data = json.loads(request.body)
        field = data.get('field')
        value = data.get('value')

        user = request.user

        if field == 'username':
            if value != user.username and User.objects.filter(username=value).exclude(id=user.id).exists():
                return JsonResponse({'success': False, 'error': 'Este nome de usuário já está em uso.'})
            user.username = value

        elif field == 'email':
            if value != user.email and User.objects.filter(email=value).exclude(id=user.id).exists():
                return JsonResponse({'success': False, 'error': 'Este e-mail já está em uso.'})
            user.email = value

        elif field == 'password':
            user.set_password(value)

        user.save()
        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ---------------------------
# UPDATE PROFILE PHOTO (AJAX)
# ---------------------------
@login_required
@require_POST
def update_profile_photo(request):
    try:
        avatar = request.FILES.get('avatar')

        if avatar:
            if not avatar.content_type.startswith('image/'):
                return JsonResponse({'success': False, 'error': 'O arquivo deve ser uma imagem.'})

            if avatar.size > 5 * 1024 * 1024:
                return JsonResponse({'success': False, 'error': 'A imagem deve ter no máximo 5MB.'})

            return JsonResponse({'success': True, 'avatar_url': '/media/avatars/default.png'})

        return JsonResponse({'success': False, 'error': 'Nenhuma imagem enviada.'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ---------------------------
# UPDATE USER TAGS (AJAX)
# ---------------------------
@login_required
@require_POST
def update_user_tags(request):
    try:
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
