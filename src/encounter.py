import random
from characters import Zombie


DEFAULT_MAP_SIZE = 6
DEFAULT_NB_SPAWN = 2
DEFAULT_LOOT_MALUS = 2
DEFAULT_LOCATION = "abandoned house"


class Tile:
    def __init__(self, position) -> None:
        self.position = position
        self.is_spawn = False
        self.is_exit = False
        self.contains = []
        self.z_count = 0
        self.loot_modifier = 0

    def remove(self, actor):
        self.contains.remove(actor)
        if actor.character_type == "z":
            self.z_count -= 1

    def append(self, actor):
        self.contains.append(actor)
        if actor.character_type == "z":
            self.z_count += 1


class Encounter:
    def __init__(
        self,
        id,
        location=DEFAULT_LOCATION,
        size=DEFAULT_MAP_SIZE,
        orientation="right",
        min_turn_count=3,
        difficulty=1,
    ) -> None:
        self.size = size
        self.tileset = [Tile(pos) for pos in range(size)]
        self.orientation = orientation
        self.zombie_list = []
        self.player_exit = False
        if orientation == "right":
            self.tileset[0].is_exit = True
            for i in range(1, DEFAULT_NB_SPAWN + 1):
                self.tileset[size - i].is_spawn = True
            for tile in self.tileset:
                tile.loot_modifier = tile.position - DEFAULT_LOOT_MALUS
        else:
            self.tileset[size - 1].is_exit = True
            for i in range(0, DEFAULT_NB_SPAWN - 1):
                self.tileset[i].is_spawn = True
            for tile in self.tileset:
                tile.loot_modifier = size - tile.position - DEFAULT_LOOT_MALUS
        self.danger_meter = 0
        self.global_z_count = 0
        self.min_turn_count = min_turn_count
        self.id = id
        self.location = location
        self.difficulty = difficulty

    def init_position(self, character):
        init_position = (
            self.tileset[0]
            if self.orientation == "right"
            else self.tileset[self.size - 1]
        )
        init_position.append(character)
        return init_position

    def update_position(self, actor, target_tile):
        actor.position.remove(actor)
        target_tile.append(actor)
        # print(f"Tile {new_position.position} contains {new_position.z_count} zombies")
        return target_tile

    def get_player_position(self):
        player_tile = None
        player = None
        for tile in self.tileset:
            for actor in tile.contains:
                if actor.character_type == "p":
                    player_tile = tile
                    player = actor
        return player_tile, player

    def spawn_zombie(self, tile):
        new_zombie = Zombie(
            f"zombie {self.global_z_count}",
            health_points=self.difficulty,
            position=tile,
        )
        self.zombie_list.append(new_zombie)
        self.global_z_count += 1
        return new_zombie

    def spawn_zombies(self):
        spawn_tiles = [tile for tile in self.tileset if tile.is_spawn == True]
        print("Spawning tiles are " + str([t.position for t in spawn_tiles]))
        if self.danger_meter <= 3:
            nb_spawned_zombies = random.randint(1, 3)
        elif 3 < self.danger_meter <= 8:
            nb_spawned_zombies = random.randint(1, 6)
        else:
            nb_spawned_zombies = 2 * random.randint(1, 6)
        print(f"{nb_spawned_zombies} zombies have spawned.")
        for _ in range(0, nb_spawned_zombies):
            min_zombies = min([t.z_count for t in spawn_tiles])
            min_tiles = []
            for prospect_spawn_tile in spawn_tiles:
                if prospect_spawn_tile.z_count <= min_zombies:
                    min_tiles.append(prospect_spawn_tile)
                    min_zombies = prospect_spawn_tile.z_count

            if len(min_tiles) == 1:
                spawn_tile = min_tiles[0]
            else:
                if self.orientation == "right":
                    idx_tile = max([t.position for t in min_tiles])
                else:
                    idx_tile = min([t.position for t in min_tiles])
                spawn_tile = self.tileset[idx_tile]

            new_zombie = self.spawn_zombie(spawn_tile)
            print(f"{new_zombie.name} is spawning on Tile {spawn_tile.position}")
        print(
            f"D: {self.danger_meter}",
            [
                f"{t.position}-Z:{t.z_count}-P:{0 if len([p for p in t.contains if p.character_type=='p'])==0 else 1}"
                for t in self.tileset
            ],
        )
        return self.zombie_list
