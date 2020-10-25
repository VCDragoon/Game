import random
import itertools



sunEncounterList = ['Navigational errors caused you to jump too close to the sun.  You must pivot to avoid complete system failure, but to pivot, we will have to expose one of our core systems: either a scanner or the cryopods.  Which do you sacrifice, scanner or cryopods?',
                    'We have miscalculated the length of the last jump, and are too far from the nearest Star to recharge our solar sails.  We have two options: either cannibalize a random scanner (which will irreversibly destroy it) or shut down 1000 cryopods (killing 1000 humans). Which do you sacrifice, scanner or cryopods?']

active_scanner_list = ['geoScanner', 'bioScanner', 'dopplerScanner', 'atmoScanner', 'internalScanner']
passive_scanner_list = ['ssScanner', 'gravScanner', 'tempScanner', 'radioScanner']
direct_scanner_list = [] # not going to implement yet

scanner_list = list(itertools.chain.from_iterable([active_scanner_list, passive_scanner_list]))

internal_systems_list = ['thruster', 'power', 'hull', 'cryoPods']

component_list = list(itertools.chain.from_iterable([scanner_list,internal_systems_list]))


system_list = component_list

lastScanRoll_dict = dict.fromkeys(scanner_list, "none")

class SeekerShip:
    def __init__(self, ship_ID, ship_num):
        self.ship_ID = ship_ID
        self.ship_num = ship_num

    # Replace description with ship ID and number
    def __str__(self):
        return f"Seeker ID: {self.ship_ID}. This is Seeker ship number {self.ship_num} of 10."

def ship_generator(shipID, shipNum):

    Ship = SeekerShip(shipID, shipNum)
    
    for component in component_list:
        if component =='cryoPods':
            setattr(Ship, component, 10000)
        else:
            setattr(Ship, component, 100)
    
    return Ship



class Planet:
    def __init__(self, scanStatus, bio, core, temp, atmo, grav):
        self.bio = bio
        self.core = core
        self.temp = temp
        self.atmo = atmo
        self.grav = grav
        self.scanStatus = scanStatus

    def planet_stats(self):
        print(f'Planet Biology: {self.bio}')
        print(f'Planet Composition: {self.core}')
        print(f'Planet Atmosphere: {self.atmo}')
        print(f'Planet Gravity: {self.grav}')
        
    def update_scanStatus(self, status):
        self.scanStatus = status
        
# auto-generate planets with random characteristics
def planet_generator():
    bio = random.choice(bio_types)
    core = random.choice(core_types)
    temp = random.choice(temp_types)
    atmo = random.choice(atmo_types)
    grav = random.choice(grav_types)
    NewPlanet = Planet("Undiscovered", bio, core, temp, atmo, grav)
    
    Planet.bio_status = "Unknown"
    Planet.core_status = "Unknown"
    Planet.temp_status = "Unknown"
    Planet.atmo_status = "Unknown"
    Planet.grav_status = "Unknown"
    
    return NewPlanet

def scan_for_SS():
    SS_in_range = random.randint(1, 5)
    SS_dict = {}
    for i in range(SS_in_range):
        SS_dict[i] = random.randint(5, 100)
    return SS_dict

def changeScannerHP(ship, scannerType, amount):
    ship.scannerType += amount

def jump(ship):
    # chances of jumping too close or too far from a sun depend on thruster & power status
    modifier = 20
    if ship.power > 97 or ship.power < 3:
        modifier += 10
    
    if ship.thruster > 97 or ship.thruster < 3:
        modifier += 10
    
    sunEncounterChoices = ["yes", "no"]
    sunEncounter = random.choices(sunEncounterChoices, weights=(modifier, 80))[0]

    ship.power = random.randint(1, 100)
    
    if sunEncounter == 'yes':
        encounter = random.choices(sunEncounterList)[0]
        print(encounter)
        return 'yes'

    else:
        encounter = "You have arrived at the next solar system without incident."
        print(encounter)
        return 'no'

def ship_attributes(ship):
    for attr, value in ship.__dict__.items():
        print(attr, value)
def planet_attributes(planet):
    for attr, value in planet.__dict__.items():
            print(attr, value)

def jump_encounter():
    while(1):
        try:
            action = input('>>').lower()

            if 'scan' in action:
                randBio = random.randrange(10, 25)
                print(f'Bioscanner has been damaged by {randBio}%!')
                Seeker1.bioScanner -= randBio
                break

            if 'cryo' in action:
                randCryo = random.randrange(90, 410)
                print(f'We have lost {randCryo} humans in cryopods!')
                Seeker1.cryoPods -= randCryo
                break

        except: 
            print("That's not a valid action, you tool.")

def player_action():
    while(1):
        try:
            action = input('>').lower()
            
            if action == 'q' or action == 'quit':
                return 'quit'

            if action =='jump':
                return 'jump'

            if action == 'status':
                ship_status(Seeker1)
                return 'continue'

        except: 
            print("That's not a valid move, you tool.")

def play_game():
    while(1):
        try:
            print('Type \'jump\' to jump to the next solar system, \'status\' to see the status of your ship!, or \'quit\' to exit!')
            keep_playing = player_action()
            if keep_playing=='quit': break
            elif keep_playing=='continue': continue
            elif keep_playing=='jump':
                if jump(Seeker1)=='yes':
                    jump_encounter()
                    continue
                else:
                    continue
            else:
                print("Unknown command - enter a known commmand you tool.")
        except KeyError:
            print("Unknown command - enter a known commmand you tool.")
            break

def ship_status(Ship):
    for component in system_list:
        status = getattr(Ship, component)
        if component == "cryoPods":
            print(f'There are {status} cryopods remaining')
        else:
            print(f'The {component} system is at {status}% functionality')

def scan_error(scanner):
    if scanner > 80:
        return 10
    elif scanner > 50:
        return 0
    elif scanner > 20:
        return -30
    else:
        return -50

def run_scan(Ship, scanner_list):
    for scanner in scanner_list:
        status = getattr(Ship, scanner)
        modifier = scan_error(status)
        roll = rollDie(100) + modifier
        result = lookupTable(roll, scanner)
        lastScanRoll_dict[scanner] = result

def run_all_scans(Ship):
    run_scan(Ship, active_scanner_list)
    run_scan(Ship, passive_scanner_list)
    return lastScanRoll_dict
    
def show_last_scan():
    print(lastScanRoll_dict)

bio_types = ['None', 'Isotopes', 'Biochemical Activity', 'Organics']

def lookupTable(roll, scanner):
    if scanner == "bioScanner":
        return bio_roll(roll)
    elif scanner == "geoScanner":
        return geo_roll(roll)
    elif scanner == "tempScanner":
        return temp_roll(roll)
    elif scanner == "atmoScanner":
        return atmo_roll(roll)
    elif scanner == "gravScanner":
        return grav_roll(roll)
    else:
        return "PLACEHOLDER"
    
def bio_roll(roll):
    if roll > 90:
        return "Organic Plant and Animal Life"
    elif roll > 70:
        return "Unspecified Organic Life"
    elif roll > 50:
        return "Biochemical Activity"
    elif roll > 35:
        return "Biological Isotopes"
    elif roll > 20:
        return "No biological signs detected"
    else:
        return "Scanner Error"
    

def geo_roll(roll):
    if roll > 90:
        return "Terrestrial - Land and Oceans"
    elif roll > 70:
        return "Terrestrial - Some Land, Mostly Ocean"
    elif roll > 60:
        return "Liquid"
    elif roll > 45:
        return "Frozen Ice"
    elif roll > 25:
        return "Gas"
    else:
        return "Scanner Error"
    
def temp_roll(roll):
    if roll > 90:
        return "Temperate"
    elif roll > 70:
        return "Roaming Temperate Zones"
    elif roll > 55:
        return "Hot"
    elif roll > 40:
        return "Cold"
    elif roll > 30:
        return "Scorching"
    elif roll > 20:
        return "Freezing"
    else:
        return "Scanner Error"
    
def atmo_roll(roll):
    if roll > 90:
        return "Breathable"
    elif roll > 60:
        return "Mildly Toxic"
    elif roll > 40:
        return "No Atmosphere"
    else:
        return "Scanner Error"
    
def grav_roll(roll):
    if roll > 90:
        return "Earth-like Gravity"
    elif roll > 70:
        return "1.5x Earth-like Gravity"
    elif roll > 50:
        return "1/2 Earth-like Gravity"
    elif roll > 40:
        return "Extremely High Gravity"
    elif roll > 30:
        return "Extremely Low Gravity"
    else:
        return "Scanner Error"
    
def internal_roll(roll):
    if roll > 75:
        run_scan(internal_systems_list)