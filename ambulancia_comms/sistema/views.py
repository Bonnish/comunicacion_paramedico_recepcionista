from datetime import datetime
from openpyxl import Workbook
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
import io
from django.http import FileResponse, HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from .models import Usuario, Paciente, Historial, Alerta

# Funcion para mostrar la pagina index

def index(request):
    return render(request, 'index.html')

# Funcion para exportar los formularios a excel

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

# Funcion para exportar el formulario seleccionado a pdf con diseño

def exportar_pdf(request, id):
    if not request.session.get('estadoSesion') or request.session.get('cargoUsuario') not in ['Hospital', 'Administrador']:
        return render(request, 'index.html', {'mensaje': 'Acceso denegado.'})

    try:
        paciente = Paciente.objects.get(id=id)
    except Paciente.DoesNotExist:
        return render(request, 'index.html', {'mensaje': 'Formulario no encontrado'})

    buffer = io.BytesIO()

    pdf = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=55,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    azul = colors.HexColor("#004aad")
    azul_oscuro = colors.HexColor("#003580")
    blanco = colors.white

    header_style = ParagraphStyle(
        name="HeaderStyle",
        parent=styles["Heading1"],
        alignment=1,
        fontSize=20,
        textColor=blanco,
        spaceAfter=10
    )

    subtitulo_style = ParagraphStyle(
        name="Subtitulo",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=azul,
        spaceAfter=6
    )

    normal = styles["Normal"]

    parrafo = lambda t: Paragraph(str(t), normal)

    contenido = []

    header = Table(
        [[Paragraph("Formulario de Paciente", header_style)]],
        colWidths=[500]
    )
    header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), azul),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
    ]))

    contenido.append(header)
    contenido.append(Spacer(1, 18))

    contenido.append(Paragraph("Datos del Paciente", subtitulo_style))

    data = [
        ["Nombre:", parrafo(paciente.nombre)],
        ["Edad:", parrafo(paciente.edad)],
        ["Estado:", parrafo(paciente.estado)],
        ["Género:", parrafo(paciente.genero)],
        ["Previsión:", parrafo(paciente.prevision)],
        ["Accidente laboral:", parrafo("Sí" if paciente.accidente_laboral else "No")],
        ["Comorbilidades:", parrafo(paciente.comorbilidades)],
        ["Funcionalidad:", parrafo(paciente.funcionalidad)],
        ["Motivo derivación:", parrafo(paciente.motivo_derivacion)],
        ["Prestación requerida:", parrafo(paciente.prestacion_requerida)],
        ["Glasgow:", parrafo(paciente.glasgow)],
        ["Llenado capilar:", parrafo(paciente.llenado_capilar)],
        ["FC:", parrafo(paciente.fc)],
        ["FR:", parrafo(paciente.fr)],
        ["FiO2:", parrafo(paciente.fio2)],
        ["SatO2:", parrafo(paciente.sat02)],
        ["Fecha registro:", parrafo(paciente.fecha_registro.strftime('%d/%m/%Y %H:%M'))],
    ]

    tabla = Table(data, colWidths=[160, 300])

    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), blanco),

        ("TEXTCOLOR", (0, 0), (0, -1), azul),

        ("TEXTCOLOR", (1, 0), (1, -1), colors.black),

        ("GRID", (0, 0), (-1, -1), 0.6, azul),

        ("VALIGN", (0, 0), (-1, -1), "TOP"),

        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    contenido.append(tabla)
    contenido.append(Spacer(1, 25))

    footer = Paragraph(
        "<para align='center' color='#004aad' fontSize='10'>"
        "Documento generado automáticamente por el sistema"
        "</para>",
        normal
    )
    contenido.append(footer)
    pdf.build(contenido)
    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename=f"paciente_{paciente.id}.pdf")


# Funcion para mostrar la pagina de creacion de usuarios

def mostrar_crear_usuario(request):
    estado = request.session.get('estadoSesion')
    cargo = request.session.get('cargoUsuario')

    if not estado or cargo != 'Administrador':
        datos = {'mensaje': 'Acceso denegado.'}
        return render(request, 'index.html', datos)

    return render(request, 'crear_usuario.html')

# Funcion para crear un usuario nuevo

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

# Funcion para listar los usuarios en la base de datos

def listar_usuarios(request):
    if not request.session.get('estadoSesion') or request.session.get('cargoUsuario') != 'Administrador':
        return render(request, 'index.html', {'mensaje': 'Acceso denegado.'})

    lista = Usuario.objects.all().order_by('nombre')
    paginator = Paginator(lista, 5)
    page = request.GET.get('page')
    usuarios = paginator.get_page(page)

    return render(request, 'listar_usuarios.html', {'usuarios': usuarios})

# Funcion para editar algun campo del usuario en la base de datos

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

# Funcion para eliminar un usuario de la base de datos

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

# Funcion para mostrar el menu del usuario con el cargo "Paramedico"

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
    
# Funcion para mostrar el menu del usuario con el cargo "Hospital"

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
    
# Funcion para mostrar la pagina del formulario

def mostrar_enviar_formulario(request):
    estado_sesion = request.session.get('estadoSesion')
    cargo_usuario = request.session.get('cargoUsuario')

    if cargo_usuario in ['Paramedico', 'Administrador'] and estado_sesion:
        return render(request, 'enviar_formulario.html')
    else:
        datos = {'mensaje': 'Acceso no autorizado. Inicie sesión con una cuenta de Paramedico o Administrador.'}
        return render(request, 'index.html', datos)

# Funcion para enviar formulario a la base de datos

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

# Funcion para cambiar el estado de los pacientes

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

# Funcion para editar formularios

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

# Funcion para ver los formularios

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

# Funcion para mostrar la pagina del login

def mostrar_login(request):
    estado_sesion = request.session.get('estadoSesion')

    if estado_sesion:
        mensaje = "Ya tienes una sesión activa."
        return render(request, 'index.html', {'mensaje': mensaje})
    else:
        return render(request, 'login.html')
    
# Funcion para procesar los datos del login

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
        
# Funcion para ver el historial de acciones de usuario (Menu Administrador)

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

# Funcion para envair alerta al paramedico (Menu Hospital)

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

# Funcion para cambiar estado alerta (Menu paramedico)

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

# Funcion para ver alertas (Menu paramedico)

def ver_alertas(request):
    cargo = request.session.get('cargoUsuario')

    if cargo == "Hospital" or cargo == "Administrador":
        alertas = Alerta.objects.all().order_by('-fecha')
    elif cargo == "Paramedico":
        alertas = Alerta.objects.all().order_by('-fecha')
    else:
        return render(request, 'index.html', {'mensaje': 'Acceso denegado.'})

    return render(request, 'ver_alertas.html', {'alertas': alertas})

# Funcion de cierre de sesión

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