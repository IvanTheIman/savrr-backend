import random as r

def randomizer(value, store):
    std = .3
    skew = 1
    if store == 'brussels':
        skew = 1.2
    if store == 'ulbi':
        skew = .8
    price = round(max(0.39, r.gauss(value, .1)), 2)

    cents = int((price * 100) * skew)

    cents = (cents // 10) * 10 + 9

    price = cents / 100
    return price