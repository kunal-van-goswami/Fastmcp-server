from fastmcp import FastMCP
from contextlib import asynccontextmanager
import os
import aiosqlite
import tempfile

TEMP_DIR = tempfile.gettempdir()
DB_PATH = os.path.join(TEMP_DIR, "expenses.db")
CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")

print(f"Database path: {DB_PATH}")

mcp = FastMCP(name="Expense Tracker")


async def init_db():
    """Initialize the SQLite database."""
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute("PRAGMA journal_mode=WAL")

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                date TEXT NOT NULL,
                category TEXT,
                subcategory TEXT,
                note TEXT
            )
        """)

        await conn.commit()


@mcp.tool()
async def add_expense(
    date: str,
    amount: float,
    description: str,
    category: str,
    subcategory: str = "",
    note: str = ""
):
    """Add a new expense entry to the database."""

    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            """
            INSERT INTO expenses
            (description, amount, date, category, subcategory, note)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (description, amount, date, category, subcategory, note)
        )

        await conn.commit()

        expense_id = cursor.lastrowid

    return {
        "status": "ok",
        "id": expense_id
    }


@mcp.tool()
async def list_expenses(
    start_date: str,
    end_date: str
):
    """List all expense entries within a date range."""

    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row

        cursor = await conn.execute(
            """
            SELECT
                id,
                date,
                amount,
                description,
                category,
                subcategory,
                note
            FROM expenses
            WHERE date BETWEEN ? AND ?
            ORDER BY date ASC
            """,
            (start_date, end_date)
        )

        rows = await cursor.fetchall()

    #return [dict(row) for row in rows]
    


@mcp.tool()
async def summarize(
    start_date: str,
    end_date: str,
    category: str = None
):
    """Summarize expenses by category and subcategory."""

    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row

        query = """
            SELECT
                category,
                subcategory,
                SUM(amount) AS total_amount
            FROM expenses
            WHERE date BETWEEN ? AND ?
        """

        params = [start_date, end_date]

        if category:
            query += " AND category = ?"
            params.append(category)

        query += """
            GROUP BY category, subcategory
            ORDER BY total_amount ASC
        """

        cursor = await conn.execute(query, params)
        rows = await cursor.fetchall()
 
    if not rows:
        return {
            "status": "ok",
            "message": "No expenses found for this date range.",
            "expenses": []
        }

    return {
        "status": "ok",
        "count": len(rows),
        "expenses": [dict(row) for row in rows]
    }
    #return [dict(row) for row in rows]


async def main():
    # Initialize database before starting MCP server
    await init_db()

    # Start FastMCP server
    await mcp.run_async(
        transport="http",
        host="0.0.0.0",
        port=8000
    )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())