"""
    rechtspraak/models.py

    Copyright 2023, Martijn Staal <uitspraken [at] martijn-staal.nl>

    Available under the EUPL-1.2, or, at your option, any later version.

    SPDX-License-Identifier: EUPL-1.2
"""

import datetime

from django.db import models


class Instantie(models.Model):
    naam = models.CharField(max_length=256, unique=True)
    instantie_type = models.CharField(max_length=256)
    identifier = models.CharField(max_length=1024)
    afkorting = models.CharField(max_length=64)
    begin_date = models.DateField()
    end_date = models.DateField(null=True)

    def __str__(self) -> str:
        return f"Instantie {self.instantie_type} {self.afkorting}"


class Uitspraak(models.Model):
    ecli = models.CharField(max_length=128, unique=True)
    zaaknummer = models.CharField(max_length=2048)

    publicatiedatum = models.DateField(default=datetime.date(1000, 1, 1))
    uitspraakdatum = models.DateField(default=datetime.date(1000, 1, 1))

    raw_xml = models.TextField()
    json = models.JSONField(default=dict)

    inhoudsindicatie = models.TextField()
    uitspraak = models.TextField()

    instantie = models.ForeignKey(Instantie, models.CASCADE)

    def __str__(self) -> str:
        return f"Uitspraak {self.ecli} ({self.instantie.afkorting})"
