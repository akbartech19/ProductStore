
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, View
from django.utils import timezone
from django.db import transaction

from sale.models import Check


class SalePage(LoginRequiredMixin, TemplateView):
    template_name = "sale.html"


class VoidSaleView(LoginRequiredMixin, UserPassesTestMixin, View):

    def test_func(self):
        return self.request.user.is_superuser

    def post(self, request, check_id):
        with transaction.atomic():
            check = get_object_or_404(
                Check.objects.select_for_update(),
                id=check_id
            )

            if check.is_voided:
                messages.error(request, "This sale is already voided.")
                return redirect(request.META.get("HTTP_REFERER", "/"))

            if not check.sta0tus:
                messages.error(request, "This sale cannot be voided.")
                return redirect(request.META.get("HTTP_REFERER", "/"))

            items = check.check_items.select_related("product")

            for item in items:
                product = item.product
                product.store_amount += item.amount
                product.save(update_fields=["store_amount"])

            check.is_voided = True
            check.voided_at = timezone.now()
            check.voided_by = request.user

            check.save(update_fields=[
                "is_voided",
                "voided_at",
                "voided_by"
            ])

        messages.success(request, "Sale successfully voided.")

        return redirect(request.META.get("HTTP_REFERER", "/"))
