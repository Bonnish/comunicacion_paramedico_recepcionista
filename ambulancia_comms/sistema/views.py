from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'index.html')

def menu_paramedico(request):
    return render(request, 'menu_paramedico.html')

def menu_hospital(request):
    return render(request, 'menu_hospital.html')

def derivar_paciente(request):
    return render(request, 'derivar_paciente.html')

def enviar_formulario(request):
    return render(request, 'enviar_formulario.html')

def ver_formularios(request):
    return render(request, 'ver_formularios.html')

def editar_datos(request):
    return render(request, 'editar_datos.html')

def login(request):
    return render(request, 'login.html')