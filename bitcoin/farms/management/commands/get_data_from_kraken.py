import datetime
import json
import requests
from pymongo import MongoClient

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    def handle(self, *args, **options):
        data_dict = {
            'XXRPZEUR': 'XRP',
            'BCHEUR': 'BCH',
            'XETHZEUR': 'ETH',
            'DASHEUR': 'DAS',
            'XREPZEUR': 'REP',
            'XXBTZEUR': 'BTC',
            'XLTCZEUR': 'LTC',
        }
        current_time = datetime.datetime.utcnow()
        client = MongoClient('mongodb', 27017)
        db = client.bitcoin
        collection = db.eu_exchange

        response = requests.get('https://api.kraken.com/0/public/Ticker?pair=XRPEUR,BCHEUR,ETHEUR,DASHEUR,REPEUR,XBTEUR,LTCEUR')
        data = json.loads(response.content)

        for key, value in data['result'].items():
            if key in data_dict.keys():
                rate = {
                    'primary': 'EUR',
                    'secondary': data_dict[key],
                    'rate': value['c'][0],
                    'date': current_time
                }
                collection.insert(rate)

        data_dict = {
            'XXRPZUSD': 'XRP',
            'BCHUSD': 'BCH',
            'XETHZUSD': 'ETH',
            'DASHUSD': 'DAS',
            'XXBTZUSD': 'BTC',
            'XLTCZUSD': 'LTC',
        }

        response = requests.get('https://api.kraken.com/0/public/Ticker?pair=XRPUSD,BCHUSD,ETHUSD,DASHUSD,XBTUSD,LTCUSD')
        data = json.loads(response.content)

        for key, value in data['result'].items():
            if key in data_dict.keys():
                rate = {
                    'primary': 'USD',
                    'secondary': data_dict[key],
                    'rate': value['c'][0],
                    'date': current_time
                }
                collection.insert(rate)