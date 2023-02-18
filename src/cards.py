import json
import os
import random

import loot

random.seed = 42


def get_melee_target_tiles(map, source):
    return map.tileset[
        max(source.position.position - 1, 0) : min(
            map.size - 1, source.position.position + 1
        )
        + 1
    ]


def get_ranged_target_tiles(map, source, range):
    return (
        map.tileset[max(source.position.position - range, 0) : source.position.position]
        + map.tileset[
            source.position.position
            + 1 : min(map.size - 1, source.position.position + range)
            + 1
        ]
    )


def get_playable_cards(hand, player, encounter, turn_count):
    i = 1
    print("Available cards:", [c.title for c in player.deck.available_cards])
    print("Discarded cards:", [c.title for c in player.deck.discarded_cards])
    print("Burned cards:", [c.title for c in player.deck.burned_cards])
    have_exit_card = "Exit" in [c.title for c in hand]
    if (
        player.position.is_exit
        and turn_count >= encounter.min_turn_count
        and not have_exit_card
    ):
        hand.append(player.deck.get_exit_card())
    print(
        f"Cards to play (remaining AP:{player.action_points}) (loot modifer: {player.position.loot_modifier}):"
    )
    for card in hand:
        card.is_playable = True
        if card.card_type == "movement":
            card.current_cost = card.base_cost
            card.current_cost += player.position.z_count
        elif card.card_type == "melee_attack":
            z_found = False
            for tile in get_melee_target_tiles(encounter, player):
                if tile.z_count > 0:
                    z_found = True
            if z_found:
                card.is_playable = True
            else:
                card.is_playable = False
        elif card.card_type == "ranged_attack":
            z_found = False
            range = card.effects["ranged_attack"]["range"]
            for tile in get_ranged_target_tiles(encounter, player, range):
                if tile.z_count > 0:
                    z_found = True
            if z_found:
                card.is_playable = True
            else:
                card.is_playable = False
        elif card.card_type == "loot":
            if player.position.z_count > 0:
                card.is_playable = False
            if player.position.loot_modifier + card.effects["loot"] <= 0:
                card.is_playable = False
        elif card.card_type == "heal":
            if player.health_points >= player.max_health_points:
                card.is_playable = False
        if card.current_cost > player.action_points:
            card.is_playable = False
        if card.title == "Exit":
            if not player.position.is_exit:
                card.is_playable = False
        print(
            f"{i} - {card.title} ({card.current_cost} ap (base {card.base_cost})): {card.description} ({card.card_id}) - playable:{card.is_playable}"
        )
        i += 1

    return [c for c in hand if c.is_playable]


def try_attack(source, target, hit_chance):
    hit_roll = random.random()
    # print(hit_roll, hit_chance/100)
    if hit_roll <= hit_chance / 100:
        print(f"{source.name} performs an attack on {target.name} !")
        return True
    else:
        print(f"Attack missed !")
        return False


def get_skill_cards_from_json(json_deck_path: str):
    card_list = []

    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, json_deck_path)

    with open(path) as json_deck_file:
        json_deck = json.load(json_deck_file)
    deck_name = json_deck["deck_name"]
    print(f"loading deck {deck_name}")
    for card_id, json_card in enumerate(json_deck["starter"]["cards"]):
        new_card = Card(
            card_id=card_id,
            title=json_card["title"],
            card_type=json_card["card_type"],
            cost=json_card["cost"],
            effects=json_card["effects"],
            description=json_card["description"],
        )
        if "is_burnt" in json_card.keys():
            new_card.is_burnt = json_card["is_burnt"]
        card_list.append(new_card)
    return card_list


def get_weapon_cards_from_json(json_deck_path: str):
    card_list = []

    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, json_deck_path)

    with open(path) as json_deck_file:
        json_deck = json.load(json_deck_file)
    deck_name = json_deck["deck_name"]
    print(f"loading deck {deck_name}")
    for card_id, json_card in enumerate(json_deck["cards"]):
        new_card = Card(
            card_id=card_id,
            title=json_card["title"],
            card_type=json_card["card_type"],
            cost=json_card["cost"],
            effects=json_card["effects"],
            description=json_card["description"],
        )
        if "is_burnt" in json_card.keys():
            new_card.is_burnt = json_card["is_burnt"]
        card_list.append(new_card)
    return card_list


def push_target(target, map, potency):
    if map.orientation == "right":
        target_tile = map.tileset[max(target.position.position + potency, map.size - 1)]
    else:
        target_tile = map.tileset[max(target.position.position - potency, 0)]
    print(f"{target.name} is pushed {potency} tiles away !")
    map.update_position(target, target_tile)


class Card:
    def __init__(self, card_id, card_type, title, cost, effects, description) -> None:
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
        self.is_unstable = False

    def activate(self, source, map):
        add_push = "push" in self.effects.keys()
        for effect_key, effect_potency in self.effects.items():
            if effect_key == "melee_attack":
                target_tiles = get_melee_target_tiles(map, source)
                print(
                    f"Target tiles are {[t.position for t in target_tiles if t.z_count>0]}"
                )
                tile_idx = int(input(f"Select target tile: "))
                target_tile = map.tileset[tile_idx]
                for _ in range(effect_potency["nb_attacks"]):
                    potential_targets = [
                        t for t in target_tile.contains if t.character_type == "z"
                    ]
                    if len(potential_targets) > 0:
                        target = random.choice(potential_targets)
                        success = try_attack(
                            source, target, effect_potency["hit_chance"]
                        )
                        if success:
                            target.lose_hp(1)
                            if add_push:
                                push_target(target, map, self.effects["push"])
                    else:
                        print("No more zombies !")

            if effect_key == "ranged_attack":
                target_tiles = get_ranged_target_tiles(
                    map, source, effect_potency["range"]
                )
                print(
                    f"Target tiles are {[t.position for t in target_tiles if t.z_count>0]}"
                )
                tile_idx = int(input(f"Select target tile: "))
                target_tile = map.tileset[tile_idx]
                for _ in range(effect_potency["nb_attacks"]):
                    potential_targets = [
                        t for t in target_tile.contains if t.character_type == "z"
                    ]
                    if len(potential_targets) > 0:
                        target = random.choice(potential_targets)
                        try_attack(source, target, effect_potency["hit_chance"])
                    else:
                        print("No more zombies !")

            if effect_key == "move":
                # TODO: select target tile here
                tile_choices = get_ranged_target_tiles(map, source, effect_potency)
                print(
                    f"{source.name} can move to: ",
                    [f"{t.position}" for t in tile_choices],
                )
                tile_idx = int(input(f"Select target tile: "))
                # target_tile = random.choice(tile_choices)
                target_tile = map.tileset[tile_idx]
                print(f"{source.name} is moving to Tile {target_tile.position}")
                source.move(target_tile, map)

            if effect_key == "loot":
                effect_modifier = source.position.loot_modifier
                loot_time = max(0, effect_potency + effect_modifier)
                if loot_time > 0:
                    for _ in range(loot_time):
                        if loot.get_loot(source, map):
                            print("looting is interrupted !")
                            break
                else:
                    print("Nothing to find here...")

            if effect_key == "noise":
                map.danger_meter += 1

            if effect_key == "exit":
                map.player_exit = True
                print(f"{source.name} is leaving !")

            if effect_key == "defend":
                source.armor_points += effect_potency
                print(f"{source.name} is armored !")

            if effect_key == "heal":
                if source.health_points < source.max_health_points:
                    source.health_points += effect_potency
                    print(f"{source.name} is healed !")
                else:
                    print(f"{source.name} is already max heatlh !")
        if self.is_burnt:
            source.deck.burn_card(self)
        else:
            source.deck.discard_card(self)


class Deck:
    def __init__(self) -> None:
        self.deck_size = 0
        self.available_cards = []
        self.discarded_cards = []
        self.burned_cards = []
        self.weapon_cards = {}

    def load_deck_from_json(self, json_deck_path):
        new_cards = get_skill_cards_from_json(json_deck_path)
        self.available_cards = new_cards
        self.deck_size = len(self.available_cards)

    def add_weapon_cards(self, weapon, weapon_deck_path):
        weapon_card_list = get_weapon_cards_from_json(weapon_deck_path)
        self.available_cards += weapon_card_list
        self.weapon_cards[weapon] = weapon_card_list
        self.deck_size = len(self.available_cards)

    def remove_weapon_cards(self, weapon):
        weapon_card_list = self.weapon_cards[weapon]
        for card in weapon_card_list:
            self.available_cards.remove(card)
        self.deck_size = len(self.available_cards)

    def show(self):
        for card in self.available_cards:
            print(
                f"   Card {card.title} (c:{card.base_cost}, {card.card_type}, effects:{card.description}) is available (id {card.card_id})"
            )
        for card in self.discarded_cards:
            print(
                f"   Card {card.title} (c:{card.base_cost}, {card.card_type}, effects:{card.description}) is discarded (id {card.card_id})"
            )
        for card in self.burned_cards:
            print(
                f"   Card {card.title} (c:{card.base_cost}, {card.card_type}, effects:{card.description}) is burned (id {card.card_id})"
            )

    def draw(self, handsize):
        drawn_cards = []
        if handsize > self.deck_size:
            handsize = self.deck_size
        if handsize <= len(self.available_cards):
            drawn_cards = random.sample(self.available_cards, k=handsize)
        else:
            print("redrawing")
            drawn_cards = random.sample(
                self.available_cards, k=len(self.available_cards)
            )
            left_to_draw = handsize - len(self.available_cards)
            self.available_cards = self.available_cards + self.discarded_cards.copy()
            self.discarded_cards = []
            drawn_cards += random.sample(
                [c for c in self.available_cards if c not in drawn_cards],
                k=left_to_draw,
            )
        # print(len(drawn_cards))
        return drawn_cards

    def reset_deck(self):
        print("resetting deck")
        for burned_card in self.burned_cards:
            if not burned_card.is_unstable:
                self.available_cards.append(burned_card)
        self.available_cards += self.discarded_cards
        self.discarded_cards = []
        self.burned_cards = []

    def burn_card(self, card):
        self.available_cards.remove(card)
        self.burned_cards.append(card)

    def discard_card(self, card):
        self.available_cards.remove(card)
        if card.is_unstable:
            self.burned_cards.append(card)
        else:
            self.discarded_cards.append(card)

    def get_exit_card(self):
        exit_card = Card(
            card_id=self.deck_size,
            card_type="move",
            title="Exit",
            cost=0,
            effects={"exit": 1},
            description="Get out of here !",
        )
        exit_card.is_burnt = True
        exit_card.is_unstable = True
        self.available_cards.append(exit_card)
        return exit_card
