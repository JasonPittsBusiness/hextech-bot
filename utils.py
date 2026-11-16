import unicodedata

import riot_api


def parse_riot_id(riot_id):
    """Takes in a riot ID (gamename#tag) splits and cleans. Returns game_name and tag_line"""
    riot_id = "".join(char for char in riot_id if unicodedata.category(char) != "Cf")
    game_name, tag_line = riot_id.split("#")
    tag_parts = tag_line.split()
    if len(tag_parts) > 1:
        tag_line, queue_type = tag_parts
        return (game_name, tag_line, queue_type)
    return (game_name, tag_line, riot_api.DEFAULT_QUEUE)
