from django import forms
from .models import Branch, Place
class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['business','name','address','open_time','close_time','is_active']
class PlaceForm(forms.ModelForm):
    class Meta:
        model = Place
        fields = ['branch','name','place_type','capacity','price','description','is_active']
