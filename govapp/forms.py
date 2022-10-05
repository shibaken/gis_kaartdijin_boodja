from django import forms
#from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, HTML, Fieldset, MultiField, Div, Button
from django.forms import Form, ModelForm, ChoiceField, FileField, CharField, Textarea, ClearableFileInput, HiddenInput, Field, RadioSelect, ModelChoiceField, Select, CheckboxInput
import re
from django.contrib.auth import get_user_model
User = get_user_model()

DEPARTMENTS = (
                (0, 'Parks and Wildlife'),
                (1, 'Rottnest Island'),
                (2 , 'Perth Zoo')
              )

class BaseFormHelper(FormHelper):
    form_class = 'form-horizontal'
    label_class = 'form-label col-xs-12 col-sm-4 col-md-3 col-lg-2'
    field_class = 'form-control col-xs-12 col-sm-8 col-md-6 col-lg-4'


class TestContactForm(forms.Form):
    first_name = forms.CharField(label="First Name",  required=False)
    last_name = forms.CharField(label="Last Name", widget=forms.TextInput(attrs={}), required=False)
    department = forms.ChoiceField(label="Departments", choices=DEPARTMENTS)


class TestContactForm(forms.ModelForm):

    class Meta:
        model = User 
        fields = ['first_name','last_name']

    def __init__(self, *args, **kwargs):
        # User must be passed in as a kwarg.
        super(TestContactForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        self.helper.form_id = 'id_test_contact_form'
        self.helper.field_class = 'form-control'
        for f in self.fields:
            self.fields[f].widget.attrs.update({'class': 'form-control'})
        self.helper.add_input(Submit('Save', 'Save', css_class='btn-lg'))

    def clean(self):
        super(TestContactForm, self).clean()

    def clean_first_name(self):
        if self.cleaned_data.get('first_name') == '' or self.cleaned_data.get('first_name') is None: 
             raise forms.ValidationError('Sorry, please provide a first name')

        return self.cleaned_data['first_name']


