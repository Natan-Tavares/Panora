from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from ..models import (
    Tags, Categoria, Noticia, Resposta, Historico,
    Noticias_salvas, Perfil
)

class ModelTests(TestCase):

    def setUp(self):
        # Usuário
        self.user = User.objects.create_user(username="gui", password="123")

        # Tag
        self.tag = Tags.objects.create(tag="Tecnologia")

        # Categoria
        self.categoria = Categoria.objects.create(categoria="Ciência")

        # Imagem fake
        self.fake_img = SimpleUploadedFile(
            "test.jpg", b"imagem_teste", content_type="image/jpeg"
        )

        # Notícia
        self.noticia = Noticia.objects.create(
            titulo="Título teste",
            subtitulo="Subtitulo teste",
            local="Brasil",
            materia="Conteúdo da matéria",
            autor="Autor X",
            fontes="Fonte Y",
            categoria=self.categoria,
            imagem=self.fake_img,
            capa=self.fake_img,
        )
        self.noticia.tags.add(self.tag)

    # ---------------------------
    # TESTES DE NOTICIA
    # ---------------------------

    def test_criacao_noticia(self):
        self.assertEqual(self.noticia.titulo, "Título teste")
        self.assertEqual(self.noticia.categoria.categoria, "Ciência")
        self.assertTrue(self.noticia.tags.exists())
        self.assertIsNotNone(self.noticia.imagem)

    # ---------------------------
    # TESTES DE RESPOSTA (COMENTÁRIOS)
    # ---------------------------

    def test_comentario_simples(self):
        comentario = Resposta.objects.create(
            noticia=self.noticia,
            texto="Comentário teste",
            usuario="Visitante"
        )
        self.assertEqual(comentario.texto, "Comentário teste")
        self.assertEqual(comentario.noticia, self.noticia)

    def test_comentario_pai_filho(self):
        pai = Resposta.objects.create(
            noticia=self.noticia,
            texto="Comentário pai",
            usuario="UserA"
        )
        filho = Resposta.objects.create(
            noticia=self.noticia,
            texto="Comentário filho",
            usuario="UserB",
            pai=pai
        )

        self.assertEqual(filho.pai, pai)
        self.assertIn(filho, pai.comentarios_filho.all())

    # ---------------------------
    # TESTES DE CURTIDAS / DENÚNCIAS
    # ---------------------------

    def test_curtidas(self):
        comentario = Resposta.objects.create(
            noticia=self.noticia,
            texto="Comentário curtido",
            usuario="UserX"
        )
        comentario.curtidas.add(self.user)

        self.assertEqual(comentario.curtidas.count(), 1)

    def test_denuncias(self):
        comentario = Resposta.objects.create(
            noticia=self.noticia,
            texto="Comentário denunciado",
            usuario="UserY",
            denuncias=0
        )
        comentario.denuncias += 1
        comentario.save()

        self.assertEqual(comentario.denuncias, 1)

    # ---------------------------
    # TESTE DO SINAL post_save DO PERFIL
    # ---------------------------

    def test_perfil_criado_automaticamente(self):
        user2 = User.objects.create_user(username="joao", password="abc")
        self.assertTrue(hasattr(user2, "perfil"))

    # ---------------------------
    # HISTÓRICO
    # ---------------------------

    def test_historico(self):
        historico = Historico.objects.create(
            noticia=self.noticia,
            usuario=self.user
        )
        self.assertEqual(historico.usuario.username, "gui")
        self.assertEqual(historico.noticia, self.noticia)

    # ---------------------------
    # NOTICIAS SALVAS
    # ---------------------------

    def test_noticia_salva(self):
        salva = Noticias_salvas.objects.create(
            noticia=self.noticia,
            usuario=self.user
        )
        self.assertEqual(salva.usuario.username, "gui")
        self.assertEqual(salva.noticia.titulo, "Título teste")
