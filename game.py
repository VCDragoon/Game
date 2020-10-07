#---------------------------------------------------------------------------------------#
# Variables
#---------------------------------------------------------------------------------------#

# Ship Class
class SeekerShip:
    def __init__(self, ship_ID, ship_num, bioSig_scanner, pcore_scanner, SS_scanner, thrusterHP
                    activeCryopods, battery):
        self.ship_ID = ship_ID
        self.ship_num = ship_num

        self.bioSig_scanner_hp = bioSig_scanner_hp
        self.pcore_scanner_hp = pcore_scanner_hp
        self.SS_scanner_hp = SS_scanner_hp
        self.thruster_hp = thruster_hp

        self.battery = battery
        self.activeCryopods = activeCryopods

    def scanner_error(self, scanner):
        # takes in a scanner var and returns probability of error
        if scanner > 80 then:
            return 1
        elif scanner > 50 then:
            return .75
        elif scanner > 20 then:
            return .5
        else:
            return .25
    
    def 

    
    # Replace description with ship ID and number
    def __str__(self):
        return f"Seeker Ship No. {self.ship_ID}. Seeker {self.ship_num} of 10."

