import datetime
import json
import requests
from pymongo import MongoClient

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    def handle(self, *args, **options):
        client = MongoClient('mongodb', 27017)
        db = client.bitcoin
        collection = db.th_exchange

        response = requests.get('https://bx.in.th/api/')
        data = json.loads(response.content)

        for key, value in data.items():
            if value['primary_currency'] == 'THB':
                rate = {
                    'primary': value['primary_currency'],
                    'secondary': value['secondary_currency'],
                    'rate': value['last_price'],
                    'date': datetime.datetime.utcnow()
                }
                collection.insert(rate)