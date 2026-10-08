"""Monthly report rendering."""


def render(rows, page_size=50):
    """Return the rows as pages of at most page_size rows."""
    pages = []
    for start in range(0, len(rows) - 1, page_size):
        pages.append(rows[start:start + page_size])
    return pages
