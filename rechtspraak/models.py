"""
    rechtspraak/models.py

    Copyright 2023, Martijn Staal <uitspraken [at] martijn-staal.nl>

    Available under the EUPL-1.2, or, at your option, any later version.

    SPDX-License-Identifier: EUPL-1.2
"""

import datetime

from django.db import models


class Rechtsgebied(models.Model):
    """Model for a rechtsgebied as listed in the waardelijst Rechtsgebieden"""

    naam = models.CharField(max_length=512)
    identifier = models.URLField(unique=True)

    class Meta:
        """Meta information for Django"""

        indexes = [
            models.Index(fields=["naam"])
        ]

    def __str__(self) -> str:
        return f"{self.naam}"

    def __repr__(self) -> str:
        return f"Rechtsgebied ({self.__str__()})"


class ProcedureSoort(models.Model):
    """Model for a type of procedure as listed in the waardelijst Procedures"""

    naam = models.CharField(max_length=512)
    identifier = models.URLField(unique=True)

    class Meta:
        """Meta information for Django"""

        indexes = [
            models.Index(fields=["naam"]),
        ]

    def __str__(self) -> str:
        return f"{self.naam}"

    def __repr__(self) -> str:
        return f"ProcedureSoort ({self.__str__()})"


class Instantie(models.Model):
    """Model for an Instantie: a specific court or body which at some point in time had the statutory power to issue legal decisions"""

    naam = models.CharField(max_length=256, unique=True)
    instantie_type = models.CharField(max_length=256)
    identifier = models.CharField(max_length=1024)
    afkorting = models.CharField(max_length=64)
    begin_date = models.DateField()
    end_date = models.DateField(null=True)

    class Meta:
        """Meta information for Django"""

        indexes = [
            models.Index(fields=["naam"]),
            models.Index(fields=["instantie_type"]),
            models.Index(fields=["afkorting"]),
            models.Index(fields=["identifier"])
        ]

    def __str__(self) -> str:
        return f"Instantie {self.instantie_type} {self.afkorting}"


class Uitspraak(models.Model):
    """A court decision: arrest, uitspraak, beschikking, conclusie, etc."""

    ecli = models.CharField(
        max_length=128,
        unique=True,
        help_text="The European Case Law Identifier (ECLI) for this Uitspraak."
    )
    zaaknummer = models.CharField(
        max_length=2048,
        help_text="The case number specific to the Instantie that issued the uitspraak."
    )

    publicatiedatum = models.DateField(default=datetime.date(1000, 1, 1))
    uitspraakdatum = models.DateField(default=datetime.date(1000, 1, 1))
    # TODO: Add support for dcterms:modified so that we can keep track of updates at the
    # authorative API from de Rechtspraak.

    raw_xml = models.TextField()

    data = models.JSONField(
        default=dict,
        help_text="JSON field to store optional extra (meta)data."
    )

    inhoudsindicatie = models.TextField()
    tekst = models.TextField()

    # TODO: Support dcterms:replaces and dcterms:isReplacedBy

    # TODO: Support dcterms:relation

    class UitspraakType(models.TextChoices):
        UITSPRAAK = "Uitspraak"
        CONCLUSIE = "Conclusie"

    uitspraak_type = models.CharField(
        max_length=64,
        choices=UitspraakType.choices,
        default="Uitspraak"
    )
    instantie = models.ForeignKey(Instantie, models.CASCADE)
    procedure_soorten = models.ManyToManyField(ProcedureSoort)
    rechtsgebieden = models.ManyToManyField(Rechtsgebied)

    class Meta:
        """Meta information for Django"""

        indexes = [
            models.Index(fields=["ecli"]),
            models.Index(fields=["zaaknummer"]),
            models.Index(fields=["instantie", "publicatiedatum"]),
            models.Index(fields=["instantie", "uitspraakdatum"]),
            models.Index(fields=["uitspraak_type"])
        ]

    def __str__(self) -> str:
        return f"Uitspraak {self.ecli} ({self.instantie.naam})"
