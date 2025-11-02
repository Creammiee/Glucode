from django import forms
from .models import GlucoseRecord

class GlucoseForm(forms.ModelForm):
    class Meta:
        model = GlucoseRecord
        fields = ['value']
        widgets = {
            'value': forms.NumberInput(attrs={
                'class': 'w-full p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-[#ce7d99]',
                'placeholder': 'Enter glucose value (mg/dL)'
            }),
        }
