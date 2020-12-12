from bs4 import BeautifulSoup as bs
from glob import glob

# Stores the html files for parsing
DATA_PATH = "./data/players/*.html"

# Main function for compiling data and generating database
def main():
    # player_col - dictionary of steam id -> player object (with matches n stuff)
    # id_name_map - dictionary of steam id -> player name (to solve duplicate names)
    player_col = {}
    id_name_map = {}
    for file_name in glob(DATA_PATH):
        player = gen_player(file_name)
        player_col[player.steam_id] = player
        # I think I'll need this later for the sake of people wanting to access
        # their data. Not using it right now
        id_name_map[player.steam_id] = player.name


# Generates and returns a single player object from a file
def gen_player(file_name):
    player_id, player_name = get_player_info(file_name)
    match_list = get_match_list(file_name)
    return Player(player_id, player_name, match_list)


# Parse file for main name of player at top of file
def get_player_info(file_name):
    # Parse only tag w/ white name at top of page
    with open(file_name, "r") as file:
        soup = bs(file, 'html5lib')
        # Parse ID first
        # TODO: Yes this steam id parsing is ... really hacky. I'm looking for a better way to do it
        # The only other reliable method I've thought of is matching the user's name
        # with their steamid from their first match -- but then you have to pass into
        # the name into the match which breaks the whole concept of the class
        # Just messy all around. I could ask people to submit their id but I don't
        # trust people enough to do this T_T
        # Look everyone makes faults and gets lazy aight
        raw_id = soup.find_all("script", {"type" : "text/javascript"})[-1].text
        tag = "g_steamID = \""
        raw_id = raw_id[raw_id.index(tag) + len(tag):]
        steam_id = int(raw_id[:raw_id.index("\"")])

        # Then get the name
        name = soup.find("a", {"class" : "whiteLink persona_name_text_content"})
        # Strip tabbing(?) stuff off name
        return steam_id, name.text.strip()


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
    

    # Return the team index 
    def get_team(self, player):
        for num in range(2):
            if player in self.teams[num]:
                return num
        raise ValueError("Player not in either team")
        


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
        self.cheaters = 0
        self.cheaters_after = 0
        self.__fill_teams__(0, match_rows[1:5])
        self.__fill_teams__(1, match_rows[7:11])
        score_list = match_rows[6].text.strip().split(":")
        self.scores = (int(score_list[0]), int(score_list[1]))


    # Fill in team dictionary with all players on that team
    def __fill_teams__(self, index, records):
        for row in records:
            record = Match.__make_record__(row)
            # Add record to team 1 using steamid
            if record["banned"]:
                self.cheaters += 1
                self.cheaters_after += 1 if record["banned_after"] else 0
            self.teams[index][record["steam_id"]] = record
        

    # Really big ugly method for compiling data from a game into useable data
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

        record["name"] = stats_rows[0].text.strip()
        
        # Since these will also be blank but we're indexing we need to do another
        # check
        mvps = stats_rows[5].text.strip()
        record["mvps"] = int(mvps[1:]) if len(mvps) > 1 else 0
        hsp = stats_rows[6].text.strip()
        record["hsp"] = int(hsp[:hsp.index("%")]) if len(hsp) > 1 else 0
        
        # Get a ban message -- set default of being banned after game to false
        record["banned"] = False

        # If the player has been banned (weird way ik)
        ban_attr = stats_rows[8].attrs
        if "style" in ban_attr:
            record["banned"] = True

            # Handle string ban message stuff
            ban_txt = stats_rows[8].text.strip()
            # Both, VAC, or Game ban
            record["ban_type"] = "Both" if '&' in ban_txt else ban_txt[:index("-")]
            # Regardless of format the number of days is through this
            # (Thanks Valve for saving me from a headache)
            record["ban_days"] = int(ban_txt[index("-") + 1:])
            
            style = ban_attr["style"].strip()
            # If the color in the browser of the ban is red they were banned after
            # the game
            record["banned_after"] = style[0: style.index(";")].split(" ")[1] == "red"  
        return record


# Class for a player -- collection of player, summary stats, and individual matches
# name - string of the name of the player of focus
# match_list - a string of match objects
# ...
class Player:
    
    def __init__(self, steam_id, name, match_list):
        self.name = name
        self.match_list = match_list
        # TODO: GACKY -- This is kind of awkward as I designed this around keys
        # to accessing the player dictionary around names
        # However -- the steamid makes way more sense. Should be an easy change
        # but I'm just getting this up and running
        self.steam_id = steam_id


    def sum_stats(self):
        return 0


    def __handle_bans__(self):
        # First let's collect all ban matches
        self.ban_stats = {}
        self.__ban_refs__ = []
        for match in self.match_list:
            if match.cheaters > 0:
                self.__ban_refs__.append(match)

        total_vac = 0
        total_game = 0
        total_p_vac = 0
        total_p_game = 0
        total_shared = 0
        total_p_shared = 0

        # Well ... this will be trickier than thought
        # for match in self.__ban_refs__:
        #     cheats = match.cheaters

main()