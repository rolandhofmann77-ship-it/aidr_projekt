# AIDR – AI Document Retrieval Assistant

AIDR ist ein KI-gestützter Dokumentenassistent, der Informationen aus hochgeladenen PDF- und DOCX-Dokumenten mittels Retrieval-Augmented Generation (RAG) verarbeitet und auf natürlich formulierte Fragen dokumentenbasierte Antworten mit Quellenangaben liefert.

## Funktionen

* Upload und Verarbeitung von PDF- und DOCX-Dokumenten
* Extraktion und Aufteilung von Dokumenttext in Chunks
* Erzeugung lokaler Text-Embeddings
* Speicherung der Embeddings mit PostgreSQL und pgvector
* Semantische Suche nach relevanten Dokumentinhalten
* Beantwortung von Fragen mit Google Gemini
* Anzeige der verwendeten Dokumente und Seiten als Quellen
* Auswahl eines einzelnen Dokuments oder Suche über alle Dokumente
* Dokumentverwaltung und Löschen von Dokumenten
* Fehlerbehandlung und Retry bei temporären KI-Dienstfehlern

## Architektur

```text
                ┌─────────────────────┐
                │      Frontend       │
                │ React / TypeScript  │
                │       / Vite        │
                └──────────┬──────────┘
                           │
                           │ REST API
                           ▼
                ┌─────────────────────┐
                │       Backend       │
                │ FastAPI / Python    │
                └──────────┬──────────┘
                           │
             ┌─────────────┴─────────────┐
             │                           │
             ▼                           ▼
    ┌─────────────────┐         ┌─────────────────┐
    │   PostgreSQL    │         │   Google Gemini │
    │    + pgvector   │         │       LLM       │
    └─────────────────┘         └─────────────────┘
```

Der RAG-Ablauf besteht vereinfacht aus:

```text
Dokument
   ↓
Textextraktion
   ↓
Chunking
   ↓
Embedding
   ↓
PostgreSQL / pgvector
   ↓
Benutzerfrage
   ↓
Embedding der Frage
   ↓
Semantische Suche
   ↓
Relevante Chunks
   ↓
Gemini
   ↓
Antwort + Quellen
```

## Technologie-Stack

| Bereich           | Technologie             |
| ----------------- | ----------------------- |
| Backend           | Python, FastAPI         |
| Frontend          | React, TypeScript, Vite |
| Datenbank         | PostgreSQL              |
| Vektorsuche       | pgvector                |
| Embeddings        | Sentence Transformers   |
| Sprachmodell      | Google Gemini           |
| Dokumente         | PDF, DOCX               |
| Containerisierung | Docker                  |

## Voraussetzungen

Für die lokale Entwicklung werden unter anderem benötigt:

* Python
* Node.js / npm
* Docker Desktop
* PostgreSQL mit pgvector (wird über Docker bereitgestellt)
* ein Google-Gemini-API-Key

## Konfiguration

Die benötigten Umgebungsvariablen sind in `.env.example` beschrieben.

Eine lokale `.env`-Datei muss angelegt werden und darf **nicht** in das Repository eingecheckt werden.

Beispiel:

```env
GEMINI_API_KEY=DEIN_GEMINI_API_KEY

DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=aidr
DB_USER=aidr
DB_PASSWORD=DEIN_DB_PASSWORT
```

## Tests

Das Projekt enthält aktuell automatisierte Tests für verschiedene Ebenen:

```text
backend/test_rag.py
→ Test der Textaufteilung / Chunking

backend/test_rag_integration.py
→ End-to-End-Test des RAG-Ablaufs

backend/test_rag_quality.py
→ Prüfung von Antwortqualität und Quellen
```

Zusätzlich wurde das System manuell mit unterschiedlichen Eingaben und Fehlerfällen getestet, unter anderem:

* leere Fragen
* unbekannte Dokument-ID
* nicht beantwortbare Fragen
* Tippfehler
* semantisch umformulierte Fragen
* Dokument-Isolation
* ungültige Dateiformate
* leere PDF-Dateien
* beschädigte PDF-Dateien
* beschädigte DOCX-Dateien
* temporäre Fehler des KI-Dienstes

## Sicherheit

API-Schlüssel und lokale Zugangsdaten werden über Umgebungsvariablen bereitgestellt.

Hochgeladene Dokumente und lokale Konfigurationsdateien werden nicht Bestandteil des öffentlichen GitHub-Repositories.

## Projektstatus

Das grundlegende System ist funktionsfähig. Die Kernkomponenten für Dokumentverarbeitung, semantische Suche, RAG und Quellenangaben sind implementiert.

Aktuell liegt der Schwerpunkt auf weiteren Quality-Tests, Fehlerbehandlung, Benutzeroberfläche, Dokumentation und abschließender Projektbereinigung.

## Lizenz

Dieses Repository wurde als Entwicklungs- und Projektarbeits-Repository erstellt. Eine konkrete Lizenz kann bei Bedarf ergänzt werden.
