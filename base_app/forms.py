from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from base_app.models import Dispositor, Paramedic, ParamedicSettings, Settings


class CustomAuthenticationForm(AuthenticationForm):
    error_messages = {
        "invalid_login": _(
            "Proszę wprowadzić poprawną nazwę użytkownika oraz hasło. Zauważ, że oba pola zwracają uwagę"
            " na wielkość liter. "
        ),
        "inactive": _("To konto jest nieaktywne"),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['password'].label = 'Hasło'
        self.fields['username'].label = 'Nazwa użytkownika'
    pass


class DispositorForm(UserCreationForm):
    # superuser dispositor creation form

    error_messages = {
        'password_mismatch': _('Wprowadzone hasła nie są takie same.')
    }
    group_name = 'dispositors'
    DataClass = Dispositor

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = _('Hasło')
        self.fields['password1'].help_text = _('<ul>'
                                               '<li>Twoje hasło nie może być zbyt podobne do innych informacji osobistych.</li>'
                                               '<li>Twoje hasło musi zawierać przynajmniej 8 znaków.</li>'
                                               '<li>Twoje hasło nie może być często używanym hasłem</li>'
                                               '<li>Twoje hasło nie może być wyłącznie numeryczne</li>'
                                               '</ul>')

        self.fields['password2'].label = _('Powtórz hasło')
        self.fields['password2'].help_text = _('Wprowadź to samo hasło, dla weryfikacji.')
        self.fields['username'].label = _('Nazwa użytkownika - Dyspozytora')
        self.fields['username'].help_text = _(
            "Wymagane. Maksymalnie 150 znaków. Litery, cyfry oraz @/./+/-/_ dozwolone.<br>"
        )

    def add_user_to_group(self, user):
        user.groups.add(Group.objects.get_or_create(name=self.group_name)[0])

    def create_user_data_instance(self, user):
        data_instance = self.DataClass.get_by_user(user)
        return data_instance

    def save(self, **kwargs):
        user = super().save()
        self.add_user_to_group(user)
        self.create_user_data_instance(user)
        return user


class ParamedicForm(DispositorForm):
    group_name = 'paramedics'
    DataClass = Paramedic

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = _('Nazwa użytkownika - Ratownika')


class ParamedicSettingsForm(forms.ModelForm):
    class Meta:
        model = ParamedicSettings
        fields = ('routing_profile', 'isochrone_range')
        labels = {
            'routing_profile': 'Rodzaj lokomocji',
            'isochrone_range': 'Zasięg izochrony (wyrażany w sekundach)'
        }


class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = '__all__'
        labels = {
            'default_latitude': 'Domyślna szerokość geograficzna',
            'default_longitude': 'Domyślna długość geograficzna',
            'default_zoom': 'Domyślne przybliżenie mapy'
        }
