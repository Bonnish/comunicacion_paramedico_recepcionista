from django.contrib import admin
from django.urls import path
from sistema import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name="index"),
    path('menu_paramedico/', views.menu_paramedico, name='menu_paramedico'),
    path('menu_hospital/', views.menu_hospital, name='menu_hospital'),
    path('derivar_paciente/', views.derivar_paciente, name='derivar_paciente'),
    path('enviar_formulario/', views.enviar_formulario, name='enviar_formulario'),
    path('ver_formularios/', views.ver_formularios, name='ver_formularios'),
    path('login/', views.login, name='login'),
    path('editar_datos/', views.editar_datos, name='editar_datos'), #POR USAR, SERÁ PARA CAMBIAR LOS DATOS DE LA CUENTA DEL USUARIO
]
