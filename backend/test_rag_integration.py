from backend.rag import answer_question


TEST_DOCUMENT_ID = 9
TEST_QUESTION = "Welcher Eigenanteil ist bei einer Projektarbeit gefordert?"


def main():
    print("Starte vollständigen RAG-Integrationstest...")
    print(f"Dokument-ID: {TEST_DOCUMENT_ID}")
    print(f"Frage: {TEST_QUESTION}")
    print()

    result = answer_question(
        TEST_QUESTION,
        TEST_DOCUMENT_ID,
    )

    assert result["question"] == TEST_QUESTION
    assert isinstance(result["answer"], str)
    assert result["answer"].strip() != ""

    assert isinstance(result["sources"], list)
    assert len(result["sources"]) > 0
    assert len(result["sources"]) <= 3

    for source in result["sources"]:
        assert source["document_id"] == TEST_DOCUMENT_ID
        assert isinstance(source["filename"], str)
        assert source["filename"].strip() != ""
        assert isinstance(source["page"], int)
        assert source["page"] >= 1

    print("TEST BESTANDEN")
    print()
    print("Antwort:")
    print(result["answer"])
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