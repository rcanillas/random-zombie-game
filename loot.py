import random
loot_rolls = {"scrap":65, "food":15, "gas":15, "zombie":5}
def get_loot(actor, map):
    loot = random.choices([k for k in loot_rolls.keys()], [v for v in loot_rolls.values()],k=1)[0]
    if loot == "scrap" or loot == "food" or loot == "gas":
        print(f"{actor.name} loots {loot}.")
        if len(actor.inventory) < actor.inventory_size:
            actor.inventory.append(loot)
        else:
            loot_choice = input(f"{actor.name} is carrying too much ! Do you want to (k)eep or (d)iscard the {loot} ? ")
            if loot_choice == "k":
                print(f"{actor.name} inventory: {[e for e in enumerate(actor.inventory)]}")
                discard_idx = int(input(f"Select an item to discard [0-{actor.inventory_size-1}]: "))
                print(f"{actor.name} discard {actor.inventory[discard_idx]}")
                actor.inventory.remove(actor.inventory[discard_idx])
                actor.inventory.append(loot)
            else: 
                print(f"{loot} is discarded.")
    elif loot == "zombie":
        new_zombie = map.spawn_zombie(actor.position)
        print(f"Bad surprise ! {new_zombie.name} surprises {actor.name} while looting !")
