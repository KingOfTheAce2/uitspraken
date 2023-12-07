"""
    rechtspraak/admin.py

    Copyright 2023, Martijn Staal <uitspraken [at] martijn-staal.nl>

    Available under the EUPL-1.2, or, at your option, any later version.

    SPDX-License-Identifier: EUPL-1.2
"""

from django.apps import AppConfig


class RechtspraakConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rechtspraak'
