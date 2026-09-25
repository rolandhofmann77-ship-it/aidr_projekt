from backend.rag import answer_question


TEST_DOCUMENT_ID = 9
TEST_QUESTION = (
    "Wie viel Zeit steht maximal für die Bearbeitung und Dokumentation "
    "der betrieblichen Projektarbeit zur Verfügung?"
)


def main():
    print("Starte RAG-Qualitätstest...")
    print(f"Dokument-ID: {TEST_DOCUMENT_ID}")
    print(f"Frage: {TEST_QUESTION}")
    print()

    result = answer_question(
        TEST_QUESTION,
        TEST_DOCUMENT_ID,
    )

    answer = result["answer"]

    assert answer.strip() != "", "Die Antwort ist leer."

    assert "80" in answer, (
        "Die erwartete Angabe '80' wurde in der Antwort nicht gefunden."
    )

    assert any(
        source["page"] == 5
        for source in result["sources"]
    ), (
        "Die erwartete Quelle auf Seite 5 wurde nicht gefunden."
    )

    print("TEST BESTANDEN")
    print()
    print("Antwort:")
    print(answer)
    print()
    print("Quellen:")

    for source in result["sources"]:
        print(
            f"- {source['filename']} | "
            f"Seite {source['page']} | "
            f"Distance {source['distance']:.4f}"
        )


if __name__ == "__main__":
    main()