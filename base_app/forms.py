from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _


class DispositorForm(UserCreationForm):
    # superuser dispositor creation form

    error_messages = {
        'password_mismatch': _('Wprowadzone hasła nie są takie same.')
    }
    group_name = 'dispositors'

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
        # add user to group
        user.groups.add(Group.objects.get_or_create(name=self.group_name)[0])

    def save(self, *args, **kwargs):
        user = super().save()
        self.add_user_to_group(user)


class ParamedicForm(DispositorForm):
    group_name = 'paramedics'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = _('Nazwa użytkownika - Ratownika')
