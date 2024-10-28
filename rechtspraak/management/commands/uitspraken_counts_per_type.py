"""
    rechtspraak/management/commands/uitspraken_counts_per_type.py

    Copyright 2024, Martijn Staal <uitspraken [at] martijn-staal.nl>

    Available under the EUPL-1.2, or, at your option, any later version.

    SPDX-License-Identifier: EUPL-1.2
"""

from typing import Any

from django.core.management import BaseCommand

from rechtspraak.models import Instantie, Uitspraak


class Command(BaseCommand):
    """Add all instanties"""

    help = "Add all instanties"

    def handle(self, *args: Any, **options: Any) -> None:
        instantie_types = Instantie.objects.order_by("instantie_type").values_list("instantie_type", flat=True).distinct()

        print("instantie\taantal uitspraken, totaal\taantal uitspraken met tekst\taantal uitspraken met data")
        total = Uitspraak.objects.all().count()
        total_tekst = Uitspraak.objects.exclude(tekst="").count()
        total_data = Uitspraak.objects.exclude(data={}).count()
        print(f"[Alle]\t{total}\t{total_tekst}\t{total_data}")
        for instantie in instantie_types:
            aantal_uitspraken = Uitspraak.objects.filter(instantie__instantie_type=str(instantie)).count()
            aantal_uitspraken_tekst = Uitspraak.objects.filter(instantie__instantie_type=str(instantie)).exclude(tekst="").count()
            aantal_uitspraken_data = Uitspraak.objects.filter(instantie__instantie_type=str(instantie)).exclude(data={}).count()
            print(f"{instantie}\t{aantal_uitspraken}\t{aantal_uitspraken_tekst}\t{aantal_uitspraken_data}")
