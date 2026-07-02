# Velotag

Velotag ist eine Cross-Platform-App für Radsportler, deren Kernfunktion die **Heatmap gefahrener Routen** ist. Jeder Nutzer sieht auf einer interaktiven Karte eine Heatmap aller eigenen Radstrecken – je öfter eine Strecke gefahren wurde, desto intensiver erscheint sie. Über die **Gruppenfunktion** können sich Radfahrer zusammenschließen und eine gemeinsame Gruppen-Heatmap aller Mitglieder einsehen, um zu sehen, welche Strecken die Gruppe als Ganzes zurückgelegt hat. Routen werden per GPX-Upload oder Strava-Import hinzugefügt und stehen als Web- sowie native iOS/Android-App zur Verfügung.

---

## Inhaltsverzeichnis

- [Architektur](#architektur)
- [Tech-Stack](#tech-stack)
- [Projektstruktur](#projektstruktur)
- [Voraussetzungen](#voraussetzungen)
- [Installation & Start](#installation--start)
  - [Backend](#backend)
  - [Frontend](#frontend)
  - [Schnellstart (Windows)](#schnellstart-windows)
  - [Mobile (iOS / Android)](#mobile-ios--android)
- [Umgebungsvariablen](#umgebungsvariablen)
- [API-Referenz](#api-referenz)
- [Features](#features)

---

## Architektur

```
┌─────────────────────────────────────┐
│  Frontend  (Vue 3 + Vite)           │
│  Web  ·  iOS  ·  Android            │
└────────────────┬────────────────────┘
                 │ REST / Token Auth
┌────────────────▼────────────────────┐
│  Backend  (Django REST Framework)   │
└────────────────┬────────────────────┘
                 │ ORM
┌────────────────▼────────────────────┐
│  PostgreSQL  (SQLite im Dev-Modus)  │
└─────────────────────────────────────┘
```

---

## Tech-Stack

| Bereich | Technologie |
|---|---|
| Frontend | Vue 3 (Composition API), Vite, Pinia, Vue Router |
| Karte | Leaflet + OpenStreetMap |
| HTTP-Client | Axios |
| Mobile | Capacitor 8 (iOS & Android) |
| Backend | Django 5, Django REST Framework 3 |
| Datenbank | PostgreSQL (Produktion), SQLite (Entwicklung) |
| Auth | DRF Token Authentication |
| Bildverarbeitung | Pillow |
| Produktionsserver | Gunicorn |
| Drittanbieter | Strava OAuth 2 |

---

## Projektstruktur

```
velotag/
├── backend/
│   ├── core/                  # Django-Einstellungen, Haupt-URL-Router, Strava-Views
│   ├── users/                 # Benutzerverwaltung (Profil, Login, Register, Logout)
│   ├── routes/                # Routen-App (GPX-Upload, Polyline-Speicherung)
│   ├── groups/                # Gruppen-App (Mitglieder, Einladungen)
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/               # Axios-Instanz mit Token-Interceptor
│   │   ├── components/        # MenuBar, Profil-, Gruppen-, GPX-Komponenten
│   │   ├── composables/       # GPX-Parser, Karten-Rendering
│   │   ├── router/            # Vue Router-Konfiguration
│   │   ├── store/             # Pinia User-Store
│   │   └── views/             # Karte, Login/Register
│   ├── android/               # Capacitor Android-Projekt
│   ├── ios/                   # Capacitor iOS-Projekt
│   ├── vite.config.js
│   └── package.json
├── start_server.bat           # Windows-Schnellstart (Backend + Frontend)
└── README.md
```

---

## Voraussetzungen

- **Python** 3.10+
- **Node.js** 20.19+ oder 22.12+
- **PostgreSQL** (für Produktion; Entwicklung läuft auch mit SQLite)
- Optional: **Android Studio** (Android-Build), **Xcode** (iOS-Build)

---

## Installation & Start

### Backend

```bash
cd backend

# Virtuelle Umgebung erstellen und aktivieren
python -m venv venv-windows          # Windows
.\venv-windows\Scripts\activate

# python -m venv venv               # Linux / macOS
# source venv/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt

# Datenbankmigrationen ausführen
python manage.py migrate

# (Optional) Admin-Benutzer anlegen
python manage.py createsuperuser

# Entwicklungsserver starten
python manage.py runserver           # http://localhost:8000
```

### Frontend

```bash
cd frontend

# Abhängigkeiten installieren
npm install

# Entwicklungsserver starten
npm run dev                          # http://localhost:5173

# Produktions-Build erstellen
npm run build

# Produktions-Build lokal vorschauen
npm run preview
```

### Schnellstart (Windows)

Das Skript `start_server.bat` im Projektstamm startet Backend und Frontend gleichzeitig in zwei Terminal-Fenstern:

```bat
start_server.bat
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

## Umgebungsvariablen

Lege die Datei `backend/.env` mit folgenden Werten an:

```env
# Django
SECRET_KEY=dein-geheimer-schlüssel

# Strava OAuth 2
STRAVA_CLIENT_ID=deine-client-id
STRAVA_CLIENT_SECRET=dein-client-secret

# PostgreSQL (nur für Produktion erforderlich)
DB_NAME=velotag_db
DB_USER=postgres
DB_PASSW=dein-passwort
DB_HOST=localhost
DB_PORT=5432
```

> Im Entwicklungsmodus wird automatisch SQLite verwendet, wenn keine PostgreSQL-Zugangsdaten angegeben sind.

---

## API-Referenz

Alle Endpunkte erfordern (sofern nicht anders angegeben) den HTTP-Header:
```
Authorization: Token <dein-token>
```

### Authentifizierung

| Methode | Endpunkt | Beschreibung |
|---|---|---|
| `POST` | `/api/register/` | Registrierung (E-Mail, Passwort, Name) |
| `POST` | `/api/login/` | Anmeldung → gibt Auth-Token zurück |
| `POST` | `/api/logout/` | Abmeldung (löscht Token) |
| `GET` | `/api/profil/` | Eigenes Profil abrufen |
| `PATCH` | `/api/profil/` | Profil aktualisieren (Name, E-Mail, Passwort, Bild) |

### Routen

| Methode | Endpunkt | Beschreibung |
|---|---|---|
| `POST` | `/api/routes/create/` | Route hochladen (GPX-Daten) |
| `GET` | `/api/routes/read/` | Alle eigenen Routen abrufen |

**Felder für `POST /api/routes/create/`:**

| Feld | Typ | Beschreibung |
|---|---|---|
| `strecken_name` | string | Name der Route |
| `polyline_map` | string | Google-codierte Polyline der Koordinaten |
| `puls_stream` | array | Herzfrequenz-Datenpunkte |
| `zeit_stream` | array | Zeitstempel |
| `watt_stream` | array | Leistungsdaten (Watt) |

### Gruppen

| Methode | Endpunkt | Beschreibung |
|---|---|---|
| `GET` | `/api/groups/` | Eigene Gruppen auflisten |
| `POST` | `/api/groups/` | Neue Gruppe erstellen |
| `GET` | `/api/groups/<id>/` | Gruppendetails abrufen |
| `DELETE` | `/api/groups/<id>/` | Mitglied entfernen (nur Admin) |
| `POST` | `/api/groups/<id>/invite/` | Mitglied per E-Mail einladen (nur Admin) |
| `GET` | `/api/user/invitations/` | Offene Einladungen abrufen |
| `POST` | `/api/user/invitations/` | Einladung annehmen oder ablehnen |

### Strava-Integration

| Methode | Endpunkt | Beschreibung |
|---|---|---|
| `GET` | `/api/strava/connect/` | OAuth-URL abrufen |
| `GET` | `/api/strava/callback/` | OAuth-Callback (speichert Tokens) |
| `GET` | `/api/strava/activities/` | Strava-Aktivitäten des Nutzers abrufen |

---

## Features

- **Interaktive Karte** – Leaflet-Karte mit OpenStreetMap-Kacheln; Routen werden als farbige Polylines dargestellt
- **GPX-Upload** – Drag-and-Drop-Upload mit automatischer Validierung (nur Radaktivitäten), Koordinaten-Extraktion und Google-Polyline-Codierung
- **Leistungsdaten** – Herzfrequenz, Watt und Zeitstempel werden pro Route gespeichert und visualisiert
- **Strava-Import** – OAuth-2-Anbindung zum Importieren vorhandener Aktivitäten aus Strava
- **Gruppen & Einladungen** – Gruppen erstellen, Mitglieder per E-Mail einladen, Einladungen annehmen/ablehnen, Mitglieder als Admin entfernen
- **Benutzerprofil** – Profilbild, Name und E-Mail jederzeit bearbeitbar
- **Cross-Platform** – Gleiche Codebasis läuft als Web-App sowie als native iOS- und Android-App über Capacitor
