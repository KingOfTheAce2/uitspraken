"""
    rechtspraak/management/commands/experiment_kamerstukcitations.py

    Copyright 2023, 2024 Martijn Staal <uitspraken [at] martijn-staal.nl>

    Available under the EUPL-1.2, or, at your option, any later version.

    SPDX-License-Identifier: EUPL-1.2
"""

import datetime
import logging

from typing import Any

import nllegalcit

from django.core.management import BaseCommand

from rechtspraak.models import Instantie, Uitspraak
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Perform experiment 1"""

    help = "Perform experiment 1"

    def add_arguments(self, parser):
        """Add arguments"""

        instanties: list[str] = [ x for x in Instantie.objects.order_by("instantie_type").values_list("instantie_type", flat=True).distinct()]

        parser.add_argument("instantie_type", type=str, help=f"The instantie type to run the experiment on, possible options: {instanties}")
        parser.add_argument("--year", type=int, help="Optionally, the year to limit to; otherwise it runs on all available since 1995-1-1")

    def handle(self, *args: Any, **options: Any) -> None:
        """Perform experiment 1"""

        instantie_type = options["instantie_type"]
        logger.info("Performing experiment one on instanties of type %s", instantie_type)

        if options["year"] is None:
            logger.info("Checking all results since 1995-1-1")
            uitspraken = Uitspraak.objects.filter(
                instantie__instantie_type=instantie_type,
                uitspraakdatum__gte=datetime.date(1995, 1, 1)
            ).exclude(tekst="").order_by("uitspraakdatum")
        else:
            year = options["year"]
            logger.info("Limiting to year %s", year)
            daterange_start = datetime.date(year, 1, 1)
            daterange_end = datetime.date(year, 12, 31)
            uitspraken = Uitspraak.objects.filter(
                instantie__instantie_type=instantie_type,
                uitspraakdatum__range=[daterange_start, daterange_end]
            ).exclude(tekst="").order_by("uitspraakdatum")

        total = uitspraken.count()

        logger.info("Found %s total uitspraken in set", total)

        experiment_name = "citations"
        if options["year"] is None:
            experiment_id = f"{experiment_name}_all_1"
        else:
            experiment_id = f"{experiment_name}_{options['year']}_1"
        experiment_timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        SKIP_SAME_EXP_ID = True

        cur = 1
        for uitspraak in uitspraken.iterator():
            print(f"{cur}/{total} ({cur/total * 100}%)")
            cur += 1

            if SKIP_SAME_EXP_ID:
                try:
                    uitspraak.data["experiments"][experiment_id]["id"] = experiment_id
                    logger.info("Have already seen %s, skipping...", uitspraak)
                    continue
                except:
                    pass
            try:
                citations = nllegalcit.parse_citations(uitspraak.tekst)

                experiment_info = {
                        "experiment": experiment_name,
                        "id": experiment_id,
                        "datetime": experiment_timestamp,
                        "citations": [cit.__dict__ for cit in citations],
                        "errors": []
                    }
            except Exception as e:
                logger.critical("Failed to parse citations in %s: %s", uitspraak, e)
                experiment_info = {
                    "experiment": experiment_name,
                    "id": experiment_id,
                    "datetime": experiment_timestamp,
                    "citations": [],
                    "errors": [str(e)]
                }
            # print(citations)

            # print(experiment_info)

            if "experiments" not in uitspraak.data:
                uitspraak.data = {"experiments": {experiment_id: experiment_info}}
            else:
                uitspraak.data["experiments"][experiment_id] = experiment_info

            # print(uitspraak.data)
            uitspraak.save()
