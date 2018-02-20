import datetime
import json
import requests
from pymongo import MongoClient

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    def handle(self, *args, **options):
        client = MongoClient('mongodb', 27017)
        db = client.thor
        collection = db.th_exchange

        response = requests.get('https://bx.in.th/api/')
        data = json.loads(response.content)

        for key, value in data.items():
            rate = {
                'primary': value['primary_currency'],
                'secondary': value['secondary_currency'],
                'rate': value['last_price'],
                'bids': value['orderbook']['bids']['highbid'],
                'asks': value['orderbook']['asks']['highbid']
                'date': datetime.datetime.utcnow()
            }
            collection.insert(rate)