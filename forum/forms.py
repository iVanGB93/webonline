from django import forms
from .models import Publicacion

class PublicacionForm(forms.ModelForm):    
    """ titulo = forms.CharField(max_length=20, label='Título:', widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'título...'
    }))
    contenido = forms.CharField(max_length=10000, label='Texto:', widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'texto...'
    })) """
    class Meta:
        model = Publicacion
        fields = [
            'imagen1',
            'imagen2',
            'imagen3',
        ]