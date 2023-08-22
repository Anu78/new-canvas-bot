import discord
from discord import app_commands, ui
from discord.app_commands import Choice
from discord.ext import commands
from discord.ext import tasks
from scripts import db_api

class Backend(db_api.Database):
    # registers guild and admin's courses
    async def registerGuild(self, guildID):
        query = """
            INSERT INTO guilds
            VALUES
            (?);
        """

        params = (guildID,)

        db = await self.open()
        
        try:
            async with db.execute(query, params) as cursor:
                pass

            await db.commit()
        except Exception as e:
            return e
        
        finally:
            await self.close(db)
            
        return True
    
    # remove guild metric
    async def unregisterGuild(self, guildID):
        query = """
            DELETE FROM guilds 
            WHERE
            (guildid = ?);
        """

        params = (guildID,)

        try:
            db = await self.open()
            async with db.execute(query, params) as cursor:
                pass
            await db.commit()
        except Exception as e:
            return e
        finally:
            await self.close(db)

        return True
    async def compareGuildCourses(parameter_list):
        pass

class GuildMetrics(commands.Cog): #name of your cog class, typically name it based off of your .py file
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await Backend.registerGuild(self, guild.id)
        return
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await Backend.unregisterGuild(self, guild.id)
        return

async def setup(client):
    #guild = client.get_guild(guildid) #uncomment this and the comment on line 18 to sync the cog to a specific guild
    await client.add_cog(GuildMetrics(client))#, guilds=[guild])
