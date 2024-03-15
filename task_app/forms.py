from django import forms
from .models import TODO

class TODOForm(forms.ModelForm):
    STATUS_CHOICES = [
        ('P', 'Pending'),
        ('C', 'Completed'),
    ]

    due_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        input_formats=['%Y-%m-%dT%H:%M'],  # Adjust the format as needed
    )
    
    status = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = TODO
        fields = ['title', 'description', 'due_date', 'status']  # Adjust fields based on your model
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
