# -*- coding: utf-8 -*-

import random
import aiowiki
import discord
from io import BytesIO
from utils import paginator
from discord.ext import commands, menus
from socialscan.util import Platforms as p
from socialscan.util import execute_queries


def setup(bot):
    bot.add_cog(API(bot))


class API(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["sscan"])
    async def socialscan(self, ctx, account):
        """Querying username and email usage on online platforms."""

        with ctx.typing():
            results = await execute_queries(
                [account],
                [
                    p.TWITTER,
                    p.INSTAGRAM,
                    p.REDDIT,
                    p.GITHUB,
                    p.GITLAB,
                    p.SPOTIFY,
                ],
            )

        embed = discord.Embed(color=self.bot.color)
        embed.description = "\n\n".join(
            [
                "**{}** on **{}**: {}\n`(Success: {}, Valid: {}, Available: {})`".format(
                    r.query,
                    r.platform,
                    r.message,
                    r.success,
                    r.valid,
                    r.available,
                )
                for r in results
            ]
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=["ss"])
    async def screenshot(self, ctx, *, website):
        """Take a website screenshot."""

        website = website.replace("<", "").replace(">", "")

        if not website.startswith("http"):
            return await ctx.send("Geçerli bir web sitesi değil!")

        with ctx.typing():
            async with self.bot.session.get(
                "https://image.thum.io/get/width/2000/crop/1200/png/{}".format(
                    website
                )
            ) as resp:
                image = BytesIO(await resp.read())

        await ctx.send(
            content="<{}>".format(website),
            file=discord.File(
                image, filename="screenshot_{}.png".format(website)
            ),
        )

    @commands.command(aliases=["deprem"])
    async def quake(self, ctx, last=1):
        """Show quake information from the Kandilli Observatory."""

        embeds = []

        async with self.bot.session.get(
            "https://api.berkealp.net/kandilli/index.php",
            params={"last": last},
        ) as resp:
            if resp.status != 200:
                return await ctx.send("Bağlantı hatası!")
            data = await resp.json()

        for d in data:
            embed = discord.Embed(color=self.bot.color)
            date, time = d["Time"].split(" ")
            embed.description = (
                "Tarih: `{}`\n"
                "Saat: `{}`\n"
                "Enlem: `{}`\n"
                "Boylam: `{}`\n"
                "Bölge: `{}`\n"
                "Büyüklük: `{}` "
                "Derinlik: `{} Km`".format(
                    date,
                    time,
                    d["Latitude"].split(";")[0],
                    d["Longitude"].split(";")[0],
                    d["Region"],
                    d["Magnitude"],
                    d["Depth"],
                ).replace("&deg", "°")
            )
            embed.set_thumbnail(url=d["MapImage"])
            embeds.append(embed)

        menu = menus.MenuPages(
            timeout=30,
            clear_reactions_after=True,
            source=paginator.EmbedSource(data=embeds),
        )
        await menu.start(ctx)

    @commands.command()
    async def pypi(self, ctx, package):
        """Show PyPi package informations."""

        async with self.bot.session.get(
            "https://pypi.org/pypi/{}/json".format(package)
        ) as resp:
            if resp.status != 200:
                return await ctx.send("Paket bulunamadı!")
            data = await resp.json()
            data = data["info"]

        try:
            project_urls = ", ".join(
                [
                    "[`{}`]({})".format(t, u)
                    for t, u in data["project_urls"].items()
                ]
            )
        except AttributeError:
            project_urls = "~"

        embed = discord.Embed(color=self.bot.color)
        embed.title = "{} | {}".format(data["name"], data["version"])
        embed.url = data["package_url"]
        embed.description = (
            "{}\n\n"
            "Lisans: `{}`\n"
            "Geliştirici: `{} ({})`\n"
            "Bağlantılar: {}"
        ).format(
            data["summary"] or " ",
            data["license"] or " ",
            data["author"] or " ",
            data["author_email"] or " ",
            project_urls,
        )
        embed.set_thumbnail(url="https://i.imgur.com/u6YG9jm.png")

        await ctx.send(embed=embed)

    @commands.command(aliases=["viki"])
    async def wiki(self, ctx, *, search):
        """Search the Turkish Wikipedia."""

        embeds = []

        async with ctx.typing():
            wiki = aiowiki.Wiki.wikipedia("tr")

            for page in await wiki.opensearch(search):
                embed = discord.Embed(colour=self.bot.color)
                embed.title = page.title
                embed.url = (await page.urls())[0].split("(")[0]
                embed.description = (await page.summary())[:2000] + "..."
                embeds.append(embed)

        menu = menus.MenuPages(
            timeout=30,
            clear_reactions_after=True,
            source=paginator.EmbedSource(data=embeds),
        )
        await menu.start(ctx)

    @commands.command()
    async def xkcd(self, ctx, num=None):
        """A webcomic of romance, sarcasm, math, and language."""

        url = "https://xkcd.com"

        async with self.bot.session.get("{}/info.0.json".format(url)) as resp:
            if resp.status != 200:
                return await ctx.send("Bağlantı hatası!")
            data = await resp.json()

        if num == None:
            num = random.randint(1, data["num"])

        async with self.bot.session.get(
            "{}/{}/info.0.json".format(url, num)
        ) as resp:
            if resp.status != 200:
                return await ctx.send("Geçersiz numara!")
            data = await resp.json()

        embed = discord.Embed(color=self.bot.color)
        embed.title = data["title"]
        embed.description = data["alt"]
        embed.set_image(url=data["img"])
        embed.set_footer(
            text="{}/{}/{} • {}".format(
                data["day"], data["month"], data["year"], data["num"]
            )
        )

        await ctx.send(embed=embed)

    async def send_activity(self, ctx, embed, data):
        embed.description = (
            "{}\n\n"
            "Tür: `{}`\n"
            "Ulaşılabilirlik: `{}`\n"
            "Katılımcılar: `{}`\n"
            "Fiyat: `{}`".format(
                data["activity"],
                data["type"].title(),
                data["accessibility"],
                data["participants"],
                data["price"],
            )
        )
        embed.set_footer(text="Anahtar: {}".format(data["key"]))

        await ctx.send(embed=embed)

    @commands.group(invoke_without_command=True)
    async def bored(self, ctx):
        """Let's find you something to do."""

        url = "http://www.boredapi.com/api"

        async with self.bot.session.get("{}/activity".format(url)) as resp:
            if resp.status != 200:
                return await ctx.send("Bağlantı hatası!")
            data = await resp.json()

        embed = discord.Embed(color=self.bot.color)
        await self.send_activity(ctx, embed, data)

    @bored.command(name="type")
    async def bored_type(self, ctx, type=None):
        """Find a random activity with a given type."""

        url = "http://www.boredapi.com/api"
        types = [
            "education",
            "recreational",
            "social",
            "diy",
            "charity",
            "cooking",
            "relaxation",
            "music",
            "busywork",
        ]
        embed = discord.Embed(color=self.bot.color)

        if type == None:
            embed.description = "Aktivite türleri:\n{}".format(
                ", ".join(["`{}`".format(t) for t in types])
            )
            return await ctx.send(embed=embed)

        params = {"type": type}

        async with self.bot.session.get(
            "{}/activity".format(url), params=params
        ) as resp:
            if resp.status != 200:
                return await ctx.send("Bağlantı hatası!")
            data = await resp.json()

        await self.send_activity(ctx, embed, data)

    @commands.command(aliases=["yn"])
    async def yesno(self, ctx):
        """Making a good decision might require some help."""

        url = "https://yesno.wtf/api"

        async with self.bot.session.get(url) as resp:
            if resp.status != 200:
                return await ctx.send("Bağlantı hatası!")
            data = await resp.json()

        embed = discord.Embed(color=self.bot.color)
        embed.title = data["answer"].title()
        embed.set_image(url=data["image"])

        await ctx.send(embed=embed)
