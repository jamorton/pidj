#!/bin/sh
rm -f pidj.sqlite3
python -c "import pidj; pidj.models.create_tables()"
