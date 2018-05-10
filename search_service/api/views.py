# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.http import HttpResponse
from elasticsearch.helpers import scan
from elasticsearch import Elasticsearch
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from settings.models import Field, KeywordSetting, KeywordGroup, SearchSetting, SuggestSetting


class SearchAPIView(APIView):
    def get(self, request, keyword, format=None):
        keyword = keyword.upper()
        search_settings = SearchSetting.objects.filter(field_type='search')
        search_field = []
        for field in search_settings:
            text = '%s^%s' % (field.field.key, field.weight)
            search_field.append(text)

        filter_settings = SearchSetting.objects.filter(field_type='filter')
        filter_field = {}
        for field in filter_settings:
            filter_field[field.field.name] = {
                "terms": {
                    "field": field.field.key
                }
            }

        bool_query = {
          "should": {
            "multi_match": {
              "query": keyword,
              "type": "cross_fields",
              "analyzer": "search_analyzer",
              "fields": search_field
            }
          }
        }

        if ':' in keyword:
            bool_query["filter"] = {
              "term": {
                "cat_1": keyword.split(':')[-1]
              }
            }

        es = Elasticsearch(['http://elastic:9200'])
        query = {
          "size": 10,
          "aggs": filter_field,
          "query": {
            "function_score": {
              "query": {
                "bool": bool_query
              },
              "script_score": {
                "script": {
                  "source": "_score + Math.log(2 + doc['weight'].value)"
                }
              },
              "score_mode": "avg"
            }
          }
        }
        res = es.search(index='products', body=query)
        result = {}
        data = []
        if not ':' in keyword :
            max_score = res['hits']['max_score']
            threshold = 0
            if max_score > 5:
                threshold = 0.9 * max_score
                query['min_score'] = threshold
                res = es.search(index='products', body=query)
        for item in res['hits']['hits']:
            if item['_score'] >= threshold:
                data.append(item['_source'])
        result['data'] = data
        result['aggr'] = res['aggregations']
        return Response(result)


class RecommendAPIView(APIView):
    def get(self, request, keyword, recommend_by, format=None):
        query = {
            "size": 4,
            "query": {
                "function_score": {
                    "query": {
                        "bool": {
                            "should": {
                                "multi_match": {
                                    "query": keyword,
                                    "type": "cross_fields",
                                    "analyzer": "search_analyzer",
                                    "fields": recommend_by
                                }
                            }
                        }
                    },
                    "score_mode": "avg"
                }
            }
        }

        es = Elasticsearch(['http://elastic:9200'])
        res = es.search(index='products', body=query)
        result = []
        for item in res['hits']['hits']:
            result.append(item['_source'])
        return Response(result)


class SuggestAPIView(APIView):
    def get(self, request, keyword, format=None):
        es = Elasticsearch(['http://elastic:9200'])
        result = []
        suggest_settings = SuggestSetting.objects.filter(is_active=True).order_by('order')
        for setting in suggest_settings:
            version = setting.suggest_type
            if version == 'v1':
                query = {
                    "suggest": {
                        "prefix-suggest": {
                            "prefix": keyword,
                            "completion": {
                                "field": "keyword_prefix",
                                "size": setting.rows,
                                "fuzzy" : {
                                    "fuzziness" : 2
                                },
                                "skip_duplicates": True
                            }
                        }
                    }
                }
                res = es.search(index='products', body=query)
                print(res['suggest']['prefix-suggest'][0]['options'])
                result.extend(res['suggest']['prefix-suggest'][0]['options'])
            elif version == 'v2':
                query = {
                  "query": {
                    "function_score": {
                      "query": {
                        "bool": {
                          "should": {
                            "multi_match": {
                              "query": keyword,
                              "type": "cross_fields",
                              "analyzer": "search_analyzer",
                              "fields": [
                                "*"
                              ]
                            }
                          }
                        }
                      },
                      "score_mode": "avg"
                    }
                  },
                  "suggest": {
                    "prefix-suggest": {
                      "prefix": keyword,
                      "completion": {
                        "field": "keyword_prefix",
                        "size": 1,
                        "skip_duplicates": True
                      }
                    }
                  },
                  "aggs": {
                    "Base Category": {
                      "terms": {
                        "field": "cat_1"
                      }
                    }
                  }
                }
                res = es.search(index='products', body=query)
                keyword = res['suggest']['prefix-suggest'][0]['options'][0]['text']
                suggests = []
                for i in range(0, setting.rows):
                    try:
                        text = keyword + ': ' + res['aggregations']['Base Category']['buckets'][i]['key']
                        suggests.append({
                            'text': text
                        })
                    except:
                        pass
                result.extend(suggests)

            elif version == 'v3':
                query = {
                    "suggest": {
                        "prefix-suggest": {
                            "prefix": keyword,
                            "completion": {
                                "field": "keyword_prefix",
                                "size": setting.rows
                            }
                        }
                    }
                }
                res = es.search(index='products', body=query)
                suggests = []
                for doc in res['suggest']['prefix-suggest'][0]['options']:
                    suggests.append({
                        'text': doc['_source']['title']
                    })
                result.extend(suggests)

        return Response(result)

class GenerateKeywordAPIView(APIView):
    def get(self, request, format=None):
        es = Elasticsearch(['http://elastic:9200'])
        res = scan(
            es,
            index='products',
            doc_type='type',
            query={"query": { "match_all" : {}}}
        )
        keyword_groups = KeywordGroup.objects.all()
        keyword_mapping = []
        for group in keyword_groups:
            keyword_settings = group.keyword_settings.all().order_by('order').values_list('field__key', flat=True)
            keyword_mapping.append(keyword_settings)
            
        for item in res:
            try:
                doc = item['_source']
                keyword = []
                for mapping in keyword_mapping:
                    keyword_data = []
                    for key in mapping:
                        keyword_data.append(doc[key])
                    text = ' '.join(keyword_data)
                    keyword.append(text)
                doc['keyword_prefix'] = {
                    'input': keyword
                }
                doc['keyword_phase'] = keyword
                if item['_id'] == '547':
                    doc['weight'] =  2
                else:
                    doc['weight'] = 1
                res = es.index(index='products', doc_type='type', id=item['_id'], body=doc)
            except:
                pass

        return Response("success")

class ReIndexAPIView(APIView):
    def post(self, request, id, format=None):
        data = request.data
        for key in data.keys():
            Field.objects.get_or_create(key=key)
        es = Elasticsearch(['http://elastic:9200'])
        res = es.index(index='products', doc_type='type', id=id, body=data)

        return Response(res)
