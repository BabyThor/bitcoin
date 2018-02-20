import datetime
from datetime import timedelta
import json
import requests
from pymongo import MongoClient
from django.core.mail import send_mail

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    def handle(self, *args, **options):
        client = MongoClient('mongodb', 27017)
        db = client.bitcoin
        th_exchange = db.th_exchange
        exchange_rate = db.exchange_rate
        eu_exchange = db.eu_exchange

        keys = ['diff_eu_th', 'diff_us_th', 'diff_currency']
        diff_data = {}
        for key in keys:
            obj, created = Setting.objects.get_or_create(key=key)
            diff_data[key] = obj.value

        current_time = datetime.datetime.utcnow()

        end_time_range = datetime.datetime.utcnow()
        start_time_range = end_time_range - timedelta(minutes=1)
        th_data = th_exchange.find({'date': {'$lte': end_time_range, '$gte': start_time_range}})

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
        min_percentage = 100
        min_currency = None
        max_percentage = 0
        max_currency = None
        for item in th_data:
            if item['secondary'] not in data.keys():
                continue
            item_date = item['date']
            start_date = datetime.datetime(item_date.year, item_date.month, item_date.day, item_date.hour, item_date.minute, 0)
            end_date = start_date + timedelta(minutes=1)
            start_date = start_date - timedelta(minutes=1)

            exchange_rate_start_date = datetime.datetime(item_date.year, item_date.month, item_date.day, item_date.hour, 0, 0)
            exchange_rate_end_date = datetime.datetime(item_date.year, item_date.month, item_date.day, item_date.hour, 59, 59)

            thb_rate = item['rate']
            eu_rate = eu_exchange.find_one({'$and': [{'date': {'$lte': end_date, '$gte': start_date}}, {'secondary': item['secondary']}, {'primary': 'EUR'}]})
            us_rate = eu_exchange.find_one({'$and': [{'date': {'$lte': end_date, '$gte': start_date}}, {'secondary': item['secondary']}, {'primary': 'USD'}]})
            if not eu_rate:
                continue
            if not us_rate:
                continue
            exchange_rate_item = exchange_rate.find_one({'date': {'$gte': exchange_rate_start_date, '$lte': exchange_rate_end_date}})

            price_th_us = float(thb_rate) / float(exchange_rate_item['thb'])
            price_eu_us = float(eu_rate['rate']) / float(exchange_rate_item['eur'])
            price_us = float(us_rate['rate'])
            eu_th_diff = ((price_th_us - price_eu_us)/price_eu_us) * 100
            us_th_diff = ((price_th_us - price_us)/price_us) * 100

            if eu_th_diff >= max_percentage:
                max_percentage = eu_th_diff
                max_currency = item['secondary']
            elif eu_th_diff <= min_percentage:
                min_percentage = eu_th_diff
                min_currency = item['secondary']

            currency_threshold = diff_data['diff_eu_th']
            if eu_th_diff >= currency_threshold:
                subject = 'Bitcoin Notification for %s currency diff more than %s' % (item['secondary'], currency_threshold)
                content = '%s difference from THB and EUR is %s' % (item['secondary'], eu_th_diff)
                send_mail(
                    subject,
                    content,
                    'w.wangtrakoon@gmail.com',
                    ['martins.benkitis@gmail.com'],
                )

            currency_threshold = diff_data['diff_us_th']
            if us_th_diff >= currency_threshold:
                subject = 'Bitcoin Notification for %s currency diff more than %s' % (item['secondary'], currency_threshold)
                content = '%s difference from THB and USD is %s' % (item['secondary'], eu_th_diff)
                send_mail(
                    subject,
                    content,
                    'w.wangtrakoon@gmail.com',
                    ['martins.benkitis@gmail.com'],
                )

        crypto_threshold = diff_data['diff_currency']
        crypto_diff = max_percentage - min_percentage
        if crypto_diff >= crypto_threshold:
            subject = 'Bitcoin Notification for %s:%s crypto diff more than %s' % (max_currency, min_currency, crypto_threshold)
            content = 'The difference between differences of %s (%s%%) and %s (%s%%) is %s%%' % (
                max_currency, max_percentage, min_currency, min_percentage, crypto_diff
            )
            send_mail(
                subject,
                content,
                'w.wangtrakoon@gmail.com',
                ['martins.benkitis@gmail.com'],
            )
