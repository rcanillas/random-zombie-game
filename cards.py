import json
import random

import loot

random.seed=42

def get_target_tiles(map, source):
    return map.tileset[max(source.position.position-1,0):min(map.size-1,source.position.position+1)+1]

class Card:
    def __init__(self, card_id, card_type,title, cost, effects, description) -> None:
        self.card_id = card_id
        self.card_type = card_type
        self.title = title
        self.base_cost = cost
        self.current_cost = cost
        self.effects = effects
        self.description = description
        self.is_burnt = False
        self.graphic = None
        self.is_playable = True

    def activate(self, source, map):
        for effect_key, effect_potency in self.effects.items():
            
            if effect_key == "attack":
                # TODO: select target tile here
                target_tiles = get_target_tiles(map, source)
                print(f"Target tiles are {[t.position for t in target_tiles if t.z_count>0]}")
                tile_idx = int(input(f"Select target tile: "))
                target_tile = map.tileset[tile_idx]
                """
                for tile in target_tiles:
                    if tile.z_count>0:
                        #print(tile.position, len([c.character_type=="z" for c in tile.contains if c.is_alive]), tile.z_count)
                        target_tile = tile
                        break
                """
                #print(f"Target tile is Tile {target_tile.position}")
                for _ in range(effect_potency):
                    potential_targets = [t for t in target_tile.contains if t.character_type =="z"]
                    if len(potential_targets) > 0:
                        target = random.choice(potential_targets)
                        print(f"{source.name} attacks {target.name} !")
                        target.lose_hp(1)
                    else: 
                        print("attack misses !")
            
            if effect_key=="move":
                # TODO: select target tile here
                tile_choices = map.tileset[max(source.position.position-effect_potency,0):source.position.position] + map.tileset[source.position.position+1:min(map.size-1,source.position.position+effect_potency)+1] 
                print(f"{source.name} can move to: ",[f"{t.position}" for t in tile_choices])
                tile_idx = int(input(f"Select target tile: "))
                #target_tile = random.choice(tile_choices)
                target_tile = map.tileset[tile_idx]
                print(f"{source.name} is moving to Tile {target_tile.position}")
                source.move(effect_potency, target_tile, map)

            if effect_key=="loot":
                effect_modifier = source.position.loot_modifier
                loot_time = max(0, effect_potency+effect_modifier)
                if loot_time > 0:
                    for _ in range(loot_time):
                        if loot.get_loot(source, map):
                            print("looting is interrupted !")
                            break
                else :
                    print("Nothing to find here...")

            if effect_key=="noise":
                map.danger_meter += 1

            if effect_key=="exit":
                map.player_exit = True
                print(f"{source.name} is leaving !")
            
        source.deck.discard_card(self)

class Deck:
    def __init__(self) -> None:
        self.deck_size = 0
        self.available_cards = []
        self.discarded_cards = []
        self.burned_cards = []
    
    def load_deck_from_json(self, json_deck_path):
        with open(json_deck_path) as json_deck_file:
            json_deck = json.load(json_deck_file)
        self.deck_name = json_deck["deck_name"]
        for card_id, json_card in enumerate(json_deck["cards"]):
            new_card = Card(card_id=card_id,
                            title=json_card["title"],
                            card_type=json_card["card_type"],
                            cost=json_card["cost"],
                            effects=json_card["effects"],
                            description=json_card["description"])
            self.available_cards.append(new_card)
            self.deck_size += 1

    def show(self):
        print(f"Deck {self.deck_name}:")
        for card in self.available_cards:
            print(f"   Card {card.title} (c:{card.base_cost}, {card.card_type}, effects:{card.description}) is available (id {card.card_id})")
        for card in self.discarded_cards:
            print(f"   Card {card.title} (c:{card.base_cost}, {card.card_type}, effects:{card.description}) is discarded (id {card.card_id})")
        for card in self.burned_cards:
            print(f"   Card {card.title} (c:{card.base_cost}, {card.card_type}, effects:{card.description}) is burned (id {card.card_id})")

    def draw(self, handsize):
        drawn_cards = []
        if handsize > self.deck_size:
            handsize = self.deck_size
        if handsize <= len(self.available_cards):
            drawn_cards =  random.sample(self.available_cards,k=handsize)
        else:
            print("redrawing")
            drawn_cards = random.sample(self.available_cards,k=len(self.available_cards))
            left_to_draw = handsize-len(self.available_cards)
            self.available_cards = self.available_cards + self.discarded_cards.copy()
            self.discarded_cards = []
            drawn_cards += random.sample([c for c in self.available_cards if c not in drawn_cards],k=left_to_draw)
        #print(len(drawn_cards))
        return drawn_cards

              
    def discard_card(self, card):
        #print(card.title, card.card_id)
        #print([c.card_id for c in self.available_cards])
        self.available_cards.remove(card)
        if card.is_burnt:
            self.burned_cards.append(card)
        else:
            self.discarded_cards.append(card)

    def get_exit_card(self):
        exit_card = Card(card_id=self.deck_size,card_type="move",title="Exit",cost=0, effects={"exit":1}, description="Get out of here !")
        exit_card.is_burnt == True
        self.available_cards.append(exit_card)
        return exit_card