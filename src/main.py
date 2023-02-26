from characters import PlayableCharacter
from campaign import Campaign

MIN_TURN_COUNT = 3

player = PlayableCharacter(
    name="Darryl", health_points=3, action_points=0, position=None
)
player.deck.load_deck_from_json("decks/skills_survivor.json")
campaign = Campaign(player)
starter_skills_decks = [{"name": "survivor", "path": "decks/skills_survivor.json"}]
starter_weapons_decks = [
    {"name": "baseball bat", "path": "decks/weapon_baseballbat.json"},
    {"name": "pistol", "path": "decks/weapon_pistol.json"},
]
first_encounter = campaign.init_campaign(starter_skills_decks, starter_weapons_decks)
nb_encounters_success = 1
# campaign.start_encounter(first_encounter)
next_encounter = campaign.prepare_next_encounter()
while next_encounter:
    print("----- New Encounter -----")
    # campaign.start_encounter(next_encounter)
    next_encounter = campaign.prepare_next_encounter()
print(f"{player.name} survived {campaign.encounter_count} !")
