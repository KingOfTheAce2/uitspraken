"""
    rechtspraak/management/commands/create_uitspraak_from_xml.py

    Parse an uitspraak from an XML file.

    For information regarding the expected XML structure, please see https://www.rechtspraak.nl/Uitspraken/Paginas/Open-Data.aspx.

    Copyright 2023, Martijn Staal <uitspraken [at] martijn-staal.nl>

    Available under the EUPL-1.2, or, at your option, any later version.

    SPDX-License-Identifier: EUPL-1.2
"""

import datetime
import logging
import xml.etree.ElementTree as ET

from pathlib import Path
from typing import Any

from django.core.management import BaseCommand, CommandParser

from rechtspraak.models import Instantie, Rechtsgebied, ProcedureSoort, Uitspraak

logger = logging.getLogger(__name__)
XML_NAMESPACES = {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "dcterms": "http://purl.org/dc/terms/",
    "psi": "http://psi.rechtspraak.nl/",
    "rs": "http://www.rechtspraak.nl/schema/rechtspraak-1.0",
    "ecli": "https://e-justice.europa.eu/ecli"
}


def create_uitspraak_from_xmlstring(xmlstring: str, xmlfilename: str) -> Uitspraak:
    """Create a new Uitspraak object based on an XML string as provided by de Rechtspraak.

    The expected XML structure is based on the structure as described in "Open Data van de Rechtspraak",
    version 1.15, dated 2019-03-20.
    This document can be found here:
    https://www.rechtspraak.nl/SiteCollectionDocuments/Technische-documentatie-Open-Data-van-de-Rechtspraak.pdf

    xmlstring -- the actual XML in string format
    xmlfilename -- the filename the XML string was read from; only used for logging purposes.
    """
    xmlroot = ET.fromstring(xmlstring)

    ecli = xmlroot.find("rdf:RDF/rdf:Description/dcterms:identifier", XML_NAMESPACES).text
    instantie_naam = xmlroot.find("rdf:RDF/rdf:Description/dcterms:creator", XML_NAMESPACES).text

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

    try:
        zaaknummer = xmlroot.find("rdf:RDF/rdf:Description/psi:zaaknummer", XML_NAMESPACES).text
    except AttributeError:
        logger.warning("Could not find a zaaknummer for %s", xmlfilename)
        zaaknummer = ""

    try:
        uitspraak_type = xmlroot.find("rdf:RDF/rdf:Description/dcterms:type", XML_NAMESPACES).text
    except AttributeError:
        logger.warning("Could not find an uitspraak type for %s", xmlfilename)
        uitspraak_type = "Uitspraak"

    proceduresoorten_xml = xmlroot.findall("rdf:RDF/rdf:Description/psi:procedure", XML_NAMESPACES)
    proceduresoorten: list[ProcedureSoort] = []

    for proceduresoort_xml in proceduresoorten_xml:
        proceduresoorten.append(ProcedureSoort.objects.get(identifier=proceduresoort_xml.get("resourceIdentifier")))

    rechtsgebieden_xml = xmlroot.findall("rdf:RDF/rdf:Description/dcterms:subject", XML_NAMESPACES)
    rechtsgebieden: list[Rechtsgebied] = []

    for rechtsgebied_xml in rechtsgebieden_xml:
        rechtsgebieden.append(Rechtsgebied.objects.get(identifier=rechtsgebied_xml.get("resourceIdentifier")))

    inhoudsindicatie_xml = xmlroot.find("rs:inhoudsindicatie", XML_NAMESPACES)
    inhoudsindicatie = ""

    try:
        for x in inhoudsindicatie_xml.iter():
            if x.text is not None:
                inhoudsindicatie += x.text + "\n"
    except AttributeError:
        logger.error("Could not find an inhoudsindicatie in XML %s", xmlfilename)

    uitspraak_xml = xmlroot.find("rs:uitspraak", XML_NAMESPACES)
    conclusie_xml = xmlroot.find("rs:conclusie", XML_NAMESPACES)
    uitspraak_text = ""

    try:
        for x in uitspraak_xml.iter():
            if x.text is not None:
                uitspraak_text += x.text + "\n"
    except AttributeError:
        logger.error("Could not find a uitspraak in XML %s, trying to find a conclusie", xmlfilename)

        try:
            for x in conclusie_xml.iter():
                if x.text is not None:
                    uitspraak_text += x.text + "\n"
        except AttributeError:
            logger.error("Neither uitspraak nor conclusie in XML %s", xmlfilename)

    uitspraak, created = Uitspraak.objects.update_or_create(
        ecli=ecli,
        instantie=instantie
    )

    uitspraak.zaaknummer = zaaknummer
    uitspraak.publicatiedatum = publicatiedatum
    uitspraak.uitspraakdatum = uitspraakdatum
    uitspraak.raw_xml = xmlstring

    uitspraak.inhoudsindicatie = inhoudsindicatie
    uitspraak.tekst = uitspraak_text

    uitspraak.uitspraak_type = uitspraak_type

    for proceduresoort in proceduresoorten:
        uitspraak.procedure_soorten.add(proceduresoort)

    for rechtsgebied in rechtsgebieden:
        uitspraak.rechtsgebieden.add(rechtsgebied)

    uitspraak.save()

    if created:
        logger.info("Successfully created uitspraak %s", uitspraak)
    else:
        logger.info("Successfully updated uitspraak %s", uitspraak)

    return uitspraak


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
