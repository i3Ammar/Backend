from django_registration.forms import RegistrationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from afkat_auth.models import User


class UserRegistrationForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = User

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Register"))
