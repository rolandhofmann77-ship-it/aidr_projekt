import { useEffect, useState } from "react"

function App() {
  const [backendStatus, setBackendStatus] = useState("Verbinde mit Backend...")
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadMessage, setUploadMessage] = useState("")
  const [extractedPages, setExtractedPages] = useState<
    { page: number; text: string }[]
  >([])
  const [question, setQuestion] = useState("")
  const [selectedDocumentId, setSelectedDocumentId] = useState<number | null>(null)
  const [answer, setAnswer] = useState("")
  const [sources, setSources] = useState<
    {
      document_id: number
      filename: string
      page: number
      distance: number
    }[]
  >([])
  const [documents, setDocuments] = useState<
    {
      id: number
      filename: string
      content_type: string
      uploaded_at: string
    }[]
  >([])

  useEffect(() => {
    fetch("http://127.0.0.1:8000/health")
      .then((response) => response.json())
      .then((data) => {
        setBackendStatus(data.status)
      })
      .catch(() => {
        setBackendStatus("Backend nicht erreichbar")
      })
  }, [])

  useEffect(() => {
    fetch("http://127.0.0.1:8000/documents")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Dokumente konnten nicht geladen werden")
        }

        return response.json()
      })
      .then((data) => {
        setDocuments(data)
      })
      .catch(() => {
        setDocuments([])
      })
  }, [])

  const handleFileChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0] ?? null

    setSelectedFile(file)
    setUploadMessage("")
    setExtractedPages([])
  }

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadMessage("Bitte zuerst eine Datei auswählen.")
      return
    }

    const formData = new FormData()
    formData.append("file", selectedFile)

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/documents",
        {
          method: "POST",
          body: formData,
        }
      )

      if (!response.ok) {
        throw new Error("Upload fehlgeschlagen")
      }

      const data = await response.json()

      setExtractedPages(data.pages ?? [])

      const documentsResponse = await fetch(
        "http://127.0.0.1:8000/documents"
      )

      if (!documentsResponse.ok) {
        throw new Error("Dokumente konnten nicht aktualisiert werden")
      }

      const documentsData = await documentsResponse.json()

      setDocuments(documentsData)

      setUploadMessage(
        `Upload erfolgreich: ${data.filename} (${data.size} Bytes)`
      )
    } catch {
      setUploadMessage("Upload fehlgeschlagen.")
    }
  }

  const handleDeleteDocument = async (documentId: number) => {
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/documents/${documentId}`,
        {
          method: "DELETE",
        }
      )

      if (!response.ok) {
        throw new Error("Dokument konnte nicht gelöscht werden")
      }

      setDocuments((currentDocuments) =>
        currentDocuments.filter(
          (document) => document.id !== documentId
        )
      )
    } catch {
      alert("Dokument konnte nicht gelöscht werden.")
    }
  }

  const handleAsk = async () => {
    if (!question.trim()) {
      setAnswer("Bitte zuerst eine Frage eingeben.")
      return
    }

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/ask",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            question: question,
            document_id: selectedDocumentId,
          }),
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail ?? "Frage konnte nicht verarbeitet werden."
        )
      }

      setAnswer(data.answer)
      setSources(data.sources ?? [])

    } catch (error) {
      if (error instanceof Error) {
        setAnswer(error.message)
      } else {
        setAnswer("Frage konnte nicht verarbeitet werden.")
      }

      setSources([])
    }
  }
  
  return (
    <div>
      <header>
        <h1>AIDR – AI Document Assistant</h1>
        <p>Dokumente hochladen und Fragen mit KI beantworten lassen.</p>
      </header>

      <main>
        <section>
          <h2>Dokumente</h2>

          <input
            type="file"
            accept=".pdf,.docx"
            onChange={handleFileChange}
          />

          {selectedFile && (
            <p>Ausgewählt: {selectedFile.name}</p>
          )}

          <button onClick={handleUpload}>
            Dokument hochladen
          </button>

          {uploadMessage && (
            <p>{uploadMessage}</p>
          )}
        </section>

        <section>
          <h2>Meine Dokumente</h2>

          {documents.length === 0 ? (
            <p>Keine Dokumente vorhanden.</p>
          ) : (
            <ul>
              {documents.map((document) => (
                <li key={document.id}>
                  <strong>{document.filename}</strong>
                  {" – "}
                  {new Date(document.uploaded_at).toLocaleString("de-DE")}
                  {" "}
                  <button
                    onClick={() => handleDeleteDocument(document.id)}
                  >
                    Löschen
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>
        
        {extractedPages.length > 0 && (
          <section>
            <h2>Extrahierter Text</h2>

            {extractedPages.map((page) => (
              <div key={page.page}>
                <h3>Seite {page.page}</h3>
                <pre>{page.text}</pre>
              </div>
            ))}
          </section>
        )}

        <section>
          <h2>Frage an die Dokumente</h2>

          <div>
            <label htmlFor="document-select">
              Dokument
            </label>

            <select
              id="document-select"
              value={selectedDocumentId ?? ""}
              onChange={(event) => {
                const value = event.target.value

                setSelectedDocumentId(
                  value === "" ? null : Number(value)
                )
              }}
            >
              <option value="">
                Alle Dokumente
              </option>

              {documents.map((document) => (
                <option
                  key={document.id}
                  value={document.id}
                >
                  {document.filename}
                </option>
              ))}
            </select>
          </div>

          <input
            type="text"
            placeholder="Stelle eine Frage zu deinen Dokumenten..."
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
          />
          
          <button onClick={handleAsk}>
            Frage stellen
          </button>
        </section>

        <section>
          <h2>Antwort</h2>

          {answer ? (
            <>
              <p>{answer}</p>

              {sources.length > 0 && (
                <div>
                  <h3>Quellen</h3>

                  {sources.map((source, index) => (
                    <div key={index}>
                      <div>📄 {source.filename}</div>
                      <div>Seite {source.page}</div>
                    </div>
                  ))}
                </div>
              )}
            </>
          ) : (
            <p>Noch keine Antwort vorhanden.</p>
          )}
        </section>

        <section>
          <h2>Systemstatus</h2>
          <p>Backend: {backendStatus}</p>
        </section>
      </main>
    </div>
  )
}

export default App
