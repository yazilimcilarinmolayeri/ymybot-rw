# -*- coding: utf-8 -*-

import discord
import mimetypes
from datetime import datetime
from utils import config, lists
from discord.ext import commands


def setup(bot):
    bot.add_cog(Info(bot))


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    def is_url_image(self, url):
        mimetype, encoding = mimetypes.guess_type(url)
        return mimetype and mimetype.startswith("image")

    @commands.group(invoke_without_command=True)
    async def profile(self, ctx, user: discord.Member = None):
        """"""

        if user is None:
            user = ctx.author

        data = self.db.get_item("Profile", ("user_id", user.id))

        if not len(data):
            return await ctx.send("Profil bulunamadı!")

        data = data[0]

        embed = discord.Embed(
            color=self.bot.color, timestamp=datetime.utcnow()
        )
        embed.description = "{} **{}**\n\n".format(
            user.mention, user
        ) + "\n".join(
            [
                "{}: `{}`".format(lists.profile_titles[i], j)
                for i, j in enumerate(data[1:-1])
            ]
        )
        embed.set_thumbnail(url=user.avatar_url)
        embed.set_image(
            url=data[-1] if data[-1] != "~" else discord.Embed.Empty
        )
        embed.set_footer(text="ID: {}".format(user.id))

        await ctx.send(embed=embed)

    @profile.command(name="setup")
    async def profile_setup(self, ctx):
        """"""

        answers = []
        author = ctx.message.author
        answers.append(author.id)

        if self.db.check_item("Profile", ("user_id", author.id)):
            return await ctx.send("Var olan profilini düzenle...")

        def check(m):
            try:
                return (m.channel.id == ctx.channel.id) and (
                    m.author.id == author.id
                )
            except:
                return False

        embed = discord.Embed(color=self.bot.color)
        embed.set_footer(
            text="'S' girerek soruyu geçebilir, 'C' girerek iptal edebilirsin."
        )
        question_embed = await ctx.send(embed=embed)

        for i, question in enumerate(lists.profile_questions):
            embed.description = "{}, {}".format(author.mention, question)
            await question_embed.edit(embed=embed)
            answer = await self.bot.wait_for("message", check=check)

            if answer.content.lower() == "s":
                answers.append("~")
            elif answer.content.lower() == "c":
                return await question_embed.delete()
            else:
                if len(lists.profile_questions) - 1 == i:
                    if not self.is_url_image(answer.content):
                        return await ctx.send(
                            "Geçersiz bağlantı! Çıkılıyor..."
                        )
                answers.append(answer.content)

            await answer.delete()
        await question_embed.delete()

        self.db.insert("Profile", *answers)
        await ctx.reply("Kurulum tamamlandı!")

        # command = self.bot.get_command("profile")
        # await command.__call__(ctx=ctx, user=author)

    @profile.group(name="delete")
    @commands.has_permissions(manage_messages=True)
    async def profile_delete(self, ctx, user: discord.Member):
        """"""

        if not self.db.check_item("Profile", ("user_id", user.id)):
            return await ctx.send("Profil bulunamadı!")

        self.db.remove("Profile", ("user_id", user.id))
        await ctx.send(
            "{} adlı kullanıcının profili silindi!".format(user.mention)
        )

    @profile.group(name="edit")
    async def profile_edit(self, ctx):
        """"""

        commands = ctx.command.commands

        embed = discord.Embed(color=self.bot.color)
        embed.description = "Profil düzenlemek için argümanlar:\n" + ", ".join(
            "`{}`".format(c.aliases[0]) for c in commands
        )

        if not ctx.invoked_subcommand:
            await ctx.send(embed=embed)

    @profile_edit.command(aliases=["os"])
    async def operation_system(self, ctx, *, new_profile_item):
        self.db.update(
            "Profile",
            ("user_id", ctx.message.author.id),
            operation_system=new_profile_item,
        )

        await ctx.message.add_reaction("\U00002705")

    @profile_edit.command(aliases=["de"])
    async def desktop_environment(self, ctx, *, new_profile_item):
        self.db.update(
            "Profile",
            ("user_id", ctx.message.author.id),
            desktop_environment=new_profile_item,
        )

        await ctx.message.add_reaction("\U00002705")

    @profile_edit.command(aliases=["themes"])
    async def desktop_themes(self, ctx, *, new_profile_item):
        self.db.update(
            "Profile",
            ("user_id", ctx.message.author.id),
            desktop_themes=new_profile_item,
        )

        await ctx.message.add_reaction("\U00002705")

    @profile_edit.command(aliases=["browser"])
    async def web_browser(self, ctx, *, new_profile_item):
        self.db.update(
            "Profile",
            ("user_id", ctx.message.author.id),
            web_browser=new_profile_item,
        )

        await ctx.message.add_reaction("\U00002705")

    @profile_edit.command(aliases=["editors"])
    async def code_editors(self, ctx, *, new_profile_item):
        self.db.update(
            "Profile",
            ("user_id", ctx.message.author.id),
            code_editors=new_profile_item,
        )

        await ctx.message.add_reaction("\U00002705")

    @profile_edit.command(aliases=["terminal"])
    async def terminal_software(self, ctx, *, new_profile_item):
        self.db.update(
            "Profile",
            ("user_id", ctx.message.author.id),
            terminal_software=new_profile_item,
        )

        await ctx.message.add_reaction("\U00002705")

    @profile_edit.command(aliases=["shell"])
    async def shell_software(self, ctx, *, new_profile_item):
        self.db.update(
            "Profile",
            ("user_id", ctx.message.author.id),
            shell_software=new_profile_item,
        )

        await ctx.message.add_reaction("\U00002705")

    @profile_edit.command(aliases=["ss"])
    async def screenshot_url(self, ctx, new_profile_item):
        if not self.is_url_image(new_profile_item):
            return await ctx.message.add_reaction("\U0000203c")

        self.db.update(
            "Profile",
            ("user_id", ctx.message.author.id),
            screenshot_url=new_profile_item,
        )

        await ctx.message.add_reaction("\U00002705")