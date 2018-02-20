import datetime
from datetime import timedelta
import json
from pymongo import MongoClient

from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView, View

from .forms import SettingsForm
from .models import Setting


class SettingsView(TemplateView):
    template = 'settings.html'

    def get(self, request):
        keys = ['diff_eu_th', 'diff_us_th', 'diff_currency']
        data = {}
        for key in keys:
            obj, created = Setting.objects.get_or_create(key=key)
            data[key] = obj.value
        form = SettingsForm(initial=data)

        return render(
            request,
            self.template,
            {
                'form': form
            }
        )

    def post(self, request):
        keys = ['diff_eu_th', 'diff_us_th', 'diff_currency']
        for key in keys:
            setting = Setting.objects.get(key=key)
            setting.value = request.POST.get(key, '')
            setting.save()

        data = {}
        for key in keys:
            data[key] = Setting.objects.get(key=key).value
        form = SettingsForm(initial=data)

        return render(
            request,
            self.template,
            {
                'form': form
            }
        )


class HistoricalRateView(TemplateView):
    template = 'history.html'

    def get(self, request, currency):
        return render(
            request,
            self.template,
            {
                'currency': currency
            }
        )


class CurrencyAPIView(View):
    def get_time_data(self, current_time, timeframe):
        if timeframe == 'hour':
            start_time_range = current_time - timedelta(hours=1)
            time_range = 1
        elif timeframe == 'day':
            start_time_range = current_time - timedelta(days=1)
            time_range = 15
        elif timeframe == 'week':
            start_time_range = current_time - timedelta(days=7)
            time_range = 60
        elif timeframe == 'month':
            start_time_range = current_time - timedelta(months=1)
            time_range = 480
        return start_time_range, time_range

    def get_json_data(self, primary, list_key, time_range, start_time_range, end_time_range):
        client = MongoClient('mongodb', 27017)
        db = client.bitcoin
        th_exchange = db.th_exchange
        exchange_rate = db.exchange_rate
        eu_exchange = db.eu_exchange

        x_date = start_time_range

        date_column = ['x']
        columns = []
        while x_date <= end_time_range:
            date_column.append(x_date.strftime('%y-%m-%d:%H %M'))
            x_date = x_date + timedelta(minutes=time_range)
        for key in list_key:
            count = 0
            exchange_data = [key]
            th_data = th_exchange.find({'$and': [{'date': {'$lte': end_time_range, '$gte': start_time_range}}, {'secondary': key}]}).sort('date')
            eu_data = eu_exchange.find({'$and': [{'date': {'$lte': end_time_range, '$gte': start_time_range}}, {'secondary': key},{'primary': primary}]}).sort('date')
            current_hour = -1
            for th_rate, eu_rate in zip(th_data, eu_data):
                if count % time_range == 0:
                    if current_hour != th_rate['date'].hour:
                        exchange_rate_start_date = datetime.datetime(th_rate['date'].year, th_rate['date'].month, th_rate['date'].day, th_rate['date'].hour, 0, 0)
                        exchange_rate_end_date = datetime.datetime(th_rate['date'].year, th_rate['date'].month, th_rate['date'].day, th_rate['date'].hour, 59, 59)
                        exchange_rate_item = exchange_rate.find_one({'date': {'$gte': exchange_rate_start_date, '$lte': exchange_rate_end_date}})
                        current_hour = th_rate['date'].hour

                    if primary == 'EUR':
                        price_eu_us = float(eu_rate['rate']) / float(exchange_rate_item['eur'])
                    elif primary == 'USD':
                        price_eu_us = float(eu_rate['rate'])
                    
                    price_th_us = float(th_rate['rate']) / float(exchange_rate_item['thb'])
                    percentage_diff = ((price_th_us - price_eu_us)/price_eu_us) * 100
                    if percentage_diff == -100:
                        exchange_data.append(exchange_data[-1])
                    else:
                        exchange_data.append(percentage_diff)
                    columns.append(exchange_data)
                count = count + 1
        columns.append(date_column)
        return columns

    def get(self, request, timeframe, currency):
        client = MongoClient('mongodb', 27017)
        db = client.bitcoin
        th_exchange = db.th_exchange
        exchange_rate = db.exchange_rate
        eu_exchange = db.eu_exchange

        current_time = datetime.datetime.utcnow()
        end_time_range = current_time - timedelta(minutes=1)
        start_time_range, time_range = self.get_time_data(current_time, timeframe)

        if currency == 'EUR':
            list_key = ['XRP','BCH','ETH','DAS','REP','BTC','LTC']
        elif currency == 'USD':
            list_key = ['XRP','BCH','ETH','DAS','BTC','LTC']
        
        columns = self.get_json_data(currency, list_key, time_range, start_time_range, end_time_range)

        return HttpResponse(json.dumps(columns))