import datetime
import json
import requests
from pymongo import MongoClient

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    def handle(self, *args, **options):
        data_dict = {
            'XRPEUR': 'XRP',
            'BCHEUR': 'BCH',
            'ETHEUR': 'ETH',
            'DASHEUR': 'DAS',
            'REPEUR': 'REP',
            'XBTEUR': 'BTC',
            'LTCEUR': 'LTC',
        }
        client = MongoClient('mongodb', 27017)
        db = client.bitcoin
        collection = db.eu_exchange

        response = requests.get('https://api.kraken.com/0/public/Ticker?pair=XRPEUR,BCHEUR,ETHEUR,DASHEUR,REPEUR,XBTEUR,LTCEUR')
        data = json.loads(response.content)

        for key, value in data['result'].items():
            rate = {
                'primary': 'EUR',
                'secondary': data_dict[key],
                'rate': value['c'][0],
                'date': datetime.datetime.utcnow()
            }
            collection.insert(rate)