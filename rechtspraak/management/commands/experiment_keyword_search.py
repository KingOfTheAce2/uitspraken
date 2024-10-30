"""
    rechtspraak/management/commands/experiment_keywordsearch.py

    A simple variable experiment for keyword searches

    Copyright 2024 Martijn Staal <uitspraken [at] martijn-staal.nl>

    Available under the EUPL-1.2, or, at your option, any later version.

    SPDX-License-Identifier: EUPL-1.2
"""

import datetime
import logging
import re

from typing import Any

from django.core.management import BaseCommand

from rechtspraak.models import Instantie, Uitspraak
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """A simple variable experiment for keyword searches"""

    help = "A simple variable experiment for keyword searches"

    def add_arguments(self, parser):
        """Add arguments"""

        instanties: list[str] = [ x for x in Instantie.objects.order_by("instantie_type").values_list("instantie_type", flat=True).distinct()]

        parser.add_argument("instantie_type", type=str, help=f"The instantie type to run the experiment on, possible options: {instanties}")
        parser.add_argument("search_pattern", type=str, help="The regex search pattern to use")
        parser.add_argument("--experiment_name", type=str, default="keywordsearch_experiment", help="The experiment name, defaults to keywordsearch_experiment")
        parser.add_argument("--year", type=int, help="Optionally, the year to limit to; otherwise it runs on all decisions.")
        parser.add_argument("--skip-same-id", action="store_true", help="Skip if experiment results with the same ID (but maybe not the same timestamp) already exists")

    def handle(self, *args: Any, **options: Any) -> None:
        """A simple variable experiment for keyword searches"""

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

        experiment_name = options["experiment_name"]
        logger.info("Experiment name is %s", experiment_name)
        if options["year"] is None:
            experiment_id = f"{experiment_name}_all_1"
        else:
            experiment_id = f"{experiment_name}_{options['year']}_1"
        experiment_timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        logger.info("Experiment id: %s", experiment_id)
        logger.info("Experiment timestamp: %s", experiment_timestamp)

        SKIP_SAME_EXP_ID = options["skip_same_id"]
        logger.info("skip same id: %s", options["skip_same_id"])

        logger.info("Provided search pattern: %s", options["search_pattern"])
        search_pattern = re.compile(options["search_pattern"])

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
                matches = search_pattern.findall(uitspraak.tekst)

                experiment_info = {
                        "experiment": experiment_name,
                        "id": experiment_id,
                        "datetime": experiment_timestamp,
                        "matches": matches,
                        "errors": []
                    }
            except Exception as e:
                logger.critical("Failed to parse citations in %s: %s", uitspraak, e)
                experiment_info = {
                    "experiment": experiment_name,
                    "id": experiment_id,
                    "datetime": experiment_timestamp,
                    "matches": [],
                    "errors": [str(e)]
                }

            logger.debug("%s: %s", uitspraak, experiment_info)

            if "experiments" not in uitspraak.data:
                uitspraak.data = {"experiments": {experiment_id: experiment_info}}
            else:
                uitspraak.data["experiments"][experiment_id] = experiment_info

            # print(uitspraak.data)
            uitspraak.save()
