import discord
from discord import app_commands, ui
from discord.app_commands import Choice
from discord.ext import commands
from discord.ext import tasks
import datetime
import asyncio
from scripts import db

global indexes
global user_assignments
indexes = {}
user_assignments = {}

class Backend(db.Database):
    # get assignments by userID or courseID
    async def getAssignments(self, userID: int = None, courseID: int = None):
        query = """
            select assignments.* 
            from assignments 
            join user_courses uc on uc.courseid = assignments.courseid
            where uc.userid = ?
            or assignments.courseid = ?
            group by assignmentid
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
            return e
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
            return e
        finally:
            await self.close(db)

    #get courses for a user
    async def getCourses(self, userID):
        query = """
            SELECT c.name, c.courseid FROM courses c
            join user_courses uc on uc.courseid = c.courseid
            WHERE
            (uc.userid = ?);
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

class Embeds():
    class Assignment(discord.Embed):
        async def build(id, name, description, due_date, allowed_extensions, points_possible, grading_type, index, count):
            embed = discord.Embed()
            embed.color = discord.Color.from_str("#E72429")
            embed.set_author(name=f"Assignment: {id}")
            embed.set_thumbnail(url="https://www.freeiconspng.com/thumbs/pencil-png/black-pencil-png-black-pencil-vector-8.png")
            embed.title = f"{name}"
            embed.description = description
            formats = ""
            extensions = allowed_extensions.split(",")
            for ext in extensions:
                formats = formats + f"{ext}\n"
            embed.add_field(name="File Formats", value=formats, inline=False)
            embed.add_field(name="Possible Points", value=points_possible, inline=False)
            embed.add_field(name="Grading Type", value=grading_type, inline=False)
            embed.add_field(name="Due Date", value=f"<t:{due_date}:R>")
            embed.set_footer(text=f"{index + 1} of {count}")
            return embed

class Views():
    class Courses(discord.ui.View):
        def __init__(self, options):
            super().__init__(timeout=None)  
            self.add_item(self.CourseSelect(options))

        class CourseSelect(discord.ui.Select):
            def __init__(self, options):
                super().__init__(placeholder="📓 Select courses to view assignments", min_values=1, max_values=len(options), options=options)

            async def callback(self, interaction: discord.Interaction):
                if self.values == []: return
                await interaction.response.defer()
                assignments = []
                if "All" not in self.values:
                    for value in self.values:
                        if value != "All":
                            course_assignments = await Backend().getAssignments(courseID=value)
                            assignments += course_assignments
                else:
                    course_assignments = await Backend().getAssignments(userID=interaction.user.id)
                    assignments = course_assignments
                user_assignments[interaction.user.id] = assignments
                embed = await Embeds.Assignment.build(id=assignments[indexes[interaction.user.id]][1], name=assignments[indexes[interaction.user.id]][0], description=assignments[indexes[interaction.user.id]][4], due_date=assignments[indexes[interaction.user.id]][2], allowed_extensions=assignments[indexes[interaction.user.id]][3], points_possible=assignments[indexes[interaction.user.id]][7], grading_type=assignments[indexes[interaction.user.id]][6], index=indexes[interaction.user.id], count=len(assignments))
                await interaction.followup.send(embed=embed, view=Views.AssignmentButtons(), ephemeral=True)
                
    class AssignmentButtons(discord.ui.View):
        status = False
        def __init__(self, status: bool = False):
            super().__init__(timeout=None)
            self.status = status
        
        @discord.ui.button(style=discord.ButtonStyle.gray, emoji="⏪")
        async def startButton(self, interaction: discord.Interaction, button: discord.ui.Button):
            if self.status: 
                await interaction.response.defer()
                return
            indexes[interaction.user.id] = 0
            assignments = user_assignments[interaction.user.id]
            embed = await Embeds.Assignment.build(id=assignments[indexes[interaction.user.id]][1], name=assignments[indexes[interaction.user.id]][0], description=assignments[indexes[interaction.user.id]][4], due_date=assignments[indexes[interaction.user.id]][2], allowed_extensions=assignments[indexes[interaction.user.id]][3], points_possible=assignments[indexes[interaction.user.id]][7], grading_type=assignments[indexes[interaction.user.id]][6], index=indexes[interaction.user.id], count=len(assignments))
            await interaction.response.defer()
            await interaction.edit_original_response(embed=embed, view=Views.AssignmentButtons())
            return
        
        @discord.ui.button(style=discord.ButtonStyle.gray, emoji="⬅️")
        async def leftButton(self, interaction: discord.Interaction, button: discord.ui.Button):
            if self.status: 
                await interaction.response.defer()
                return
            if indexes[interaction.user.id] > 0: 
                indexes[interaction.user.id] -= 1
            assignments = user_assignments[interaction.user.id]
            embed = await Embeds.Assignment.build(id=assignments[indexes[interaction.user.id]][1], name=assignments[indexes[interaction.user.id]][0], description=assignments[indexes[interaction.user.id]][4], due_date=assignments[indexes[interaction.user.id]][2], allowed_extensions=assignments[indexes[interaction.user.id]][3], points_possible=assignments[indexes[interaction.user.id]][7], grading_type=assignments[indexes[interaction.user.id]][6], index=indexes[interaction.user.id], count=len(assignments))
            await interaction.response.defer()
            await interaction.edit_original_response(embed=embed, view=Views.AssignmentButtons())
            return

        @discord.ui.button(style=discord.ButtonStyle.green, label="Turn In", emoji="📝")
        async def submit(self, interaction: discord.Interaction, button: discord.ui.Button):
            time = datetime.datetime.now()
            wait_time = 30
            future = time + datetime.timedelta(seconds=wait_time)
            future = future.timestamp()
            future = round(future)
            id = interaction.message.embeds[0].author.name
            id = id.replace("Assignment: ", "")
            assignment = await Backend().getAssignment(id)
            types = assignment[3].split(",")
            allowed_extensions = []
            for type in types:
                allowed_extensions.append(str(type).lower())
            await interaction.response.send_message(f"Please upload a file via Discord Attachments <t:{future}:R>")
            await asyncio.sleep(wait_time)
            attachment = None
            async for message in interaction.channel.history(limit=1):
                if len(message.attachments) > 0: 
                    attachment = message.attachments[0].url
                    type = attachment.split(".")[-1]
            if attachment is None:
                await interaction.edit_original_response(content="Time expired for upload. Please use the command again.")
            elif attachment is not None and type in allowed_extensions:
                await interaction.edit_original_response(content=f"Your file is located at: {attachment}. It has a type of {type}")
            elif attachment is not None and type not in allowed_extensions:
                await interaction.edit_original_response(content=f"You uploaded a file of the wrong type.")
            return
        
        @discord.ui.button(style=discord.ButtonStyle.gray, emoji="➡️")
        async def rightButton(self, interaction: discord.Interaction, button: discord.ui.Button):
            if self.status: 
                await interaction.response.defer()
                return
            assignments = user_assignments[interaction.user.id]
            if indexes[interaction.user.id] + 1 < len(assignments):
                indexes[interaction.user.id] += 1
            embed = await Embeds.Assignment.build(id=assignments[indexes[interaction.user.id]][1], name=assignments[indexes[interaction.user.id]][0], description=assignments[indexes[interaction.user.id]][4], due_date=assignments[indexes[interaction.user.id]][2], allowed_extensions=assignments[indexes[interaction.user.id]][3], points_possible=assignments[indexes[interaction.user.id]][7], grading_type=assignments[indexes[interaction.user.id]][6], index=indexes[interaction.user.id], count=len(assignments))
            await interaction.response.defer()
            await interaction.edit_original_response(embed=embed, view=Views.AssignmentButtons())
            return
        
        @discord.ui.button(style=discord.ButtonStyle.gray, emoji="⏩")
        async def endButton(self, interaction: discord.Interaction, button: discord.ui.Button):
            if self.status: 
                await interaction.response.defer()
                return
            assignments = user_assignments[interaction.user.id]
            indexes[interaction.user.id] = len(assignments) - 1
            embed = await Embeds.Assignment.build(id=assignments[indexes[interaction.user.id]][1], name=assignments[indexes[interaction.user.id]][0], description=assignments[indexes[interaction.user.id]][4], due_date=assignments[indexes[interaction.user.id]][2], allowed_extensions=assignments[indexes[interaction.user.id]][3], points_possible=assignments[indexes[interaction.user.id]][7], grading_type=assignments[indexes[interaction.user.id]][6], index=indexes[interaction.user.id], count=len(assignments))
            await interaction.response.defer()
            await interaction.edit_original_response(embed=embed, view=Views.AssignmentButtons())
            return

class Assignments(commands.Cog): #name of your cog class, typically name it based off of your .py file
    def __init__(self, client):
        self.client = client

    assignments = app_commands.Group(name="assignments", description="All commands relating to assignments.")
    @assignments.command(name="browse", description="This is a command to view assignments available to you using the Assignment Viewer.") #this is what names your command in the tree
    async def browse(self, interaction: discord.Interaction, id: str = None): #function the command will perform
        if interaction.guild is not None: #check if we are in a dm
            await interaction.response.send_message("This command is only available in Direct Messages.", ephemeral=True) 
            return
        if id is None:
            indexes[interaction.user.id] = 0
            courses = await Backend().getCourses(interaction.user.id)
            options = []
            for name, id in courses:
                options.append(discord.SelectOption(label=name, value=id))
            options.append(discord.SelectOption(label="All"))
            await interaction.response.send_message(content="Select 1 or more courses", view=Views.Courses(options=options), ephemeral=True)
        else:
            assignment = await Backend().getAssignment(id)
            embed = await Embeds.Assignment.build(id=assignment[1], name=assignment[0], description=assignment[4], due_date=assignment[2], allowed_extensions=assignment[3], points_possible=assignment[7], grading_type=assignment[6], index=0, count=1)
            await interaction.response.send_message(embed=embed, view=Views.AssignmentButtons(True), ephemeral=True)

    @assignments.command(name="list", description="This is a command to list all your assignments by name in text form.")
    async def list(self, interaction: discord.Interaction):
        if interaction.guild is not None: #check if we are in a dm
            await interaction.response.send_message("This command is only available in Direct Messages.", ephemeral=True) 
            return
        return


async def setup(client):
    #guild = client.get_guild(1038598934265864222) #uncomment this and the comment on line 18 to sync the cog to a specific guild
    await client.add_cog(Assignments(client))#, guilds=[guild])