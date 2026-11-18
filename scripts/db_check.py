import asyncio

from sqlalchemy import text

from securecodecoach.db.session import engine


async def main():
    async with engine.connect() as connection:
        result = await connection.execute(text("SELECT current_database(), version()"))
        database_name, version = result.one()

        print(f"Connected to database '{database_name}'")
        print(version)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
