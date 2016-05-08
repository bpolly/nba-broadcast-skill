#!/bin/env python
###############################
# NBA Broadcast Schedule Scraper
# By Braden Polly
# 5/6/16
# python2.7
###############################
from lxml import html
import sys
import json
import requests
import time

#####
# Possible Input Cases
###
# What channel is the cavs game on tonight/tomorrow/next week?
# When is the next cavs game on ABC?
# Do the cavs play on ESPN tonight?

link = "http://www.nba.com/schedules/national_tv_schedule/"
page = requests.get(link)
tree = html.fromstring(page.content)
network_options = ['abc', 'tnt', 'espn']
team_nickname_list = {
    "atlanta hawks": ["atlanta hawks", "atlanta", "hawks"],
    "boston celtics": ["boston celtics", "boston", "celtics"],
    "brooklyn nets": ["brooklyn nets", "brooklyn", "nets", "new jersey"],
    "charlotte bobcats": ["charlotte bobcats", "charlotte", "bobcats"],
    "chicago bulls": ["chicago bulls", "chicago", "bulls"],
    "cleveland cavaliers": ["cleveland cavaliers", "cleveland", "cavaliers", "cavs"],
    "dallas mavericks": ["dallas mavericks", "dallas", "mavericks", "mavs"],
    "denver nuggets": ["denver nuggets", "denver", "nuggets", "nugs"],
    "detroit pistons": ["detroit pistons", "detroit", "pistons"],
    "golden state warriors": ["golden state warriors", "golden state", "warriors", "dubs"],
    "houston rockets": ["houston rockets", "houston", "rockets"],
    "indiana pacers": ["indiana pacers", "indiana", "pacers"],
    "la clippers": ["la clippers","los angeles clippers", "clippers", "clips"],
    "la lakers": ["la lakers", "lakers", "los angeles lakers"],
    "memphis grizzlies": ["memphis grizzlies", "memphis", "grizzlies", "grizz"],
    "miami heat": ["miami heat", "miami", "heat"],
    "milwaukee bucks": ["milwaukee bucks", "milwaukee", "bucks"],
    "minnesota timberwolves": ["minnesota timberwolves", "minnesota", "wolves", "timberwolves"],
    "new orleans hornets": ["new orleans hornets", "orleans", "hornets"],
    "new york knicks": ["new york knicks", "knicks", "new york", "knickerbockers"],
    "oklahoma city thunder": ["oklahoma city thunder", "oklahoma", "okc", "thunder", "sonics"],
    "orlando magic": ["orlando magic", "orlando", "magic"],
    "philadelphia sixers": ["philadelphia sixers","philadelphia", "seventy sixers", "sixers"],
    "phoenix suns": ["phoenix suns", "phoenix", "suns"],
    "portland trail blazers": ["portland trail blazers", "portland", "trail", "blazers", "fourth seed"],
    "sacramento kings": ["sacramento kings", "sacramento", "kings"],
    "san antonio spurs": ["san antonio spurs", "san antonio", "spurs"],
    "toronto raptors": ["toronto raptors", "toronto", "raptors", "raps"],
    "utah jazz": ["utah jazz", "utah", "jazz"],
    "washington wizards": ["washington wizards", "washington", "wizards"]
}
games = {}


def populate_game_list():
    games_list = tree.xpath("//div[@id='scheduleMain']/table//tr[@class!='title' and @class!='header' or not(@class)]")
    last_date=""
    for i in range(1, len(games_list)):
        time_xpath_string = "//div[@id='scheduleMain']/table//tr[@class!='title' and @class!='header' or not(@class)][%i]/td[@class='tm']/text()" % i
        teams_xpath_string = "//div[@id='scheduleMain']/table//tr[@class!='title' and @class!='header' or not(@class)][%i]/td[@class='gm']//a/text()" % i
        networks_xpath_string = "//div[@id='scheduleMain']/table//tr[@class!='title' and @class!='header' or not(@class)][%i]/td[@class='ntv']/img/@src" % i
        date_xpath_string = "//div[@id='scheduleMain']/table//tr[@class!='title' and @class!='header' or not(@class)][%i]/td[@class='dt']/text()" % i

        date_node = tree.xpath(date_xpath_string)
        if(len(date_node[0]) < 3):
            date = last_date
        else:
            date = date_node[0]
            last_date = date
        time_node = tree.xpath(time_xpath_string)
        time = time_node[0]
        teams_node = tree.xpath(teams_xpath_string)
        networks_node = tree.xpath(networks_xpath_string)
        networks = find_networks(networks_node)

        games[i] = {}
        games[i]["date"] = date
        games[i]["time"] = time
        games[i]["teams"] = teams_node
        games[i]["networks"] = networks

        # #print path
        # print "Date: " + str(date)
        # print "Time: " + str(time)
        # print "teams: " + str(teams_node)
        # print "networks: " + str(networks)
        #print games

    games_odd = tree.xpath("//tr[@class='odd']/td[@class='gm']//a/text()")
    games_even = tree.xpath("//tr[not(@class='odd')]/td[@class='gm']//a/text()")



    games_total_count = (len(games_odd) + len(games_even))/2
    first_game = tree.xpath("//tr[3][not(@class)]/td[@class='gm']//a/text()")
    first_game_date = tree.xpath("//tr[3][not(@class)]/td[@class='dt']/text()")
    first_game_networks = tree.xpath("//tr[3][not(@class)]/td[@class='ntv']/img/@src")

# pass in list of urls for network images
# look for network options in links
# if found, return network option
def find_networks(network_list):
    found_networks = []
    for network_link in network_list:
        network_link = network_link.lower()
        for network_option in network_options:
            if (network_option in network_link):
                found_networks.append(network_option)
    return found_networks

def find_games_given_team(team):
    team_games = {}
    count = 0
    # for each game
    for i in range(1, len(games)):
        # if chosen team listed in game teams
        if team in games[i]["teams"]:
            team_games[count]={}
            team_games[count]=games[i]
            count += 1
    return team_games

def find_todays_games():
    todays_games = {}
    todays_date = time.strftime("%a, %B %-d")
    print todays_date
    count = 0
    for i in range(1, len(games)):
        if todays_date == games[i]["date"]:
            todays_games[count]={}
            todays_games[count]=games[i]
            count += 1
    return todays_games

def print_json(games):
    print json.dumps(games, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)

def build_output(game):
    teams = game["teams"]
    time = game["time"]
    network = game["networks"][0].upper()
    output = "%s plays %s tonight at %s on %s" % (teams[0], teams[1], time, network)
    print output

def find_team_given_nickname(nickname):
    found_team = ""
    # for all teams
    for team in team_nickname_list:
        # if nickname is in that team's nickname list
        if nickname in team_nickname_list[team]:
            found_team = team
            break
    return team

def parse_input(input):
    # Test - what channel does Cleveland play on tonight?
    # look for "what channel"

    possible_teams = find_teams_referenced()
    possible_beginnings = ["what channel", "do the"]


# def find_teams_referenced(input):
#     possible_teams
#     for team in team_list:
#         for nickname in team:
#             if (nickname in input) and (team !in possible_teams):
#                 possible_teams.append(team)

if __name__ == "__main__":
    populate_game_list()
    cavs_games = find_games_given_team("Golden State")
    #print_json(find_todays_games())
    #print_json(team_nickname_list)
    #build_output(cavs_games[0])
    #print(team_nickname_list["cleveland cavaliers"])
    nickname_given = raw_input('Enter a team name: ')
    print find_team_given_nickname(nickname_given)
