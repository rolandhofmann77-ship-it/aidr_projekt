import { useEffect, useState } from "react"

function App() {
  const [backendStatus, setBackendStatus] = useState("Verbinde mit Backend...")
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadMessage, setUploadMessage] = useState("")

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

      setUploadMessage(
        `Upload erfolgreich: ${data.filename} (${data.size} Bytes)`
      )
    } catch {
      setUploadMessage("Upload fehlgeschlagen.")
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
          <h2>Frage an die Dokumente</h2>

          <input
            type="text"
            placeholder="Stelle eine Frage zu deinen Dokumenten..."
          />

          <button>Frage stellen</button>
        </section>

        <section>
          <h2>Antwort</h2>
          <p>Hier wird später die Antwort der KI angezeigt.</p>
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