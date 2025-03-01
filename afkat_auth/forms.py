from afkat_auth.models import User
from django_registration.forms import RegistrationForm

class AfkatRegistrationForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = User


