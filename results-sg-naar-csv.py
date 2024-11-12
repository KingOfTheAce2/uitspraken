#!/usr/bin/env python

import csv
import json

filename = "results_socialegrondrechten_2024-11-12T19:11.json"

with open(filename, "rt", encoding="utf-8") as resultsfile:
    results = json.load(resultsfile)

export_filename = filename.replace(".json", ".csv")

with open(export_filename, "wt", encoding="utf-8") as csvfile:
    csvwr = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_ALL, quotechar='|')

    csvwr.writerow([
        "ECLI",
        "Uitspraakdatum",
        "Instantie",
        "Uitspraak type",
        "Inhoudsindicatie",
        "Aantal matches voor 'toeslagen'",
        "Aantal matches voor 'sociale grondrechten'",
        "Gevonden matches voor 'toeslagen'",
        "Gevonden matches voor 'sociale grondrechten'"
    ])

    for result in results:
        if len(result["data-socialegrondrechten_all"]["matches"]) > 0:
            csvwr.writerow([
                result["ecli"],
                result["uitspraakdatum"],
                result["instantie"],
                result["uitspraak_type"],
                result["inhoudsindicatie"].strip(),
                len(result["data-socialegrondrechten_all"]["matches"]),
                len(result["data-socialegrondrechten_all"]["additional_matches"]),
                result["data-socialegrondrechten_all"]["matches"],
                result["data-socialegrondrechten_all"]["additional_matches"],
            ])
