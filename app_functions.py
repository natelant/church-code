import sqlite3
import plotly.graph_objects as go

def query_scriptures(word, case_sensitive=False, db_path="db_scriptures.db", return_per_word=False):
    """
    Query the scriptures database for verses containing any of the words,
    with optional case sensitivity. Words are separated by commas.
    If return_per_word is True, returns a dict: {word: [results]}.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    words = [w.strip() for w in word.split(",") if w.strip()]
    if not words:
        return {} if return_per_word else []

    if return_per_word:
        results = {}
        for w in words:
            if case_sensitive:
                cursor.execute(
                    "SELECT volume, book, chapter, verse_number, verse_text FROM verses WHERE verse_text GLOB ?",
                    (f"*{w}*",)
                )
            else:
                cursor.execute(
                    "SELECT volume, book, chapter, verse_number, verse_text FROM verses WHERE verse_text LIKE ?",
                    (f"%{w}%",)
                )
            results[w] = cursor.fetchall()
        conn.close()
        return results
    else:
        if case_sensitive:
            conditions = " OR ".join(["verse_text GLOB ?"] * len(words))
            params = [f"*{w}*" for w in words]
        else:
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

def create_visual(results, comparison=False):
    """
    Create a bar chart of verse counts by volume using Plotly.
    If comparison=True, results should be a dict {word: [rows]}.
    """
    from collections import Counter
    import plotly.graph_objects as go

    if comparison:
        # results: {word: [rows]}
        volumes = set()
        word_counts = {}
        for word, rows in results.items():
            counts = Counter(row[0] for row in rows)  # row[0] is volume
            word_counts[word] = counts
            volumes.update(counts.keys())
        volumes = sorted(volumes)
        fig = go.Figure()
        for word, counts in word_counts.items():
            y = [counts.get(v, 0) for v in volumes]
            fig.add_bar(x=volumes, y=y, name=word)
        fig.update_layout(
            barmode='group',
            xaxis_title="Volume",
            yaxis_title="Verse Count",
            title="Occurrences by Volume (Comparison)",
            xaxis_tickangle=-45,
            margin=dict(b=120)
        )
        return fig
    else:
        # results: list of rows
        volumes = [row[0] for row in results]
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
