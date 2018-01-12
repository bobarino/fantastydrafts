import sys
import os
import psycopg2
from collections import defaultdict
from fantasy_data_spider import settings
import datetime
import csv
from subprocess import Popen
import shlex
import time

players = defaultdict(list)
espn_table = settings.ESPN_TABLE
dk_table = settings.DK_TABLE
possible_pos = settings.POSSIBLE_POS
budget = settings.BUDGET


'''Creates rosters filling up all possible positions with the best available
    points per dollar players'''
def pick_greedy_roster(players_cur, positions, total_weight):
    roster = []
    flex = []
    pos = list(positions)
    weight = 0
    value = 0
    for k in players_cur:
        playername = k[0]
        if weight + get_salary(playername) <= total_weight:
            if get_position(playername) in pos:
                roster.append([playername, get_position(playername)])
                weight = weight + get_salary(playername)
                value = value + get_all_points(playername)
                pos.remove(get_position(playername))
            elif "FLEX" in pos and (get_position(playername) == "RB" or get_position(playername) == "WR" or get_position(playername) == "TE"):
                roster.append([playername, "FLEX"])
                flex.append(playername)
                weight = weight + get_salary(playername)
                value = value + get_all_points(playername)
                pos.remove("FLEX")
            elif get_position(playername) == "RB" or get_position(playername) == "WR" or get_position(playername) == "TE":
                flex.append(playername)
    if len(pos) > 0 and len(players_cur) > 0:
        players_cur.pop(0)
        return pick_greedy_roster(players_cur, possible_pos, budget)
    '''So the roster doesn't default pick the Tight End (only 1 position to fill) as the FLEX the majority of the time'''
    for r in roster:
        if r[1] == "FLEX":
            weight = weight - get_salary(r[0])
            value = value - get_all_points(r[0])
            max_flex = [r[0], get_all_points(r[0])]
            roster.remove(r)
            for f in flex:
                if weight + get_salary(f) <= total_weight and get_all_points(f) > max_flex[1]:
                    max_flex = [f, get_all_points(f)]
            roster.append([max_flex[0], "FLEX"])
            weight = weight + get_salary(max_flex[0])
            value = value + max_flex[1]
            break
    roster.append(weight)
    roster.append(value)
    return roster

'''Creates multiple rosters, popping off the most efficient point per dollar player every time
    (read in docs why this is applicable)'''
def create_multiple_rosters(players):
    players_sorted = sorted(players.iteritems(), key=lambda (k,v):((get_avg_points_per_game(k) + (get_points_tot(k)))/get_salary(k)), reverse=True)
    rosters = []
    while players_sorted:
       rosters.append(pick_greedy_roster(players_sorted, possible_pos, budget))
       if len(players_sorted) == 0:
           break
       else:
           players_sorted.pop(0)
    return rosters

'''Method picking the best roster based off of the total projected points each roster contains'''
def get_best_roster(rosters):
    max_roster_val = 0
    max_roster = []
    for r in rosters:
        if r[-1] > max_roster_val:
            max_roster_val = r[-1]
            max_roster = r
    return max_roster

'''Optimizes the final roster by individually picking better players until salary is maxed out to mitigate efficiency effect further'''
def optimize_chosen_roster(roster):
    players_sorted = sorted(players.iteritems(), key=lambda (k,v):((get_avg_points_per_game(k) + (get_points_tot(k)))/get_salary(k)), reverse=True)
    for i in range(len(roster) - 3):
        for new_p in players_sorted:
            remaining_budget = 50000 - roster[-2] + get_salary(roster[i][0])
            playername = new_p[0]
            check = 0
            for x in range(len(roster) - 3):
                if playername == roster[x][0]:
                    check = 1
            if check == 0 and roster[i][1] == get_position(playername) and get_all_points(playername) > get_all_points(roster[i][0]) and remaining_budget - get_salary(playername) >= 0:
                roster[-2] = roster[-2] - get_salary(roster[i][0]) + get_salary(playername)
                roster[-1] = roster[-1] - get_all_points(roster[i][0]) + get_all_points(playername)
                roster[i] = [playername, get_position(playername)]
                break
    return roster

'''Fills the player dictionary with all info from the database'''
def fill_player_dict(conn):
    cur = conn.cursor()

    cur.execute("SELECT * FROM " + dk_table + " a JOIN " + espn_table + " b ON (LTRIM(RTRIM(a.name)) = LTRIM(RTRIM(b.playername)) AND LTRIM(RTRIM(a.position)) = LTRIM(RTRIM(b.pos))) WHERE status_type = 'y';")

    for position, name, salary, game_info, avg_points_per_game, team_abbrev, parsed_on, ffl_source, playername, team, pos, status_type, passing_c, passing_a, passing_yds, passing_td, passing_int, rushing_r, rushing_yds, rushing_td, receiving_rec, receiving_yds, receiving_tot, pts_total, parsed_on in cur.fetchall():
        players[name].append(position)
        players[name].append(int(salary))
        players[name].append(game_info)
        players[name].append(float(avg_points_per_game))
        players[name].append(team_abbrev)
        players[playername].append(status_type)
        players[playername].append(passing_c)
        players[playername].append(passing_a)
        players[playername].append(passing_yds)
        players[playername].append(passing_td)
        players[playername].append(passing_int)
        players[playername].append(rushing_r)
        players[playername].append(rushing_yds)
        players[playername].append(rushing_td)
        players[playername].append(receiving_rec)
        players[playername].append(receiving_yds)
        players[playername].append(receiving_tot)
        espn_score = 0
        if position.strip() != "DST":
            three_hundred_qb = 0
            one_hundred_rb = 0
            one_hundred_wr = 0
            if passing_yds >= 300:
                three_hundred_qb = 3
            if rushing_yds >= 100:
                one_hundred_rb = 3
            if receiving_yds >= 100:
                one_hundred_wr = 3
            espn_score = (4 * passing_td) + (0.04 * passing_yds) + (three_hundred_qb) + (-1 * passing_int) + (6 * rushing_td) + (0.1 * rushing_yds) + (one_hundred_rb) + (6 * receiving_tot) + (0.1 * receiving_yds) + (one_hundred_wr) + (receiving_rec)
        else:
            espn_score = pts_total
        players[playername].append(espn_score)

def fill_draft_kings_db(file_name, connection):
    drop_dk_table = """DROP TABLE IF EXISTS """ + dk_table + """;"""
    create_dk_table = """CREATE TABLE IF NOT EXISTS """ + dk_table + """ (position varchar, name varchar, salary varchar, game_info varchar, avg_points_per_game varchar, team_abbrev varchar, parsed_on varchar); """
    cur = connection.cursor()
    cur.execute(drop_dk_table)
    connection.commit()
    cur.execute(create_dk_table)
    connection.commit()
    with open(file_name) as dk_csv:
        data = csv.reader(dk_csv)
        next(data, None)
        for row in data:
            position = row[0]
            name = row[1]
            salary = row[2]
            game_info = row[3]
            avg_points_per_game = row[4]
            team_abbrev = row[5]
            parsed_on = datetime.datetime.now()
            insert_dk = """INSERT INTO """ + dk_table + """ (position, name, salary, game_info, avg_points_per_game, team_abbrev, parsed_on) VALUES(%s, %s, %s, %s, %s, %s, %s)"""
            cur.execute(insert_dk, (position, name, salary, game_info, avg_points_per_game, team_abbrev, parsed_on))
            connection.commit()

'''Gets position'''
def get_position(name):
    return players[name][0]

'''Gets salary'''
def get_salary(name):
    return players[name][1]

'''Gets game info'''
def get_game_info(name):
    return players[name][2]

'''Gets average points per game'''
def get_avg_points_per_game(name):
    return players[name][3]

'''Gets team'''
def get_team_abbrev(name):
    return players[name][4]

'''Gets week status'''
def get_status_type(name):
    return players[name][5]

'''Gets passing completions'''
def get_passing_c(name):
    return players[name][6]

'''Gets passing attempts'''
def get_passing_a(name):
    return players[name][7]

'''Gets passing yards'''
def get_passing_yds(name):
    return players[name][8]

'''Gets passing touchdowns'''
def get_passing_td(name):
    return players[name][9]

'''Gets passing interceptions'''
def get_passing_int(name):
    return players[name][10]

'''Gets rushing reps'''
def get_rushing_r(name):
    return players[name][11]

'''Gets rushing yards'''
def get_rushing_yds(name):
    return players[name][12]

'''Gets rushing touchdowns'''
def get_rushing_td(name):
    return players[name][13]

'''Gets receptions'''
def get_receiving_rec(name):
    return players[name][14]

'''Gets receiving yards'''
def get_receiving_yds(name):
    return players[name][15]

'''Gets receiving touchdowns'''
def get_receiving_tot(name):
    return players[name][16]

'''Gets total projected points'''
def get_points_tot(name):
    return players[name][17]

'''Gets all projected points from all sources'''
def get_all_points(name):
    return get_avg_points_per_game(name) + get_points_tot(name)

'''Pass in a 1 to update scraped data or a 0 to not update data.
    Follow this with the name of the csv file from DraftKings to update the DraftKings table'''
if __name__ == "__main__":
    try:
        conn = psycopg2.connect("dbname='fantasyfb' user='postgres' host='localhost' password='bandit'")
    except:
        print "I am unable to connect to the database"
    if len(sys.argv) > 1:
        if float(sys.argv[1]) == 1:
            cmd = shlex.split("scrapy crawl espn")
            p = Popen(cmd)
            p.wait()
            time.sleep(12)
        if len(sys.argv) > 2:
            fill_draft_kings_db(sys.argv[2], conn)
            time.sleep(12)

    fill_player_dict(conn)
    print optimize_chosen_roster(get_best_roster(create_multiple_rosters(players)))
