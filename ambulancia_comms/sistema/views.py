from datetime import datetime
from openpyxl import Workbook
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
from django.http import FileResponse, HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from .models import Usuario, Paciente, Historial, Alerta

def index(request):
    return render(request, 'index.html')

def exportar_excel(request):
    if not request.session.get('estadoSesion') or request.session.get('cargoUsuario') not in ['Hospital', 'Administrador']:
        return render(request, 'index.html', {'mensaje': 'Acceso denegado.'})

    wb = Workbook()
    ws = wb.active
    ws.title = "Formularios"

    columnas = [
        "ID", "Nombre", "Edad", "Estado", "Género", "Previsión",
        "Accidente", "Glasgow", "FC", "FR", "FiO2", "SatO2", "Fecha Registro"
    ]
    ws.append(columnas)

    for p in Paciente.objects.all():
        ws.append([
            p.id, p.nombre, p.edad, p.estado, p.genero, p.prevision,
            "Sí" if p.accidente_laboral else "No",
            p.glasgow, p.fc, p.fr, p.fio2, p.sat02,
            p.fecha_registro.strftime("%d-%m-%Y %H:%M")
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = 'attachment; filename="formularios.xlsx"'
    wb.save(response)
    return response

def exportar_pdf(request, id):
    if not request.session.get('estadoSesion') or request.session.get('cargoUsuario') not in ['Hospital', 'Administrador']:
        return render(request, 'index.html', {'mensaje': 'Acceso denegado.'})

    try:
        paciente = Paciente.objects.get(id=id)
    except Paciente.DoesNotExist:
        return render(request, 'index.html', {'mensaje': 'Formulario no encontrado'})

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(200, 750, "Formulario de Paciente")

    pdf.setFont("Helvetica", 12)
    y = 720

    def linea(texto):
        nonlocal y
        pdf.drawString(50, y, texto)
        y -= 20

    linea(f"Nombre: {paciente.nombre}")
    linea(f"Edad: {paciente.edad}")
    linea(f"Estado: {paciente.estado}")
    linea(f"Género: {paciente.genero}")
    linea(f"Previsión: {paciente.prevision}")
    linea(f"Accidente laboral: {'Sí' if paciente.accidente_laboral else 'No'}")
    linea(f"Comorbilidades: {paciente.comorbilidades}")
    linea(f"Funcionalidad: {paciente.funcionalidad}")
    linea(f"Motivo derivación: {paciente.motivo_derivacion}")
    linea(f"Prestación requerida: {paciente.prestacion_requerida}")
    linea(f"Glasgow: {paciente.glasgow}")
    linea(f"Llenado capilar: {paciente.llenado_capilar}")
    linea(f"FC: {paciente.fc}")
    linea(f"FR: {paciente.fr}")
    linea(f"FiO2: {paciente.fio2}")
    linea(f"SatO2: {paciente.sat02}")
    linea(f"Fecha registro: {paciente.fecha_registro.strftime('%d/%m/%Y %H:%M')}")

    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f"paciente_{paciente.id}.pdf")

def mostrar_crear_usuario(request):
    estado = request.session.get('estadoSesion')
    cargo = request.session.get('cargoUsuario')

    if not estado or cargo != 'Administrador':
        datos = {'mensaje': 'Acceso denegado.'}
        return render(request, 'index.html', datos)

    return render(request, 'crear_usuario.html')

def crear_usuario(request):
    estado = request.session.get('estadoSesion')
    cargo = request.session.get('cargoUsuario')

    if not estado or cargo != 'Administrador':
        datos = {'mensaje': 'Acceso denegado.'}
        return render(request, 'index.html', datos)

    if request.method == 'POST':
        rut = request.POST['rut']
        nombre = request.POST['nombre']
        email = request.POST['email']
        telefono = request.POST['telefono']
        cargo_new = request.POST['cargo']
        contraseña = request.POST['contraseña']

        if Usuario.objects.filter(rut=rut):
            datos = {'mensaje': 'El RUT ('+str(rut)+') ya existe'}
            return render(request, 'crear_usuario.html', datos)

        if Usuario.objects.filter(email=email):
            datos = {'mensaje': 'El correo ('+str(email)+') ya existe'}
            return render(request, 'crear_usuario.html', datos)

        u = Usuario(
            rut=rut,
            nombre=nombre,
            cargo=cargo_new,
            email=email,
            telefono=telefono,
            contraseña=make_password(contraseña)
        )
        u.save()

        descripcion = 'Creación de usuario: '+str(nombre)+' ('+str(rut)+')'
        tabla = 'Usuario'
        usuario = request.session['idUsuario']
        his = Historial(usuario_id=usuario, descripcion=descripcion, tabla_afectada=tabla, fecha_hora=datetime.now())
        his.save()

        datos = {'mensaje_exito': 'Usuario ('+str(nombre)+') creado correctamente'}
        return render(request, 'crear_usuario.html', datos)

    return render(request, 'crear_usuario.html')

def listar_usuarios(request):
    if not request.session.get('estadoSesion') or request.session.get('cargoUsuario') != 'Administrador':
        return render(request, 'index.html', {'mensaje': 'Acceso denegado.'})

    lista = Usuario.objects.all().order_by('nombre')
    paginator = Paginator(lista, 5)
    page = request.GET.get('page')
    usuarios = paginator.get_page(page)

    return render(request, 'listar_usuarios.html', {'usuarios': usuarios})

def editar_usuario(request, id):
    estado = request.session.get('estadoSesion')
    cargo = request.session.get('cargoUsuario')

    if not estado or cargo != 'Administrador':
        return render(request, 'index.html', {'mensaje': 'Acceso denegado.'})

    try:
        usuario = Usuario.objects.get(id=id)
    except Usuario.DoesNotExist:
        return render(request, 'listar_usuarios.html', {'mensaje': 'El usuario no existe.'})

    if request.method == 'POST':
        usuario.nombre = request.POST['nombre']
        usuario.email = request.POST['email']
        usuario.telefono = request.POST['telefono']
        usuario.cargo = request.POST['cargo']

        nueva_pass = request.POST['password']

        if nueva_pass.strip() != "":
            usuario.contraseña = make_password(nueva_pass)

        usuario.save()

        descripcion = f"Edición de usuario: {usuario.nombre} ({usuario.rut})"
        his = Historial(usuario_id=request.session['idUsuario'], descripcion=descripcion,
                        tabla_afectada="Usuario", fecha_hora=datetime.now())
        his.save()

        return render(request, 'editar_usuario.html', {
            'usuario': usuario,
            'mensaje_exito': 'Usuario actualizado correctamente.'
        })

    return render(request, 'editar_usuario.html', {'usuario': usuario})

def eliminar_usuario(request, id):
    estado = request.session.get('estadoSesion')
    cargo = request.session.get('cargoUsuario')

    if not estado or cargo != 'Administrador':
        return render(request, 'index.html', {'mensaje': 'Acceso denegado.'})

    if id == request.session['idUsuario']:
        return render(request, 'listar_usuarios.html',
                      {'mensaje': 'No puedes eliminar tu propio usuario.'})

    try:
        usuario = Usuario.objects.get(id=id)
    except Usuario.DoesNotExist:
        return render(request, 'listar_usuarios.html',
                      {'mensaje': 'El usuario no existe.'})

    if usuario.cargo == "Administrador" and Usuario.objects.filter(cargo="Administrador").count() == 1:
        return render(request, 'listar_usuarios.html',
                      {'mensaje': 'No puedes eliminar al único administrador.'})

    usuario.delete()

    descripcion = f"Eliminación de usuario: {usuario.nombre} ({usuario.rut})"
    his = Historial(usuario_id=request.session['idUsuario'],
                    descripcion=descripcion, tabla_afectada="Usuario",
                    fecha_hora=datetime.now())
    his.save()

    return render(request, 'listar_usuarios.html',
                  {'mensaje_exito': 'Usuario eliminado correctamente.',
                   'usuarios': Usuario.objects.all()})

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

    if estado_sesion and cargo_usuario in ['Paramedico', 'Administrador']:
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
    if not request.session.get('estadoSesion') or request.session.get('cargoUsuario') not in ['Paramedico', 'Administrador']:
        return render(request, 'index.html', {'mensaje': 'Acceso denegado.'})

    if request.method == 'POST':
        import re

        nom = request.POST['nombre']
        edad = re.sub(r'[^0-9]', '', request.POST['edad'])
        genero = request.POST['genero']
        prevision = request.POST['prevision']
        accidente = request.POST['accidente_laboral'] == 'True'
        comor = request.POST['comorbilidades']
        func = request.POST['funcionalidad']
        motivo = request.POST['motivo_derivacion']
        prestacion = request.POST['prestacion_requerida']

        glasgow = re.sub(r'[^0-9]', '', request.POST['glasgow'])
        llenado = request.POST['llenado_capilar']

        fc = re.sub(r'[^0-9]', '', request.POST['fc'])
        fr = re.sub(r'[^0-9]', '', request.POST['fr'])
        fio2 = re.sub(r'[^0-9]', '', request.POST['fio2'])
        sat = re.sub(r'[^0-9]', '', request.POST['sat02'])

        pa = Paciente(
            nombre=nom,
            edad=edad,
            estado="Enviado",
            genero=genero,
            prevision=prevision,
            accidente_laboral=accidente,
            comorbilidades=comor,
            funcionalidad=func,
            motivo_derivacion=motivo,
            prestacion_requerida=prestacion,
            glasgow=glasgow or None,
            llenado_capilar=llenado,
            fc=fc or None,
            fr=fr or None,
            fio2=fio2 or None,
            sat02=sat or None,
            fecha_registro=datetime.now()
        )
        pa.save()

        Historial.objects.create(
            usuario_id=request.session['idUsuario'],
            descripcion='Registro de Paciente: ('+str(nom.upper())+')',
            tabla_afectada='Paciente',
            fecha_hora=datetime.now()
        )

        datos = {
            'nomUsuario': request.session['nomUsuario'],
            'mensaje': 'Paciente ('+str(nom.upper())+') registrado correctamente'
        }
        return render(request, 'enviar_formulario.html', datos)

    return render(request, 'enviar_formulario.html', {
        'nomUsuario': request.session['nomUsuario'],
        'mensaje': 'No se puede procesar la solicitud'
    })

def cambiar_estado(request, id_paciente, nuevo_estado):
    estado_sesion = request.session.get('estadoSesion')
    cargo = request.session.get('cargoUsuario')

    if not estado_sesion or cargo != 'Hospital':
        return render(request, 'index.html', {'mensaje': 'Acceso denegado.'})

    estados_validos = ['Enviado', 'En tránsito', 'Recibido']
    if nuevo_estado not in estados_validos:
        return render(request, 'index.html', {'mensaje': 'Estado inválido.'})

    try:
        paciente = Paciente.objects.get(id=id_paciente)
        paciente.estado = nuevo_estado
        paciente.save()

        Historial.objects.create(
            usuario_id=request.session['idUsuario'],
            descripcion=f"Cambio de estado del paciente {paciente.nombre} a {nuevo_estado}",
            tabla_afectada="Paciente",
            fecha_hora=datetime.now()
        )

        return redirect('ver_formularios')

    except Paciente.DoesNotExist:
        return render(request, 'index.html', {'mensaje': 'Paciente no encontrado'})

def editar_formulario(request, id):
    if request.session.get('cargoUsuario') != 'Paramedico':
        return render(request, 'index.html', {'mensaje': 'Acceso denegado.'})

    try:
        paciente = Paciente.objects.get(id=id)
    except Paciente.DoesNotExist:
        return render(request, 'index.html', {'mensaje': 'Formulario no encontrado.'})

    if request.method == 'POST':
        paciente.nombre = request.POST['nombre']
        paciente.edad = request.POST['edad']
        paciente.genero = request.POST['genero']
        paciente.prevision = request.POST['prevision']
        paciente.accidente_laboral = request.POST.get('accidente_laboral') == 'True'
        paciente.comorbilidades = request.POST['comorbilidades']
        paciente.funcionalidad = request.POST['funcionalidad']
        paciente.motivo_derivacion = request.POST['motivo_derivacion']
        paciente.prestacion_requerida = request.POST['prestacion_requerida']
        paciente.glasgow = request.POST['glasgow']
        paciente.llenado_capilar = request.POST['llenado_capilar']
        paciente.fc = request.POST['fc']
        paciente.fr = request.POST['fr']
        paciente.fio2 = request.POST['fio2']
        paciente.sat02 = request.POST['sat02']
        paciente.save()

        return render(request, 'enviar_formulario.html', {
            'mensaje': 'Formulario actualizado correctamente',
            'nomUsuario': request.session['nomUsuario']
        })

    return render(request, 'editar_formulario.html', {
        'paciente': paciente,
        'nomUsuario': request.session['nomUsuario']
    })

def ver_formularios(request):
    if not request.session.get('estadoSesion'):
        datos = {'mensaje': 'Debe iniciar sesión para ver los formularios.'}
        return render(request, 'index.html', datos)

    lista = Paciente.objects.all().order_by('-fecha_registro')
    paginator = Paginator(lista, 5)
    page = request.GET.get('page')
    pa = paginator.get_page(page)

    datos = {
        'nomUsuario': request.session['nomUsuario'],
        'pa': pa
    }
    return render(request, 'ver_formularios.html', datos)

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

        try:
            usuario = Usuario.objects.get(rut=rut)
        except Usuario.DoesNotExist:
            mensaje = "RUT o Contraseña incorrectos. Intente nuevamente."
            return render(request, 'login.html', {'mensaje': mensaje})

        if check_password(con, usuario.contraseña):
            request.session['estadoSesion'] = True
            request.session['rutUsuario'] = rut
            request.session['idUsuario'] = usuario.id
            request.session['nomUsuario'] = usuario.nombre
            cargo = request.session['cargoUsuario'] = usuario.cargo

            descripcion = "Inicio de sesión"
            tabla = "Usuario"
            his = Historial(usuario_id=usuario.id, descripcion=descripcion, tabla_afectada=tabla, fecha_hora=datetime.now())
            his.save()

            datos = {'rut': rut, 'nombre': usuario.nombre}

            if cargo == 'Paramedico':
                return render(request, 'menu_paramedico.html', datos)
            elif cargo == 'Hospital':
                return render(request, 'menu_hospital.html', datos)
            elif cargo == 'Administrador':
                return render(request, 'index.html', datos)
        else:
            mensaje = "RUT o Contraseña incorrectos. Intente nuevamente."
            return render(request, 'login.html', {'mensaje': mensaje})

def ver_historial(request):
    estado = request.session.get('estadoSesion')
    cargo = request.session.get('cargoUsuario')

    if not estado or cargo != 'Administrador':
        datos = {'mensaje': 'Acceso denegado.'}
        return render(request, 'index.html', datos)

    lista = Historial.objects.all().order_by('-fecha_hora')

    paginator = Paginator(lista, 12)
    page = request.GET.get('page')
    historial = paginator.get_page(page)

    datos = {
        'nomUsuario': request.session['nomUsuario'],
        'historial': historial
    }

    return render(request, 'historial.html', datos)

def enviar_alerta(request, id_paciente):
    if request.session.get('cargoUsuario') != 'Hospital':
        return render(request, 'index.html', {'mensaje': 'Acceso denegado.'})

    mensaje = request.POST.get('mensaje')

    if not mensaje:
        return redirect('ver_formularios')

    Alerta.objects.create(
        paciente_id=id_paciente,
        mensaje=mensaje,
        estado="Pendiente"
    )

    return redirect('ver_formularios')

def resolver_alerta(request, id_alerta):
    if request.session.get('cargoUsuario') != 'Paramedico':
        return render(request, 'index.html', {'mensaje': 'Acceso denegado.'})

    try:
        alerta = Alerta.objects.get(id=id_alerta)
        alerta.estado = "Solucionado"
        alerta.save()
    except Alerta.DoesNotExist:
        pass

    return redirect('ver_alertas')

def ver_alertas(request):
    cargo = request.session.get('cargoUsuario')

    if cargo == "Hospital" or cargo == "Administrador":
        alertas = Alerta.objects.all().order_by('-fecha')
    elif cargo == "Paramedico":
        alertas = Alerta.objects.all().order_by('-fecha')
    else:
        return render(request, 'index.html', {'mensaje': 'Acceso denegado.'})

    return render(request, 'ver_alertas.html', {'alertas': alertas})

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