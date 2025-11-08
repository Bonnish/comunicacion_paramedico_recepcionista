from django.shortcuts import render
import hashlib
from .models import Usuario, Paciente

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

def mostrar_login(request):
    return render(request, 'login.html')

def procesar_login(request):
    if request.method == 'POST':
        rut = request.POST['txtrut']
        con = request.POST['txtpas']
        has = hashlib.md5(con.encode('utf-8')).hexdigest()
        comprobar = Usuario.objects.filter(rut=rut, contraseña=has).exists()

        if comprobar:
            request.session['estadoSesion'] = True
            request.session['rutUsuario'] = rut
            request.session['nomUsuario'] = Usuario.objects.get(rut=rut).nombre
            cargo = request.session['cargoUsuario'] = Usuario.objects.get(rut=rut).cargo

            datos = {'rut': rut, 'nombre': request.session['nomUsuario']}
            if cargo == 'Paramedico':
                return render(request, 'menu_paramedico.html', datos)
            elif cargo == 'Hospital':
                return render(request, 'menu_hospital.html', datos)
            elif cargo == 'Administrador':
                return render(request, 'index.html', datos)
        else:
            mensaje = "RUT o Contraseña incorrectos. Intente nuevamente."
            return render(request, 'login.html', {'mensaje': mensaje})
        
def cerrar_sesion(request):
    request.session.flush()
    return render(request, 'index.html')