import sqlite3
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px

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

def create_visual(results, comparison=False, volume=None):
    """
    If volume is None: show occurrences by volume.
    If volume is set: show occurrences by book within that volume.
    """
    from collections import Counter
    import plotly.graph_objects as go

    if comparison:
        if volume is None or volume == "All Volumes":
            # Show occurrences by volume for each word
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
                title="Occurrences in Scripturesby Volume (Comparison)",
                xaxis_tickangle=-45,
                margin=dict(b=120)
            )
            return fig
        else:
            # Show occurrences by book within the selected volume for each word
            books = set()
            word_counts = {}
            for word, rows in results.items():
                filtered_rows = [row for row in rows if row[0] == volume]
                counts = Counter(row[1] for row in filtered_rows)  # row[1] is book
                word_counts[word] = counts
                books.update(counts.keys())
            books = sorted(books)
            fig = go.Figure()
            for word, counts in word_counts.items():
                y = [counts.get(b, 0) for b in books]
                fig.add_bar(x=books, y=y, name=word)
            fig.update_layout(
                barmode='group',
                xaxis_title="Book",
                yaxis_title="Verse Count",
                title=f"Occurrences in {volume} by Book (Comparison)",
                xaxis_tickangle=-45,
                margin=dict(b=120)
            )
            return fig
    else:
        if volume is None:
            # Show occurrences by volume
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
        else:
            # Show occurrences by book within the selected volume
            books = [row[1] for row in results if row[0] == volume]
            counts = Counter(books)
            fig = go.Figure(
                data=[go.Bar(x=list(counts.keys()), y=list(counts.values()))]
            )
            fig.update_layout(
                xaxis_title="Book",
                yaxis_title="Verse Count",
                title=f"Occurrences in {volume} by Book",
                xaxis_tickangle=-45,
                margin=dict(b=120)
            )
            return fig

def query_conference(word, case_sensitive=False, return_per_word=False):
    """
    Query db_conference.db for occurrences of word(s) in body_text, grouped by date_published.
    Returns a dict if return_per_word, else a list of dicts with date, count, and extra info.
    Normalizes months: 03->04, 09->10.
    """
    conn = sqlite3.connect('db_conference.db')
    cursor = conn.cursor()
    words = [w.strip() for w in word.split(",") if w.strip()]
    if not words:
        return {} if return_per_word else []

    def fetch_rows(word_clause, params):
        query = f"""
            SELECT date_published, listed_author, title, author_role
            FROM talks
            WHERE {word_clause}
        """
        cursor.execute(query, params)
        return cursor.fetchall()

    if return_per_word and len(words) > 1:
        results = {}
        for w in words:
            if case_sensitive:
                word_clause = "body_text LIKE ?"
                params = (f"%{w}%",)
            else:
                word_clause = "LOWER(body_text) LIKE ?"
                params = (f"%{w.lower()}%",)
            rows = fetch_rows(word_clause, params)
            results[w] = rows
        conn.close()
        return _normalize_conference_dates(results)
    else:
        # Search for any of the words (OR)
        if case_sensitive:
            conditions = " OR ".join(["body_text LIKE ?"] * len(words))
            params = [f"%{w}%" for w in words]
        else:
            conditions = " OR ".join(["LOWER(body_text) LIKE ?"] * len(words))
            params = [f"%{w.lower()}%" for w in words]
        rows = fetch_rows(conditions, params)
        conn.close()
        return _normalize_conference_dates(rows)

def _normalize_conference_dates(results):
    """
    Normalize months and group by year-month.
    For each date, sum count and collect lists of authors, titles, and roles for hover.
    Adds a formatted date_display and hover_details for custom hover.
    """
    from collections import defaultdict
    import re

    def normalize_ym(date_str):
        match = re.match(r"(\d{4})[-/](\d{2})", date_str)
        if match:
            year, month = match.groups()
            if month == "03":
                month = "04"
            elif month == "09":
                month = "10"
            return f"{year}-{month}"
        return date_str[:7]

    def display_month(ym):
        year, month = ym.split('-')
        if month == "04":
            return f"Apr {year}"
        elif month == "10":
            return f"Oct {year}"
        else:
            return f"{month} {year}"

    def aggregate(data):
        grouped = defaultdict(list)
        for date, listed_author, title, author_role in data:
            ym = normalize_ym(date)
            grouped[ym].append((listed_author, author_role, title))
        result = []
        for ym, talks in sorted(grouped.items()):
            count = len(talks)
            # Use <br> for HTML line breaks
            hover_details = "<br>".join(
                f"{author}, {role}, {title}" for author, role, title in talks
            )
            result.append({
                "date_published": ym,
                "date_display": display_month(ym),
                "count": count,
                "hover_details": hover_details
            })
        return result

    if isinstance(results, dict):
        normed = {}
        for w, data in results.items():
            normed[w] = aggregate(data)
        return normed
    else:
        return aggregate(results)

def create_conference_visual(results, comparison=False, chart_type="line"):
    """
    Create a plotly visual for conference occurrences.
    If comparison=True, results is a dict {word: [dict, ...]}
    Else, results is a list of dicts.
    chart_type: "line" or "bar"
    """
    import plotly.express as px
    import pandas as pd

    chart_func = px.line if chart_type == "line" else px.bar

    if comparison:
        dfs = []
        for word, data in results.items():
            df = pd.DataFrame(data)
            df['word'] = word
            dfs.append(df)
        df_all = pd.concat(dfs)
        # Ensure chronological order for x-axis
        date_order = sorted(df_all['date_display'].unique(), key=lambda d: (
            int(d.split()[1]), 4 if d.startswith("Apr") else 10 if d.startswith("Oct") else 0
        ))
        fig = chart_func(
            df_all,
            x='date_display',
            y='count',
            color='word',
            custom_data=['hover_details'],
            title="Occurrences in General Conference",
            category_orders={"date_display": date_order}
        )
        fig.update_traces(
            hovertemplate=
                "date_published=%{x}<br>" +
                "count=%{y}<br>" +
                "%{customdata[0]}"
        )
    else:
        df = pd.DataFrame(results)
        date_order = sorted(df['date_display'].unique(), key=lambda d: (
            int(d.split()[1]), 4 if d.startswith("Apr") else 10 if d.startswith("Oct") else 0
        ))
        fig = chart_func(
            df,
            x='date_display',
            y='count',
            custom_data=['hover_details'],
            title="Occurrences in General Conference",
            category_orders={"date_display": date_order}
        )
        fig.update_traces(
            hovertemplate=
                "date_published=%{x}<br>" +
                "count=%{y}<br>" +
                "%{customdata[0]}"
        )
    fig.update_layout(xaxis_title="Date Published", yaxis_title="Count")
    return fig
