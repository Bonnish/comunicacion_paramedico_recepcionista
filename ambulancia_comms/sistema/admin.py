from django.contrib import admin
from django.contrib.auth.hashers import make_password
from .models import Usuario, Paciente

class UsuarioAdmin(admin.ModelAdmin):
    list_display = ("rut", "nombre", "cargo", "email", "telefono")

    def save_model(self, request, obj, form, change):
        contraseña = form.cleaned_data.get("contraseña")

        if contraseña and not contraseña.startswith("pbkdf2_"):
            obj.contraseña = make_password(contraseña)

        super().save_model(request, obj, form, change)

admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Paciente)
