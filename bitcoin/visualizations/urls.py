from django.urls import path

from . import views


urlpatterns = [
    path(
        '',
        views.HistoricalRateView.as_view(),
        name='historical'
    ),
    path(
        'api',
        views.CurrencyAPIView.as_view(),
        name='currency_api'
    ),
]