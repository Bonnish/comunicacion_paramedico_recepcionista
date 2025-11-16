from django.contrib import admin
from django.urls import path
from sistema import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name="index"),
    path('menu_paramedico/', views.menu_paramedico, name='menu_paramedico'),
    path('menu_hospital/', views.menu_hospital, name='menu_hospital'),
    path('derivar_paciente/', views.mostrar_derivar_paciente, name='derivar_paciente'),
    path('enviar_formulario/', views.mostrar_enviar_formulario, name='enviar_formulario'),
    path('formulario/', views.enviar_formulario, name='formulario'),
    path('ver_formularios/', views.ver_formularios, name='ver_formularios'),
    path('login/', views.mostrar_login, name='mostrar_login'),
    path('procesar_login/', views.procesar_login, name='procesar_login'),
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),
    path('crear_usuario/', views.mostrar_crear_usuario, name='mostrar_crear_usuario'),
    path('crear_usuario/procesar/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/', views.listar_usuarios, name='listar_usuarios'),
    path('usuarios/editar/<int:id>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/eliminar/<int:id>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('paciente/estado/<int:id_paciente>/<str:nuevo_estado>/', views.cambiar_estado, name='cambiar_estado'),
    path('historial/', views.ver_historial, name='ver_historial'),
    path('formulario/editar/<int:id>/', views.editar_formulario, name='editar_formulario'),
    path('exportar/excel/', views.exportar_excel, name="exportar_excel"),
    path('exportar/pdf/<int:id>/', views.exportar_pdf, name="exportar_pdf"),
    path('alertas/', views.ver_alertas, name='ver_alertas'),
    path('alertas/resolver/<int:id_alerta>/', views.resolver_alerta, name='resolver_alerta'),
    path('alerta/enviar/<int:id_paciente>/', views.enviar_alerta, name='enviar_alerta'),
]
