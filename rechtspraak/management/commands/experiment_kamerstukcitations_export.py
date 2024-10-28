"""
    rechtspraak/management/commands/experiment_kamerstukcitations_export.py

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
        experiment_name = "citations"
        experiment_id = f"{experiment_name}_all_1"
        uitspraken = Uitspraak.objects.filter(data__experiments__citations_all_1__id="citations_all_1")

        total = uitspraken.count()
        with_citations = 0
        with_kst_citations = 0

        results = []

        kst_citations_per_uitspraak_with_at_least_1 = {}
        kst_citations_total = 0
        kst_citations_probably_mvt = 0

        for uitspraak in uitspraken.iterator():

            try:
                citations_all = uitspraak.data["experiments"][experiment_id]["citations"]
                citations_kst = [cit for cit in citations_all if "kamer" in cit]

                if len(citations_all) > 0:
                    with_citations += 1

                if len(citations_kst) > 0:
                    with_kst_citations += 1
                    kst_citations_per_uitspraak_with_at_least_1[uitspraak.ecli] = citations_kst

                    for citkst in citations_kst:
                        kst_citations_total += 1
                        if citkst["ondernummer"] == "3":
                            kst_citations_probably_mvt += 1

                # print(f"{uitspraak} {uitspraak.data['experiments']}: has {len(citations_kst)} kstcitations")
            except Exception as exc:
                logger.info("%s has no citations: %s", uitspraak, exc)
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
                "data": uitspraak.data
            })

        print(f"{with_kst_citations / total} {with_kst_citations} {total}")

        print(kst_citations_total)
        print(kst_citations_probably_mvt)

        resultsfilename: str = f"results_{datetime.datetime.now().strftime('%Y-%m-%dT%H:%M')}.json"
        with open(resultsfilename, "wt", encoding="utf-8") as resultsfile:
            json.dump(results, resultsfile)
