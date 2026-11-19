from sqlalchemy.engine import make_url


def to_async_database_url(database_url: str) -> str:
    """Convert a PostgreSQL URL into an asyncpg-compatible URL."""
    url = make_url(database_url)
    if url.drivername in {"postgres", "postgresql"}:
        url = url.set(drivername="postgresql+asyncpg")
    query = dict(url.query)
    query.pop("sslmode", None)
    query.pop("ssl", None)
    query.pop("channel_binding", None)
    url = url.set(query=query)
    return url.render_as_string(hide_password=False)


def get_connect_args(database_url: str) -> dict:
    """Return asyncpg connect_args based on URL query or host."""
    url = make_url(database_url)
    ssl_val = url.query.get("sslmode") or url.query.get("ssl")
    if ssl_val == "disable" or url.host in {"localhost", "127.0.0.1", "db"}:
        return {"ssl": False}
    if ssl_val:
        return {"ssl": "require" if ssl_val == "require" else ssl_val}
    return {"ssl": "require"}
