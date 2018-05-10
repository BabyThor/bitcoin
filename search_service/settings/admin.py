# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Field, SearchSetting, KeywordSetting, KeywordGroup, RecommendSetting, SuggestSetting

class KeywordGroupInline(admin.TabularInline):
    model = KeywordGroup.keyword_settings.through

class KeywordGroupAdmin(admin.ModelAdmin):
    inlines = [
        KeywordGroupInline,
    ]
    exclude = ('keyword_settings',)

admin.site.register(KeywordGroup, KeywordGroupAdmin)
admin.site.register(Field)
admin.site.register(SearchSetting)
admin.site.register(KeywordSetting)
admin.site.register(RecommendSetting)
admin.site.register(SuggestSetting)
