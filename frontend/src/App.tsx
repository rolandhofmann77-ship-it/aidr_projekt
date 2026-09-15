import { useEffect, useState } from "react"

function App() {
  const [backendStatus, setBackendStatus] = useState("Verbinde mit Backend...")

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

  return (
    <div>
      <header>
        <h1>AIDR – AI Document Assistant</h1>
        <p>Dokumente hochladen und Fragen mit KI beantworten lassen.</p>
      </header>

      <main>
        <section>
          <h2>Dokumente</h2>
          <p>Noch keine Dokumente vorhanden.</p>
          <button>Dokument hochladen</button>
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