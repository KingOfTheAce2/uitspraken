"""
    rechtspraak/admin.py

    Copyright 2023, Martijn Staal <uitspraken [at] martijn-staal.nl>

    Available under the EUPL-1.2, or, at your option, any later version.

    SPDX-License-Identifier: EUPL-1.2
"""

from django.contrib import admin

from rechtspraak.models import Uitspraak, Instantie, Rechtsgebied, ProcedureSoort

# Register your models here.
admin.site.register(Uitspraak)
admin.site.register(Instantie)
