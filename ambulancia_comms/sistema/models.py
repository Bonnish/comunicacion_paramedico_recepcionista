from django.db import models

# Create your models here.
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