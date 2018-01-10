from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns(
    '',
    url(
        r'^$',
        login_required(views.HistoricalRateView.as_view()),
        name='historical'
    ),
    url(
        r'^api/$',
        login_required(views.CurrencyAPIView.as_view()),
        name='currency_api'
    ),