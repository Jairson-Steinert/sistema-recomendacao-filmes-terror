from django import forms

class MovieSearchForm(forms.Form):
    """
    Formulário para busca de filmes
    """
    search = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite o nome do filme ou gênero...',
            'autocomplete': 'off'
        })
    )
