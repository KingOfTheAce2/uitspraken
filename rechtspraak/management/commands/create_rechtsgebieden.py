"""
    rechtspraak/management/commands/create_rechtsgebieden.py

    Copyright 2023, Martijn Staal <uitspraken [at] martijn-staal.nl>

    Available under the EUPL-1.2, or, at your option, any later version.

    SPDX-License-Identifier: EUPL-1.2
"""

import logging
import xml.etree.ElementTree as ET

from typing import Any

import requests

from django.core.management import BaseCommand

from rechtspraak.models import Rechtsgebied

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Add all rechtsgebieden"""

    help = "Add all rechtsgebieden"

    def handle(self, *args: Any, **options: Any) -> None:
        rechtsgebieden_url = "https://data.rechtspraak.nl/Waardelijst/Rechtsgebieden"

        resp = requests.get(rechtsgebieden_url, timeout=30)

        xmlroot = ET.fromstring(resp.text)

        for rechtsgebied in xmlroot.findall(".//Rechtsgebied"):
            rechtsgebied, created = Rechtsgebied.objects.update_or_create(
                naam=rechtsgebied.find("./Naam").text,
                identifier=rechtsgebied.find("./Identifier").text
            )

            if created:
                logger.info("Succesfully created %s", rechtsgebied)
            else:
                logger.info("Succesfully updated %s", rechtsgebied)
