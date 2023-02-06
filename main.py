import discord
import server
import emoji

from discord.ui import View, Select
from aiohttp import web

# Configuring discord bot
bot = discord.Bot(command_prefix="!", description="example", intents=discord.Intents.all())


@bot.event
async def on_ready():
    # Configuring the web server
    bot.server = server.HTTPServer(
        bot=bot,
        host="127.0.0.1",
        port=8000,
    )

    # starting the web server
    await bot.server.start()


@bot.event
async def on_guild_join(guild: discord.Guild):
    # Creating new category
    category = await guild.create_category('Exam Hall')

    # creating new channel for all the questions
    await guild.create_text_channel('questions', category=category)


@bot.event
async def on_message(message: discord.Message):
    # If someone says hello, Greeting them with response
    if message.content == "hello":
        await message.channel.send(f"hey {message.author.name}")


@bot.command()
async def ping(ctx, arg):
    # /ping command response
    await ctx.respond(f'This is the argument => {arg}')


@server.add_route(path="/ask-question", method="POST")
async def ask(request: web.Request):
    # Getting the channel for questions
    channel = discord.utils.get(bot.get_all_channels(), name='questions')

    # Getting Question object from Json post request
    data = await request.json()

    # Configuring the answer selector
    select = Select(
            custom_id=str(data['id']),
            placeholder="Choose an Answer",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(
                    label=option["label"],
                    value=str(option["id"]),
                    emoji="emoji" in option and emoji.is_emoji(option["emoji"]) and option["emoji"] or None,
                    description=option["description"]
                ) for option in list(data['options'])
            ],
        )

    async def answer_callback(interaction: discord.Interaction):
        # Disabling the answer selector for selected already
        select.disabled = True

        # Printing the result
        print({
            "student_id": interaction.user.id,
            "question_id": select.custom_id,
            "answer": select.values[0]
        })

        # Sending response according to the answer
        if select.values[0] == str(data['answer']):
            await interaction.response.reply(content=f'Your given answer is correct.', view=view)
        else:
            await interaction.response.reply(content=f'Your given answer is not correct.', view=view)

    # Assigning Callback function for the answer selector
    select.callback = answer_callback

    # Creating the answer selector view and add the selector to the view
    view = View()
    view.add_item(select)

    # Sending the question to discord
    await channel.send(data['question'], view=view)

    # Sending the response for the user
    return web.json_response(data={"message": "Question posted to the exam hall."}, status=200)


bot.run('MTA3MTA5Njg0NjI0MTUwOTQzOA.GTJE5i.UuUdkV0U9oK3uvPLGEpqiA_GgGwiPgyN5QRI9I')
