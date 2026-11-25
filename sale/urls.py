
from django.urls import path
from . import views

app_name = "sale"

urlpatterns = [
    path('', views.SalePage.as_view(), name='sale_page'),
    path(
        'void/<int:check_id>/',
        views.VoidSaleView.as_view(),
        name='void_sale'
    ),
]
