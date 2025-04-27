import sqlite3
import plotly.graph_objects as go

def query_scriptures(word, case_sensitive=False, db_path="scriptures.db"):
    """
    Query the scriptures database for verses containing any of the words,
    with optional case sensitivity. Words are separated by commas.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Split input by commas, strip whitespace, and ignore empty terms
    words = [w.strip() for w in word.split(",") if w.strip()]
    if not words:
        return []

    # Build dynamic WHERE clause
    if case_sensitive:
        # Use GLOB for case-sensitive search
        conditions = " OR ".join(["verse_text GLOB ?"] * len(words))
        params = [f"*{w}*" for w in words]
    else:
        # Use LIKE for case-insensitive search
        conditions = " OR ".join(["verse_text LIKE ?"] * len(words))
        params = [f"%{w}%" for w in words]

    query = f"""
        SELECT volume, book, chapter, verse_number, verse_text
        FROM verses
        WHERE {conditions}
    """
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return results

def create_visual(results):
    """Create a bar chart of verse counts by volume using Plotly."""
    from collections import Counter
    volumes = [row[0] for row in results]  # volume is now at index 0
    counts = Counter(volumes)
    fig = go.Figure(
        data=[go.Bar(x=list(counts.keys()), y=list(counts.values()))]
    )
    fig.update_layout(
        xaxis_title="Volume",
        yaxis_title="Verse Count",
        title="Occurrences by Volume",
        xaxis_tickangle=-45,
        margin=dict(b=120)
    )
    return fig
