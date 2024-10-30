"""
    rechtspraak/management/commands/download_uitspraken_for_instantie_since.py

    Download all uitspraken for a given instantie type that were updated since a given date.

    Copyright 2024 Martijn Staal <uitspraken [at] martijn-staal.nl>

    Available under the EUPL-1.2, or, at your option, any later version.

    SPDX-License-Identifier: EUPL-1.2
"""

import datetime
import logging
import time

from typing import Any

from django.core.management import BaseCommand

from rechtspraak.models import Instantie, Uitspraak
from rechtspraak.utils import get_updated_eclis_for_instantie_since, create_uitspraak_from_ecli
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Download all uitspraken for a given instantie type that were updated since a given date."""

    help = "Download all uitspraken for a given instantie type that were updated since a given date."

    def add_arguments(self, parser):
        """Add arguments"""

        instanties_types: list[str] = [ x for x in Instantie.objects.order_by("instantie_type").values_list("instantie_type", flat=True).distinct()]

        parser.add_argument("instantie_type", type=str, choices=instanties_types, help="The instantie type to run the experiment on")
        parser.add_argument("since_year", type=int, default=datetime.datetime.now().year, help="Since date, year; defaults to the current year.")
        parser.add_argument("since_month", type=int, default=1, choices=[i for i in range(1, 13)], help="Since date, month; defaults to January")
        parser.add_argument("since_day", type=int, default=1, choices=[i for i in range(1, 32)], help="Since date, day; defaults to 1")

    def handle(self, *args: Any, **options: Any) -> None:
        """Download all uitspraken for a given instantie type that were updated since a given date."""

        instantie_type = options["instantie_type"]
        logger.info("Performing experiment one on instanties of type %s", instantie_type)

        instanties = Instantie.objects.filter(instantie_type=instantie_type)
        logger.info("Instanties found: %s", instanties)

        since_date = datetime.date(options["since_year"], options["since_month"], options["since_day"])
        logger.info("Since date: %s", since_date)
        all_eclis = []

        for instantie in instanties:
            eclis = get_updated_eclis_for_instantie_since(instantie, since_date)

            logger.info("Found ecli's for %s: %s", instantie, eclis)

            all_eclis += eclis

        logger.info("Found %s updated ecli's", len(all_eclis))

        cur = 1
        for ecli in all_eclis:
            print(f"{cur}/{len(all_eclis)} ({cur/len(all_eclis) * 100}%)")
            cur += 1

            try:
                uitspraak = Uitspraak.objects.get(ecli=ecli)
                logger.info("%s already exists, skipping", uitspraak)
                # TODO add update mechanism
            except Uitspraak.DoesNotExist:
                try:
                    create_uitspraak_from_ecli(ecli)
                except:
                    logger.error("Failed to crawl %s", ecli)

                time.sleep(1)
            print(ecli)