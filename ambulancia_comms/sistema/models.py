from django.db import models

class Usuario(models.Model):
    rut = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=100)
    cargo = models.CharField(max_length=50)
    contraseña = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=15)

class Paciente(models.Model):
    nombre = models.CharField(max_length=100)
    edad = models.IntegerField()
    estado = models.CharField(max_length=20, default="Enviado", choices=[ ("Enviado", "Enviado"), ("En tránsito", "En tránsito"), ("Recibido", "Recibido"), ])
    genero = models.CharField(max_length=10)
    prevision = models.CharField(max_length=50)
    accidente_laboral = models.BooleanField(default=False)
    comorbilidades = models.TextField(blank=True)
    funcionalidad = models.CharField(max_length=100)
    motivo_derivacion = models.TextField()
    prestacion_requerida = models.TextField()
    glasgow = models.IntegerField()
    llenado_capilar = models.CharField(max_length=20)
    fc = models.IntegerField()
    fr = models.IntegerField()
    fio2 = models.CharField(max_length=10)
    sat02 = models.IntegerField()
    fecha_registro = models.DateTimeField(auto_now_add=True)

class Historial(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=200)
    tabla_afectada = models.CharField(max_length=100)
    fecha_hora = models.DateTimeField()
    def __str__ (self):
        return str(self.usuario)+"-"+str(self.descripcion)+"-"+str(self.tabla_afectada)+"-"+str(self.fecha_hora)
    
class Alerta(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    mensaje = models.TextField()
    estado = models.CharField(
        max_length=20,
        choices=[('Pendiente', 'Pendiente'), ('Solucionado', 'Solucionado')],
        default='Pendiente'
    )
    fecha = models.DateTimeField(auto_now_add=True)