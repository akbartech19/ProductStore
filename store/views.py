from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, ListView

from .models import Products, Discount, Categories

from .forms import ProductAddForm, DiscountAddForm


class StorePage(LoginRequiredMixin, UserPassesTestMixin,ListView):
    template_name = "products.html"
    model = Products
    
    
    def get_context_data(self):
        context = super().get_context_data()
        context["product_form"] = ProductAddForm()
        context["discount_form"] = DiscountAddForm()
        return context
    
    
    def post(self, request):
        
        if "product_add" in request.POST:
            form = ProductAddForm(request.POST)
            if form.is_valid():
                form.save()
                form = ProductAddForm()
                
                return redirect("store:store_page") 
               
            messages.error(request, "There has been error during product creation !")
            return redirect("store:store_page")
        
        
        if "discount_add" in request.POST:
            form = DiscountAddForm(request.POST)
            if form.is_valid():
                discount = form.save(commit=False)
                discount.product_id = request.POST.get("product")
                discount.save()
                messages.success(request, "New Discount is created !")
                return redirect("store:store_page")
            
            messages.error(request, "Something went bad !")
            return redirect("store:store_page")
        
            
    def test_func(self):
        return self.request.user.is_superuser
    
    def handle_no_permission(self):
        messages.error(self.request, "Sizning bu bo'limga kirishga ruxsatingiz yo'q!")
        return redirect("/auth/login")
    