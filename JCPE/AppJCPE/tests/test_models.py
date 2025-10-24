from django.test import TestCase
from django.contrib.auth.models import User
from AppJCPE.models import Tags, Noticia, Resposta, Historico, Noticias_salvas, Perfil

class ModelsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="guilherme", password="123")

        self.tag = Tags.objects.create(tag="Tecnologia")

        self.noticia = Noticia.objects.create(
            titulo="Notícia",
            materia="Corpo da notícia.",
            autor="Admin",
            tag=self.tag
        )

    def test_criacao_tag(self):
        self.assertEqual(str(self.tag), "[Tecnologia]")

    def test_criacao_noticia(self):
        self.assertEqual(self.noticia.titulo, "Nova IA lançada")
        self.assertEqual(str(self.noticia), f"[{self.noticia.id}] {self.noticia.titulo}")

    def test_criacao_resposta(self):
        resposta = Resposta.objects.create(
            noticia=self.noticia,
            texto="Concordo com a matéria!",
            usuario="Leitor"
        )
        self.assertIn("Concordo", resposta.texto)
        self.assertEqual(resposta.pai, None)

    def test_relacionamento_resposta_pai_filho(self):
        pai = Resposta.objects.create(
            noticia=self.noticia, texto="Comentário principal", usuario="João"
        )
        filho = Resposta.objects.create(
            noticia=self.noticia, texto="Resposta ao comentário", usuario="Maria", pai=pai
        )
        self.assertEqual(filho.pai, pai)
        self.assertIn(filho, pai.comentarios_filho.all())

    def test_criacao_historico(self):
        historico = Historico.objects.create(noticia=self.noticia, usuario=self.user)
        self.assertIn("acessou", str(historico))
        self.assertEqual(historico.usuario.username, "guilherme")

    def test_criacao_noticia_salva(self):
        salva = Noticias_salvas.objects.create(noticia=self.noticia, usuario=self.user)
        self.assertIn("salvou", str(salva))
        self.assertEqual(salva.usuario.username, "guilherme")

    def test_perfil_criado_automaticamente(self):
        perfil = Perfil.objects.get(usuario=self.user)
        self.assertEqual(str(perfil), "Perfil de guilherme")

    def test_atualizar_perfil(self):
        perfil = self.user.perfil
        perfil.foto = "fotos_perfil/teste.jpg"
        perfil.save()
        self.assertEqual(perfil.foto, "fotos_perfil/teste.jpg")
