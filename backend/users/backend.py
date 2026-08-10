from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmailBackend(ModelBackend):
    # Nicht in AUTHENTICATION_BACKENDS (settings.py) eingetragen, aktuell also ungenutzt -
    # Login läuft über das Standard-ModelBackend, weil username dort immer = email ist.
    def authenticate(self, request, username = None, password = None, **kwargs):
        UserModel = get_user_model()

        # Django reicht die Login-Kennung konventionell als "username" durch, auch wenn hier die E-Mail gemeint ist
        email = username or kwargs.get('email')
        try:
            # setzt Eindeutigkeit der E-Mail voraus - anders als username ist email beim
            # Standard-User-Model nicht auf DB-Ebene unique (nur RegisterView prüft das)
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            return None
        
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None