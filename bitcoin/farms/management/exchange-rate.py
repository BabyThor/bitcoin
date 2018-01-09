import datetime
import json
import requests
from pymongo import MongoClient

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    def handle(self, *args, **options):
        client = MongoClient('mongodb', 27017)
        db = client.bitcoin
        collection = db.exchange_rate

        response = requests.get('http://www.apilayer.net/api/live?access_key=912e3bee55aa971e76b014964e07fa1b&format=1')
        data = json.loads(response.content)

        rate = {
            'thb': data['quotes']['USDTHB'],
            'eur': data['quotes']['USDEUR'],
            'date': datetime.datetime.utcnow()
        }
        collection.insert(rate)
