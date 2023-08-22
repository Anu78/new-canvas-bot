import aiosqlite

class Database():
    db = "database.db"

    def __init__(self):
        return
    
    async def open(self):
        return await aiosqlite.connect(self.db)

    async def close(self, connection):
        await connection.close()
    
    async def runQuery(self, query: str):
        try:
            db, cursor = await self.open()
            await cursor.execute(query)
            await self.close(db, cursor)
        except Exception as e:
            return e
        finally:
            await self.close(db, cursor)