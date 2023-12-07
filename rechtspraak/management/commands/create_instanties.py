"""
    rechtspraak/management/commands/create_instanties.py

    Copyright 2023, Martijn Staal <uitspraken [at] martijn-staal.nl>

    Available under the EUPL-1.2, or, at your option, any later version.

    SPDX-License-Identifier: EUPL-1.2
"""

import datetime

from typing import Any

import requests
import xmltodict

from django.core.management import BaseCommand

from rechtspraak.models import Instantie


class Command(BaseCommand):
    """Add all instanties"""

    help = "Add all instanties"

    def handle(self, *args: Any, **options: Any) -> None:
        instanties_url = "https://data.rechtspraak.nl/Waardelijst/Instanties"

        resp = requests.get(instanties_url, timeout=30)

        instanties_dict = xmltodict.parse(resp.text)

        for instantie in instanties_dict["Instanties"]["Instantie"]:
            print(instantie)
            try:
                begin_date = datetime.datetime.strptime(instantie["BeginDate"], "%Y-%m-%d")
            except KeyError:
                begin_date = datetime.datetime(1000, 1, 1)
            try:
                end_date = datetime.datetime.strptime(instantie["EndDate"], "%Y-%m-%d")
            except KeyError:
                end_date = None
            try:
                afkorting = instantie["Afkorting"]
            except KeyError:
                afkorting = ""
            Instantie.objects.update_or_create(
                naam=instantie["Naam"],
                instantie_type=instantie["Type"],
                identifier=instantie["Identifier"],
                afkorting=afkorting,
                begin_date=begin_date,
                end_date=end_date
            )
