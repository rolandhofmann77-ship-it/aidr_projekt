from backend.main import chunk_text


test_text = """
Das Projekt verwendet Python und FastAPI für das Backend. Das Backend stellt eine REST-Schnittstelle bereit und übernimmt die Verarbeitung der hochgeladenen Dokumente. Außerdem werden die Fragen der Benutzer entgegengenommen und an die RAG-Komponente weitergeleitet.

Das Frontend wird mit React, TypeScript und Vite umgesetzt. Die Benutzeroberfläche ermöglicht das Hochladen von Dokumenten, die Anzeige vorhandener Dokumente und das Stellen von Fragen. Die Antworten des Systems werden anschließend zusammen mit den gefundenen Quellen angezeigt.

Für die Datenhaltung wird PostgreSQL mit pgvector verwendet. PostgreSQL speichert die Dokumente und die daraus erzeugten Textabschnitte. Die Embeddings werden als Vektoren gespeichert und können anschließend für eine semantische Suche verwendet werden.

Die Dokumente werden automatisch verarbeitet und in kleinere Textabschnitte aufgeteilt. Dabei sollen möglichst zusammenhängende Inhalte gemeinsam in einem Chunk gespeichert werden. Zu große Textabschnitte werden an geeigneten Absatzgrenzen aufgeteilt.

Anschließend werden für die Textabschnitte Embeddings erzeugt und in der Datenbank gespeichert. Jeder Chunk erhält dadurch eine numerische Repräsentation seines Inhalts. Diese Repräsentation kann später mit dem Embedding einer Benutzerfrage verglichen werden.

Über eine semantische Suche werden passende Textabschnitte zu einer Benutzerfrage gefunden. Dazu wird zunächst ein Embedding für die Frage erzeugt. Anschließend werden die gespeicherten Embeddings verglichen und die inhaltlich ähnlichsten Textabschnitte ausgewählt.

Die gefundenen Textabschnitte werden anschließend als Kontext an das Sprachmodell übergeben. Das Sprachmodell soll die Frage ausschließlich anhand dieses bereitgestellten Kontextes beantworten. Dadurch soll verhindert werden, dass Antworten unabhängig vom Inhalt der hochgeladenen Dokumente erzeugt werden.

Das System soll außerdem die verwendeten Quellen zurückgeben. Dadurch kann der Benutzer nachvollziehen, aus welchen Dokumenten und Textabschnitten die Antwort abgeleitet wurde.

Für die spätere Benutzeroberfläche sind verschiedene Funktionen vorgesehen. Dazu gehören die Dokumentverwaltung, die Anzeige des Upload-Status, ein Eingabefeld für Fragen und die Darstellung der generierten Antworten. Die Oberfläche soll zunächst funktional umgesetzt und später optisch verbessert werden.
"""


chunks = chunk_text(test_text)

print(f"Anzahl Chunks: {len(chunks)}")

for index, chunk in enumerate(chunks, start=1):
    print()
    print(f"--- Chunk {index} ---")
    print(f"Länge: {len(chunk)} Zeichen")
    print(chunk)