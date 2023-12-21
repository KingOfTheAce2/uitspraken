# uitspraken

`uitspraken` is a simple Python program to easily load in Dutch court decision XML-files as published by the Dutch judiciary (*de Rechtspraak*) into a database.

## How to use
Clone the repository:
```
$ git clone https://github.com/mastaal/uitspraken.git
```

Create a Python environment and install all dependencies:
```
$ cd uitspraken
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -U -r requirements.txt
```
If you want to use a different database than the default SQLite database, make the appropriate changes to the `DATABASES` variable in `uitspraken/settings.py`.

Then, we can initialize the database:
```
$ ./manage migrate
$ ./manage create_instanties
$ ./manage create_rechtsgebieden
$ ./manage create_procedures
```

You are now ready to load in any XML-format uitspraken you have:

```
$ ./manage create_uitspraak_from_xml data/2021/ECLI_NL_RBLIM_2021_4036.xml
```

Note that you may supply multiple different XML files to this command, or use wildcards:
```
$ ./manage create_uitspraak_from_xml data/2021/ECLI_NL_HR*
$ ./manage create_uitspraak_from_xml ECLI_NL_RBLIM_2021_4036.xml ECLI_NL_RBLIM_2021_4037.xml
```

You may also supply one or more directories, which contain XML files in the expected format:
```
$ ls data
ECLI_NL_GHAMS_1922_10.xml ECLI_NL_GHAMS_1922_11.xml ECLI_NL_GHAMS_1922_12.xml ...
$ ./manage create_uitspraak_from_xml data
```

Note that this may take some time. Once done, you can make queries directly in your database, or in Python using [the Django database-abstraction API](https://docs.djangoproject.com/en/5.0/topics/db/queries/).

## Open Data Rechtspraak
Up until January 2023, the Rechtspraak periodically published an XML-dump with all uitspraken in their database. Sadly, they no longer provide this server. There is however still an API to directly query their database. For more information, see [Open Data Rechtspraak (NL)](https://www.rechtspraak.nl/Uitspraken/Paginas/Open-Data.aspx).

If you just want a copy of the complete XML-dump from January 2023, please get in touch.

## License

Copyright (c) 2023 Martijn Staal <uitspraken [a t ] martijn-staal.nl>

Available under the European Union Public License v1.2 (EUPL-1.2), or, at your option, any later version.
