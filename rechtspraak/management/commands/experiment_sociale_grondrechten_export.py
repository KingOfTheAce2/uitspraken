"""
    rechtspraak/management/commands/experiment_sociale_grondrechten_export.py

    Copyright 2024, Martijn Staal <uitspraken [at] martijn-staal.nl>

    Available under the EUPL-1.2, or, at your option, any later version.

    SPDX-License-Identifier: EUPL-1.2
"""

import datetime
import json
import logging

from typing import Any

from django.core.management import BaseCommand
from django.core import serializers

from rechtspraak.models import Uitspraak
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Add all instanties"""

    help = "Add all instanties"

    def handle(self, *args: Any, **options: Any) -> None:
        experiment_name = "socialegrondrechten"
        experiment_id = f"{experiment_name}_all"
        uitspraken = Uitspraak.objects.filter(data__experiments__socialegrondrechten_all__id="socialegrondrechten_all", uitspraakdatum__gte=datetime.date(2004,1,1), uitspraakdatum__lte=datetime.date(2021,12,31))

        total = uitspraken.count()
        with_matches = 0
        with_second_matches = 0

        results = []

        for uitspraak in uitspraken.iterator():

            try:
                matches = uitspraak.data["experiments"][experiment_id]["matches"]
                additional_matches = uitspraak.data["experiments"][experiment_id]["additional_matches"]

                if len(matches) > 0:
                    with_matches += 1

                if (len(additional_matches)) > 0:
                    with_second_matches += 1
            except Exception as exc:
                logger.info("%s has no experiment results: %s", uitspraak, exc)
                pass

            results.append({
                "ecli": uitspraak.ecli,
                "publicatiedatum": uitspraak.publicatiedatum.strftime("%Y-%m-%d"),
                "uitspraakdatum": uitspraak.uitspraakdatum.strftime("%Y-%m-%d"),
                "instantie": uitspraak.instantie.naam,
                "instantie_type": uitspraak.instantie.instantie_type,
                "uitspraak_type": uitspraak.uitspraak_type,
                "rechtsgebieden": [rechtsgebied.naam for rechtsgebied in uitspraak.rechtsgebieden.all()],
                "procedure_soorten": [proceduresoort.naam for proceduresoort in uitspraak.procedure_soorten.all()],
                "inhoudsindicatie": uitspraak.inhoudsindicatie,
                f"data-{experiment_id}": uitspraak.data["experiments"][experiment_id]
            })

        print(f"{with_matches / total} {with_matches} {total}")
        print(f"{with_second_matches / total} {with_second_matches} {total}")

        resultsfilename: str = f"results_socialegrondrechten_{datetime.datetime.now().strftime('%Y-%m-%dT%H:%M')}.json"
        with open(resultsfilename, "wt", encoding="utf-8") as resultsfile:
            json.dump(results, resultsfile)
