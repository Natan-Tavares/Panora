"""
URL configuration for JCPE project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from AppJCPE import views
from AppJCPE.views import InserirRespostaView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('criar/', views.criar_noticia,name='criar_noticia'),
    path('', views.inicial,name='inicial'),
    path('noticia/<int:id>', views.ler_noticia,name='ler_noticia'),
    path('noticia/<int:id>/apagar', views.apagar_noticia,name='apagar_noticia'),
     path('noticia/<int:noticia_id>/responder', InserirRespostaView.as_view(), name='inserir_resposta'),
]
