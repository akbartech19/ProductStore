
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView

from .models import Products, Discount
from .forms import ProductAddForm, DiscountAddForm
from django.db.models import Q


class StorePage(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = "products.html"
    model = Products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["product_form"] = ProductAddForm()
        context["discount_form"] = DiscountAddForm()

        return context

    def post(self, request, *args, **kwargs):
        print("POST DATA:", request.POST)

        # EDIT PRODUCT
        if "product_edit" in request.POST:
            product_id = request.POST.get("product_id")

            product = get_object_or_404(Products, id=product_id)

            product.name = request.POST.get("name")
            product.sell_price = request.POST.get("sell_price")
            product.original_price = request.POST.get("original_price")
            product.store_amount = request.POST.get("store_amount")
            product.unit = request.POST.get("unit")

            product.save()

            messages.success(request, "Product updated successfully!")
            return redirect("store:store_page")

        # ADD PRODUCT
        if "product_add" in request.POST:
            form = ProductAddForm(request.POST)

            if form.is_valid():
                form.save()
                messages.success(request, "Product added successfully!")
            else:
                messages.error(request, str(form.errors))

            return redirect("store:store_page")

        # ADD DISCOUNT
        if "discount_add" in request.POST:
            form = DiscountAddForm(request.POST)

            if form.is_valid():
                product_id = request.POST.get("product")
                product = get_object_or_404(Products, id=product_id)

                discount = form.save(commit=False)
                discount.product = product
                discount.save()

                messages.success(request, "New discount created successfully!")
            else:
                messages.error(request, str(form.errors))

            return redirect("store:store_page")

        # DELETE PRODUCT
        if "delete" in request.POST:
            product_id = request.POST.get("product_id")

            product = get_object_or_404(Products, id=product_id)
            product.delete()

            messages.success(request, "Product deleted successfully!")
            return redirect("store:store_page")

        # REMOVE DISCOUNT
        if "remove" in request.POST:
            product_id = request.POST.get("product")

            product = get_object_or_404(Products, id=product_id)
            discount = product.discounts.order_by("-created_at").first()

            if discount:
                discount.delete()
                messages.success(request, "Discount removed successfully!")
            else:
                messages.warning(request, "This product has no discount!")

            return redirect("store:store_page")

        return redirect("store:store_page")

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(
            self.request,
            "Sizning bu bo'limga kirishga ruxsatingiz yo'q!"
        )

        return redirect("/auth/login")
    

    
    def get_queryset(self):
        queryset = super().get_queryset()

        search = self.request.GET.get("q", "").strip()
        category = self.request.GET.get("cat", "").strip()

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(barcode__icontains=search)
            )

        if category:
            queryset = queryset.filter(
                category__name__iexact=category
            )

        return queryset
