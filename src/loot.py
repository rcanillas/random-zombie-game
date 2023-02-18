import random
import os
import json

loot_rolls = {"scrap": 75, "food": 10, "gas": 10, "zombie": 5}
WEAPON_DROP_TABLE = {1:{"bronze":85,"silver":10,"gold":5},
                     2:{"bronze":79,"silver":15,"gold":6},
                     3:{"bronze":73,"silver":20,"gold":7},
                     4:{"bronze":67,"silver":25,"gold":8},
                     5:{"bronze":61,"silver":30,"gold":9},
                     6:{"bronze":55,"silver":35,"gold":10},
                     7:{"bronze":48,"silver":40,"gold":12},
                     8:{"bronze":41,"silver":45,"gold":14},
                     9:{"bronze":33,"silver":50,"gold":17},
                     10:{"bronze":30,"silver":50,"gold":20}}

WEAPON_LIST = {"bronze":[], "silver":[], "gold":[]}
DECK_FOLDER = "src/decks/"
for deck in os.listdir(DECK_FOLDER):
    deck_path = os.path.join(DECK_FOLDER,deck)
    with open(deck_path,"rb") as deck_file:
        deck_json = json.load(deck_file)
        if deck_json["deck_type"] == "weapon":
            WEAPON_LIST[deck_json["weapon_grade"]].append((deck_json["deck_name"], os.path.join("decks/",deck)))
print(WEAPON_LIST)

def perform_forge(scrap_amount):
    drop_rates_dict = WEAPON_DROP_TABLE[scrap_amount]
    print(drop_rates_dict)
    drop_keys = list(drop_rates_dict.keys())
    drop_values = list(drop_rates_dict.values())
    weapon_grade = random.choices(
        drop_keys, drop_values, k=1
    )[0]
    print("looted weapon grade:", weapon_grade)
    weapon = random.choice(WEAPON_LIST[weapon_grade])
    return weapon


def get_loot(actor, map):
    loot = random.choices(
        [k for k in loot_rolls.keys()], [v for v in loot_rolls.values()], k=1
    )[0]
    if loot == "scrap" or loot == "food" or loot == "gas":
        print(f"{actor.name} loots {loot}.")
        if len(actor.inventory) < actor.inventory_size:
            actor.inventory.append(loot)
        else:
            loot_choice = input(
                f"{actor.name} is carrying too much ! Do you want to (k)eep or (d)iscard the {loot} ? "
            )
            if loot_choice == "k":
                print(
                    f"{actor.name} inventory: {[e for e in enumerate(actor.inventory)]}"
                )
                discard_idx = int(
                    input(f"Select an item to discard [0-{actor.inventory_size-1}]: ")
                )
                print(f"{actor.name} discard {actor.inventory[discard_idx]}")
                actor.inventory.remove(actor.inventory[discard_idx])
                actor.inventory.append(loot)
            else:
                print(f"{loot} is discarded.")
            return False
    elif loot == "zombie":
        new_zombie = map.spawn_zombie(actor.position)
        print(
            f"Bad surprise ! {new_zombie.name} surprises {actor.name} while looting !"
        )
        return True
