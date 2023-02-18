import random
from cards import Deck

DEFAULT_HANDSIZE = 5
DEFAULT_ARMOR = 0
DEFAULT_P_AP = 3
DEFAULT_P_HP = 3
DEFAULT_INV_SIZE = 4

DEFAULT_Z_ATTACK = 1
DEFAULT_Z_SPEED = 1
DEFAULT_Z_HP = 1
DEFAULT_Z_AP = 1


class Actor:
    def __init__(self, name, health_points, action_points, position) -> None:
        self.name = name
        self.armor_points = DEFAULT_ARMOR
        self.health_points = health_points
        self.action_points = action_points
        self.max_health_points = DEFAULT_P_HP
        self.max_action_points = DEFAULT_P_AP
        self.position = position
        self.is_alive = True
        self.hand = []

    def lose_armor(self, attack_potency):
        print(f"{self.name} is hit on the armor !")
        if self.armor_points - attack_potency >= 0:
            self.armor_points = self.armor_points - attack_potency
            print(f"The armor protects {self.name}")
            return 0
        else:
            remainder = attack_potency-self.armor_points
            print(f"The armor is gone ! {remainder} hit point(s) goes through !")
            return remainder
    
    def lose_hp(self, attack_potency):
        if self.armor_points > 0:
            health_hit = self.lose_armor(attack_potency)
        else:
            health_hit = attack_potency
        self.health_points = max(self.health_points - health_hit, 0)
        if self.health_points <= 0:
            print(f"{self.name} is dead...")
            self.is_alive = False
            self.position.remove(self)

    def move(self, target_tile, map):
        self.position = map.update_position(self, target_tile)

    def show(self):
        if self.is_alive:
            print(
                f"{self.name} is on Tile {self.position.position} with {self.health_points} hp and {self.action_points} ap"
            )
        else:
            print(f"{self.name} is dead on Tile {self.position.position}")


class PlayableCharacter(Actor):
    def __init__(self, name, health_points, action_points, position) -> None:
        super().__init__(name, health_points, action_points, position)
        self.deck = Deck()
        self.handsize = DEFAULT_HANDSIZE
        self.character_type = "p"
        self.inventory = []
        self.inventory_size = DEFAULT_INV_SIZE
        self.weapons = []

    def replenish_ap(self):
        self.action_points = self.max_action_points

    def play_card(self, card, map):
        card.activate(self, map)
        self.hand.remove(card)
        self.action_points -= card.current_cost
        return self.hand

    def equip_weapon(self, weapon, weapon_deck_path):
        self.weapons.append(weapon)
        self.deck.add_weapon_cards(weapon, weapon_deck_path)

    def unequip_weapon(self, weapon):
        self.weapons.remove(weapon)
        self.deck.remove_weapon_cards(weapon)

    def draw_hand(self):
        self.replenish_ap()
        self.hand = self.deck.draw(self.handsize)
        return self.hand


class Zombie(Actor):
    def __init__(
        self,
        name,
        position,
        health_points=DEFAULT_Z_HP,
        action_points=DEFAULT_Z_AP,
        speed=DEFAULT_Z_SPEED,
        attack=DEFAULT_Z_ATTACK
    ) -> None:
        super().__init__(name, health_points, action_points, position,)
        self.character_type = "z"
        self.speed = speed
        self.position.append(self)
        self.attack = attack

    def attack_target(self, target):
        target.lose_hp(self.attack)

    def perform_action(self, map):
        player_position, player = map.get_player_position()
        if player_position:
            if player_position.position == self.position.position:
                print(f"{self.name} is attacking !")
                self.attack_target(player)
            else:
                print(f"{self.name} is moving towards the player !")
                direction = (
                    "left"
                    if self.position.position - player_position.position > 0
                    else "right"
                )
                if direction == "left":
                    target_tile = (
                        map.tileset[self.position.position - self.speed]
                        if self.position.position - self.speed >= 0
                        else map.tileset[0]
                    )
                else:
                    target_tile = (
                        map.tileset[self.position.position + self.speed]
                        if self.position.position - self.speed <= map.size
                        else map.tileset[map.size - 1]
                    )
                self.move(target_tile, map)
        else:
            print(f"{self.name} is feasting on the corpse.")
