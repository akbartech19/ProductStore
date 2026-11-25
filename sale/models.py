from django.db import models
from django.contrib.auth.models import User
from store.models import Products


class Check(models.Model):
    payment_type = models.CharField(max_length=10)
    sold = models.DateTimeField(blank=True, null=True)
    status = models.BooleanField(default=False)
    is_voided = models.BooleanField(default=False)
    voided_at = models.DateTimeField(blank=True, null=True)
    voided_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="voided_checks"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="checks"
    )



class CheckItem(models.Model):
    product = models.ForeignKey(
        Products,
        on_delete=models.CASCADE,
        related_name="items"
    )
    amount = models.FloatField(default=0)
    checks = models.ForeignKey(
        Check,
        on_delete=models.CASCADE,
        related_name="check_items"
    )


class SaleReturn(models.Model):
    sale_check = models.ForeignKey(
        Check,
        on_delete=models.CASCADE,
        related_name="returns"
    )
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="processed_returns"
    )
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ReturnItem(models.Model):
    sale_return = models.ForeignKey(
        SaleReturn,
        on_delete=models.CASCADE,
        related_name="items"
    )
    check_item = models.ForeignKey(
        CheckItem,
        on_delete=models.CASCADE,
        related_name="return_items"
    )
    amount = models.FloatField(default=0)
    refund_price = models.FloatField(default=0)