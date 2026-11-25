from datetime import timedelta
import csv

from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from django.utils import timezone

from sale.models import Check

User = get_user_model()


class ReportsPage(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "reports.html"

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect("/auth/login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        now = timezone.now()
        selected_range = self.request.GET.get("range", "7")
        selected_cashier = self.request.GET.get("cashier", "all")

        if selected_range == "30":
            start_date = now - timedelta(days=30)

        elif selected_range == "month":
            start_date = now.replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )

        else:
            selected_range = "7"
            start_date = now - timedelta(days=7)

        checks = Check.objects.filter(
            status=True,
            created_at__gte=start_date
        )

        if selected_cashier != "all":
            try:
                cashier_id = int(selected_cashier)
                checks = checks.filter(user_id=cashier_id)

            except (ValueError, TypeError):
                selected_cashier = "all"

        checks = checks.select_related(
            "user"
        ).prefetch_related(
            "check_items__product"
        )

        cashier_data = {}
        revenue = 0

        for check in checks:
            cashier = check.user

            if cashier.id not in cashier_data:
                cashier_data[cashier.id] = {
                    "name": cashier.get_full_name() or cashier.username,
                    "sales": 0,
                    "revenue": 0,
                }

            check_total = 0

            for item in check.check_items.all():
                check_total += item.amount * item.product.sell_price

            cashier_data[cashier.id]["sales"] += 1
            cashier_data[cashier.id]["revenue"] += check_total

            revenue += check_total

        cashier_stats = []

        for cashier in cashier_data.values():
            cashier["avg_basket"] = (
                cashier["revenue"] / cashier["sales"]
                if cashier["sales"] > 0 else 0
            )

            cashier_stats.append(cashier)

        cashier_stats.sort(
            key=lambda cashier: cashier["revenue"],
            reverse=True
        )

        max_revenue = (
            cashier_stats[0]["revenue"]
            if cashier_stats else 0
        )

        for cashier in cashier_stats:
            cashier["share_percent"] = (
                cashier["revenue"] / max_revenue * 100
                if max_revenue > 0 else 0
            )

        transactions = checks.count()

        avg_basket = (
            revenue / transactions
            if transactions > 0 else 0
        )

        top_cashier = (
            cashier_stats[0]["name"]
            if cashier_stats else "—"
        )

        context["revenue"] = revenue
        context["transactions"] = transactions
        context["avg_basket"] = avg_basket
        context["cashier_stats"] = cashier_stats
        context["top_cashier"] = top_cashier

        context["cashiers"] = User.objects.filter(
            is_superuser=False
        ).order_by("first_name", "last_name")

        context["selected_range"] = selected_range
        context["selected_cashier"] = selected_cashier

        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get("export") == "csv":
            response = HttpResponse(
                content_type="text/csv; charset=utf-8"
            )

            response["Content-Disposition"] = (
                'attachment; filename="cashier_report.csv"'
            )

            response.write("\ufeff")

            writer = csv.writer(response)

            writer.writerow(["Cashier Reports"])
            writer.writerow([])

            writer.writerow([
                "Cashier",
                "Sales",
                "Revenue",
                "Average Basket"
            ])

            for cashier in context["cashier_stats"]:
                writer.writerow([
                    cashier["name"],
                    cashier["sales"],
                    round(cashier["revenue"], 2),
                    round(cashier["avg_basket"], 2)
                ])

            writer.writerow([])

            writer.writerow([
                "TOTAL",
                context["transactions"],
                round(context["revenue"], 2),
                round(context["avg_basket"], 2)
            ])

            return response

        return super().render_to_response(
            context,
            **response_kwargs
        )
