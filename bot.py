import discord
from discord.ext import commands

# =========================
# НАСТРОЙКИ БОТА
# =========================

TOKEN = "ТВОЙ_ТОКЕН_БОТА"

TICKET_CATEGORY_NAME = "ꜰᴀᴍɪʟʏ ᴛɪᴄᴋᴇᴛ"
FAMILY_ROLE_NAME = "ɢʀᴀᴠᴇꜱɪᴅᴇ"
LOG_CHANNEL_NAME = "логи-заявок"

# Роли, которые будут видеть тикет
STAFF_ROLES = [
    "support",
    "ᴏᴡɴᴇʀ",
    "ᴅᴇᴘᴜᴛʏ",
    "ʜɪɢʜ"
]

# Роли для пинга при создании заявки
PING_ROLES = [
    "ᴏᴡɴᴇʀ",
    "ᴅᴇᴘᴜᴛʏ",
    "ʜɪɢʜ"
]

# =========================
# ИНТЕНТЫ
# =========================

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# МОДАЛЬНОЕ ОКНО ЗАЯВКИ
# =========================

class ApplicationModal(discord.ui.Modal, title="Заявка в семью"):

    name = discord.ui.TextInput(
        label="Имя IRL",
        required=True
    )

    age = discord.ui.TextInput(
        label="Возраст (14+)",
        required=True
    )

    dm_proof = discord.ui.TextInput(
        label="Откат с ДМ (любой подойдет)",
        required=True
    )

    hours = discord.ui.TextInput(
        label="История фам | Часы в игре",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):

        guild = interaction.guild

        # =========================
        # СОЗДАНИЕ КАТЕГОРИИ
        # =========================

        category = discord.utils.get(
            guild.categories,
            name=TICKET_CATEGORY_NAME
        )

        if category is None:
            category = await guild.create_category(
                TICKET_CATEGORY_NAME
            )

        # =========================
        # ПРАВА КАНАЛА
        # =========================

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(
                read_messages=False
            ),

            interaction.user: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True
            )
        }

        # Доступ стафф ролям
        for role_name in STAFF_ROLES:

            role = discord.utils.get(
                guild.roles,
                name=role_name
            )

            if role:
                overwrites[role] = discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True
                )

        # =========================
        # СОЗДАНИЕ ТИКЕТА
        # =========================

        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )

        # =========================
        # EMBED ЗАЯВКИ
        # =========================

        embed = discord.Embed(
            title="📋 Новая заявка",
            color=discord.Color.green()
        )

        embed.add_field(
            name="👤 Имя",
            value=self.name.value,
            inline=False
        )

        embed.add_field(
            name="🎂 Возраст",
            value=self.age.value,
            inline=False
        )

        embed.add_field(
            name="🚫 Откат с ДМ",
            value=self.dm_proof.value,
            inline=False
        )

        embed.add_field(
            name="⏱️ Часы",
            value=self.hours.value,
            inline=False
        )

        embed.add_field(
            name="📎 Пользователь",
            value=interaction.user.mention,
            inline=False
        )

        # =========================
        # ПИНГ РОЛЕЙ
        # =========================

        mentions = []

        for role_name in PING_ROLES:

            role = discord.utils.get(
                guild.roles,
                name=role_name
            )

            if role:
                mentions.append(role.mention)

        ping_message = " ".join(mentions)

        # =========================
        # КНОПКИ
        # =========================

        view = DecisionButtons(interaction.user)

        await channel.send(
            content=f"{ping_message} 📩 Новая заявка!",
            embed=embed,
            view=view
        )

        await interaction.response.send_message(
            f"✅ Заявка отправлена: {channel.mention}",
            ephemeral=True
        )

# =========================
# КНОПКИ ПРИНЯТЬ / ОТКАЗАТЬ
# =========================

class DecisionButtons(discord.ui.View):

    def __init__(self, applicant):
        super().__init__(timeout=None)
        self.applicant = applicant

    @discord.ui.button(
        label="Принять",
        style=discord.ButtonStyle.green
    )
    async def accept(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        # ❌ Запрет принимать свою заявку
        if interaction.user.id == self.applicant.id:

            await interaction.response.send_message(
                "❌ Ты не можешь принять свою собственную заявку!",
                ephemeral=True
            )

            return

        guild = interaction.guild

        # ✅ Выдача роли семьи
        role = discord.utils.get(
            guild.roles,
            name=FAMILY_ROLE_NAME
        )

        if role:
            await self.applicant.add_roles(role)

        # 📜 Логи
        log_channel = discord.utils.get(
            guild.text_channels,
            name=LOG_CHANNEL_NAME
        )

        if log_channel:

            await log_channel.send(
                f"✅ {self.applicant.mention} "
                f"принят модератором "
                f"{interaction.user.mention}"
            )

        # ✅ Сообщение
        await interaction.channel.send(
            f"✅ {self.applicant.mention} "
            f"принят модератором "
            f"{interaction.user.mention}"
        )

        await interaction.channel.delete()

    @discord.ui.button(
        label="Отказать",
        style=discord.ButtonStyle.red
    )
    async def reject(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        # ❌ Запрет отклонять свою заявку
        if interaction.user.id == self.applicant.id:

            await interaction.response.send_message(
                "❌ Ты не можешь отклонить свою собственную заявку!",
                ephemeral=True
            )

            return

        guild = interaction.guild

        # 📜 Логи
        log_channel = discord.utils.get(
            guild.text_channels,
            name=LOG_CHANNEL_NAME
        )

        if log_channel:

            await log_channel.send(
                f"❌ {self.applicant.mention} "
                f"получил отказ от "
                f"{interaction.user.mention}"
            )

        # ❌ Сообщение
        await interaction.channel.send(
            f"❌ {self.applicant.mention} "
            f"отклонён модератором "
            f"{interaction.user.mention}"
        )

        await interaction.channel.delete()
class TicketButton(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="📩 Подать заявку",
        style=discord.ButtonStyle.green
    )
    async def create_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_modal(
            ApplicationModal()
        )

# =========================
# КОМАНДА ПАНЕЛИ
# =========================

@bot.command()
async def ticket(ctx):

    text = """
:krest:   Твой путь может начаться прямо сейчас.   :krest:
----------------------------------------------------------

                         ✝︎ ᴛɪᴄᴋᴇᴛꜱ ᴏᴘᴇɴ 𐕣
                                   ↓↓↓

:zvzda2~1: Перед подачей ознакомься с критериями :zvzda2~1:
----------------------------------------------------------

             :krest1: Минимальный возраст: 14+ лет :krest1:
----------------------------------------------------------

              :zvzda1: Подойдёт любой откат с DM :zvzda1:
----------------------------------------------------------

:krest: Для подачи заявки нажми на кнопку :krest:
                                   ↓↓↓

                         «Подать заявку»
"""

    embed = discord.Embed(
        description=text,
        color=discord.Color.from_rgb(20, 20, 20)
    )

    await ctx.send(
        embed=embed,
        view=TicketButton()
    )

# =========================
# ЗАПУСК БОТА
# =========================

@bot.event
async def on_ready():
    print(f"Бот запущен как {bot.user}")

import os

bot.run(os.getenv("TOKEN"))
