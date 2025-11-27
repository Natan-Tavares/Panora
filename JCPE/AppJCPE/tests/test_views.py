from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from ..models import (
    Noticia, Resposta, Historico, Noticias_salvas,
    Tags, Categoria
)

class ViewTests(TestCase):

    def setUp(self):
        self.client = Client()

        # Usuário
        self.user = User.objects.create_user(
            username="gui", password="123"
        )

        # Tags e categoria
        self.tag = Tags.objects.create(tag="Tech")
        self.cat = Categoria.objects.create(categoria="Mundo")

        # Fake image
        self.fake_img = SimpleUploadedFile(
            "teste.jpg", b"abc", content_type="image/jpeg"
        )

        # Notícia
        self.noticia = Noticia.objects.create(
            titulo="Notícia Teste",
            subtitulo="Sub",
            local="Brasil",
            materia="Texto...",
            autor="Autor X",
            categoria=self.cat,
            imagem=self.fake_img,
            capa=self.fake_img,
        )
        self.noticia.tags.add(self.tag)

    # --------------------------------
    # CRIAR NOTÍCIA
    # --------------------------------
    def test_criar_noticia(self):
        self.client.force_login(self.user)
        resp = self.client.post(reverse("criar_noticia"), {
            "titulo": "Nova notícia",
            "materia": "Corpo",
            "tag": self.tag.id,
            "categoria": self.cat.id
        })
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Noticia.objects.filter(titulo="Nova notícia").exists())

    # --------------------------------
    # EDITAR NOTÍCIA
    # --------------------------------
    def test_editar_noticia(self):
        self.client.force_login(self.user)
        resp = self.client.post(reverse("editar_noticia", args=[self.noticia.id]), {
            "titulo": "Editada",
            "materia": "Nova matéria",
            "subtitulo": "Novo sub",
            "local": "EUA",
            "fontes": "Google",
            "tag": self.tag.id,
            "categoria": self.cat.id
        })
        self.assertEqual(resp.status_code, 302)
        self.noticia.refresh_from_db()
        self.assertEqual(self.noticia.titulo, "Editada")

    # --------------------------------
    # LISTAR NOTÍCIAS
    # --------------------------------
    def test_inicial(self):
        resp = self.client.get(reverse("inicial"))
        self.assertContains(resp, "Notícia Teste")

    # --------------------------------
    # LER NOTÍCIA
    # --------------------------------
    def test_ler_noticia(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse("ler_noticia", args=[self.noticia.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Historico.objects.filter(usuario=self.user).exists())

    # --------------------------------
    # APAGAR NOTÍCIA
    # --------------------------------
    def test_apagar_noticia(self):
        self.client.force_login(self.user)
        resp = self.client.post(reverse("apagar_noticia", args=[self.noticia.id]))
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Noticia.objects.filter(id=self.noticia.id).exists())

    # --------------------------------
    # INSERIR RESPOSTA
    # --------------------------------
    def test_inserir_resposta_post(self):
        self.client.force_login(self.user)
        resp = self.client.post(reverse("inserir_resposta", args=[self.noticia.id]), {
            "texto": "Comentário test"
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Resposta.objects.filter(texto="Comentário test").exists())

    # --------------------------------
    # LOGIN / CADASTRO / LOGOUT
    # --------------------------------
    def test_cadastro(self):
        resp = self.client.post(reverse("cadastro"), {
            "username": "novo",
            "email": "a@a.com",
            "senha": "123"
        })
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(User.objects.filter(username="novo").exists())

    def test_login_view(self):
        resp = self.client.post(reverse("login"), {
            "username": "gui",
            "senha": "123"
        })
        self.assertEqual(resp.status_code, 200)

    def test_logout(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse("logout"))
        self.assertEqual(resp.status_code, 302)

    # --------------------------------
    # SALVAR / REMOVER / LISTAR NOTÍCIAS SALVAS
    # --------------------------------
    def test_salvar_noticia(self):
        self.client.force_login(self.user)
        resp = self.client.post(reverse("salvar_noticia", args=[self.noticia.id]))
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Noticias_salvas.objects.filter(usuario=self.user).exists())

    def test_remover_noticia_salva(self):
        self.client.force_login(self.user)
        salva = Noticias_salvas.objects.create(usuario=self.user, noticia=self.noticia)
        resp = self.client.post(reverse("apagar_salvos", args=[salva.id]))
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Noticias_salvas.objects.filter(id=salva.id).exists())

    # --------------------------------
    # CURTIR / DENUNCIAR
    # --------------------------------
    def test_curtir_resposta(self):
        self.client.force_login(self.user)
        resposta = Resposta.objects.create(
            noticia=self.noticia, texto="Oi", usuario="X"
        )
        resp = self.client.get(reverse("curtir_resposta", args=[resposta.id]))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(self.user, resposta.curtidas.all())

    def test_denunciar_comentario(self):
        self.client.force_login(self.user)
        resposta = Resposta.objects.create(
            noticia=self.noticia, texto="Oi", usuario="X"
        )
        resp = self.client.get(reverse("denunciar_comentario", args=[resposta.id]))
        self.assertEqual(resp.status_code, 302)
        resposta.refresh_from_db()
        self.assertEqual(resposta.denuncias, 1)

    # --------------------------------
    # EDITAR PERFIL
    # --------------------------------
    def test_editar_perfil(self):
        self.client.force_login(self.user)
        resp = self.client.post(reverse("editar_conta"), {
            "username": "novoNome",
            "email": "new@mail.com"
        })
        self.assertEqual(resp.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "novoNome")

    # --------------------------------
    # TAGS E CATEGORIAS
    # --------------------------------
    def test_criar_tag(self):
        self.client.post(reverse("criar_tag"), {"tag": "Esportes"})
        self.assertTrue(Tags.objects.filter(tag="Esportes").exists())

    def test_criar_categoria(self):
        self.client.post(reverse("criar_categoria"), {"categoria": "Política"})
        self.assertTrue(Categoria.objects.filter(categoria="Política").exists())

    # --------------------------------
    # NOTÍCIAS POR CATEGORIA
    # --------------------------------
    def test_noticias_por_categoria(self):
        resp = self.client.get(reverse("noticias_por_categoria", args=[self.cat.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Notícia Teste")
