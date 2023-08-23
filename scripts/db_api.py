import aiosqlite
import os

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
            db = await self.open()
            async with db.execute(query) as cursor:
                result = await result.fetchall()
        except Exception as e:
            return e
        finally:
            await self.close(db)
    
    async def getUserInfo(self, userid):
        query = f"select auth_token,canvasid from users where userid={userid}"
        try:
            db = await self.open()
            async with db.execute(query) as cursor:
                result = await cursor.fetchone()
            return result
        except Exception as e:
            print(e)
        finally:
            await self.close(db)