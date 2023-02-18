from encounter import Encounter
from cards import get_playable_cards, get_weapon_cards_from_json
from loot import perform_forge

import random

INIT_FOOD = 2
INIT_GAS = 2
INIT_SCRAP = 2

location_list = [
    "silent hospital",
    "spooky garage",
    "abandoned building",
    "deserted house",
    "decrepit hangar",
]

class Campaign:
    def __init__(self, player):
        self.player = player
        self.player_stash = {"food": INIT_FOOD, "gas": INIT_GAS, "scrap": INIT_SCRAP}
        self.encounter_id = 1
        self.encounter_count = 1

    def init_campaign(self, skills_starter_decks, weapon_starter_decks):
        print(
            "Available survivor decks:",
            [
                (deck[0] + 1, deck[1]["name"])
                for deck in enumerate(skills_starter_decks)
            ],
        )
        deck_index = (
            int(input(f"Choose a skill deck: (1-{len(skills_starter_decks)})")) - 1
        )
        skill_deck = skills_starter_decks[deck_index]
        self.player.deck.load_deck_from_json(skill_deck["path"])
        # TODO: Maybe assign a "starter" weapon linked to deck possible synergies ?
        print(
            "Available weapons:",
            [
                (deck[0] + 1, deck[1]["name"])
                for deck in enumerate(weapon_starter_decks)
            ],
        )
        deck_index = (
            int(input(f"Choose a starting weapon: (1-{len(weapon_starter_decks)})")) - 1
        )
        weapon_deck = weapon_starter_decks[deck_index]
        self.player.equip_weapon(weapon_deck["name"], weapon_deck["path"])
        print("You have the following cards :")
        self.player.deck.show()
        first_encounter = Encounter(id=self.encounter_id)
        return first_encounter

    def start_encounter(self, encounter):
        f"Starting Encounter {encounter.id}"
        turn_count = 1
        self.player.position = encounter.init_position(self.player)
        self.player.armor_points = 0
        while self.player.is_alive:
            print(f"Turn {turn_count} - Player turn")
            player_hand = self.player.draw_hand()
            self.player.show()
            print(
                f"{self.player.name} draws {min(self.player.handsize, len(self.player.deck.available_cards))} cards:"
            )
            playable_hand = get_playable_cards(
                player_hand, self.player, encounter, turn_count
            )
            card_min_cost = min([c.current_cost for c in player_hand])
            while self.player.action_points >= card_min_cost and len(player_hand) != 0:
                if len(playable_hand) > 0:
                    card_idx = input(
                        f"Select a card [1-{len(player_hand)}] (p to end turn): "
                    )
                    if card_idx != "p":
                        selected_card = player_hand[int(card_idx) - 1]
                        if selected_card.is_playable:
                            print(
                                f"{self.player.name} selects and plays {selected_card.title}"
                            )
                            player_hand = self.player.play_card(
                                selected_card, encounter
                            )
                            if encounter.player_exit:
                                return True
                            playable_hand = get_playable_cards(
                                player_hand, self.player, encounter, turn_count
                            )
                            card_min_cost = min([c.current_cost for c in player_hand])
                        else:
                            print("This card is not playable now.")
                    else:
                        print(f"{self.player.name} waits ...")
                        [self.player.deck.discard_card(c) for c in player_hand]
                        break
                else:
                    print(f"{self.player.name} can't play a card.")
                    [self.player.deck.discard_card(c) for c in player_hand]
                    break
            if self.player.action_points == 0:
                print("No more AP.")
            self.player.action_points = 0
            print(f"Turn {turn_count} - Zombies turn")
            for zombie in encounter.zombie_list:
                if zombie.is_alive:
                    zombie.perform_action(encounter)
                else:
                    encounter.zombie_list.remove(zombie)
            encounter.spawn_zombies()
            turn_count += 1
        return False

    def prepare_next_encounter(self):
        self.player.deck.reset_deck()
        if not self.player.is_alive:
            print(f"{self.player.name} is dead. Game over.")
            return None
        else:
            for loot in self.player.inventory:
                self.player_stash[loot] += 1
            print(f"{self.player.name} stash is now: ", self.player_stash)
            self.player.inventory = []
            if self.player_stash["gas"] <= 0 or self.player_stash["food"] <= 0:
                print(
                    f"{self.player.name} ran out of supplies. The zombies overran him. Game over."
                )
                return None
            self.get_updates()
            self.encounter_count += 1
            encounter_choices = []
            for i in range(1, random.randint(2, 6)):
                encounter_choices.append(
                    Encounter(
                        id=self.encounter_id + i,
                        location=random.choice(location_list),
                        difficulty=self.encounter_count,
                        orientation=random.choice(["left", "right"]),
                    )
                )
            print(f"{self.player.name} can move to (traveling costs 1 food, 1 gas):")
            for encouter_temp_id, encounter in enumerate(encounter_choices):
                #TODO: difficulty increase HP or Damage or Number of zombies instead of just hp
                print(
                    "    ",
                    encouter_temp_id + 1,
                    encounter.location,
                    encounter.orientation,
                    encounter.difficulty,
                )
            next_encounter_id = input(
                f"select the next encounter [1-{len(encounter_choices)}]: "
            )
            self.player_stash["food"] -= 1
            self.player_stash["gas"] -= 1
            next_encounter = encounter_choices[int(next_encounter_id) - 1]
            return next_encounter

    def perform_rest(self):
        # TODO: maybe remove injuries ? need to add injury mechanism
        print(f"{self.player.name} uses 1 food to recover full health.")
        self.player_stash["food"] -= 1
        self.player.health_points = self.player.max_health_points
        return self

    def perform_train(self):
        # player can choose between obtaining a new skill card or removing an existing one
        # new cards are found in the deck with 3 kind of rarity - common rare legendary
        # 3 cards are drawn and player choose 1
        # TODO: implement new skill cards
        return

    def get_updates(self):
        if self.player_stash["scrap"] > 0:
            update_choice = input(
                "Do you want to rest (1), forge a weapon (2) or train (3) ? (p) to pass."
            )
            if update_choice == "1":
                self.perform_rest()
            elif update_choice == "2":
                    print(f"{self.player.name} has {self.player_stash['scrap']} scrap(s). How much scrap do you want to forge ?")
                    print(f"More scrap means better chances to get a good weapon.")
                    scrap_amount = int(input(f"Enter amount of scrap (1-{min(self.player_stash['scrap'],10)})"))
                    weapon_name, weapon_path = perform_forge(scrap_amount)
                    self.player_stash['scrap'] -= scrap_amount
                    print("looted weapon:",  weapon_name)
                    print("weapon deck path: ", weapon_path)
                    self.player.equip_weapon(weapon_name, weapon_path)          

            elif update_choice == "3":
                self.perform_train()
            else:
                pass
        else:
            update_choice = input(
                "Do you want to rest (1) or train (2) ? (not enough scrap to forge...) (p) to pass."
            )
            if update_choice == "1":
                self.perform_rest()
            elif update_choice == "2":
                self.perform_train()
            else:
                pass
        return self
