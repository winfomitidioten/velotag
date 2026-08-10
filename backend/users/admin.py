from django.contrib import admin

# Register your models here.
from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

User = get_user_model()
class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(
        label="Passwort", 
        widget=forms.PasswordInput,
        help_text="Gib ein sicheres Passwort ein."
    )
    
    class Meta:
        model = User
        fields = ('email', 'password')  # kein username-Feld: wird per pre_save-Signal (users/signals.py) automatisch erzeugt 

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"]) # Verschlüsselung der Passwörter
        if commit:
            user.save()
        return user


# Anpassung des Admin-Panels (testweise)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    
    list_display = ('email', 'username', 'is_staff', 'is_active')
    
    search_fields = ('email', 'username')
    ordering = ('email',)

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password'),
        }),
    )

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)