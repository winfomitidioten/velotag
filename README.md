# Velotag

Velotag ist eine Cross-Platform-App für Radsportler, deren Kernfunktion die **Heatmap gefahrener Gruppen-Routen** ist. Jede:r Nutzer:in sieht auf einer interaktiven Karte eine Heatmap aller eigenen Radstrecken – je öfter eine Strecke gefahren wurde, desto intensiver erscheint sie. Über die **Gruppenfunktion** können sich Radfahrer:innen zusammenschließen, eine gemeinsame Gruppen-Heatmap einsehen und sich über ein Leaderboard vergleichen. Routen werden per GPX-Upload oder Strava-Import hinzugefügt und stehen als Web- sowie als native iOS/Android-App zur Verfügung.

Das Projekt löst damit das Problem, dass klassische Trainings-Apps zwar einzelne Fahrten zeigen, aber selten sichtbar machen, welche Strecken eine Person oder eine Gruppe über die Zeit *tatsächlich* am häufigsten befährt – inklusive gemeinsamer Fotopunkte, Leistungsdaten (Puls/Watt) und ortsbezogener Auswertungen.

---

## Inhaltsverzeichnis

- [Features](#features)
- [Technologie-Stack](#technologie-stack)
- [Voraussetzungen](#voraussetzungen)
- [Datenbank einrichten (PostgreSQL + PostGIS)](#datenbank-einrichten-postgresql--postgis)
- [Installation & Setup](#installation--setup)
- [Konfiguration: Wohin zeigt das Frontend?](#konfiguration-wohin-zeigt-das-frontend)
- [Nutzung / Ausführung](#nutzung--ausführung)
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
- **API-Dokumentation** – interaktive Swagger UI unter `/api/docs/` (generiert mit drf-spectacular)
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
| API-Doku | drf-spectacular (OpenAPI 3 / Swagger UI) |
| Bildverarbeitung | Pillow |
| Push-Benachrichtigungen | Firebase Admin SDK |
| Produktionsserver | Gunicorn |
| Drittanbieter | Strava OAuth 2, OpenStreetMap Nominatim (Geocoding) |

---

## Voraussetzungen

- **Python** 3.10+
- **Node.js** `^20.19.0` oder `>=22.12.0` (siehe `frontend/package.json` → `engines`)
- **PostgreSQL mit PostGIS-Erweiterung** – siehe [Datenbank einrichten](#datenbank-einrichten-postgresql--postgis). Ein einfaches PostgreSQL ohne PostGIS oder SQLite funktioniert **nicht**.
- Optional: **Android Studio** (für Android-Build), **Xcode** (für iOS-Build)
- Optional: **Firebase-Projekt** inkl. `firebase_credentials.json`, falls Push-Benachrichtigungen genutzt werden sollen. Ohne die Datei startet das Backend normal, Push ist dann nur deaktiviert.

---

## Datenbank einrichten (PostgreSQL + PostGIS)

Das Backend nutzt GeoDjango und ist in `settings.py` fest auf die PostGIS-Engine eingestellt (`django.contrib.gis.db.backends.postgis`). Eine PostgreSQL-Instanz **mit aktivierter PostGIS-Erweiterung** wird deshalb immer benötigt – auch, wenn man nur lokal testen will.

### 1. PostgreSQL + PostGIS installieren

| System | Vorgehen |
|---|---|
| **Windows** | [PostgreSQL-Installer](https://www.postgresql.org/download/windows/) ausführen. Am Ende startet der **Stack Builder** – dort unter *Spatial Extensions* **PostGIS** mit auswählen und installieren. |
| **macOS** | `brew install postgresql postgis` und anschließend `brew services start postgresql` |
| **Linux (Debian/Ubuntu)** | `sudo apt install postgresql postgis postgresql-<version>-postgis-3` |

Die PostGIS-Installation liefert gleichzeitig die benötigten **GDAL-/GEOS-Bibliotheken** mit. `backend/core/settings.py` sucht diese auf Windows und macOS automatisch in den Standardpfaden (z. B. `C:\Program Files\PostgreSQL\18\bin` bzw. `/opt/homebrew/lib`). Nur falls sie dort nicht liegen, muss der Pfad in der `.env` gesetzt werden (`WINDOWS_GDAL_BIN_PATH` bzw. `MACOS_GDAL_LIB_PATH`).

### 2. Datenbank und Benutzer anlegen

Als PostgreSQL-Superuser verbinden (Windows: *SQL Shell (psql)* aus dem Startmenü, macOS/Linux: `psql -U postgres`) und ausführen:

```sql
CREATE DATABASE velotag;
CREATE USER velotag_dev WITH PASSWORD 'dein-passwort';
GRANT ALL PRIVILEGES ON DATABASE velotag TO velotag_dev;
```

### 3. PostGIS in der Datenbank aktivieren

Die Erweiterung muss **in der Datenbank selbst** aktiviert werden – weiterhin als Superuser:

```sql
\c velotag

CREATE EXTENSION postgis;

-- Ab PostgreSQL 15 hat ein neuer Benutzer standardmäßig keine Schreibrechte
-- im public-Schema. Ohne diese Zeile scheitern die Django-Migrationen.
GRANT ALL ON SCHEMA public TO velotag_dev;
```

Prüfen, ob PostGIS aktiv ist:

```sql
SELECT PostGIS_Version();
```

Kommt hier eine Versionsnummer zurück, ist die Datenbank fertig eingerichtet. Die dabei vergebenen Werte (`velotag`, `velotag_dev`, Passwort) werden gleich in `backend/.env` als `DB_NAME`, `DB_USER` und `DB_PASSW` eingetragen.

---

## Installation & Setup

### 1. Repository klonen

```bash
git clone [REPOSITORY-URL]
cd velotag
```

### 2. Datenbank einrichten

Siehe [Datenbank einrichten](#datenbank-einrichten-postgresql--postgis) – muss vor dem ersten `migrate` erledigt sein.

### 3. Backend einrichten

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

> Die Namen `venv-windows` bzw. `venv-macos` sind nicht beliebig: die Schnellstart-Skripte `start_server.bat` / `start_server.sh` erwarten genau diese Ordner.

### 4. Umgebungsvariablen anlegen (`backend/.env`)

Datei `backend/.env` mit folgendem Inhalt anlegen. Bis auf `DEBUG` sind alle Werte **Pflicht** – fehlt einer davon, startet das Backend gar nicht:

```env
# Django
SECRET_KEY=dein-geheimer-schluessel

# Einziger optionaler Wert hier (Standard: False) - lokal auf True setzen
DEBUG=True

# Datenbank (Werte aus dem Datenbank-Setup oben)
DB_NAME=velotag
DB_USER=velotag_dev
DB_PASSW=dein-passwort
DB_HOST=localhost
DB_PORT=5432

# Strava OAuth 2 (App unter https://www.strava.com/settings/api registrieren)
STRAVA_CLIENT_ID=deine-client-id
STRAVA_CLIENT_SECRET=dein-client-secret
STRAVA_REDIRECT_URI=http://127.0.0.1:8000/api/strava/callback/
```

Optionale Werte, die nur bei Bedarf gesetzt werden müssen:

```env
# Ziel-Deep-Link, in den das Backend nach dem Strava-Login zurückspringt
# (Standard, wenn nicht gesetzt: velotag://strava-callback)
STRAVA_APP_REDIRECT_URL=velotag://strava-callback

# Nur nötig, wenn GDAL/GEOS NICHT in den Standardpfaden liegen
WINDOWS_GDAL_BIN_PATH=C:\Program Files\PostgreSQL\18\bin
MACOS_GDAL_LIB_PATH=/opt/homebrew/lib
```

Anschließend die Migrationen ausführen:

```bash
python manage.py migrate

# Optional: Admin-Benutzer für /admin/ anlegen
python manage.py createsuperuser
```

Falls Push-Benachrichtigungen genutzt werden sollen, zusätzlich `firebase_credentials.json` (aus der Firebase-Konsole) im `backend/`-Verzeichnis ablegen.

### 5. Frontend einrichten

```bash
cd frontend
npm install
```

Wohin das Frontend seine Anfragen schickt, hängt vom Einsatzszenario ab – siehe nächster Abschnitt.

---

## Konfiguration: Wohin zeigt das Frontend?

Das ist der Punkt, an dem beim Aufsetzen am häufigsten etwas schiefgeht. Es gibt **zwei** Stellschrauben, und welche greift, hängt davon ab, wie das Frontend läuft:

| Stellschraube | Wirkt bei | Wirkt **nicht** bei |
|---|---|---|
| Proxy in `frontend/vite.config.js` | nur `npm run dev` (Browser) | Mobile-Builds, `npm run build` |
| `VITE_API_BASE_URL` in `frontend/.env.local` | immer – **überschreibt den Proxy** | – |

Die Auflösung in `src/api/client.js` / `src/api/api.js` ist:

1. `VITE_API_BASE_URL` gesetzt → **gewinnt immer**
2. sonst im Dev-Server (`npm run dev`) → relativer Pfad `/api` durch den Vite-Proxy
3. sonst (fertiger Build, also auch Mobile) → fest `http://167.233.33.166/api`

> **Häufigster Fehler:** Eine `frontend/.env.local` von einem früheren Mobile-Test liegt noch herum. Sie überschreibt auch bei `npm run dev` still den Proxy, und man wundert sich, warum die Proxy-Änderung in `vite.config.js` keine Wirkung zeigt. Im Zweifel die Datei löschen oder umbenennen.

### Szenario A: Alles lokal auf dem Rechner (Backend + Frontend im Browser)

1. Sicherstellen, dass **keine** `frontend/.env.local` existiert (bzw. `VITE_API_BASE_URL` darin auskommentiert ist)
2. In `frontend/vite.config.js` in **beiden** Proxy-Einträgen (`/api` und `/media`) das `target` auf das lokale Backend umstellen:

Konkret heißt das: in beiden Blöcken die Produktions-Zeile auskommentieren und die lokale aktivieren. Die übrigen Optionen (`changeOrigin`, `rewrite`) bleiben unverändert.

```js
'/api': {
//  target: 'http://167.233.33.166',   // <- auskommentieren
    target: 'http://127.0.0.1:8000',   // <- aktivieren
    ...
},
'/media': {
//  target: 'http://167.233.33.166',   // <- auskommentieren
    target: 'http://127.0.0.1:8000',   // <- aktivieren
    ...
}
```

3. In `backend/.env` sollte `STRAVA_REDIRECT_URI=http://127.0.0.1:8000/api/strava/callback/` stehen, damit auch der Strava-Login lokal zurückfindet
4. Beide Server starten (siehe [Nutzung / Ausführung](#nutzung--ausführung))

### Szenario B: Mobile-App gegen den echten Server (Normalfall)

Hier ist **keine Konfiguration nötig**: ohne `VITE_API_BASE_URL` fällt ein fertiger Build automatisch auf den Produktionsserver `http://167.233.33.166/api` zurück. Der Proxy aus `vite.config.js` spielt keine Rolle, weil im Mobile-Build kein Dev-Server läuft.

```bash
cd frontend
# Falls vorhanden: .env.local loeschen oder VITE_API_BASE_URL darin auskommentieren
npm run build
npx cap sync android      # bzw. ios
npx cap open android      # bzw. ios
```

### Szenario C: Mobile-App gegen das lokale Backend (zum Entwickeln)

Dafür `frontend/.env.local` anlegen:

```env
# Android-Emulator: 10.0.2.2 ist die Adresse, unter der der Emulator den
# Host-Rechner erreicht. localhost/127.0.0.1 zeigt im Emulator auf das
# Geraet selbst und funktioniert hier NICHT.
VITE_API_BASE_URL=http://10.0.2.2:8000/api/
```

Danach neu bauen und übertragen (`.env.local` wird nur beim Build eingelesen):

```bash
npm run build
npx cap sync android
```

Das Backend kann dabei ganz normal mit `python manage.py runserver` laufen – `10.0.2.2` ist in `ALLOWED_HOSTS` bereits eingetragen.

> **Physisches Gerät statt Emulator:** Dann die LAN-IP des Rechners verwenden (z. B. `VITE_API_BASE_URL=http://192.168.1.23:8000/api/`), das Backend mit `python manage.py runserver 0.0.0.0:8000` starten **und** dieselbe IP in `ALLOWED_HOSTS` in `backend/core/settings.py` ergänzen – sonst blockt Django die Anfragen mit `DisallowedHost` ab.

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

# macOS (öffnet zwei Terminal-Fenster)
./start_server.sh
```

### API-Dokumentation

Bei laufendem Backend erreichbar unter:

| URL | Inhalt |
|---|---|
| `http://localhost:8000/api/docs/` | Swagger UI (interaktiv, Endpunkte direkt testbar) |
| `http://localhost:8000/api/redoc/` | Redoc (lesefreundliche Darstellung) |
| `http://localhost:8000/api/schema/` | OpenAPI-3-Schema als YAML |

### Mobile (iOS / Android)

Vor dem Build klären, gegen welchen Server die App laufen soll – siehe [Konfiguration](#konfiguration-wohin-zeigt-das-frontend), Szenario B (echter Server) bzw. C (lokales Backend).

```bash
cd frontend

# Produktions-Build erzeugen
npm run build

# Android
npx cap sync android
npx cap open android        # Öffnet Android Studio

# iOS
npx cap sync ios
npx cap open ios            # Öffnet Xcode
```

### Produktionsbetrieb (Backend)

```bash
cd backend
gunicorn core.wsgi:application
```

---

## Projektstruktur

```
velotag/
├── backend/
│   ├── core/                     # Django-Settings, Haupt-URL-Router, Strava-Views (core/views/strava.py)
│   ├── users/                    # Auth, Profil, Registrierung, Onboarding, Geocoding-Proxy, Device/Push-Token
│   ├── routes/                   # Routen-App: GPX-Upload, Polyline-Speicherung, Stats, Performance, Likes,
│   │                             #   Gruppen-Streckenüberschneidungen (GeoJSON)
│   ├── groups/                   # Gruppen-App: Mitglieder, Einladungen (E-Mail & Link/QR), Leaderboard,
│   │                             #   Favoriten, Admin-Übertragung
│   ├── photos/                   # Foto-Pins: Erstellen, Auflisten je Nutzer/Gruppe, Bearbeiten/Löschen
│   ├── utils/                    # Geteilte Hilfsfunktionen, u. a. Push-Benachrichtigungen (Firebase)
│   ├── media/                    # Hochgeladene Bilder — wird beim ersten Upload erzeugt, nicht versioniert
│   ├── manage.py
│   ├── requirements.txt
│   └── .env                      # Lokale Konfiguration — nicht versioniert
├── frontend/
│   ├── src/
│   │   ├── api/                  # Axios-Instanzen (client.js, api.js) mit Token-Interceptor
│   │   ├── assets/               # Statische Assets (Logos, Kartenlayer-Vorschaubilder, globales CSS)
│   │   ├── components/           # Wiederverwendbare UI-Komponenten (Modals, TabBar, Header, Picker …)
│   │   ├── composables/          # GPX-Parsing, Karten-Rendering, Foto-Pins, Favoriten, Strava-Import u. a.
│   │   ├── router/               # Vue-Router-Konfiguration inkl. Auth- & Onboarding-Guard
│   │   ├── store/                # Pinia-Stores (User, Heatmap-Style, Settings)
│   │   ├── utils/                # Kleine Utility-Funktionen (z. B. Intensitäts-Farbverlauf der Heatmap)
│   │   └── views/                # Seiten: Karte, Login/Register, Onboarding, Profil, Gruppen, Strecken, Settings
│   ├── android/                  # Capacitor Android-Projekt
│   ├── ios/                      # Capacitor iOS-Projekt
│   ├── vite.config.js            # Dev-Server-Proxy (nur für npm run dev)
│   └── package.json
├── start_server.bat              # Windows-Schnellstart (Backend + Frontend)
├── start_server.sh               # macOS-Schnellstart (Backend + Frontend)
└── README.md
```

---

## API-Referenz

Eine interaktive, immer aktuelle Fassung dieser Übersicht liefert die Swagger UI unter `/api/docs/` (siehe [API-Dokumentation](#api-dokumentation)).

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
| `PATCH` | `/api/routes/<id>/` | Route bearbeiten (Name, Gruppe) |
| `DELETE` | `/api/routes/<id>/` | Route löschen |
| `POST` | `/api/routes/<id>/like/` | Route liken |
| `DELETE` | `/api/routes/<id>/like/` | Like zurücknehmen |
| `GET` | `/api/routes/intersections/<group_id>/` | Streckenüberschneidungen einer Gruppe als GeoJSON |

### Gruppen

| Methode | Endpunkt | Beschreibung |
|---|---|---|
| `GET` | `/api/groups/` | Eigene Gruppen auflisten |
| `POST` | `/api/groups/` | Neue Gruppe erstellen |
| `GET` | `/api/groups/<id>/` | Gruppendetails abrufen |
| `PATCH` | `/api/groups/<id>/` | Gruppe bearbeiten (Name, Beschreibung, Bild; nur Admin) |
| `DELETE` | `/api/groups/<id>/` | Gruppe löschen (nur Admin) |
| `POST` | `/api/groups/<id>/invite/` | Mitglied per E-Mail einladen (nur Admin) |
| `GET` | `/api/groups/<id>/invite-link/` | Einladungslink/QR-Code für die Gruppe erzeugen (nur Admin) |
| `POST` | `/api/groups/join/` | Gruppe per Einladungstoken beitreten |
| `POST` | `/api/groups/<id>/leave` | Eigene Mitgliedschaft in Gruppe kündigen |
| `DELETE` | `/api/groups/<id>/kick/` | Mitglied aus Gruppe entfernen (nur Admin) |
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
| `PATCH` | `/api/photo-pins/<id>/` | Eigenen Foto-Pin bearbeiten (Beschreibung, Gruppen) |
| `DELETE` | `/api/photo-pins/<id>/` | Eigenen Foto-Pin löschen |

### Strava-Integration

| Methode | Endpunkt | Beschreibung |
|---|---|---|
| `GET` | `/api/strava/status/` | Verbindungsstatus zu Strava abrufen |
| `GET` | `/api/strava/connect/` | OAuth-URL abrufen |
| `GET` | `/api/strava/callback/` | OAuth-Callback (speichert Tokens) |
| `GET` | `/api/strava/activities/` | Strava-Aktivitäten des Nutzers abrufen |
| `POST` | `/api/strava/activities/<id>/import/` | Einzelne Strava-Aktivität als Route importieren |
