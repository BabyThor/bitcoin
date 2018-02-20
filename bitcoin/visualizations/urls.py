from django.urls import path

from . import views


urlpatterns = [
    path(
        '<str:currency>',
        views.HistoricalRateView.as_view(),
        name='historical'
    ),
    path(
        'settings/',
        views.SettingsView.as_view(),
        name='settings'
    ),
    path(
        'api/<str:timeframe>/<str:currency>',
        views.CurrencyAPIView.as_view(),
        name='currency_api'
    )
]