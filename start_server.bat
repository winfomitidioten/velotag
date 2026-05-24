@echo off
:: Holt den absoluten Pfad des aktuellen Ordners
set PROJECT_ROOT=%cd%

echo [System] Starte geteilten Bildschirm im Windows Terminal...

:: Öffnet das Django-Backend in der linken Hälfte und splittet dann für Vue nach rechts
wt -d "%PROJECT_ROOT%\backend" cmd /k "title Django-Backend && call venv-windows\Scripts\python.exe manage.py runserver" ; split-pane -d "%PROJECT_ROOT%\frontend" cmd /k "title Vue-Frontend && npm run dev"