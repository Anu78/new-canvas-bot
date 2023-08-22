import scripts.db_api as db_api
import asyncio

class Backend(db_api.Database):
    # get assignments by userID or courseID
    async def getAssignments(self, userID: int = None, courseID: int = None):
        query = """
            SELECT * FROM assignments
            WHERE
                (userid = ?) OR
                (courseid = ?)
            ORDER BY due_at
            LIMIT 30
        """

        params = (userID, courseID)

        try:
            db = await self.open()
            async with db.execute(query, params) as cursor:
                result = await cursor.fetchall()
            return result
        except Exception as e:
            print(e)
        finally:
            await self.close(db)

    # get assignment by assignmentID
    async def getAssignment(self, assignmentID):
        query = """
            SELECT * FROM assignments
            WHERE assignmentid = ?
        """
        params = (assignmentID,)

        try:
            db = await self.open()
            async with db.execute(query, params) as cursor:
                result = await cursor.fetchone()
            return result
        except Exception as e:
            print(e)
        finally:
            await self.close(db)

async def main():
    backend = Backend()

    test = await backend.getAssignments(courseID=1)

    print(test)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())