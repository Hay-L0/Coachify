def chunk_text(
    text,
    chunk_size=300,
    overlap=50,
):
    if not text:
        return []

    words = text.split()

    if not words:
        return []

    chunks = []

    start = 0

    while start < len(words):

        end = min(
            start + chunk_size,
            len(words),
        )

        chunk = " ".join(
            words[start:end]
        ).strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(words):
            break

        start = end - overlap

    return chunks