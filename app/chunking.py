"""Split documents into pieces small enough to embed and to fit in a prompt."""


def chunk_text(text: str, max_chars: int = 800) -> list[str]:
    """Group paragraphs into chunks of at most max_chars.

    A paragraph longer than max_chars is cut into max_chars slices.
    """
    chunks: list[str] = []
    current = ""
    for para in (p.strip() for p in text.split("\n\n")):
        if not para:
            continue
        while len(para) > max_chars:
            if current:
                chunks.append(current)
                current = ""
            chunks.append(para[:max_chars])
            para = para[max_chars:]
        if current and len(current) + 2 + len(para) > max_chars:
            chunks.append(current)
            current = para
        else:
            current = f"{current}\n\n{para}" if current else para
    if current:
        chunks.append(current)
    return chunks
