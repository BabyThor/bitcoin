# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Field(models.Model):
    name = models.CharField(max_length=200)
    key = models.CharField(max_length=200)
    def __str__(self):
       return self.name

class SearchSetting(models.Model):
    FIELD_TYPE_CHOICES = (
        ('search', 'Search'),
        ('filter', 'Filter'),
    )
    
    field = models.ForeignKey(
        Field, on_delete=models.CASCADE
    )
    field_type = models.CharField(
        max_length=10,
        choices=FIELD_TYPE_CHOICES,
        default='search',
    )
    weight = models.IntegerField(
        default=0
    )

    def __str__(self):
       return '%s: %s' % (self.field.name, self.field_type)

class SuggestSetting(models.Model):
    name = models.CharField(max_length=200)
    suggest_type = models.CharField(max_length=200)
    order = models.IntegerField(default=0)
    rows = models.IntegerField(default=0)
    is_active = models.BooleanField(default=False)

    def __str__(self):
       return self.name

class RecommendSetting(models.Model):
    field = models.ForeignKey(
        Field, on_delete=models.CASCADE
    )
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=False)

    def __str__(self):
       return self.field.name


class KeywordSetting(models.Model):
    field = models.ForeignKey(
        Field, on_delete=models.CASCADE
    )
    weight = models.IntegerField(
        default=0
    )
    order = models.FloatField(
        default=0
    )

    def __str__(self):
       return '%s [%s]' % (self.field.name, self.order)

class KeywordGroup(models.Model):
    name = models.CharField(max_length=50)
    keyword_settings = models.ManyToManyField(KeywordSetting, related_name='groups')

    def __str__(self):
       return self.name
