from encounter import Encounter
from cards import get_playable_cards

INIT_FOOD = 2
INIT_GAS = 2
INIT_SCRAP = 0

class Campaign:
    
    def __init__(self, player, seed=42):
        self.player = player
        self.player_stash = {"food":INIT_FOOD, "gas":INIT_GAS, "scrap":INIT_SCRAP}

    def init_campaign(self, skills_starter_decks, weapon_starter_decks):
        print("Available survivor decks:" , [(deck[0]+1, deck[1]["name"]) for deck in enumerate(skills_starter_decks)])
        deck_index = int(input(f"Choose a skill deck: (1-{len(skills_starter_decks)})"))-1
        skill_deck = skills_starter_decks[deck_index]
        self.player.deck.load_deck_from_json(skill_deck["path"])
        print("Available weapons:" , [(deck[0]+1, deck[1]["name"]) for deck in enumerate(weapon_starter_decks)])
        deck_index = int(input(f"Choose a starting weapon: (1-{len(weapon_starter_decks)})"))-1
        weapon_deck = weapon_starter_decks[deck_index]
        self.player.equip_weapon(weapon_deck["name"], weapon_deck["path"])
        print("You have the following cards :")
        self.player.deck.show()
        return self

    def start_encounter(self, encounter_id):
        f"Starting Encounter {encounter_id}"
        turn_count = 1
        encounter = Encounter()
        self.player.position = encounter.init_position(self.player)
        self.player.armor_points = 0
        while self.player.is_alive:
            print(f"Turn {turn_count} - Player turn")
            player_hand = self.player.draw_hand()
            self.player.show()
            print(
                f"{self.player.name} draws {min(self.player.handsize, len(self.player.deck.available_cards))} cards:"
                )
            playable_hand = get_playable_cards(player_hand, self.player, encounter, turn_count)
            card_min_cost = min([c.current_cost for c in player_hand])
            while self.player.action_points >= card_min_cost and len(player_hand) != 0:
                if len(playable_hand) > 0:
                    card_idx = input(
                        f"Select a card [1-{len(player_hand)}] (p to end turn): ")
                        # selected_card = random.choice(playable_hand)
                    if card_idx != "p":
                        selected_card = player_hand[int(card_idx) - 1]
                        if selected_card.is_playable:
                            print(f"{self.player.name} selects and plays {selected_card.title}")
                            player_hand = self.player.play_card(selected_card, encounter)
                            if encounter.player_exit:
                                return self.player
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
        return self.player

    def prepare_next_encounter(self):
        if not self.player.is_alive:
            print(f"{self.player.name} is dead. Game over.")
            return False
        else:
            for loot in self.player.inventory:
                self.player_stash[loot] += 1
            print(f"{self.player.name} stash is now: ", self.player_stash)
            self.player.inventory = []
        return True