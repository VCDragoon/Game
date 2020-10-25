from random import randint, seed

def rollDie(sides = 6):
    return randint(1, sides)



def difficultyCheck(num_dice = 1, sides = 6, difficulty = 1, success = 5):
    for i in range(num_dice):
        rollResult = 0 # reset roll result
        rollResult = rollDie(sides)
        if rollResult >= success:
            difficulty -= 1
        
        if difficulty <= 0:
            return True
    
    return False
