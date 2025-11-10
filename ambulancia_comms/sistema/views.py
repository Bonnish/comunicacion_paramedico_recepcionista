from datetime import datetime
from django.shortcuts import render
import hashlib
from .models import Usuario, Paciente, Historial

# Create your views here.
def index(request):
    return render(request, 'index.html')

def menu_paramedico(request):
    estado_sesion = request.session.get('estadoSesion')
    cargo_usuario = request.session.get('cargoUsuario')
    nom_usuario = request.session.get('nomUsuario')

    if estado_sesion:
        if cargo_usuario == 'Paramedico' or cargo_usuario == 'Administrador':
            datos = {'nombre': nom_usuario}
            return render(request, 'menu_paramedico.html', datos)
        else:
            datos = {'mensaje': 'Acceso no autorizado. Por favor, inicie sesión con una cuenta de Paramedico.'}
            return render(request, 'index.html', datos)
    else:
        datos = {'mensaje': 'Por favor, inicie sesión para acceder al menú de Paramedico.'}
        return render(request, 'index.html', datos)

def menu_hospital(request):
    estado_sesion = request.session.get('estadoSesion')
    cargo_usuario = request.session.get('cargoUsuario')
    nom_usuario = request.session.get('nomUsuario')

    if estado_sesion:
        if cargo_usuario == 'Hospital' or cargo_usuario == 'Administrador':
            datos = {'nombre': nom_usuario}
            return render(request, 'menu_hospital.html', datos)
        else:
            datos = {'mensaje': 'Acceso no autorizado. Por favor, inicie sesión con una cuenta de Hospital.'}
            return render(request, 'index.html', datos)
    else:
        datos = {'mensaje': 'Por favor, inicie sesión para acceder al menú de Hospital.'}
        return render(request, 'index.html', datos)

def mostrar_derivar_paciente(request):
    estado_sesion = request.session.get('estadoSesion')
    cargo_usuario = request.session.get('cargoUsuario')
    
    if cargo_usuario == 'Paramedico' or cargo_usuario == 'Administrador' and estado_sesion:
        return render(request, 'derivar_paciente.html')
    else:
        datos = {'mensaje': 'Acceso no autorizado. Por favor, inicie sesión con una cuenta de Paramedico.'}
        return render(request, 'index.html', datos)
    

def mostrar_enviar_formulario(request):
    estado_sesion = request.session.get('estadoSesion')
    cargo_usuario = request.session.get('cargoUsuario')

    if cargo_usuario in ['Paramedico', 'Administrador'] and estado_sesion:
        return render(request, 'enviar_formulario.html')
    else:
        datos = {'mensaje': 'Acceso no autorizado. Inicie sesión con una cuenta de Paramedico o Administrador.'}
        return render(request, 'index.html', datos)


def enviar_formulario(request):
    if request.method == 'POST':
        nom = request.POST['nombre']
        edad = request.POST['edad']
        genero = request.POST['genero']
        prevision = request.POST['prevision']
        accidente = request.POST['accidente_laboral'] == 'True'
        comor = request.POST['comorbilidades']
        func = request.POST['funcionalidad']
        motivo = request.POST['motivo_derivacion']
        prestacion = request.POST['prestacion_requerida']
        glasgow = request.POST['glasgow']
        llenado = request.POST['llenado_capilar']
        fc = request.POST['fc']
        fr = request.POST['fr']
        fio2 = request.POST['fio2']
        sat = request.POST['sat02']

        comprobarPaciente = Paciente.objects.filter(nombre=nom, edad=edad)
        if comprobarPaciente:
            pa = Paciente.objects.all().values().order_by('nombre')
            datos = {
                'nomUsuario': request.session['nomUsuario'],
                'pa': pa,
                'mensaje': 'El paciente ('+str(nom.upper())+') ya está registrado'
            }
            return render(request, 'enviar_formulario.html', datos)
        
        else:
            pa = Paciente(
                nombre=nom,
                edad=edad,
                genero=genero,
                prevision=prevision,
                accidente_laboral=accidente,
                comorbilidades=comor,
                funcionalidad=func,
                motivo_derivacion=motivo,
                prestacion_requerida=prestacion,
                glasgow=glasgow,
                llenado_capilar=llenado,
                fc=fc,
                fr=fr,
                fio2=fio2,
                sat02=sat,
                fecha_registro=datetime.now()
            )
            pa.save()

            descripcion = 'Registro de Paciente: ('+str(nom.upper())+')'
            tabla = 'Paciente'
            fechayhora = datetime.now()
            usuario = request.session['idUsuario']
            his = Historial(usuario_id=usuario, descripcion=descripcion, tabla_afectada=tabla, fecha_hora=fechayhora)
            his.save()

            datos = {
                'nomUsuario': request.session['nomUsuario'],
                'mensaje': 'Paciente ('+str(nom.upper())+') registrado correctamente'
            }
            return render(request, 'enviar_formulario.html', datos)
    else:
        datos = {
            'nomUsuario': request.session['nomUsuario'],
            'mensaje': 'No se puede procesar la solicitud'
        }
        return render(request, 'enviar_formulario.html', datos)


def ver_formularios(request):
    estado_sesion = request.session.get('estadoSesion')

    if not estado_sesion:
        datos = {'mensaje': 'Debe iniciar sesión para ver los formularios.'}
        return render(request, 'index.html', datos)

    pa = Paciente.objects.all().order_by('-fecha_registro')
    datos = {
        'nomUsuario': request.session['nomUsuario'],
        'pa': pa
    }
    return render(request, 'ver_formularios.html', datos)


def editar_datos(request):
    return render(request, 'editar_datos.html')

def mostrar_login(request):
    estado_sesion = request.session.get('estadoSesion')

    if estado_sesion:
        mensaje = "Ya tienes una sesión activa."
        return render(request, 'index.html', {'mensaje': mensaje})
    else:
        return render(request, 'login.html')

def procesar_login(request):
    if request.session.get('estadoSesion'):
        mensaje = "Ya tienes una sesión activa."
        return render(request, 'index.html', {'mensaje': mensaje})

    if request.method == 'POST':
        rut = request.POST['txtrut']
        con = request.POST['txtpas']
        has = hashlib.md5(con.encode('utf-8')).hexdigest()
        comprobar = Usuario.objects.filter(rut=rut, contraseña=has).values()
        
        if comprobar:
            request.session['estadoSesion'] = True
            request.session['rutUsuario'] = rut
            request.session['idUsuario'] = comprobar[0]['id']
            request.session['nomUsuario'] = Usuario.objects.get(rut=rut).nombre
            cargo = request.session['cargoUsuario'] = Usuario.objects.get(rut=rut).cargo

            descripcion = "Inicio de sesión"
            tabla = "Usuario"
            usuario = request.session['idUsuario']
            his = Historial(usuario_id=usuario, descripcion=descripcion, tabla_afectada=tabla, fecha_hora=datetime.now())
            his.save()

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
    rut = request.session.get('rutUsuario')
    if rut:
        usuario = Usuario.objects.get(rut=rut)
        desc = "Cierre de sesión"
        tabla = "Usuario"
        his = Historial(usuario=usuario, descripcion=desc, tabla_afectada=tabla, fecha_hora=datetime.now())
        his.save()
    request.session.flush()
    return render(request, 'index.html')