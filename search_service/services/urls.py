from django.urls import path

from . import views


urlpatterns = [
    path(
        'search',
        views.SearchView.as_view(),
        name='search_view'
    ),
    path(
        'result/<str:keyword>',
        views.ResultView.as_view(),
        name='result_view'
    ),
    # path(
    #     'sugggest/<str:keyword>',
    #     views.SuggestAPIView.as_view(),
    #     name='suggest_api'
    # ),
    # path(
    #     'reindex/<int:id>',
    #     views.ReIndexAPIView.as_view(),
    #     name='reindex_api'
    # )
]