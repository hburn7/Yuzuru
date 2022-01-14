from discord import Embed
from discord import Color


class YuzuruEmbed(Embed):
    def __init__(self):
        super().__init__(color=Color.nitro_pink())
