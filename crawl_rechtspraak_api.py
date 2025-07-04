#!/usr/bin/env python3
"""Crawl the Open Data Rechtspraak API and store results in the database."""

import argparse
import datetime
import logging
import os
import time

import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "uitspraken.settings")
django.setup()

from rechtspraak.models import Instantie, Uitspraak
from rechtspraak.utils import (
    get_updated_eclis_for_instantie_since,
    create_uitspraak_from_ecli,
)

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    instanties_types = list(
        Instantie.objects.order_by("instantie_type")
        .values_list("instantie_type", flat=True)
        .distinct()
    )

    parser = argparse.ArgumentParser(
        description="Crawl the Open Data Rechtspraak API for updated uitspraken"
    )
    parser.add_argument(
        "instantie_type",
        choices=instanties_types,
        help="The instantie type to crawl",
    )
    parser.add_argument(
        "since",
        help="Only include uitspraken modified since this date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between API requests in seconds (default: 1.0)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    since_date = datetime.datetime.strptime(args.since, "%Y-%m-%d").date()

    instanties = Instantie.objects.filter(instantie_type=args.instantie_type)
    logger.info("Found %s instanties", instanties.count())

    all_eclis: list[str] = []
    for instantie in instanties:
        eclis = get_updated_eclis_for_instantie_since(instantie, since_date)
        logger.info("Found %s ECLI's for %s", len(eclis), instantie)
        all_eclis.extend(eclis)

    logger.info("Total ECLI's found: %s", len(all_eclis))

    total = len(all_eclis)
    for idx, ecli in enumerate(all_eclis, start=1):
        logger.info("(%s/%s, %.2f%%) Fetching %s", idx, total, idx / total * 100, ecli)
        try:
            Uitspraak.objects.get(ecli=ecli)
            logger.info("%s already exists, skipping", ecli)
        except Uitspraak.DoesNotExist:
            try:
                create_uitspraak_from_ecli(ecli)
            except Exception as exc:  # noqa: BLE001
                logger.error("Failed to crawl %s: %s", ecli, exc)
            time.sleep(args.delay)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
