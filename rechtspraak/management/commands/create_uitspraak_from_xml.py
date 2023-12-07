"""
    rechtspraak/management/commands/create_uitspraak_from_xml.py

    Parse an uitspraak from an XML file.

    Copyright 2023, Martijn Staal <uitspraken [at] martijn-staal.nl>

    Available under the EUPL-1.2, or, at your option, any later version.

    SPDX-License-Identifier: EUPL-1.2
"""

import datetime
import logging
import xml.etree.ElementTree as ET

from typing import Any

from django.core.management import BaseCommand, CommandParser

from rechtspraak.models import Instantie, Uitspraak

logger = logging.getLogger(__name__)
XML_NAMESPACES = {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "dcterms": "http://purl.org/dc/terms/",
    "psi": "http://psi.rechtspraak.nl/",
    "rs": "http://www.rechtspraak.nl/schema/rechtspraak-1.0"
}


class Command(BaseCommand):
    """Add all instanties"""

    help = "Add all instanties"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("xmlfile", type=str, nargs="+", help="The XML file to read the uitspraak from.")

    def handle(self, *args: Any, **options: Any) -> None:
        print(options["xmlfile"])

        for xmlfilename in options["xmlfile"]:
            with open(xmlfilename, "rt", encoding="utf-8") as xmlfile:
                raw_xml = xmlfile.read()

            tree = ET.parse(xmlfilename)
            xmlroot = tree.getroot()

            ecli = xmlroot.find("rdf:RDF/rdf:Description/dcterms:identifier", XML_NAMESPACES).text
            instantie_naam = xmlroot.find("rdf:RDF/rdf:Description/dcterms:creator", XML_NAMESPACES).text
            uitspraaktype = xmlroot.find("rdf:RDF/rdf:Description/dcterms:creator", XML_NAMESPACES).text

            try:
                instantie = Instantie.objects.get(naam=instantie_naam)
            except Instantie.DoesNotExist:
                logger.error("Could not find instantie for naam %s", instantie_naam)
                instantie = Instantie.objects.get(afkorting="XX")

            try:
                uitspraakdatum = datetime.datetime.strptime(
                    xmlroot.find("rdf:RDF/rdf:Description/dcterms:date", XML_NAMESPACES).text,
                    "%Y-%m-%d"
                )
            except KeyError:
                uitspraakdatum = None

            try:
                publicatiedatum = datetime.datetime.strptime(
                    xmlroot.find("rdf:RDF/rdf:Description/dcterms:issued", XML_NAMESPACES).text,
                    "%Y-%m-%d"
                )
            except KeyError:
                publicatiedatum = None

            zaaknummer = xmlroot.find("rdf:RDF/rdf:Description/psi:zaaknummer", XML_NAMESPACES).text

            inhoudsindicatie_xml = xmlroot.find("rs:inhoudsindicatie", XML_NAMESPACES)
            inhoudsindicatie = ""

            try:
                for x in inhoudsindicatie_xml.iter():
                    if x.text is not None:
                        inhoudsindicatie += x.text + "\n"
            except AttributeError:
                logger.error("Could not find an inhoudsindicatie in XLM %s", xmlfilename)

            uitspraak_xml = xmlroot.find("rs:uitspraak", XML_NAMESPACES)
            uitspraak_text = ""

            try:
                for x in uitspraak_xml.iter():
                    if x.text is not None:
                        uitspraak_text += x.text + "\n"
            except AttributeError:
                logger.error("Could not find a uitspraak in XML %s", xmlfilename)

            uitspraak, created = Uitspraak.objects.update_or_create(
                ecli=ecli,
                instantie=instantie
            )

            uitspraak.zaaknummer = zaaknummer
            uitspraak.publicatiedatum = publicatiedatum
            uitspraak.uitspraakdatum = uitspraakdatum
            uitspraak.raw_xml = raw_xml

            uitspraak.inhoudsindicatie = inhoudsindicatie
            uitspraak.uitspraak = uitspraak_text

            uitspraak.save()

            if created:
                logger.info("Successfully created uitspraak %s", uitspraak)
            else:
                logger.info("Successfully updated uitspraak %s", uitspraak)
