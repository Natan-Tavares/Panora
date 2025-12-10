from django.shortcuts import render, get_object_or_404, redirect
from .models import Noticia, Resposta, Historico, Noticias_salvas, Tags, Categoria
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
import json,os
from django.conf import settings
from datetime import datetime, timedelta

categorias_noticias = [
    "Pernambuco",
    "Economia e Negócios",
    "Mundo (Internacional)",
    "Tecnologia e Inovação",
    "Ciência e Saúde",
    "Esportes",
    "Entretenimento e Cultura",
    "Meio Ambiente e Sustentabilidade",
    "Cotidiano",
    "Educação e Carreira"
]

tags_noticias = [
    "Política Nacional",
    "Mercado Financeiro",
    "Relações Internacionais",
    "Inteligência Artificial",
    "Pesquisa Científica",
    "Futebol",
    "Cinema",
    "Mudanças Climáticas",
    "Segurança Pública",
    "Ensino Superior"
]
# ---------------------------
# CRIAR NOTICIA
# ---------------------------
def criar_noticia(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    todas_tags = Tags.objects.all()
    categoria = Categoria.objects.all()

    if request.method == "POST":
        titulo = request.POST.get("titulo")
        materia = request.POST.get("materia")
        autor_user = request.user.username  # Campo é autor_user, não autor
        
        tag_escolhida = request.POST.get('tag')
        tag = Tags.objects.get(id=tag_escolhida) if tag_escolhida else None
        
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
            autor_user=autor_user,  # CORRIGIDO: autor_user, não autor
            data_criacao=data,
            local=local,
            fontes=fontes,
            categoria=cat,
            imagem=imagem,
            capa=capa
        )

        if tag:
            noticia.tags.add(tag)

        messages.success(request, "Notícia criada com sucesso!")
        return redirect('ler_noticia', id=noticia.id)

    return render(request, 'criar_noticia.html', {'tags': todas_tags, 'categorias': categoria})

def migrar_autores(request):
    """Migra autores de string para User objects"""
    noticias = Noticia.objects.filter(autor__isnull=True)  # Para o novo campo
    # noticias = Noticia.objects.all()
    
    for noticia in noticias:
        if hasattr(noticia, 'autor_nome'):
            username = noticia.autor_nome.lower().replace(' ', '_')
            try:
                user = User.objects.get(username=username)
                noticia.autor_user = user
                noticia.save()
            except User.DoesNotExist:
                # Criar usuário se não existir
                user = User.objects.create_user(
                    username=username,
                    email=f"{username}@example.com",
                    password='temp123'
                )
                noticia.autor_user = user
                noticia.save()
    
    return HttpResponse("Autores migrados com sucesso!")
# ---------------------------
# EDITAR NOTÍCIA
# ---------------------------
def editar_noticia(request, id):
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
        if tag_escolhida:
            tag = Tags.objects.get(id=tag_escolhida)
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

# views.py - ATUALIZE a parte do JSON em inicial
def inicial(request):
    if not Noticia.objects.exists():
        if not Tags.objects.exists():
            Criar_tag = [
                Tags(tag=nome) for nome in tags_noticias 
            ]
            Tags.objects.bulk_create(Criar_tag)
        
        if not Categoria.objects.exists():
            Criar_categoria = [
                Categoria(categoria=nome) for nome in categorias_noticias
            ]
            Categoria.objects.bulk_create(Criar_categoria)

        caminho_arquivo = os.path.join(settings.BASE_DIR, 'AppJCPE', 'noticias.json')
        dados_noticias = []

        if os.path.exists(caminho_arquivo):
            with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
                dados_noticias = json.load(arquivo)
        
        for item in dados_noticias:
            try:
                cat_obj = Categoria.objects.get(categoria=item["categoria_nome"])
            except Categoria.DoesNotExist:
                cat_obj = None 
            
            nova_noticia = Noticia(
                titulo=item["titulo"],
                subtitulo=item["subtitulo"],
                local=item["local"],
                materia=item["materia"],
                autor_user=item["autor"],
                fontes=item["fontes"],
                categoria=cat_obj,
                imagem=f"noticias/imagens/{item['img_nome']}",
                capa=f"noticias/imagens/{item['img_nome']}" 
            )
            
            nova_noticia.save()

            tag_obj = Tags.objects.get(tag=item["tag_nome"])
            nova_noticia.tags.add(tag_obj)
        User.objects.create_superuser(
            username='admin',
            email='',
            password='1'
        )
    
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
    todas_tags = Tags.objects.all()
    categorias = Categoria.objects.all()

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
            'categorias': categorias,
            'noticias_salvas_ids': noticias_salvas_ids,
            'recent_searches': recent_searches,
            'q': q,
        }
    )

def colunistas(request):
    busca = request.GET.get('busca', '').strip()
    
    autores_distintos = Noticia.objects.exclude(autor_user__isnull=True).values_list('autor_user', flat=True).distinct()
    
    # Filtar por busca se houver
    autores_filtrados = []
    for nome_autor in autores_distintos:
        if busca and busca.lower() not in nome_autor.lower():
            continue
        
        # Contar notícias deste autor
        noticias_autor = Noticia.objects.filter(autor_user=nome_autor)
        total_noticias = noticias_autor.count()
        ultimas_noticias = noticias_autor.order_by('-data_criacao')[:3]
        
        autores_filtrados.append({
            'id': nome_autor,
            'nome': nome_autor,
            'total_noticias': total_noticias,
            'ultimas_noticias': ultimas_noticias,
            'primeira_noticia': noticias_autor.order_by('data_criacao').first() if total_noticias > 0 else None
        })
    
    # Ordenar por número de notícias (mais produtivos primeiro)
    autores_filtrados.sort(key=lambda x: x['total_noticias'], reverse=True)
    
    return render(request, 'colunistas.html', {
        'autores': autores_filtrados,
        'busca': busca
    })

def noticias_por_colunista(request, autor_id):
    # Como autor_user é CharField, o "autor_id" é na verdade o nome do autor
    nome_autor = autor_id
    
    # Buscar notícias por nome do autor
    noticias = Noticia.objects.filter(autor_user=nome_autor).order_by('-data_criacao')
    
    if not noticias.exists():
        raise Http404("Colunista não encontrado")
    
    # IDs das notícias salvas
    noticias_salvas_ids = []
    if request.user.is_authenticated:
        noticias_salvas_ids = Noticias_salvas.objects.filter(
            usuario=request.user
        ).values_list('noticia_id', flat=True)
    
    todas_tags = Tags.objects.all()
    
    return render(request, 'noticias_por_colunista.html', {
        'autor': {'id': nome_autor, 'nome': nome_autor},
        'noticias': noticias,
        'total_noticias': noticias.count(),
        'noticias_salvas_ids': list(noticias_salvas_ids),
        'tags': todas_tags
    })

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
    todas_tags = Tags.objects.all()
    
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

        return render(request, "login.html", {
    "erro": "Usuário ou senha incorretos"
})

    return render(request, "conta.html")


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
        Tags.objects.get_or_create(tag=tag)

    tags = Tags.objects.all()
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

# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

@csrf_exempt
@require_POST
def api_login(request):
    try:
        data = json.loads(request.body)
        identifier = data.get('identifier', '').strip()
        password = data.get('password', '')
        
        # Tentar autenticar por username
        user = authenticate(username=identifier, password=password)
        
        # Se não encontrar por username, tentar por email
        if user is None:
            try:
                user_by_email = User.objects.get(email=identifier)
                user = authenticate(username=user_by_email.username, password=password)
            except User.DoesNotExist:
                user = None
        
        if user is not None and user.is_active:
            auth_login(request, user)
            return JsonResponse({
                'success': True,
                'message': 'Login realizado com sucesso!',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Credenciais inválidas.'
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro no servidor: {str(e)}'
        }, status=500)

@csrf_exempt
@require_POST
def api_register(request):
    try:
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Validações
        if not username or not email or not password:
            return JsonResponse({
                'success': False,
                'message': 'Todos os campos são obrigatórios.'
            }, status=400)
        
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                'success': False,
                'message': 'Nome de usuário já está em uso.'
            }, status=400)
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                'success': False,
                'message': 'E-mail já está cadastrado.'
            }, status=400)
        
        if len(password) < 6:
            return JsonResponse({
                'success': False,
                'message': 'A senha deve ter pelo menos 6 caracteres.'
            }, status=400)
        
        # Criar usuário
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        # Fazer login automaticamente após registro
        auth_login(request, user)
        
        return JsonResponse({
            'success': True,
            'message': 'Conta criada com sucesso!',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro no servidor: {str(e)}'
        }, status=500)

@csrf_exempt
@login_required
@require_POST
def api_update_profile(request):
    try:
        data = json.loads(request.body)
        user = request.user
        
        # Atualizar username
        if 'username' in data:
            new_username = data['username'].strip()
            if new_username and new_username != user.username:
                if User.objects.filter(username=new_username).exclude(id=user.id).exists():
                    return JsonResponse({
                        'success': False,
                        'message': 'Nome de usuário já está em uso.'
                    }, status=400)
                user.username = new_username
        
        # Atualizar email
        if 'email' in data:
            new_email = data['email'].strip()
            if new_email and new_email != user.email:
                if User.objects.filter(email=new_email).exclude(id=user.id).exists():
                    return JsonResponse({
                        'success': False,
                        'message': 'E-mail já está em uso.'
                    }, status=400)
                user.email = new_email
        
        # Atualizar senha
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        
        user.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Perfil atualizado com sucesso!',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro no servidor: {str(e)}'
        }, status=500)

@csrf_exempt
@require_POST
def api_logout(request):
    auth_logout(request)
    return JsonResponse({
        'success': True,
        'message': 'Logout realizado com sucesso!'
    })

@csrf_exempt
def api_check_auth(request):
    if request.user.is_authenticated:
        return JsonResponse({
            'authenticated': True,
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
            }
        })
    else:
        return JsonResponse({
            'authenticated': False
        })