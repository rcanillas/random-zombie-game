import pygame
import random

from characters import PlayableCharacter, Zombie
from cards import get_target_tiles
from map import Map

def get_playable_cards(hand, player, map):
    i = 1
    print(f"Cards to play (remaining AP:{player.action_points}):")
    for card in hand:
        card.is_playable = True
        if card.card_type == "movement":
            card.current_cost = card.base_cost
            card.current_cost += player.position.z_count
        elif card.card_type == "attack":
            z_found = False
            for tile in get_target_tiles(map, player):
                if tile.z_count>0:
                    z_found = True  
            if z_found:
                card.is_playable = True
            else:
                card.is_playable = False
        if card.current_cost > player.action_points:
            card.is_playable = False
        print(f"{i} - {card.title} ({card.current_cost} ap (base {card.base_cost})): {card.description} ({card.card_id}) - playable:{card.is_playable}")
        i += 1
    return [c for c in hand if c.is_playable]

pygame.init()
map = Map()
player = PlayableCharacter(name="Darryl", health_points=3, action_points=0, position=map.tileset[0])
player.deck.load_deck_from_json("decks/test.json")
player.deck.show()
#zombie = Zombie(name="Patient Zero", position=map.tileset[map.size-1])
zombie_list = []
i = 1
while player.is_alive:
    print(f"Turn {i} - Player turn")
    player_hand = player.draw_hand()
    player.show()
    print(f"{player.name} draws {min(player.handsize, len(player.deck.available_cards))} cards:")
    playable_hand = get_playable_cards(player_hand, player, map)       
    card_min_cost = min([c.current_cost for c in player_hand])
    while player.action_points >= card_min_cost and len(player_hand) != 0:
        if len(playable_hand) > 0:
            card_idx = int(input(f"Select a card [1-{len(player_hand)}]: "))-1
            #selected_card = random.choice(playable_hand)
            selected_card = player_hand[card_idx]
            if selected_card.is_playable:
                print(f"{player.name} selects and plays {selected_card.title}")
                player_hand = player.play_card(selected_card, map)
                playable_hand = get_playable_cards(player_hand, player, map)
            else:
                print("This card is not playable now.")        
        else:
            print(f"{player.name} can't play a card.")
            [player.deck.discard_card(c) for c in player_hand]
            break
    if player.action_points == 0:
        print("No more AP.")
    player.action_points = 0
    print(f"Turn {i} - Zombies turn")
    for zombie in zombie_list:
        if zombie.is_alive:
            zombie.perform_action(map)
            #zombie.show()
        else:
            zombie_list.remove(zombie)
    zombie_list += map.spawn_zombies()
    i+=1
    if i == 5:
        break


