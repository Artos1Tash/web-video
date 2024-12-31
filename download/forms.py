from django import forms

class ResponseForm(forms.Form):
    url = forms.URLField(label='URL', max_length=1000)
    
    
