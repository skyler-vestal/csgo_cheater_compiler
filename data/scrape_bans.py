from bs4 import BeautifulSoup as bs
from glob import glob

# Stores the html files for parsing
DATA_PATH = "./data/players/*.html"

# Main function for compiling data and generating database
def main():
    # Dictionary for player names -> player data (could be list -- not sure)
    player_col = {}
    for file_name in glob(DATA_PATH):
        get_player_name(open(file_name, "r"))
        # player = gen_player(file_name)
        # player_col[player.name] = player


# Generates and returns a single player object from a file
def gen_player(file_name):
    f = open(file_name, "r")
    player_name = get_player_name(f)
    match_list = get_match_list(f)
    f.close()
    return Player(player_name, match_list)


# Parse file for main name of player at top of file
def get_player_name(file):
    # Parse only tag w/ white name at top of page
    soup = bs(file, 'html5lib')
    name = soup.find("a", {"class" : "whiteLink persona_name_text_content"})
    # Strip tabbing(?) stuff off name
    return name.text.strip()


# Parses a file and returns a list of match objects
def get_match_list(file):
    soup = bs(file, 'html5lib')
    raw_matches = soup.find("")


# Class for a single match data -- just a container but makes it easier to hold
class Match:

    def __init__(self, data):
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