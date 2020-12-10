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
        assert len(match_map_list) == len(match_players_list)

        # Now make a new match for each game
        for index in range(len(match_map_list)):
            new_match = Match(match_map_list[index], match_players_list[index])
            match_list.append(new_match)
    return match_list


# Class for a single match data -- just a container but makes it easier to hold
# Useful stuff:
#   map_data - Dictionary for map, date, time, wait_time, and match_time
#   teams - Tuple of 2 dictionaries for two teams
#   scores - Tuple of 2 ints for two teams
class Match:

    def __init__(self, map_data, match_data):
        self.map_data = {}
        self.match_data = {}
        self.parse_map_data(map_data)
        self.parse_match_data(match_data)


    # Initialize variables for map data
    def parse_map_data(self, map_data):
        map_rows = map_data.find("table", {"class": "csgo_scoreboard_inner_left"}).find("tbody").find_all("tr")
        self.map_data["map"] = map_rows[0].text.strip().split(" ")[1]
        time_data = map_rows[1].text.strip().split(" ")
        self.map_data["date"] = time_data[0].strip()
        self.map_data["time"] = time_data[1].strip()
        self.map_data["wait_time"] = map_rows[2].text.strip().split(": ")[1]
        self.map_data["match_time"] = map_rows[3].text.strip().split(": ")[1]

    
    def parse_match_data(self, match_data):
        match_rows = match_data.find("tbody").find_all("tr")
        self.teams = ({}, {})
        for row in match_rows[1:5]:
            record = Match.__make_record__(row)
            # Add record to team 1
            self.teams[0][record["name"]] = record
        for row in match_rows[7:11]:
            record = Match.__make_record__(row)
            # Add record to team 1
            self.teams[1][record["name"]] = record
        score_str = match_rows[6].text.strip().split(":")
        self.scores = (int(scores_str[0]), int(scores_str[1]))
        


    @staticmethod
    def __make_record__(record_data):
        record = {}

        # Lots of ugly parsing. Shoud be able to ignore this
        record["steam_id"] = record_data.attrs["data-steamid64"]
        # I'm iterating through blank elements after this and replacing blanks
        # with 0s. Just making sure if the steam id is off we'll detect it
        # though it should just crash on the line above. This is just to make sure
        # we won't debug for 30 minutes
        assert record["steam_id"] != 0 and record["steam_id"] != ""

        stats_rows = record_data.find_all("td")
        record["ping"] = stats_rows[1].text.strip()
        record["kills"] = stats_rows[2].text.strip()
        record["assists"] = stats_rows[3].text.strip()
        record["deaths"] = stats_rows[4].text.strip()
        record["score"] = stats_rows[7].text.strip()

        # Seems like if stats > 0 then they're blank. Let's fill them in w/ 0s
        for stat in record:
            record[stat] = 0 if not len(record[stat]) else int(record[stat])
        print(record)

        record["name"] = stats_rows[0].text.strip()
        
        # Since these will also be blank but we're indexing we need to do another
        # check
        mvps = stats_rows[5].text.strip()
        print(mvps)
        record["mvps"] = int(mvps[1:]) if len(mvps) > 1 else 0
        hsp = stats_rows[6].text.strip()
        record["hsp"] = int(hsp[:hsp.index("%")]) if len(hsp) > 1 else 0
        
        # Get a ban message -- set default of being banned after game to false
        record["ban_msg"] = stats_rows[8].text.strip()
        ban_attr = stats_rows[8].attrs
        record["banned"] = False
        record["banned_after"] = False

        # If the player has been banned (weird way ik)
        if "style" in ban_attr:
            record["banned"] = True
            style = ban_attr["style"].strip()
            # If the color in the browser of the ban is red they were banned after
            # the game
            record["banned_after"] = style[0: style.index(";")].split(" ")[1] == "red"  
        return record


# Class for a player -- collection of player, summary stats, and individual matches
class Player:
    
    def __init__(self, name, match_list):
        self.name = name
        self.match_list = match_list
        sum_stats()


    def sum_stats():
        return 0


main()