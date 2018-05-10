import datetime
from datetime import timedelta
import json
import requests

from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView, View
from settings.models import RecommendSetting


class SearchView(TemplateView):
    template = 'search.html'

    def get(self, request):
        query = self.request.GET.get('q')
        if query:
            keyword = query
            url = 'http://0.0.0.0:8000/api/search/' + keyword
            res = requests.get(url)
            content = json.loads(res.content)
            data = content['data']
            aggr = content['aggr']

            recommend = {}
            for setting in RecommendSetting.objects.all():
                recommend_by = setting.field.key + '^100'
                url = 'http://0.0.0.0:8000/api/recommend/' + keyword + '/' + recommend_by
                res = requests.get(url)
                items = json.loads(res.content)
                recommend[setting.field.name] = items

            return render(
                request,
                self.template,
                {
                    'keyword': keyword,
                    'data': data,
                    'aggr': aggr,
                    'recommend': recommend
                }
            )
        else:
            return render(
                request,
                self.template
            )


class ResultView(TemplateView):
    template = 'result.html'

    def get(self, request, keyword):
        return render(
            request,
            self.template,
            {
            'keyword': keyword
            }
        )
