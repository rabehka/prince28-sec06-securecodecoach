from sqlalchemy.engine import make_url


def to_async_database_url(database_url: str) -> str:
    """Convert a PostgreSQL URL into an asyncpg-compatible URL."""
    url = make_url(database_url)

    if url.drivername in {"postgres", "postgresql"}:
        url = url.set(drivername="postgresql+asyncpg")

    query = dict(url.query)

    sslmode = query.pop("sslmode", None)
    query.pop("channel_binding", None)

    url = url.set(query=query)

    connect_args = {}
    if sslmode:
        connect_args["ssl"] = "require" if sslmode == "require" else sslmode

    return url.render_as_string(hide_password=False)
