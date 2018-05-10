from django.urls import path

from . import views


urlpatterns = [
    path(
        'search/<str:keyword>',
        views.SearchAPIView.as_view(),
        name='search_api'
    ),
    path(
        'suggest/<str:keyword>',
        views.SuggestAPIView.as_view(),
        name='suggest_api'
    ),
    path(
        'recommend/<str:keyword>/<str:recommend_by>',
        views.RecommendAPIView.as_view(),
        name='recommend_api'
    ),
    path(
        'reindex/<int:id>',
        views.ReIndexAPIView.as_view(),
        name='reindex_api'
    ),
    path(
        'generate_keyword',
        views.GenerateKeywordAPIView.as_view(),
        name='generate_keyword'
    )
]