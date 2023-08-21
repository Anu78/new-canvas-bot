import discord
from discord import app_commands, ui
from discord.app_commands import Choice
from discord.ext import commands
from discord.ext import tasks
from discord.interactions import Interaction
# from scripts.db import Database
from scripts.encrypt import Encrypt

class Backend():
    # check if user is registered
    async def isUser(self, userID):
        query = """
            SELECT COUNT(*) FROM users
            WHERE (userid = ?)
        """

        params = (userID,)

        try:
            db = await self.open()
            async with db.execute(query, params) as cursor:
                result = await cursor.fetchone()
            return False if result == 0 else True
        except Exception as e:
            return e
        finally:
            await self.close(db)
    
    # check if user has token
    async def hasToken(self, userID):
        query = """
            SELECT auth_token FROM users
            WHERE (userid = ?)
        """

        params = (userID,)
        
        try:
            db = await self.open()
            async with db.execute(query, params) as cursor:
                result = await cursor.fetchone()
            return False if result[0] is None else True
        except Exception as e:
            return e
        finally:
            await self.close(db)
    
    async def delUser(self, userID): 
        query = """
            DELETE FROM users 
            WHERE (userid = ?)
        """

        params = (userID,)

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
    # get all courses for user in db
    async def getCourses(self, userID):
        query = """
            SELECT courseid FROM user_courses 
            WHERE
            (userid = ?);
        """
        params = (userID,)

        try: 
            db = await self.open()
            async with db.execute(query, params) as cursor:
                result = await cursor.fetchall()
            return result
        except Exception as e:
            return e
        finally:
            await self.close(db)
    
    # get courses that are registered to a guild
    async def getCoursesForGuild(self, guildID):
        query = """
            SELECT * FROM guilds 
            WHERE
            (guildid = ?)
        """

        params = (guildID,)

        try: 
            db = await self.open()
            async with db.execute(query, params) as cursor:
                result = await cursor.fetchall()
            return result
        except Exception as e:
            return e
        finally:
            await self.close(db)
    
    # adds user to database given userid and token. adds courses automatically
    async def addUser(self, userID, token, notifs):
        e = Encrypt()

        query = """
            INSERT INTO users 
            VALUES
            (?, ?, ?)
        """

        params = (userID, e.encrypt(token), notifs)

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
    
    # add one course to a guild
    async def addCourseToGuild(self, guildID, course):
        query = """
            INSERT INTO guilds
            VALUES
            (?, ?, ?)
        """

        params = (guildID, course[0], course[1])

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
    
    # remove one course from guild
    async def removeCourseFromGuild(self, guildID, course):
        query = """
            DELETE FROM guilds 
            WHERE
            (guildid = ?) AND
            (courseid = ?);
        """

        params = (guildID, course[1])

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
    
    async def updateNotifs(self, userid, notif):
        query = """
            UPDATE users
            SET notif_freq = ?
            WHERE userid = ?
        """
        
        params = (notif, userid)

        try:
            db = await self.open()
            async with db.execute(query, params) as cursor:
                pass
            await db.commit()
        except Exception as e:
            return e
        finally:
            await self.close(db)

class UserSetup(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label="Open Canvas Login", url="https://uncc.instructure.com/profile/settings"))

    class Modal(discord.ui.Modal):
        def __init__(self):
            super().__init__(title="Enter Token", timeout=None)

        token = ui.TextInput(style=discord.TextStyle.short, label="Token", placeholder="Canvas Access Token", required=True)
        async def on_submit(self, interaction: discord.Interaction):
            encrypted_token = Encrypt().encrypt(self.token.value)
            decrypted_token = Encrypt().decrypt(encrypted_token)
            await interaction.response.send_message(f"Pretend I sent {encrypted_token} to the database.\nWe can decode it to look like: {decrypted_token}", ephemeral=True)
            return 

    @discord.ui.button(style=discord.ButtonStyle.primary, label="Apply Token", emoji="⚙️", custom_id="applyToken", row=1)
    async def applyToken(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(self.Modal())
        return

class ReminderSetup(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(self.FrequencySelect())

    class FrequencySelect(discord.ui.Select):
        def __init__(self):
            options = [
                discord.SelectOption(label="1 hour before due", value=1, emoji="⏰"),
                discord.SelectOption(label="6 hours before due", value=2, emoji="⏰"),
                discord.SelectOption(label="12 hours before due", value=4, emoji="⏰"),
                discord.SelectOption(label="1 day before due", value=8, emoji="⏰"),
                discord.SelectOption(label="3 days before due", value=16, emoji="⏰"),
                discord.SelectOption(label="5 days before due", value=32, emoji="⏰"),
                discord.SelectOption(label="1 week before due", value=64, emoji="⏰"),
                discord.SelectOption(label="2 weeks before due", value=128, emoji="⏰"),
                discord.SelectOption(label="1 month before due", value=256, emoji="⏰"),
            ]
            super().__init__(placeholder="📅 When should we remind you?", min_values=0, max_values=9, options=options)

        async def callback(self, interaction: discord.Interaction):
            if self.values == []: return
            await interaction.response.defer()
            bit = 0
            for value in self.values:
                value = int(value)
                bit = bit + value
            await interaction.followup.send(f"Selected {self.values}, total of bits are {bit}", ephemeral=True)

class Setup(commands.Cog): #name of your cog class, typically name it based off of your .py file
    def __init__(self, client):
        self.client = client

    setupCmdGroup = app_commands.Group(name="setup", description="Commands related to changing your settings.")

    @setupCmdGroup.command(name="reminders", description="Change your reminder frequency.")
    async def reminders(self, interaction: discord.Interaction):
        await interaction.response.send_message(view=ReminderSetup(), ephemeral=True)


    @setupCmdGroup.command(name="courses", description="View courses attached to your user, so you may add them to this Guild.")
    async def courses(self, interaction: discord.Interaction):
        user = await Backend().hasToken(interaction.user.id)
        if user:
            await interaction.response.send_message("You are a user. I would show you the dropdown now.", ephemeral=True)
        else:
            await interaction.response.send_message("You are not a user. Please run </setup user:1142364470983790623> to add a Token to your account so I can access your available courses.", ephemeral=True)
        return
        
    @setupCmdGroup.command(name="user", description="Add a Canvas Token to your Discord User so we can access data like your courses and assignments.")
    async def user(self, interaction: discord.Interaction):
        embed = discord.Embed()
        embed.title = "⚙️ User Setup Guide ⚙️"
        embed.description = "Steps to setup a user token.\n1. do\n2. this\n3. PLEASE"
        embed.color = discord.Color.from_str("#E72429")
        await interaction.response.send_message(embed=embed, view=UserSetup(), ephemeral=True)
        return


async def setup(client: discord.Client):
    guild = client.get_guild(1038598934265864222) #uncomment this and the comment on line 18 to sync the cog to a specific guild
    await client.add_cog(Setup(client), guilds=[guild])
