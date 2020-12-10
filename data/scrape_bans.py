from bs4 import BeautifulSoup as bs
from glob import glob

# Stores the html files for parsing
DATA_PATH = "./data/players/*.html"

# Main function for compiling data and generating database
def main():
    # Dictionary for player names -> player data (could be list -- not sure)
    player_col = {}
    for file_name in glob(DATA_PATH):
        gen_player(file_name)
        # player = gen_player(file_name)
        # player_col[player.name] = player


# Generates and returns a single player object from a file
def gen_player(file_name):
    player_name = get_player_name(file_name)
    match_list = get_match_list(file_name)
    #return Player(player_name, match_list)


# Parse file for main name of player at top of file
def get_player_name(file_name):
    # Parse only tag w/ white name at top of page
    with open(file_name, "r") as file:
        soup = bs(file, 'html5lib')
        name = soup.find("a", {"class" : "whiteLink persona_name_text_content"})
        # Strip tabbing(?) stuff off name
        return name.text.strip()


# Parses a file and returns a list of match objects
def get_match_list(file_name):
    match_list = []
    with open(file_name, "r") as file:
        soup = bs(file, 'html5lib')
        # Find main table contaning all map and player data (the darker blue panel)
        raw_all_table = soup.find("table", {"class": "generic_kv_table csgo_scoreboard_root"})
        # It should exist -- probably renamed if this fails
        assert raw_all_table is not None
        # This part is super awkward to parse due to the chrome extension not making a new tbody nor appending
        # to the current tbody. I'll just create two lists instead even if it's a little gacky
        match_map_list = [x for x in raw_all_table.find_all("td", {"class": "val_left banchecker-counted"})]
        match_players_list = [x for x in raw_all_table.find_all("table", {"class": "csgo_scoreboard_inner_right banchecker-formatted banchecker-withcolumn"})]
        # Should have the same num of map data and player data tables
        assert len(match_map_list == match_players_list)

        # Now make a new match for each game
        for index in len(match_map_list):
            new_match = Match(match_map_list[index], match_players_list[index])
            match_list.append(new_match)
    return match_list

# Class for a single match data -- just a container but makes it easier to hold
class Match:

    def __init__(self, map_data, match_data):
        return 0


# Class for a player -- collection of player, summary stats, and individual matches
class Player:
    
    def __init__(self, name, match_list):
        self.name = name
        self.match_list = match_list
        sum_stats()


    def sum_stats():
        return 0


main()