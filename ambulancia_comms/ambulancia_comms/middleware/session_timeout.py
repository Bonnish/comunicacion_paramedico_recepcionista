from datetime import datetime, timedelta
from django.shortcuts import redirect

# Funcion para cerrar la sesion automaticamente despues de detectar inactividad de parte del usuario

class SessionTimeoutMiddleware:
    SESSION_TIMEOUT_MINUTES = 30

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.session.get("estadoSesion"):

            ahora = datetime.now()
            ultimo = request.session.get("ultima_actividad")

            if ultimo:
                ultimo = datetime.fromisoformat(ultimo)
                if ahora - ultimo > timedelta(minutes=self.SESSION_TIMEOUT_MINUTES):
                    request.session.flush()
                    return redirect("mostrar_login")
            
            request.session["ultima_actividad"] = ahora.isoformat()

        return self.get_response(request)
