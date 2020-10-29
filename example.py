"""This is an example script for automated star system generation"""

import starengine.starsystem as starsys
from starengine.tables import StEvoTable, IndexTable, SequenceTable

# Change from None to a value if you want to set an argument
args = {
    'open_cluster': None,  # True or False
    'num_stars': 1,  # 1, 2 or 3
    'age': None  # Number > 0
}

# Generate starsystems until one is made that contains a Garden world.
garden = False
cycle_num = 0

mysys = starsys.StarSystem(**args)
print("        Age:\t{}".format(mysys.age))
print(" # of Stars:\t{}".format(len(mysys.stars)))
print("OpenCluster:\t{}".format(mysys.opencluster))

starThing = mysys.stars[0]
# print(starThing)

print("  Star {} Info".format(starThing.letter))
print("  ---------")
print("       Mass:\t{}".format(mysys.stars[0].mass))
print("   Sequence:\t{}".format(SequenceTable[mysys.stars[0].SeqIndex]))
print(" Luminosity:\t{}".format(mysys.stars[0].luminosity))
print("Temperature:\t{}".format(mysys.stars[0].temperature))
print("     Radius:\t{}".format(round(mysys.stars[0].radius, 6)))
print("       Type:\t{}".format(mysys.stars[0].star_type))

# Nicely formatted orbital zone
norzone = (round(mysys.stars[0].innerlimit, 3), round(mysys.stars[0].outerlimit, 3))
print("Orbital Zne:\t{}".format(norzone))
# Nicely formatted snow line
nsnline = round(mysys.stars[0].snowline, 3)
print("  Snow Line:\t{}".format(nsnline))
if mysys.stars[0].hasforbiddenzone:
    # Nicely formatted forbidden zone
    nforb = [round(fz) for fz in mysys.stars[0].forbiddenzone]
    print(" Forbid Zne:\t{}".format(nforb))



mysys.stars[0].planetsystem.printinfo()
print("  ---------\n")


#star.stars[i].print_info()
print('Total number of cycles: {}'.format(cycle_num))
mysys.write_latex()
