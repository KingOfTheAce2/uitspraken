"""
    rechtspraak/management/commands/create_procedures.py

    Copyright 2023, Martijn Staal <uitspraken [at] martijn-staal.nl>

    Available under the EUPL-1.2, or, at your option, any later version.

    SPDX-License-Identifier: EUPL-1.2
"""

import logging
import xml.etree.ElementTree as ET

from typing import Any

import requests

from django.core.management import BaseCommand

from rechtspraak.models import ProcedureSoort

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Add all procedures"""

    help = "Add all procedures"

    def handle(self, *args: Any, **options: Any) -> None:
        procedures_url = "https://data.rechtspraak.nl/Waardelijst/Proceduresoorten"

        resp = requests.get(procedures_url, timeout=30)

        xmlroot = ET.fromstring(resp.text)

        for proceduresoort in xmlroot.findall(".//Proceduresoort"):
            proceduresoort, created = ProcedureSoort.objects.update_or_create(
                naam=proceduresoort.find("./Naam").text,
                identifier=proceduresoort.find("./Identifier").text
            )

            if created:
                logger.info("Succesfully created %s", proceduresoort)
            else:
                logger.info("Succesfully updated %s", proceduresoort)
