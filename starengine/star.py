from . import dice
from . import planetsystem
from .tables import StEvoTable, IndexTable, SequenceTable


class Star:
    roller = dice.DiceRoller()

    def __init__(self, age):
        if age <= 0:
            raise ValueError("Age needs to be a positive number.")

        self.hasforbiddenzone = False
        self.forbiddenzone = None
        self.age = age
        self.StEvoIndex = self.make_index()
        self.SeqIndex = self.find_sequence()
        self.mass = self.make_mass()
        self.luminosity = self.make_luminosity()
        self.temperature = self.make_temperature()
        self.radius = self.make_radius()
        self.innerlimit, self.outerlimit = self.compute_orbit_limits()
        self.snowline = self.compute_snow_line()
        self.letter = 'A'
        self.star_type = self.get_star_type()
        self.planetsystem = None

    def __repr__(self):
        return repr((self.mass, self.luminosity, self.temperature))

    def print_info(self):
        print("  Star {} Info".format(self.letter))
        print("  ---------")
        print("       Mass:\t{}".format(self.mass))
        print("   Sequence:\t{}".format(SequenceTable[self.SeqIndex]))
        print(" Luminosity:\t{}".format(self.luminosity))
        print("Temperature:\t{}".format(self.temperature))
        print("     Radius:\t{}".format(round(self.radius, 6)))
        # print("       Type:\t{}".format(self.__type))

        # Nicely formatted orbital zone
        norzone = (round(self.innerlimit, 3), round(self.outerlimit, 3))
        print("Orbital Zne:\t{}".format(norzone))
        # Nicely formatted snow line
        nsnline = round(self.snowline, 3)
        print("  Snow Line:\t{}".format(nsnline))
        if self.hasforbiddenzone:
            # Nicely formatted forbidden zone
            nforb = [round(fz) for fz in self.forbiddenzone]
            print(" Forbid Zne:\t{}".format(nforb))
        self.planetsystem.printinfo()
        print("  ---------\n")

    def get_mass(self) -> float:
        return self.mass

    def get_age(self):
        return self.age

    def make_index(self) -> int:
        # Roll to randomly select the index for the StEvoTable
        diceroll1 = self.roller.roll_dice(3, 0)
        diceroll2 = self.roller.roll_dice(3, 0)
        return IndexTable[diceroll1][diceroll2]

    def make_mass(self) -> float:
        """
        Find or calculate the mass appropriate to the star.
        :return: The mass of the star, relative to the sun.
        """
        if self.SeqIndex == 3:  # The star is a white dwarf, and its mass is treated specially
            return self.roller.roll_dice(2, -2) * 0.05 + 0.9
        return StEvoTable['mass'][self.StEvoIndex]

    def find_sequence(self) -> int:
        # Check what sequences are available
        seq = StEvoTable['internaltype'][self.StEvoIndex]
        age = self.age
        sequence_index = 0

        # If we have a main-sequence-only star that can decay to a white dwarf
        if seq == 1:
            span = StEvoTable['Mspan'][self.StEvoIndex]
            if age > span:
                sequence_index = 3

        # If we have a star with sub- and giant type capabilities
        elif seq == 2:
            mspan = StEvoTable['Mspan'][self.StEvoIndex]
            sspan = StEvoTable['Sspan'][self.StEvoIndex]
            gspan = StEvoTable['Gspan'][self.StEvoIndex]
            if age > (mspan + sspan + gspan):
                sequence_index = 3
            elif age > (mspan + sspan):
                sequence_index = 2
            elif age > mspan:
                sequence_index = 1
        return sequence_index

    def get_sequence(self) -> str:
        return SequenceTable[self.SeqIndex]

    def make_luminosity(self):
        seq = self.SeqIndex
        age = self.age
        lmin = StEvoTable['Lmin'][self.StEvoIndex]
        lmax = StEvoTable['Lmax'][self.StEvoIndex]
        mspan = StEvoTable['Mspan'][self.StEvoIndex]
        lum = 0
        if seq == 0:
            # For stars with no Mspan value (mspan == 0)
            if mspan == 0:
                lum = lmin
            else:
                lum = lmin + (age / mspan * (lmax - lmin))
        elif seq == 1:  # Subgiant star
            lum = lmax
        elif seq == 2:  # Giant star
            lum = 25 * lmax
        elif seq == 3:  # White dwarf
            lum = 0.001

        return lum

    def make_temperature(self):
        seq = self.SeqIndex
        age = self.age
        #  lmin = StEvoTable['Lmin'][self.StEvoIndex]
        #  lmax = StEvoTable['Lmax'][self.StEvoIndex]
        mspan = StEvoTable['Mspan'][self.StEvoIndex]
        sspan = StEvoTable['Sspan'][self.StEvoIndex]
        #  gspan = StEvoTable['Gspan'][self.StEvoIndex]
        if seq == 0:
            temp = StEvoTable['temp'][self.StEvoIndex]
        elif seq == 1:  # Subgiant star
            m = StEvoTable['temp'][self.StEvoIndex]
            a = age - mspan
            s = sspan
            temp = m - (a / s * (m - 4800))
        elif seq == 2:  # Giant star
            temp = self.roller.roll_dice(2, -2) * 200 + 3000
        elif seq == 3:  # White dwarf
            temp = 8000  # Not defined in the rulebook, so arbitrarily assigned

        return temp

    def get_temp(self):
        return self.temperature

    def make_radius(self):
        lum = self.luminosity
        temp = self.temperature
        rad = 155000 * lum ** 0.5 / temp ** 2
        if self.SeqIndex == 3:  # If we're a white dwarf
            rad = 0.000043  # The size is comparable to the one of Earth

        return rad

    def compute_orbit_limits(self):
        mass = self.mass
        lum = self.luminosity

        # Inner Orbital Limit
        inner1 = 0.1 * mass
        inner2 = 0.01 * lum ** 0.5
        if inner1 > inner2:
            inner_limit = inner1
        else:
            inner_limit = inner2

        # Outer Orbital Limit
        outer_limit = 40 * mass
        return inner_limit, outer_limit

    def compute_snow_line(self):
        initlum = StEvoTable['Lmin'][self.StEvoIndex]
        return 4.85 * initlum ** 0.5

    def set_forbidden_zone(self, inner, outer):
        if inner >= outer:
            raise ValueError("Inner limit must be smaller than outer limit.")
        self.forbiddenzone = (inner, outer)
        self.hasforbiddenzone = True

    def make_planetsystem(self):
        # TODO: Why not call this in the constructor and avoid this side effect too?
        self.planetsystem = planetsystem.PlanetSystem(self)

    def get_orbit_limits(self):
        return self.innerlimit, self.outerlimit

    def get_snowline(self):
        return self.snowline

    def get_luminosity(self):
        return self.luminosity

    def has_forbidden_zone(self):
        return self.hasforbiddenzone

    def get_forbidden_zone(self):
        return self.forbiddenzone

    def get_radius(self):
        return self.radius

    def set_letter(self, letter):
        self.letter = letter

    def get_letter(self):
        return self.letter

    def get_star_type(self) -> str:
        """
        Get the star spectral type by the star temperature
        :return: Spectral Index
        """
        sp_index = min(range(len(StEvoTable['temp'])),
                       key=lambda i: abs(StEvoTable['temp'][i] - self.get_temp()))
        return StEvoTable['type'][sp_index]
