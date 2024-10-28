"""
    rechtspraak/management/commands/create_uitspraak_from_xml.py

    Parse an uitspraak from an XML file.

    For information regarding the expected XML structure, please see https://www.rechtspraak.nl/Uitspraken/Paginas/Open-Data.aspx.

    Copyright 2023, 2024 Martijn Staal <uitspraken [at] martijn-staal.nl>

    Available under the EUPL-1.2, or, at your option, any later version.

    SPDX-License-Identifier: EUPL-1.2
"""

import logging

from pathlib import Path
from typing import Any

from django.core.management import BaseCommand, CommandParser

from rechtspraak.utils import create_uitspraak_from_xmlstring

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Add all instanties"""

    help = "Add all instanties"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("xml_file_or_dir", type=str, nargs="+", help="The XML file (or directory with XML files) to read the uitspraak from.")

    def handle(self, *args: Any, **options: Any) -> None:
        print(options["xml_file_or_dir"])

        for xmlpath_str in options["xml_file_or_dir"]:
            path = Path(xmlpath_str)

            if path.exists() and path.is_file():
                logger.info("%s is a file", xmlpath_str)
                with path.open("rt", encoding="utf-8") as xmlfile:
                    raw_xml = xmlfile.read()

                create_uitspraak_from_xmlstring(raw_xml, xmlpath_str)

            elif path.exists() and path.is_dir():
                logger.info("%s is a directory", xmlpath_str)
                xmlfilepaths = path.glob("./*.xml")

                for xmlfilepath in xmlfilepaths:
                    if xmlfilepath.exists() and xmlfilepath.is_file():
                        logger.info("Found %s", xmlfilepath)
                        with xmlfilepath.open("rt", encoding="utf-8") as xmlfile:
                            raw_xml = xmlfile.read()

                        create_uitspraak_from_xmlstring(raw_xml, str(xmlfilepath))
