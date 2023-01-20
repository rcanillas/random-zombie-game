import pygame
import random

from characters import PlayableCharacter
from cards import get_melee_target_tiles, get_ranged_target_tiles
from map import Map

MIN_TURN_COUNT = 3

def get_playable_cards(hand, player, map, turn_count):
    i = 1
    have_exit_card = "Exit" in [c.title for c in hand]
    if player.position.is_exit and turn_count >= MIN_TURN_COUNT and not have_exit_card:
        hand.append(player.deck.get_exit_card())
    print(f"Cards to play (remaining AP:{player.action_points}) (loot modifer: {player.position.loot_modifier}):")
    for card in hand:
        card.is_playable = True
        if card.card_type == "movement":
            card.current_cost = card.base_cost
            card.current_cost += player.position.z_count
        elif card.card_type == "melee_attack":
            z_found = False
            for tile in get_melee_target_tiles(map, player):
                if tile.z_count>0:
                    z_found = True  
            if z_found:
                card.is_playable = True
            else:
                card.is_playable = False
        elif card.card_type== "ranged_attack":
            z_found = False
            range = card.effects["ranged_attack"]["range"]
            for tile in get_ranged_target_tiles(map, player, range):
                if tile.z_count>0:
                    z_found = True  
            if z_found:
                card.is_playable = True
            else:
                card.is_playable = False
        elif card.card_type == "loot":
            if player.position.z_count > 0:
                card.is_playable = False
        elif card.card_type == "heal":
            if player.health_points >= player.max_health_points:
                card.is_playable = False
        if card.current_cost > player.action_points:
            card.is_playable = False
        print(f"{i} - {card.title} ({card.current_cost} ap (base {card.base_cost})): {card.description} ({card.card_id}) - playable:{card.is_playable}")
        i += 1
        
    return [c for c in hand if c.is_playable]

pygame.init()
map = Map()
player = PlayableCharacter(name="Darryl", health_points=3, action_points=0, position=map.tileset[0])
player.deck.load_deck_from_json("decks/skills_survivor.json")
player.equip_weapon("baseball bat", "decks/weapon_baseballbat.json")
player.equip_weapon("pistol", "decks/weapon_pistol.json")
player.deck.show()
#zombie = Zombie(name="Patient Zero", position=map.tileset[map.size-1])
turn_count = 1
while player.is_alive and (not map.player_exit):
    print(f"Turn {turn_count} - Player turn")
    player_hand = player.draw_hand()
    player.show()
    print(f"{player.name} draws {min(player.handsize, len(player.deck.available_cards))} cards:")
    playable_hand = get_playable_cards(player_hand, player, map, turn_count)       
    card_min_cost = min([c.current_cost for c in player_hand])
    while player.action_points >= card_min_cost and len(player_hand) != 0:
        if len(playable_hand) > 0:
            card_idx = input(f"Select a card [1-{len(player_hand)}] (p to end turn): ")
            #selected_card = random.choice(playable_hand)
            if card_idx != "p":
                selected_card = player_hand[int(card_idx)-1]
                if selected_card.is_playable:
                    print(f"{player.name} selects and plays {selected_card.title}")
                    player_hand = player.play_card(selected_card, map)
                    if map.player_exit:
                        break
                    playable_hand = get_playable_cards(player_hand, player, map, turn_count)
                    card_min_cost = min([c.current_cost for c in player_hand])
                else:
                    print("This card is not playable now.")        
            else:
                print(f"{player.name} waits ...")
                [player.deck.discard_card(c) for c in player_hand]
                break
        else:
            print(f"{player.name} can't play a card.")
            [player.deck.discard_card(c) for c in player_hand]
            break
    if player.action_points == 0:
        print("No more AP.")
    player.action_points = 0
    if map.player_exit:
        break
    print(f"Turn {turn_count} - Zombies turn")
    for zombie in map.zombie_list:
        if zombie.is_alive:
            zombie.perform_action(map)
        else:
            map.zombie_list.remove(zombie)
    map.spawn_zombies()
    turn_count+=1


