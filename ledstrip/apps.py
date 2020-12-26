# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class LedstripConfig(AppConfig):
    name = 'ledstrip'

    def ready(self):
        # put your startup code here
        print("startup code")
