# forms.py
from django import forms

class MensagemForm(forms.Form):
    mensagem = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Digite sua mensagem'}))
