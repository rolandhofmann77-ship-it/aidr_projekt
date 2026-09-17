import { useEffect, useState } from "react"

function App() {
  const [backendStatus, setBackendStatus] = useState("Verbinde mit Backend...")
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadMessage, setUploadMessage] = useState("")
  const [extractedPages, setExtractedPages] = useState<
    { page: number; text: string }[]
  >([])
  const [question, setQuestion] = useState("")
  const [answer, setAnswer] = useState("")
  const [sources, setSources] = useState<
    { document_id: number; page: number; distance: number }[]
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

      setUploadMessage(
        `Upload erfolgreich: ${data.filename} (${data.size} Bytes)`
      )
    } catch {
      setUploadMessage("Upload fehlgeschlagen.")
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
          }),
        }
      )

      if (!response.ok) {
        throw new Error("Frage konnte nicht verarbeitet werden")
      }

      const data = await response.json()

      setAnswer(data.answer)
      setSources(data.sources ?? [])
    } catch {
      setAnswer("Die Frage konnte nicht verarbeitet werden.")
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

                  <ul>
                    {sources.map((source, index) => (
                      <li key={index}>
                        Dokument {source.document_id} – Seite {source.page}
                      </li>
                    ))}
                  </ul>
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
