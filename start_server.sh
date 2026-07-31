#!/bin/bash
# Holt den absoluten Pfad des aktuellen Ordners
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "[System] Starte Django-Backend und Vue-Frontend..."

# Django-Backend starten
osascript -e "tell application \"Terminal\"
    do script \"cd '$PROJECT_ROOT/backend' && source venv-macos/bin/activate && python manage.py runserver\"
end tell"

# Vue-Frontend starten
osascript -e "tell application \"Terminal\"
    do script \"cd '$PROJECT_ROOT/frontend' && npm run dev\"
end tell"
