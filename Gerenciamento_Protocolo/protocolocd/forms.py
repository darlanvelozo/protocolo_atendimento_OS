# forms.py
from django import forms
from .models import Responsavel

from .models import SuporteProtocolo
class MensagemForm(forms.Form):
    mensagem = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Digite sua mensagem'}))

class ResponsavelForm(forms.ModelForm):
    class Meta:
        model = Responsavel
        fields = ['nome', 'telefone', 'email', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do responsável'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '86999998888'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'exemplo@email.com'}),
        }
        
    def clean_telefone(self):
        """Valida o formato do telefone."""
        telefone = self.cleaned_data.get('telefone', '')
        # Remove caracteres não numéricos
        telefone = ''.join(filter(str.isdigit, telefone))
        
        # Verifica se o telefone tem pelo menos 10 dígitos
        if len(telefone) < 10:
            raise forms.ValidationError('O telefone deve ter pelo menos 10 dígitos')
            
        return telefone

class SuporteProtocoloForm(forms.ModelForm):
    class Meta:
        model = SuporteProtocolo
        fields = ['id_cliente_servico', 'descricao', 'responsavel', 'id_tipo_atendimento', 'id_atendimento_status', 'ativo', 'protocolo', 'data_hora_falha']