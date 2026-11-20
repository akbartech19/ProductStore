from django import forms
from .models import Products, Categories, Discount


class ProductAddForm(forms.ModelForm):
    unit = forms.ChoiceField(choices=[("KG", "kg"), ("L", "L"), ("PEACE", "peace")])   
    
    class Meta:
        model = Products
        fields = [
                  "barcode", 
                  "name", 
                  "sell_price", 
                  "original_price", 
                  "store_amount",
                  "unit",
                  "category"
                ]


class DiscountAddForm(forms.ModelForm):
    type_discount = forms.ChoiceField(choices=[("percent", "% percent"), ("sum", "Sum")])   
    start_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={"type":"datetime-local"}))
    end_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={"type":"datetime-local"}))
    
    
    class Meta:
        model = Discount
        fields = ["type_discount", "value", "start_time", "end_time"]