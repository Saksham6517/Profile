# ==============================================================
#   BENNETT SPORTS - Court Booking and Player Matchmaker
#   Sports    : Badminton (main sport) and Tennis
#   Game type : Singles only (2 players per court)
#   How to run: open this file in IDLE and press F5
# ==============================================================

import json                     # used to save and load our data in a file
from datetime import datetime   # used to check that a date is typed correctly

DATA_FILE = "bennett_data.json"    # the file where all data is saved

# Court name of each sport (a dictionary)
COURTS = {
    "Badminton": "B1",
    "Tennis": "T1"
}

SPORTS = ["Badminton", "Tennis"]          # Badminton comes first (main sport)

SLOTS = ["06:00-07:00", "07:00-08:00", "16:00-17:00", "17:00-18:00",
         "18:00-19:00", "19:00-20:00", "20:00-21:00"]

SKILLS = ["Beginner", "Intermediate", "Advanced"]

PLAYERS_PER_GAME = 2    # singles game = 2 players


# --------------------------------------------------------------
#   FILE HANDLING
# --------------------------------------------------------------

def load_data():
    # Try to open the data file. If it does not exist yet
    # (first time running), start with empty data.
    try:
        file = open(DATA_FILE, "r")
        data = json.load(file)
        file.close()
    except FileNotFoundError:
        data = {"players": {}, "bookings": []}
    return data


def save_data(data):
    # Write all players and bookings into the file
    file = open(DATA_FILE, "w")
    json.dump(data, file, indent=4)
    file.close()


# --------------------------------------------------------------
#   INPUT HELPER
# --------------------------------------------------------------

def choose_from_list(title, options):
    # Shows a numbered list and returns the option the user picks
    print(title)
    for i in range(len(options)):
        print("  " + str(i + 1) + ". " + options[i])

    while True:                       # keep asking until input is correct
        try:
            choice = int(input("Enter number: "))
            if choice >= 1 and choice <= len(options):
                return options[choice - 1]
            else:
                print("Please pick a number from the list.")
        except ValueError:            # user typed letters instead of a number
            print("Please type a number, not letters.")


# --------------------------------------------------------------
#   LOGIN / REGISTER
# --------------------------------------------------------------

def login(data):
    name = input("Enter your name: ").strip()
    while name == "":
        name = input("Name cannot be empty. Enter your name: ").strip()

    if name in data["players"]:
        print("Welcome back, " + name + "!")
    else:
        print("New player! Let's create your profile.")
        enrollment = input("Enrollment number: ")
        sport = choose_from_list("Your main sport:", SPORTS)
        skill = choose_from_list("Your skill level:", SKILLS)

        # each player is stored as a dictionary
        data["players"][name] = {
            "enrollment": enrollment,
            "sport": sport,
            "skill": skill
        }
        save_data(data)
        print("Profile created! Welcome, " + name + "!")
    return name


# --------------------------------------------------------------
#   CLASH CHECKS
# --------------------------------------------------------------

def is_player_busy(data, name, date, slot):
    # Checks if the player already has a game at this date and slot
    for booking in data["bookings"]:
        if booking["date"] == date and booking["slot"] == slot:
            if name in booking["players"]:
                return True
    return False


def is_slot_taken(data, date, slot):
    # Only ONE booking is allowed on a date and time slot.
    # This loop checks if someone has already booked this date + slot.
    for booking in data["bookings"]:
        if booking["date"] == date and booking["slot"] == slot:
            return True
    return False


def read_date():
    # Asks for a date and makes sure it is in DD-MM-YYYY format,
    # so "23-11-2026" and "23/11/2026" are not treated as different dates
    while True:
        date = input("Enter date (DD-MM-YYYY): ").strip()
        try:
            datetime.strptime(date, "%d-%m-%Y")   # gives an error if the date is wrong
            return date
        except ValueError:
            print("Wrong date. Please type it like 23-11-2026.")


# --------------------------------------------------------------
#   1. BOOK A COURT
# --------------------------------------------------------------

def book_court(data, name):
    sport = choose_from_list("Choose sport:", SPORTS)
    date = read_date()
    slot = choose_from_list("Choose time slot:", SLOTS)

    if is_player_busy(data, name, date, slot):
        print("You already have a game on " + date + " at " + slot + "!")
        return

    if is_slot_taken(data, date, slot):
        print("Sorry, " + slot + " on " + date + " is already booked.")
        print("Please choose another time slot or date.")
        return

    court = COURTS[sport]

    booking_id = "BK" + str(len(data["bookings"]) + 1)
    booking = {
        "id": booking_id,
        "sport": sport,
        "court": court,
        "date": date,
        "slot": slot,
        "players": [name],          # the person who booked is the host
        "status": "OPEN"            # OPEN = still needs 1 more player
    }
    data["bookings"].append(booking)
    save_data(data)
    print("Booking " + booking_id + " created on court " + court + ".")
    print("It is now on the Match Finder Board, waiting for 1 opponent.")


# --------------------------------------------------------------
#   2. MATCH FINDER BOARD
# --------------------------------------------------------------

def show_board(data):
    choice = choose_from_list("Show games for:", ["All sports", "Badminton", "Tennis"])

    print()
    print("ID     Sport       Court  Date         Slot          Host")
    print("-----------------------------------------------------------")
    count = 0
    for booking in data["bookings"]:
        if booking["status"] == "OPEN":
            if choice == "All sports" or choice == booking["sport"]:
                print(booking["id"].ljust(7) + booking["sport"].ljust(12) +
                      booking["court"].ljust(7) + booking["date"].ljust(13) +
                      booking["slot"].ljust(14) + booking["players"][0])
                count = count + 1

    if count == 0:
        print("No open games right now.")


# --------------------------------------------------------------
#   3. MATCH SCORE AND RECOMMENDATIONS
# --------------------------------------------------------------

def match_score(data, name, booking):
    # Gives a score out of 100 for how well a game suits the player
    me = data["players"][name]
    host = data["players"][booking["players"][0]]
    score = 0

    # Rule 1: skill match (60 marks)
    gap = abs(SKILLS.index(me["skill"]) - SKILLS.index(host["skill"]))
    if gap == 0:
        score = score + 60       # same level
    elif gap == 1:
        score = score + 30       # one level apart
    else:
        score = score + 0        # Beginner vs Advanced

    # Rule 2: sport match (40 marks)
    if booking["sport"] == me["sport"]:
        score = score + 40

    return score


def recommend_games(data, name):
    print()
    print("Recommended games for " + name + " (score out of 100):")
    best_score = -1
    best_id = ""

    for booking in data["bookings"]:
        if booking["status"] == "OPEN" and name not in booking["players"]:
            if is_player_busy(data, name, booking["date"], booking["slot"]) == False:
                score = match_score(data, name, booking)
                print("  " + booking["id"] + "  " + booking["sport"] + "  " +
                      booking["date"] + "  " + booking["slot"] +
                      "  host: " + booking["players"][0] + "  ->  " + str(score))
                if score > best_score:
                    best_score = score
                    best_id = booking["id"]

    if best_id == "":
        print("  No games available for you right now.")
    else:
        print("Best match for you: " + best_id + " with " + str(best_score) + "/100")


# --------------------------------------------------------------
#   4. JOIN A GAME
# --------------------------------------------------------------

def join_game(data, name):
    booking_id = input("Enter booking ID to join (e.g. BK1): ").strip().upper()

    # find the booking with this ID
    found = None
    for booking in data["bookings"]:
        if booking["id"] == booking_id:
            found = booking

    if found == None:
        print("Booking " + booking_id + " does not exist.")
    elif name in found["players"]:
        print("You are already in this game.")
    elif found["status"] == "FULL":
        print("Sorry, this game is already full.")
    elif is_player_busy(data, name, found["date"], found["slot"]):
        print("You already have another game at this time.")
    else:
        found["players"].append(name)
        if len(found["players"]) == PLAYERS_PER_GAME:
            found["status"] = "FULL"
        save_data(data)
        print("You joined " + booking_id + "! Your opponent is " + found["players"][0] + ".")


# --------------------------------------------------------------
#   5. MY GAMES
# --------------------------------------------------------------

def my_games(data, name):
    print()
    print("Your games:")
    count = 0
    for booking in data["bookings"]:
        if name in booking["players"]:
            print("  " + booking["id"] + "  " + booking["sport"] + "  court " +
                  booking["court"] + "  " + booking["date"] + "  " +
                  booking["slot"] + "  players: " + ", ".join(booking["players"]) +
                  "  [" + booking["status"] + "]")
            count = count + 1
    if count == 0:
        print("  You have no games yet.")


# --------------------------------------------------------------
#   MAIN PROGRAM (the menu)
# --------------------------------------------------------------

def main():
    print("========================================")
    print("   BENNETT SPORTS - Singles Matchmaker  ")
    print("========================================")

    data = load_data()
    name = login(data)

    running = True
    while running:                  # menu keeps showing until user exits
        print()
        print("----------- MENU -----------")
        print("1. Book a court")
        print("2. Match Finder Board")
        print("3. Recommended games for me")
        print("4. Join a game")
        print("5. My games")
        print("6. Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            book_court(data, name)
        elif choice == "2":
            show_board(data)
        elif choice == "3":
            recommend_games(data, name)
        elif choice == "4":
            join_game(data, name)
        elif choice == "5":
            my_games(data, name)
        elif choice == "6":
            print("Data saved. Goodbye, " + name + "!")
            running = False
        else:
            print("Invalid choice. Please enter a number from 1 to 6.")


main()