from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from AppJCPE.models import Noticia, Resposta, Noticias_salvas, Historico


class ViewsTestCase(TestCase):
    def setUp(self):
        # Cliente para simular requisições
        self.client = Client()

        # Usuário de teste
        self.user = User.objects.create_user(username="testeuser", password="123456")

        # Notícia inicial
        self.noticia = Noticia.objects.create(
            titulo="Título teste",
            materia="Conteúdo da notícia",
            autor="Autor teste",
            data_criacao=timezone.now(),
        )

    # ---------- PÁGINA INICIAL ----------
    def test_inicial_lista_noticias(self):
        response = self.client.get(reverse("inicial"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Título teste")

    # ---------- LER NOTÍCIA ----------
    def test_ler_noticia_existe(self):
        response = self.client.get(reverse("ler_noticia", args=[self.noticia.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.noticia.titulo)

    def test_ler_noticia_registra_historico_quando_logado(self):
        self.client.login(username="testeuser", password="123456")
        self.client.get(reverse("ler_noticia", args=[self.noticia.id]))
        self.assertTrue(Historico.objects.filter(usuario=self.user, noticia=self.noticia).exists())

    # ---------- CRIAR NOTÍCIA ----------
    def test_criar_noticia_post(self):
        self.client.login(username="testeuser", password="123456")
        response = self.client.post(reverse("criar_noticia"), {
            "titulo": "Nova notícia",
            "materia": "Texto de teste",
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Noticia.objects.filter(titulo="Nova notícia").exists())

    # ---------- APAGAR NOTÍCIA ----------
    def test_apagar_noticia_post(self):
        noticia = Noticia.objects.create(titulo="Apagar", materia="Teste", autor="A")
        response = self.client.post(reverse("apagar_noticia", args=[noticia.id]))
        self.assertRedirects(response, "/")
        self.assertFalse(Noticia.objects.filter(id=noticia.id).exists())

    # ---------- LOGIN E CADASTRO ----------
    def test_cadastro_cria_usuario(self):
        response = self.client.post(reverse("cadastro"), {
            "username": "novo",
            "email": "teste@teste.com",
            "senha": "1234"
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username="novo").exists())

    def test_login_view_sucesso(self):
        response = self.client.post(reverse("login"), {
            "username": "testeuser",
            "senha": "123456"
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bem-vindo")

    # ---------- SALVAR E REMOVER NOTÍCIA ----------
    def test_salvar_noticia_post(self):
        self.client.login(username="testeuser", password="123456")
        response = self.client.post(reverse("salvar_noticia", args=[self.noticia.id]))
        self.assertRedirects(response, reverse("ler_noticia", args=[self.noticia.id]))
        self.assertTrue(Noticias_salvas.objects.filter(usuario=self.user, noticia=self.noticia).exists())

    def test_remover_noticias_salvas_post(self):
        self.client.login(username="testeuser", password="123456")
        salvo = Noticias_salvas.objects.create(usuario=self.user, noticia=self.noticia)
        response = self.client.post(reverse("remover_noticias_salvas", args=[salvo.id]))
        self.assertRedirects(response, reverse("vizualizar_salvos"))
        self.assertFalse(Noticias_salvas.objects.filter(id=salvo.id).exists())

    # ---------- INSERIR RESPOSTA ----------
    def test_inserir_resposta_post(self):
        self.client.login(username="testeuser", password="123456")
        response = self.client.post(reverse("inserir_resposta", args=[self.noticia.id]), {
            "texto": "Comentário de teste"
        })
        self.assertRedirects(response, reverse("ler_noticia", args=[self.noticia.id]))
        self.assertTrue(Resposta.objects.filter(texto="Comentário de teste").exists())
