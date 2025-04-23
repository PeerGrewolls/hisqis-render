#!/bin/bash

while true
do
    echo "🔁 Starte HISQIS-Check..."
    python hisqis_checker.py
    echo "⏳ Warten auf nächsten Durchlauf..."
    sleep 1800
done