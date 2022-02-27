from django import forms

class ClaimFundsForm(forms.Form):
        email = forms.EmailField()
