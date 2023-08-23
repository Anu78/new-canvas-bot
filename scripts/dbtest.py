from db_api import Database
import asyncio

class Backend(Database):
    async def getUserInfo(self, userid):
        query = f"select auth_token,canvasid from users where userid={userid}"
        try:
            db = await self.open()
            async with db.execute(query) as cursor:
                result = await cursor.fetchone()
            return result
        except Exception as e:
            return e
        finally:
            await self.close(db)

async def main():
    backend = Backend()

    test = await backend.getUserInfo(userid=492179045379866634)

    print(test)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())