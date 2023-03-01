from django import forms
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox

class ZipFileForm(forms.Form):
    docfile = forms.FileField(label='Select a file', help_text='max. 10 megabytes')
    file_name = forms.TextInput()
    language = forms.TextInput()

class CaptchaTestForm(forms.Form):
    captcha = ReCaptchaField()