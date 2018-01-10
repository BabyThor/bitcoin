import datetime, timedelta
import itertools
import json
from pymongo import MongoClient

from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView, View


class HistoricalRateView(TemplateView):
    template = 'history.html'

    def get(self, request):
        return render(
            request,
            self.template
        )


class CurrencyAPIView(View):

    def get(self, request):
        client = MongoClient('mongodb', 27017)
        db = client.bitcoin
        th_exchange = db.th_exchange
        exchange_rate = db.exchange_rate
        eu_exchange = db.eu_exchange

        24hours_before = datetime.datetime.utcnow() - timedelta(hours=1)
        th_data = th_exchange.find({'date': {'$gte': 24hours_before}}).sort('date')

        data = {
            'x': [],
            'XRP': [],
            'BCH': [],
            'ETH': [],
            'DAS': [],
            'REP': [],
            'BTC': [],
            'LTC': [],
        }
        for item in th_data:
            item_date = item['date']
            start_date = datetime.datetime(item_date.year, item_date.month, item_date.day, item_date.hour, item_date.minute, 0)
            end_date = start_date + timedelta(minutes=1)

            exchange_rate_start_date = datetime.datetime(item_date.year, item_date.month, item_date.day, item_date.hour, 0, 0)
            exchange_rate_end_date = datetime.datetime(item_date.year, item_date.month, item_date.day, item_date.hour, 59, 59)
            
            thb_rate = item['rate']
            eu_rate = eu_exchange.find_one({'date': {'$lte': end_date}}, {'secondary': item['secondary']})
            exchange_rate_item = exchange_rate.find_one({'date': {'$gte': exchange_rate_start_date, '$lte': exchange_rate_end_date}})

            price_th_us = float(thb_rate) / float(exchange_rate_item['thb'])
            price_eu_us = float(eu_rate['rate']) / float(exchange_rate_item['eur'])
            percentage_diff = ((price_th_us - price_eu_us)/price_eu_us) * 100

            data['x'] = data['x'].append(start_date.strftime('%y-%m-%d:%H %M'))
            data[item['secondary']] = data[item['secondary']].append(percentage_diff)

        columns = []
        for key,value in data.items():
            column_data = [key].extend(value)
            columns.append(column_data)

        return HttpResponse(json.dumps(columns))