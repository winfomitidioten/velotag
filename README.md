# Velotag

Velotag ist eine Cross-Platform-App für Radsportler, deren Kernfunktion die **Heatmap gefahrener Gruppen-Routen** ist. Jede:r Nutzer:in sieht auf einer interaktiven Karte eine Heatmap aller eigenen Radstrecken – je öfter eine Strecke gefahren wurde, desto intensiver erscheint sie. Über die **Gruppenfunktion** können sich Radfahrer:innen zusammenschließen, eine gemeinsame Gruppen-Heatmap einsehen und sich über ein Leaderboard vergleichen. Routen werden per GPX-Upload oder Strava-Import hinzugefügt und stehen als Web- sowie als native iOS/Android-App zur Verfügung.

Das Projekt löst damit das Problem, dass klassische Trainings-Apps zwar einzelne Fahrten zeigen, aber selten sichtbar machen, welche Strecken eine Person oder eine Gruppe über die Zeit *tatsächlich* am häufigsten befährt – inklusive gemeinsamer Fotopunkte, Leistungsdaten (Puls/Watt) und ortsbezogener Auswertungen.

---

## Inhaltsverzeichnis

- [Features](#features)
- [Technologie-Stack](#technologie-stack)
- [Voraussetzungen](#voraussetzungen)
- [Installation & Setup](#installation--setup)
- [Nutzung / Ausführung](#nutzung--ausführung)
- [Tests](#tests)
- [Projektstruktur](#projektstruktur)
- [API-Referenz](#api-referenz)

---

## Features

- **Interaktive Heatmap-Karte** – Leaflet-Karte mit OpenStreetMap-Kacheln (inkl. mehrerer Kartenlayer); eigene und Gruppen-Routen werden als Heatmap/Polylines dargestellt
- **GPX-Upload** – Upload mit automatischer Validierung (nur Radaktivitäten), Koordinaten-Extraktion und Google-Polyline-Codierung
- **Strava-Import** – OAuth-2-Anbindung, um bestehende Strava-Aktivitäten direkt zu importieren
- **Leistungsdaten & Performance-Ansicht** – Herzfrequenz-, Watt- und Zeit-Streams pro Route, inkl. eigener Performance-Kartenansicht
- **Gruppen** – Gruppen erstellen, per E-Mail oder Einladungslink/QR-Code einladen, Mitglieder verwalten, Admin-Rechte übertragen, Mitglieder entfernen, Gruppe verlassen
- **Gruppen-Leaderboard** – Vergleich der Gruppenmitglieder anhand gefahrener Strecken
- **Favoriten** – Lieblingsgruppe markieren/entfernen für schnellen Zugriff
- **Foto-Pins** – Fotos mit Standort an Strecken/Gruppen anheften und in einer Galerie ansehen
- **Onboarding-Flow** – dreistufiger Onboarding-Prozess nach der Registrierung (Name/Foto, Standort per Sensor oder manueller Ortssuche, Erklärung), per Router-Guard erzwungen solange `onboarding_completed = False` ist
- **Geocoding-Proxy** – Backend-Proxy zu Nominatim (Adress-Suche & Reverse-Geocoding), damit der Client nicht direkt gegen OSM-Nominatim spricht
- **Push- & lokale Benachrichtigungen** – Firebase-Cloud-Messaging-Anbindung über Capacitor
- **Benutzerprofil** – öffentliches und eigenes Profil, Profilbild, Name und E-Mail bearbeitbar
- **Cross-Platform** – identische Codebasis läuft als Web-App sowie als native iOS- und Android-App über Capacitor

---

## Technologie-Stack

| Bereich | Technologie |
|---|---|
| Frontend | Vue 3 (Composition API), Vite, Pinia, Vue Router |
| Karte / Geodaten | Leaflet, OpenStreetMap, Turf.js |
| HTTP-Client | Axios |
| Mobile | Capacitor 8 (iOS & Android) – Geolocation, Camera, Push/Local Notifications, Status Bar |
| Sonstiges Frontend | QRCode-Generierung für Einladungslinks |
| Backend | Django 5, Django REST Framework 3 |
| Geodaten-Backend | GeoDjango (`django.contrib.gis`) mit PostGIS, GDAL/GEOS |
| Datenbank | PostgreSQL mit PostGIS-Erweiterung |
| Auth | DRF Token Authentication |
| Bildverarbeitung | Pillow |
| Push-Benachrichtigungen | Firebase Admin SDK |
| Produktionsserver | Gunicorn |
| Drittanbieter | Strava OAuth 2, OpenStreetMap Nominatim (Geocoding) |

---

## Voraussetzungen

- **Python** 3.10+
- **Node.js** `^20.19.0` oder `>=22.12.0` (siehe `frontend/package.json` → `engines`)
- **PostgreSQL** mit installierter **PostGIS**-Erweiterung (die Anwendung nutzt GeoDjango und erwartet die Postgis-Backend-Engine – ein einfaches PostgreSQL ohne PostGIS oder SQLite reicht **nicht**)
- **GDAL** und **GEOS** Bibliotheken lokal installiert
  - Windows: z. B. über die PostgreSQL-Installation (`C:\Program Files\PostgreSQL\<Version>\bin`) – `backend/core/settings.py` sucht diesen Pfad automatisch; alternativ eigenen Pfad über `WINDOWS_GDAL_BIN_PATH` setzen
  - macOS: über Homebrew (`brew install gdal geos`); alternativer Pfad über `MACOS_GDAL_LIB_PATH`
  - Linux: über die jeweilige Paketverwaltung (z. B. `apt install gdal-bin libgeos-dev`)
- Optional: **Android Studio** (für Android-Build), **Xcode** (für iOS-Build)
- Optional: **Firebase-Projekt** inkl. `firebase_credentials.json`, falls Push-Benachrichtigungen genutzt werden sollen

---

## Installation & Setup

### 1. Repository klonen

```bash
git clone [REPOSITORY-URL]
cd velotag
```

### 2. Backend einrichten

```bash
cd backend

# Virtuelle Umgebung erstellen und aktivieren
python -m venv venv-windows          # Windows
.\venv-windows\Scripts\activate

# python -m venv venv-macos          # macOS
# source venv-macos/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt
```

Lege anschließend die Datei `backend/.env` an (siehe [Umgebungsvariablen](#umgebungsvariablen)) und führe die Migrationen aus:

```bash
python manage.py migrate

# Optional: Admin-Benutzer anlegen
python manage.py createsuperuser
```

Falls Push-Benachrichtigungen genutzt werden sollen, `firebase_credentials.json` (aus der Firebase-Konsole) im `backend/`-Verzeichnis ablegen.

### 3. Frontend einrichten

```bash
cd frontend
npm install
```

In `frontend/vite.config.js` ist der Dev-Proxy standardmäßig auf einen entfernten Server (`167.233.33.166`) konfiguriert. Für lokale Entwicklung gegen das lokale Backend die auskommentierte Zeile aktivieren bzw. das `target` auf `http://127.0.0.1:8000` umstellen (in beiden Proxy-Einträgen `/api` und `/media`).

### Umgebungsvariablen

Lege die Datei `backend/.env` mit folgenden Werten an:

```env
# Django
SECRET_KEY=dein-geheimer-schluessel
DEBUG=True

# PostgreSQL / PostGIS (Produktion)
DB_NAME=velotag_db
DB_USER=postgres
DB_PASSW=dein-passwort
DB_HOST=localhost
DB_PORT=5432

# PostgreSQL / PostGIS (lokale Entwicklung, optional getrennt von Prod)
DEV_DB_NAME=velotag_dev_db
DEV_DB_USER=postgres
DEV_DB_PASSW=dein-passwort
DEV_DB_HOST=localhost
DEV_DB_PORT=5432

# Strava OAuth 2
STRAVA_CLIENT_ID=deine-client-id
STRAVA_CLIENT_SECRET=dein-client-secret
STRAVA_REDIRECT_URI=http://127.0.0.1:8000/api/strava/callback/
STRAVA_APP_REDIRECT_URL=velotag://strava-callback

# Nur Windows, falls GDAL/GEOS nicht automatisch gefunden werden
WINDOWS_GDAL_BIN_PATH=[PFAD-ZU-POSTGRESQL-BIN]

# Nur macOS, falls GDAL/GEOS nicht automatisch gefunden werden
MACOS_GDAL_LIB_PATH=[PFAD-ZU-HOMEBREW-LIB]
```

> Die Datenbank-Engine ist fest auf PostGIS eingestellt (`django.contrib.gis.db.backends.postgis`). Eine laufende PostgreSQL-Instanz mit aktivierter PostGIS-Erweiterung wird also **immer** benötigt, auch lokal.

---

## Nutzung / Ausführung

### Backend starten

```bash
cd backend
python manage.py runserver           # http://localhost:8000
```

### Frontend starten

```bash
cd frontend
npm run dev                          # http://localhost:5173

# Produktions-Build erstellen
npm run build

# Produktions-Build lokal vorschauen
npm run preview
```

### Schnellstart (beide Server gleichzeitig)

```bash
# Windows (öffnet Windows Terminal mit geteiltem Bildschirm)
start_server.bat

# macOS
./start_server.sh
```

### Produktionsbetrieb (Backend)

```bash
cd backend
gunicorn core.wsgi:application
```

### Mobile (iOS / Android)

```bash
cd frontend

# Produktions-Build erzeugen
npm run build

# Android
npx cap copy android
npx cap open android        # Öffnet Android Studio

# iOS
npx cap copy ios
npx cap open ios            # Öffnet Xcode
```

---

## Tests

**Backend:**

```bash
cd backend
python manage.py test
```

Django's Test-Runner erkennt automatisch die `tests.py`-Dateien in den Apps (`routes/tests.py`, `groups/tests.py`). Aktuell enthalten diese Dateien nur das Standard-Gerüst (`TestCase`) und noch keine ausgefüllten Testfälle – neue Tests werden nach dem Django-`TestCase`-Muster in der jeweiligen App ergänzt.

**Frontend:**

Für das Frontend ist aktuell kein automatisierter Test-Runner in `frontend/package.json` konfiguriert. Manuelle Verifikation erfolgt über `npm run dev` bzw. `npm run build` + `npm run preview`.

---

## Projektstruktur

```
velotag/
├── backend/
│   ├── core/                    # Django-Settings, Haupt-URL-Router, Strava-Views (core/views/strava.py)
│   ├── users/                   # Auth, Profil, Registrierung, Onboarding, Geocoding-Proxy, Device/Push-Token
│   ├── routes/                  # Routen-App: GPX-Upload, Polyline-Speicherung, Stats, Performance, Likes,
│   │                             #   Gruppen-Streckenüberschneidungen (GeoJSON)
│   ├── groups/                  # Gruppen-App: Mitglieder, Einladungen (E-Mail & Link/QR), Leaderboard,
│   │                             #   Favoriten, Admin-Übertragung
│   ├── photos/                  # Foto-Pins: Erstellen, Auflisten je Nutzer/Gruppe, Detailansicht
│   ├── utils/                   # Geteilte Hilfsfunktionen, u. a. Push-Benachrichtigungen (Firebase)
│   ├── media/                   # Hochgeladene Bilder (Profilbilder, Foto-Pins) — nicht versioniert
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/                 # Axios-Instanz (client.js) mit Token-Interceptor + gebündelte API-Calls (api.js)
│   │   ├── components/          # Wiederverwendbare UI-Komponenten (Modals, TabBar, Header, Picker …)
│   │   ├── composables/         # GPX-Parsing, Karten-Rendering, Foto-Pins, Favoriten, Strava-Import u. a.
│   │   ├── router/               # Vue-Router-Konfiguration inkl. Auth- & Onboarding-Guard
│   │   ├── store/                # Pinia-Stores (User, Heatmap-Style, Settings)
│   │   ├── utils/                 # Kleine Utility-Funktionen (z. B. Intensitäts-Farbverlauf der Heatmap)
│   │   └── views/                # Seiten: Karte, Login/Register, Onboarding, Profil, Gruppen, Strecken, Settings
│   ├── android/                  # Capacitor Android-Projekt
│   ├── ios/                      # Capacitor iOS-Projekt
│   ├── vite.config.js
│   └── package.json
├── docs/                         # Projektdokumentation [aktuell noch leer]
├── start_server.bat              # Windows-Schnellstart (Backend + Frontend)
├── start_server.sh               # macOS-Schnellstart (Backend + Frontend)
└── README.md
```

---

## API-Referenz

Alle Endpunkte erfordern (sofern nicht anders angegeben) den HTTP-Header:

```
Authorization: Token <dein-token>
```

### Authentifizierung & Profil

| Methode | Endpunkt | Beschreibung |
|---|---|---|
| `POST` | `/api/register/` | Registrierung (E-Mail, Passwort) |
| `POST` | `/api/login/` | Anmeldung → gibt Auth-Token zurück |
| `POST` | `/api/logout/` | Abmeldung (löscht Token) |
| `GET` | `/api/profil/` | Eigenes Profil abrufen |
| `PATCH` | `/api/profil/` | Profil aktualisieren (Name, E-Mail, Passwort, Bild) |
| `GET` | `/api/users/<id>/profile/` | Öffentliches Profil eines anderen Nutzers abrufen |
| `POST` | `/api/onboarding/` | Onboarding-Daten speichern (Name/Foto, Standort) & `onboarding_completed` setzen |
| `GET` | `/api/geocode/` | Adress-Suche über Nominatim-Proxy |
| `GET` | `/api/geocode/reverse/` | Reverse-Geocoding (Koordinaten → Adresse) über Nominatim-Proxy |
| `POST` | `/api/user/save-push-token/` | Push-Benachrichtigungs-Gerätetoken speichern |

### Routen

| Methode | Endpunkt | Beschreibung |
|---|---|---|
| `POST` | `/api/routes/create/` | Route hochladen (GPX-Daten) |
| `GET` | `/api/routes/list/` | Alle eigenen Routen (Liste) abrufen |
| `GET` | `/api/routes/map/` | Routendaten für die Kartenansicht (Heatmap) |
| `GET` | `/api/routes/stats/` | Statistiken zu den eigenen Routen |
| `GET` | `/api/routes/performance/` | Performance-Daten (Puls/Watt/Zeit) |
| `GET` | `/api/routes/<id>/` | Detailansicht einer Route |
| `POST` | `/api/routes/<id>/like/` | Route liken |
| `GET` | `/api/routes/intersections/<group_id>/` | Streckenüberschneidungen einer Gruppe als GeoJSON |

### Gruppen

| Methode | Endpunkt | Beschreibung |
|---|---|---|
| `GET` | `/api/groups/` | Eigene Gruppen auflisten |
| `POST` | `/api/groups/` | Neue Gruppe erstellen |
| `GET` | `/api/groups/<id>/` | Gruppendetails abrufen |
| `DELETE` | `/api/groups/<id>/` | Gruppe/Mitglied entfernen (nur Admin) |
| `POST` | `/api/groups/<id>/invite/` | Mitglied per E-Mail einladen (nur Admin) |
| `GET`/`POST` | `/api/groups/<id>/invite-link/` | Einladungslink/QR-Code für die Gruppe erzeugen |
| `POST` | `/api/groups/join/` | Gruppe per Einladungstoken beitreten |
| `POST` | `/api/groups/<id>/leave` | Eigene Mitgliedschaft in Gruppe kündigen |
| `POST` | `/api/groups/<id>/kick/` | Mitglied aus Gruppe entfernen (nur Admin) |
| `POST` | `/api/groups/<id>/transfer-admin/` | Admin-Rechte an anderes Mitglied übertragen |
| `GET` | `/api/groups/<id>/leaderboard/` | Gruppen-Leaderboard abrufen |
| `GET` | `/api/groups/favorite/` | Favorisierte Gruppe abrufen |
| `POST` | `/api/groups/<id>/favorite/` | Gruppe als Favorit markieren |
| `POST` | `/api/groups/remove_favorite/` | Favoritenmarkierung entfernen |
| `GET` | `/api/user/invitations/` | Offene Einladungen abrufen |
| `POST` | `/api/user/invitations/` | Einladung annehmen oder ablehnen |

### Foto-Pins

| Methode | Endpunkt | Beschreibung |
|---|---|---|
| `POST` | `/api/photo-pins/create/` | Foto-Pin (Bild + Standort) erstellen |
| `GET` | `/api/photo-pins/list/` | Eigene Foto-Pins auflisten |
| `GET` | `/api/photo-pins/group/<id>/` | Foto-Pins einer Gruppe auflisten |
| `GET` | `/api/photo-pins/<id>/` | Detailansicht eines Foto-Pins |

### Strava-Integration

| Methode | Endpunkt | Beschreibung |
|---|---|---|
| `GET` | `/api/strava/status/` | Verbindungsstatus zu Strava abrufen |
| `GET` | `/api/strava/connect/` | OAuth-URL abrufen |
| `GET` | `/api/strava/callback/` | OAuth-Callback (speichert Tokens) |
| `GET` | `/api/strava/activities/` | Strava-Aktivitäten des Nutzers abrufen |
| `POST` | `/api/strava/activities/<id>/import/` | Einzelne Strava-Aktivität als Route importieren |

---

## Lizenz

[LIZENZ-INFORMATION EINFÜGEN]
