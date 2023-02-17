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

    def lose_hp(self, lost_hp):
        print(f"{self.name} is hit !")
        if self.armor_points - lost_hp >= 0:
            self.armor_points = self.armor_points - lost_hp
            print(f"The armor protects {self.name}")
        else:
            lost_hp = abs(self.armor_points - lost_hp)

        self.health_points = max(self.health_points - lost_hp, 0)
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

    def replenish_ap(self, ap):
        self.action_points += ap

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
        self.replenish_ap(self.max_action_points)
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
    ) -> None:
        super().__init__(name, health_points, action_points, position)
        self.character_type = "z"
        self.speed = speed
        self.position.append(self)

    def attack(self, target):
        target.lose_hp(DEFAULT_Z_ATTACK)

    def perform_action(self, map):
        player_position, player = map.get_player_position()
        if player_position:
            if player_position.position == self.position.position:
                print(f"{self.name} is attacking !")
                self.attack(player)
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
                        else map.tileset[map.size]
                    )
                self.move(target_tile, map)
        else:
            print(f"{self.name} is feasting on the corpse.")
