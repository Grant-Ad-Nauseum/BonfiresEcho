import random
import time
import json
import os
from typing import Dict, List, Tuple, Optional

# --- Constants ---
VERSION = "1.1.0"
SAVE_FILE = "bonfires_echo_save.json"
SOUND_ENABLED = False  # Placeholder for future audio integration

# --- Lore Introduction ---
def print_lore() -> None:
    """Display the game's introductory lore with dramatic pacing."""
    lore_lines = [
        "\nThe Underground Empire once blazed with forbidden light, its spires clawing at the heavens, powered by the Relic of Ages—a shard of creation’s wrath.",
        "Greed and betrayal tore it asunder, plunging all into shadow. The relic lies entombed, guarded by nightmares of its own making.",
        "You, a scarred drifter, descend into this abyss to seize it, to etch your name in blood or fade into dust.",
        "Bonfires smolder amid the ruins—fragile refuges where the empire’s whispers cling to life.",
        "Brace yourself. The dark craves your soul, and every step is a dance with ruin.\n"
    ]
    for line in lore_lines:
        print(line)
        time.sleep(1.5 if SOUND_ENABLED else 0.5)  # Simulate sound effect duration
    if SOUND_ENABLED:
        print("[Sound: Distant wind howls, embers crackle]")

# --- Player Setup ---
def setup_player() -> Dict:
    """Initialize the player with name, weapon choice, and starting stats."""
    print("\nWhat name do you bear into this cursed pit?")
    player_name = input("Enter your name: ").strip() or "Nameless"
    print(f"\n{player_name}, pick your starting edge—none will save you from the grind:")
    print("1. Sword - Balanced grit (Attack: 10, Defense: 3, Mana: 50)")
    print("2. Staff - Arcane bite (Attack: 5, Defense: 1, Mana: 80)")
    print("3. Bow - Sharp sting (Attack: 12, Defense: 2, Mana: 50)")
    while True:
        choice = input("Enter 1, 2, or 3: ").strip()
        starting_weapons = {
            '1': ('sword', 10, 3, 50),
            '2': ('staff', 5, 1, 80),
            '3': ('bow', 12, 2, 50)
        }
        if choice in starting_weapons:
            weapon, attack, defense, mana = starting_weapons[choice]
            print(f"\nYou clutch the {weapon}. It’s a start.")
            break
        print("Choose, or face the dark empty-handed.")
    return {
        'name': player_name,
        'health': 100, 'max_health': 100,
        'mana': mana, 'max_mana': mana,
        'attack': attack, 'defense': defense,
        'xp': 0, 'level': 1,
        'spells': [],
        'inventory': [],
        'equipped_weapon': weapon,
        'equipped_armor': None,
        'trinkets': [],
        'explored': {'ruined_atrium'},
        'souls': 0,  # New currency for crafting/upgrades
        'stealth': False,
        'achievements': []
    }

# --- Player Stats Display ---
def print_stats(player: Dict) -> None:
    """Display the player's current stats with enhanced formatting."""
    print(f"\n===== {player['name']}'s Toll =====")
    print(f"Level: {player['level']} (XP: {player['xp']}/{player['level'] * 100})")
    print(f"Health: {player['health']}/{player['max_health']}")
    print(f"Mana: {player['mana']}/{player['max_mana']}")
    print(f"Attack: {player['attack']}")
    print(f"Defense: {player['defense']}")
    print(f"Weapon: {player['equipped_weapon'].capitalize()}")
    print(f"Armor: {player['equipped_armor'].capitalize() if player['equipped_armor'] else 'None'}")
    print(f"Trinkets: {', '.join([t.capitalize() for t in player['trinkets']]) if player['trinkets'] else 'None'}")
    print(f"Inventory: {', '.join([i.capitalize() for i in player['inventory']]) if player['inventory'] else 'Empty'}")
    print(f"Spells: {', '.join([s.capitalize() for s in player['spells']]) if player['spells'] else 'None'}")
    print(f"Souls: {player['souls']}")
    print(f"Achievements: {', '.join(player['achievements']) if player['achievements'] else 'None'}")
    print("=======================\n")

# --- Map Display ---
def print_map(player: Dict) -> None:
    """Display the explored portions of the map with directional context."""
    print("\n--- The Empire’s Shattered Web ---")
    layout = {
        'ruined_atrium': {'north': 'grand_hall', 'east': 'windy_tunnel', 'west': 'shattered_vestibule'},
        'grand_hall': {'south': 'ruined_atrium', 'north': 'throne_antechamber', 'west': 'dark_abyss', 'east': 'library'},
        'windy_tunnel': {'west': 'ruined_atrium', 'east': 'crystal_cavern', 'north': 'ashen_gorge'},
        'shattered_vestibule': {'east': 'ruined_atrium', 'north': 'echoing_crypt'},
        'crystal_cavern': {'west': 'windy_tunnel', 'south': 'flooded_passage', 'north': 'ice_passage'},
        'flooded_passage': {'north': 'crystal_cavern', 'east': 'sunken_chamber'},
        'sunken_chamber': {'west': 'flooded_passage', 'up': 'secret_trove', 'north': 'labyrinth_of_echoes'},
        'secret_trove': {'down': 'sunken_chamber'},
        'dark_abyss': {'east': 'grand_hall', 'north': 'hidden_vault', 'south': 'relic_vault'},
        'hidden_vault': {'south': 'dark_abyss', 'east': 'forge_of_the_ancients'},
        'library': {'west': 'grand_hall', 'north': 'oracle_chamber', 'east': 'arcane_sanctum'},
        'oracle_chamber': {'south': 'library', 'west': 'tower_of_the_mage'},
        'throne_antechamber': {'south': 'grand_hall', 'north': 'throne_room'},
        'throne_room': {'south': 'throne_antechamber', 'west': 'chamber_of_trials', 'north': 'relic_vault'},
        'forge_of_the_ancients': {'west': 'hidden_vault', 'north': 'forgotten_mines', 'south': 'lava_chamber'},
        'garden_of_shadows': {'west': 'crypt_of_the_fallen', 'south': 'deep_cavern'},
        'crypt_of_the_fallen': {'south': 'grand_hall', 'east': 'garden_of_shadows'},
        'tower_of_the_mage': {'down': 'oracle_chamber', 'up': 'labyrinth_of_echoes'},
        'labyrinth_of_echoes': {'down': 'tower_of_the_mage', 'south': 'sunken_chamber'},
        'chamber_of_trials': {'east': 'throne_room'},
        'echoing_crypt': {'south': 'shattered_vestibule', 'west': 'shadow_vault'},
        'shadow_vault': {'east': 'echoing_crypt', 'north': 'ice_passage'},
        'ice_passage': {'south': 'shadow_vault', 'north': 'frozen_lair', 'west': 'crystal_cavern'},
        'frozen_lair': {'south': 'ice_passage', 'east': 'lava_chamber', 'north': 'frosted_depths'},
        'lava_chamber': {'west': 'frozen_lair', 'north': 'forge_of_the_ancients', 'east': 'cinder_halls'},
        'arcane_sanctum': {'west': 'library', 'east': 'mana_well'},
        'mana_well': {'west': 'arcane_sanctum', 'north': 'relic_vault'},
        'forgotten_mines': {'south': 'forge_of_the_ancients', 'east': 'deep_cavern'},
        'deep_cavern': {'west': 'forgotten_mines', 'north': 'garden_of_shadows', 'south': 'relic_vault', 'east': 'void_chasm'},
        'relic_vault': {'south': 'throne_room', 'north': 'mana_well', 'east': 'deep_cavern', 'west': 'dark_abyss'},
        'ashen_gorge': {'north': 'windy_tunnel', 'south': 'bleak_ruins'},
        'bleak_ruins': {'north': 'ashen_gorge', 'east': 'wraith_spire'},
        'wraith_spire': {'west': 'bleak_ruins', 'north': 'soul_pit'},
        'soul_pit': {'south': 'wraith_spire', 'east': 'relic_vault'},
        'cinder_halls': {'west': 'lava_chamber', 'north': 'ember_vault'},
        'ember_vault': {'south': 'cinder_halls', 'east': 'relic_vault'},
        'frosted_depths': {'south': 'frozen_lair', 'north': 'glacial_tomb'},
        'glacial_tomb': {'south': 'frosted_depths', 'west': 'relic_vault'},
        'void_chasm': {'east': 'deep_cavern', 'north': 'abyssal_rift'},
        'abyssal_rift': {'south': 'void_chasm', 'west': 'relic_vault'}
    }
    for room in sorted(player['explored']):
        exits = layout.get(room, {})
        explored_exits = {d: dest for d, dest in exits.items() if dest in player['explored']}
        print(f"{room.capitalize()}: {', '.join([f'{dir}: {dest}' for dir, dest in explored_exits.items()])}")
    unexplored_count = len(layout) - len(player['explored'])
    print(f"Unexplored realms: {unexplored_count}")
    print("------------------------\n")

# --- ASCII Art ---
def print_ascii_art() -> None:
    """Display a dragon ASCII art as a dramatic intro."""
    dragon_art = r"""
                                             ,--,  ,.-.
               ,                   \,       '-,-`,'-.' | ._
              /|           \    ,   |\         }  )/  / `-,',
              [ ,          |\  /|   | |        /  \|  |/`  ,`
              | |       ,.`  `,` `, | |       (   (      .',
              \  \  __ ,-` `  ,  , `/ |        Y     (   /_L\
               \  \_\,``,   ` , ,  /  |         )         _,/
                \  '  `  ,_ _`_,-,<._.<        /         /
                 ', `>.,`  `  `   ,., |_      |         /
                   \/`  `,   `   ,`  | /__,.-`    _,   `\
               -,-..\  _  \  `  /  ,  / `._) _,-\`       \
                \_,,.) /\    ` /  / ) (-,, ``    ,        |
               ,` )  | \_\       '-`  |  `(               \
              /  /```(   , --, ,' \   |`<`    ,            |
             /  /_,--`\   <\  V /> ,` )<_/)  | \      _____)
       ,-, ,`   `   (_,\ \    |   /) / __/  /   `----`
      (-, \           ) \ ('_.-._)/ /,`    /
      | /  `          `/ \\ V   V, /`     /
   ,--\(        ,     <_/`\\     ||      /
  (   ,``-     \/|         \-A.A-`|     /
 ,>,_ )_,..(    )\          -,,_-`  _--`
(_ \|`   _,/_  /  \_            ,--`
 \( `   <.,../`     `-.._   _,-`
    """
    print(dragon_art)
    if SOUND_ENABLED:
        print("[Sound: Dragon’s roar echoes through the abyss]")

# --- Items ---
player_default = {
    'health': 100, 'max_health': 100,
    'mana': 50, 'max_mana': 50,
    'attack': 5, 'defense': 0,
    'spells': [],
    'inventory': [],
    'equipped_weapon': 'fists',
    'equipped_armor': None,
    'souls': 0
}

weapons = {
    'fists': {'attack': 5, 'desc': 'Bare knuckles, raw and unyielding.'},
    'rusted_sword': {'attack': 10, 'desc': 'A blade dulled by time.'},
    'iron_sword': {'attack': 15, 'desc': 'Solid steel, cold and heavy.'},
    'gleaming_sword': {'attack': 18, 'desc': 'Polished to a deadly sheen.'},
    'forge_hammer': {'attack': 20, 'desc': 'A smith’s tool turned weapon.'},
    'sword': {'attack': 10, 'desc': 'A balanced blade for a drifter.'},
    'staff': {'attack': 5, 'spell_bonus': 5, 'desc': 'Wood carved with arcane intent.'},
    'bow': {'attack': 12, 'range': True, 'desc': 'A taut string sings death.'},
    'shadow_blade': {'attack': 14, 'stealth': True, 'desc': 'A knife that drinks light.'},
    'flame_spear': {'attack': 16, 'fire_damage': 5, 'desc': 'A spear kissed by flame.'},
    'ice_dagger': {'attack': 12, 'ice_slow': True, 'desc': 'A blade of frozen malice.'},
    'thunder_mace': {'attack': 20, 'shock': True, 'desc': 'Crackling with storm’s fury.'},
    'crystal_staff': {'attack': 8, 'spell_bonus': 10, 'desc': 'Glowing with mystic power.'},
    'dragon_sword': {'attack': 25, 'fire_resist': True, 'desc': 'Forged in drake’s breath.'},
    'void_axe': {'attack': 22, 'dark_damage': 3, 'desc': 'A cleaver of the abyss.'},
    'bone_scythe': {'attack': 17, 'bleed': True, 'desc': 'Reaps flesh and soul alike.'},
    'soul_reaver': {'attack': 30, 'mana_bonus': 15, 'desc': 'A blade that hungers.'},
    'ashen_bow': {'attack': 18, 'range': True, 'desc': 'Strung with cinder sinew.'},
    'cinder_claw': {'attack': 19, 'fire_damage': 4, 'desc': 'Claws of molten wrath.'},
    'frost_glaive': {'attack': 16, 'ice_slow': True, 'desc': 'A polearm of ice.'},
    'abyssal_whip': {'attack': 15, 'dark_damage': 5, 'desc': 'Lashes from the void.'},
    'rune_blade': {'attack': 20, 'spell_bonus': 8, 'desc': 'Etched with power.'}
}

armor = {
    'leather_armor': {'defense': 3, 'desc': 'Tough hide, worn but trusty.'},
    'iron_plate': {'defense': 5, 'desc': 'Heavy steel guards your bones.'},
    'chain_vest': {'defense': 4, 'desc': 'Links rattle with each step.'},
    'mage_cloak': {'defense': 2, 'mana_bonus': 20, 'desc': 'Woven with arcane thread.'},
    'shadow_mail': {'defense': 6, 'stealth': True, 'desc': 'Armor of night’s embrace.'},
    'dragon_scale': {'defense': 8, 'fire_resist': True, 'desc': 'Scales of a fallen drake.'},
    'bone_plate': {'defense': 7, 'bleed_resist': True, 'desc': 'Carved from death’s remnants.'},
    'rune_shroud': {'defense': 4, 'spell_bonus': 5, 'desc': 'Hums with mystic wards.'},
    'void_guard': {'defense': 10, 'dark_resist': True, 'desc': 'Forged in the abyss.'},
    'ashen_hide': {'defense': 5, 'fire_resist': True, 'desc': 'Charred but resilient.'},
    'frost_mail': {'defense': 6, 'ice_resist': True, 'desc': 'Gleams with frost.'},
    'soul_weave': {'defense': 3, 'mana_bonus': 25, 'desc': 'Threads of lost spirits.'}
}

spells = {
    'fireball': {'damage': 20, 'mana_cost': 10, 'desc': 'A blazing orb of ruin.'},
    'heal': {'heal': 30, 'mana_cost': 15, 'desc': 'Mends flesh with light.'},
    'levitation': {'mana_cost': 5, 'desc': 'Defies the earth’s pull.'},
    'frost_bolt': {'damage': 15, 'slow': True, 'mana_cost': 12, 'desc': 'Freezes and shatters.'},
    'lightning_strike': {'damage': 25, 'mana_cost': 20, 'desc': 'Thunder rends the dark.'},
    'shadow_veil': {'stealth': True, 'mana_cost': 15, 'desc': 'Cloaks you in gloom.'},
    'barrier': {'defense_bonus': 5, 'duration': 3, 'mana_cost': 15, 'desc': 'A shield of will.'},
    'teleport': {'mana_cost': 30, 'desc': 'Warps space to your whim.'},
    'soul_drain': {'damage': 18, 'heal': 10, 'mana_cost': 20, 'desc': 'Steals life’s essence.'},
    'ash_cloud': {'blind': True, 'mana_cost': 25, 'desc': 'Chokes sight with ash.'},
    'void_pull': {'damage': 22, 'mana_cost': 18, 'desc': 'Drags foes to doom.'},
    'ice_shield': {'defense_bonus': 7, 'duration': 2, 'mana_cost': 20, 'desc': 'A frigid bulwark.'}
}

trinkets = {
    'ruby_ring': {'attack_bonus': 3, 'desc': 'Glows with martial fire.'},
    'sapphire_amulet': {'mana_bonus': 20, 'desc': 'Pulses with mana’s tide.'},
    'emerald_clasp': {'defense_bonus': 2, 'desc': 'Steadies your stance.'},
    'dragon_tooth': {'attack_bonus': 5, 'fire_resist': True, 'desc': 'A drake’s fang, sharp.'},
    'skull_charm': {'mana_bonus': 10, 'dark_resist': True, 'desc': 'Whispers of the dead.'},
    'rune_stone': {'spell_bonus': 3, 'desc': 'Enhances arcane might.'},
    'ashen_ember': {'fire_damage': 2, 'fire_resist': True, 'desc': 'Smolders eternally.'},
    'frost_shard': {'ice_resist': True, 'mana_bonus': 15, 'desc': 'Chills to the touch.'}
}

consumables = {
    'healing_potion': {'heal': 30, 'desc': 'Restores vigor swiftly.'},
    'mana_elixir': {'mana_restore': 25, 'desc': 'Replenishes mystic reserves.'},
    'strength_draught': {'attack_bonus': 5, 'duration': 5, 'desc': 'Surges with power.'},
    'endurance_vial': {'defense_bonus': 3, 'duration': 5, 'desc': 'Hardens your shell.'},
    'fire_tonic': {'fire_damage': 5, 'duration': 3, 'desc': 'Ignites your strikes.'},
    'ice_draught': {'ice_resist': True, 'duration': 5, 'desc': 'Wards off frost.'},
    'shadow_essence': {'stealth': True, 'duration': 3, 'desc': 'Fades you from sight.'}
}

chests = {
    'dusty_chest': {'contents': ['healing_potion', 'rusted_sword'], 'locked': False, 'desc': 'Coated in ages of grime.'},
    'rune_chest': {'contents': ['spell_scroll_frost_bolt', 'ruby_ring'], 'locked': True, 'key': 'rune_key', 'desc': 'Etched with glowing runes.'},
    'shadow_chest': {'contents': ['shadow_blade', 'mana_elixir'], 'locked': False, 'desc': 'Dark as the abyss.'},
    'dragon_hoard': {'contents': ['dragon_sword', 'dragon_scale'], 'locked': True, 'key': 'dragon_key', 'desc': 'Piled with drake’s riches.'},
    'void_coffer': {'contents': ['void_axe', 'endurance_vial'], 'locked': True, 'key': 'void_key', 'desc': 'Hums with dark energy.'},
    'cinder_box': {'contents': ['cinder_claw', 'fire_tonic'], 'locked': False, 'desc': 'Warm to the touch.'}
}

# --- Crafting Recipes ---
crafting_recipes = {
    'healing_potion': {'ingredients': {'herb': 2, 'vial': 1}, 'souls': 10, 'desc': 'A potion to mend wounds.'},
    'mana_elixir': {'ingredients': {'crystal_shard': 1, 'vial': 1}, 'souls': 15, 'desc': 'Restores arcane energy.'},
    'iron_sword': {'ingredients': {'iron_ore': 2, 'leather': 1}, 'souls': 25, 'desc': 'A sturdy blade.'},
    'rune_blade': {'ingredients': {'iron_sword': 1, 'rune_stone': 1}, 'souls': 50, 'desc': 'Infused with magic.'}
}

# --- Enemies ---
enemies = {
    'skeleton': {'name': 'Skeleton', 'health': 20, 'attack': 5, 'defense': 2, 'xp': 10, 'souls': 5, 'description': 'A rattling husk with a dull blade.', 'ai': 'basic'},
    'golem': {'name': 'Golem', 'health': 50, 'attack': 10, 'defense': 5, 'xp': 25, 'souls': 15, 'description': 'A lumbering stone brute.', 'ai': 'tank'},
    'shadow_beast': {'name': 'Shadow Beast', 'health': 30, 'attack': 8, 'defense': 3, 'xp': 15, 'souls': 10, 'description': 'A clawed nightmare from the dark.', 'ai': 'aggressive'},
    'mage_apprentice': {'name': 'Mage Apprentice', 'health': 25, 'attack': 7, 'defense': 2, 'xp': 20, 'souls': 12, 'description': 'A reckless spell-slinger.', 'ai': 'caster'},
    'minotaur': {'name': 'Minotaur', 'health': 40, 'attack': 12, 'defense': 4, 'xp': 30, 'souls': 20, 'description': 'A horned beast of raw fury.', 'ai': 'aggressive'},
    'guardian': {'name': 'Guardian', 'health': 60, 'attack': 15, 'defense': 6, 'xp': 40, 'souls': 25, 'description': 'A stoic sentinel of the relic.', 'ai': 'tank'},
    'wraith': {'name': 'Wraith', 'health': 25, 'attack': 7, 'defense': 2, 'xp': 20, 'souls': 15, 'description': 'A spectral wail in the gloom.', 'ai': 'stealth'},
    'drake': {'name': 'Drake', 'health': 70, 'attack': 18, 'defense': 7, 'xp': 50, 'souls': 30, 'description': 'A fire-spitting scale-wall.', 'ai': 'aggressive'},
    'necromancer': {'name': 'Necromancer', 'health': 40, 'attack': 10, 'defense': 3, 'xp': 35, 'souls': 25, 'description': 'A death-weaver with cold eyes.', 'ai': 'caster'},
    'ice_wyrm': {'name': 'Ice Wyrm', 'health': 55, 'attack': 14, 'defense': 5, 'xp': 45, 'souls': 28, 'description': 'A frozen terror with icy fangs.', 'ai': 'tank'},
    'relic_warden': {'name': 'Relic Warden', 'health': 150, 'attack': 25, 'defense': 10, 'xp': 100, 'souls': 50, 'description': 'A towering knight clad in relic-forged steel, its blade hums with doom.', 'ai': 'boss'},
    'ashen_hound': {'name': 'Ashen Hound', 'health': 35, 'attack': 9, 'defense': 3, 'xp': 20, 'souls': 12, 'description': 'A charred beast with ember eyes.', 'ai': 'aggressive'},
    'void_stalker': {'name': 'Void Stalker', 'health': 45, 'attack': 11, 'defense': 4, 'xp': 30, 'souls': 18, 'description': 'A shadow that hunts with glee.', 'ai': 'stealth'},
    'frost_specter': {'name': 'Frost Specter', 'health': 30, 'attack': 8, 'defense': 2, 'xp': 25, 'souls': 15, 'description': 'A chill spirit of icy wrath.', 'ai': 'caster'}
}

# --- Rooms ---
rooms = {
    'ruined_atrium': {
        'description': 'A crumbled atrium, the empire’s broken gate. Moss chokes the stones, a bonfire sputters.',
        'exits': {'north': 'grand_hall', 'east': 'windy_tunnel', 'west': 'shattered_vestibule'},
        'objects': ['rusted_sword', 'healing_potion'],
        'enemies': [],
        'traps': [],
        'bonfire': True,
        'lore': 'The empire’s welcome, now a grave marker.',
        'chests': ['dusty_chest']
    },
    'windy_tunnel': {
        'description': 'A howling tunnel of jagged rock. The wind bites like a ghost’s wail.',
        'exits': {'west': 'ruined_atrium', 'east': 'crystal_cavern', 'north': 'ashen_gorge'},
        'objects': ['mana_elixir'],
        'enemies': ['shadow_beast'],
        'traps': ['poison_gas_trap'],
        'bonfire': False,
        'lore': 'The air screams of lost souls.',
        'chests': []
    },
    'crystal_cavern': {
        'description': 'Crystals gleam like frozen stars, casting eerie light on bones.',
        'exits': {'west': 'windy_tunnel', 'south': 'flooded_passage', 'north': 'ice_passage'},
        'objects': ['crystal_staff', 'spell_scroll_fireball'],
        'enemies': ['skeleton', 'skeleton'],
        'traps': [],
        'bonfire': True,
        'lore': 'Mages bled here to bind the crystals’ power.',
        'chests': ['rune_chest']
    },
    'flooded_passage': {
        'description': 'A drowned hall, water black and still. A bridge creaks north.',
        'exits': {'north': 'crystal_cavern', 'east': 'sunken_chamber'},
        'objects': ['rope', 'leather_armor'],
        'enemies': [],
        'traps': ['thorny_vines'],
        'bonfire': False,
        'lore': 'The flood swallowed the unworthy.',
        'chests': []
    },
    'sunken_chamber': {
        'description': 'A submerged ruin, carvings weeping with age. A grate looms.',
        'exits': {'west': 'flooded_passage', 'up': 'secret_trove', 'north': 'labyrinth_of_echoes'},
        'objects': ['iron_sword'],
        'enemies': ['mage_apprentice'],
        'traps': [],
        'bonfire': False,
        'lore': 'The walls mourn the empire’s collapse.',
        'chests': ['shadow_chest']
    },
    'secret_trove': {
        'description': 'A thief’s cache, glittering with stolen glory.',
        'exits': {'down': 'sunken_chamber'},
        'objects': ['emerald', 'iron_plate', 'strength_draught'],
        'enemies': [],
        'traps': [],
        'bonfire': False,
        'lore': 'Greed’s last laugh echoes here.',
        'chests': []
    },
    'grand_hall': {
        'description': 'A vast hall of faded grandeur, pillars cracked like old bones.',
        'exits': {'south': 'ruined_atrium', 'north': 'throne_antechamber', 'west': 'dark_abyss', 'east': 'library'},
        'objects': ['torch', 'chain_vest'],
        'enemies': [],
        'traps': [],
        'bonfire': True,
        'lore': 'Kings feasted here; now silence reigns.',
        'chests': []
    },
    'dark_abyss': {
        'description': 'A pit of black despair, alive with skittering dread.',
        'exits': {'east': 'grand_hall', 'north': 'hidden_vault', 'south': 'relic_vault'},
        'objects': ['golden_key', 'shadow_blade'],
        'enemies': ['shadow_beast'],
        'traps': ['false_floor'],
        'bonfire': False,
        'lore': 'The abyss devoured the empire’s sins.',
        'chests': []
    },
    'hidden_vault': {
        'description': 'A hollow vault, its treasure long plundered.',
        'exits': {'south': 'dark_abyss', 'east': 'forge_of_the_ancients'},
        'objects': ['silver_coin', 'iron_ore', 'mana_elixir'],
        'enemies': [],
        'traps': [],
        'bonfire': False,
        'lore': 'A tomb for what once was.',
        'chests': ['dusty_chest']
    },
    'library': {
        'description': 'Shelves groan under dust and secrets, a tome pulsing faintly.',
        'exits': {'west': 'grand_hall', 'north': 'oracle_chamber', 'east': 'arcane_sanctum'},
        'objects': ['arcane_tome', 'spell_scroll_frost_bolt'],
        'enemies': ['mage_apprentice'],
        'traps': [],
        'bonfire': False,
        'lore': 'Knowledge rots here, unclaimed.',
        'chests': []
    },
    'oracle_chamber': {
        'description': 'The Oracle looms, a statue of cryptic silence.',
        'exits': {'south': 'library', 'west': 'tower_of_the_mage'},
        'objects': ['rune_key', 'ruby_ring'],
        'enemies': [],
        'traps': [],
        'bonfire': False,
        'lore': 'The Oracle saw the end and said nothing.',
        'chests': []
    },
    'throne_antechamber': {
        'description': 'A cracked marble hall, prelude to royal ruin.',
        'exits': {'south': 'grand_hall', 'north': 'throne_room'},
        'objects': ['mage_cloak'],
        'enemies': ['guardian'],
        'traps': [],
        'bonfire': False,
        'lore': 'Guards bled here for a dead king.',
        'chests': []
    },
    'throne_room': {
        'description': 'A throne of cold stone, flanked by shattered statues.',
        'exits': {'south': 'throne_antechamber', 'west': 'chamber_of_trials', 'north': 'relic_vault'},
        'objects': ['crown', 'gleaming_sword'],
        'enemies': ['guardian'],
        'traps': [],
        'bonfire': True,
        'lore': 'Betrayal was crowned here.',
        'chests': []
    },
    'forge_of_the_ancients': {
        'description': 'A smithy of eternal flame, anvil scarred by legend.',
        'exits': {'west': 'hidden_vault', 'north': 'forgotten_mines', 'south': 'lava_chamber'},
        'objects': ['forge_hammer', 'flame_spear'],
        'enemies': ['golem'],
        'traps': [],
        'bonfire': False,
        'lore': 'Steel sang here, now it rusts.',
        'chests': [],
        'crafting_station': True
    },
    'garden_of_shadows': {
        'description': 'A festering tangle of thorns and rot, alive with malice.',
        'exits': {'west': 'crypt_of_the_fallen', 'south': 'deep_cavern'},
        'objects': ['poison_antidote', 'shadow_mail'],
        'enemies': ['shadow_beast', 'shadow_beast'],
        'traps': ['thorny_vines'],
        'bonfire': False,
        'lore': 'Beauty died here, choked by darkness.',
        'chests': []
    },
    'crypt_of_the_fallen': {
        'description': 'A crypt of restless dead, tombs cracked and weeping.',
        'exits': {'south': 'grand_hall', 'east': 'garden_of_shadows'},
        'objects': ['ancient_key', 'bone_scythe'],
        'enemies': ['skeleton', 'skeleton'],
        'traps': ['poison_gas_trap'],
        'bonfire': False,
        'lore': 'The fallen guard their shame.',
        'chests': ['shadow_chest']
    },
    'tower_of_the_mage': {
        'description': 'A spire of cracked stone, buzzing with old magic.',
        'exits': {'down': 'oracle_chamber', 'up': 'labyrinth_of_echoes'},
        'objects': ['spell_scroll_levitation', 'sapphire_amulet'],
        'enemies': ['mage_apprentice', 'mage_apprentice'],
        'traps': ['magical_runes'],
        'bonfire': False,
        'lore': 'A mage’s pride crumbled here.',
        'chests': []
    },
    'labyrinth_of_echoes': {
        'description': 'A maze of stone and madness, echoes twisting your mind.',
        'exits': {'down': 'tower_of_the_mage', 'south': 'sunken_chamber'},
        'objects': ['thunder_mace'],
        'enemies': ['minotaur'],
        'traps': ['false_floor'],
        'bonfire': False,
        'lore': 'Lost souls wander these turns.',
        'chests': []
    },
    'chamber_of_trials': {
        'description': 'A gauntlet of riddles and ruin, testing the bold.',
        'exits': {'east': 'throne_room'},
        'objects': ['rune_of_passage', 'endurance_vial'],
        'enemies': ['guardian'],
        'traps': [],
        'bonfire': False,
        'lore': 'Only the cunning survive this crucible.',
        'chests': [],
        'puzzle': {'riddle': 'I am full of holes, yet hold water. What am I?', 'answer': 'sponge', 'reward': 'void_axe'}
    },
    'shattered_vestibule': {
        'description': 'A hall of fractured mirrors, reflecting broken fates.',
        'exits': {'east': 'ruined_atrium', 'north': 'echoing_crypt'},
        'objects': ['healing_potion'],
        'enemies': ['wraith'],
        'traps': [],
        'bonfire': False,
        'lore': 'Vanity’s shards cut deep.',
        'chests': []
    },
    'echoing_crypt': {
        'description': 'A crypt where every sound haunts, tombs agape.',
        'exits': {'south': 'shattered_vestibule', 'west': 'shadow_vault'},
        'objects': ['bone_plate'],
        'enemies': ['skeleton', 'wraith'],
        'traps': ['poison_gas_trap'],
        'bonfire': False,
        'lore': 'The dead chorus never fades.',
        'chests': []
    },
    'shadow_vault': {
        'description': 'A vault of eternal night, hoarding cursed spoils.',
        'exits': {'east': 'echoing_crypt', 'north': 'ice_passage'},
        'objects': ['emerald_clasp', 'ice_dagger'],
        'enemies': ['shadow_beast'],
        'traps': ['false_floor'],
        'bonfire': False,
        'lore': 'Darkness sealed its treasures here.',
        'chests': ['rune_chest']
    },
    'ice_passage': {
        'description': 'A frozen vein of the empire, ice sharp as blades.',
        'exits': {'south': 'shadow_vault', 'north': 'frozen_lair', 'west': 'crystal_cavern'},
        'objects': ['dragon_key'],
        'enemies': ['ice_wyrm'],
        'traps': ['ice_spikes'],
        'bonfire': True,
        'lore': 'Cold guards its own.',
        'chests': []
    },
    'frozen_lair': {
        'description': 'A lair of frost and fury, dragon’s breath frozen in time.',
        'exits': {'south': 'ice_passage', 'east': 'lava_chamber', 'north': 'frosted_depths'},
        'objects': ['dragon_tooth'],
        'enemies': ['ice_wyrm'],
        'traps': [],
        'bonfire': False,
        'lore': 'A wyrm’s tomb, icy and unyielding.',
        'chests': ['dragon_hoard']
    },
    'lava_chamber': {
        'description': 'A hellscape of molten rivers, heat choking the air.',
        'exits': {'west': 'frozen_lair', 'north': 'forge_of_the_ancients', 'east': 'cinder_halls'},
        'objects': ['fire_tonic', 'ashen_bow'],
        'enemies': ['drake'],
        'traps': ['lava_flow'],
        'bonfire': False,
        'lore': 'Fire forged the empire’s wrath.',
        'chests': []
    },
    'arcane_sanctum': {
        'description': 'A sanctum of humming runes, magic thick as blood.',
        'exits': {'west': 'library', 'east': 'mana_well'},
        'objects': ['rune_shroud', 'spell_scroll_soul_drain'],
        'enemies': ['necromancer'],
        'traps': ['magical_runes'],
        'bonfire': False,
        'lore': 'Spells were born in this crucible.',
        'chests': []
    },
    'mana_well': {
        'description': 'A well of liquid mana, glowing with forbidden light.',
        'exits': {'west': 'arcane_sanctum', 'north': 'relic_vault'},
        'objects': ['mana_elixir', 'skull_charm'],
        'enemies': [],
        'traps': [],
        'bonfire': True,
        'lore': 'The empire drank deep from this font.',
        'chests': []
    },
    'forgotten_mines': {
        'description': 'Tunnels of dust and despair, ore veins long dead.',
        'exits': {'south': 'forge_of_the_ancients', 'east': 'deep_cavern'},
        'objects': ['thunder_mace', 'rune_stone'],
        'enemies': ['golem'],
        'traps': ['collapsing_ceiling'],
        'bonfire': False,
        'lore': 'Miners woke what should’ve slept.',
        'chests': []
    },
    'deep_cavern': {
        'description': 'A cavern of dripping fangs, shadows thick with menace.',
        'exits': {'west': 'forgotten_mines', 'north': 'garden_of_shadows', 'south': 'relic_vault', 'east': 'void_chasm'},
        'objects': ['void_guard'],
        'enemies': ['drake'],
        'traps': [],
        'bonfire': False,
        'lore': 'The deep hides its own kings.',
        'chests': ['dusty_chest']
    },
    'relic_vault': {
        'description': 'A sanctum of power, the Relic of Ages pulsing on its dais.',
        'exits': {'south': 'throne_room', 'north': 'mana_well', 'east': 'deep_cavern', 'west': 'dark_abyss'},
        'objects': ['relic_of_ages'],
        'enemies': ['relic_warden'],
        'traps': [],
        'bonfire': False,
        'lore': 'The empire’s soul rests here, fiercely guarded.',
        'chests': []
    },
    'ashen_gorge': {
        'description': 'A ravine of soot and cinders, air thick with ash.',
        'exits': {'north': 'windy_tunnel', 'south': 'bleak_ruins'},
        'objects': ['ashen_hide', 'fire_tonic'],
        'enemies': ['ashen_hound'],
        'traps': ['lava_flow'],
        'bonfire': False,
        'lore': 'Fire scarred this wound in the earth.',
        'chests': ['cinder_box']
    },
    'bleak_ruins': {
        'description': 'A husk of crumbled walls, ash drifting like snow.',
        'exits': {'north': 'ashen_gorge', 'east': 'wraith_spire'},
        'objects': ['cinder_claw'],
        'enemies': [],
        'traps': [],
        'bonfire': True,
        'lore': 'Once a stronghold, now a whisper.',
        'chests': []
    },
    'wraith_spire': {
        'description': 'A twisted spire piercing the gloom, wraiths circling.',
        'exits': {'west': 'bleak_ruins', 'north': 'soul_pit'},
        'objects': ['spell_scroll_ash_cloud'],
        'enemies': ['wraith', 'wraith'],
        'traps': ['magical_runes'],
        'bonfire': False,
        'lore': 'Spirits guard this forsaken peak.',
        'chests': []
    },
    'soul_pit': {
        'description': 'A pit of moaning souls, air heavy with despair.',
        'exits': {'south': 'wraith_spire', 'east': 'relic_vault'},
        'objects': ['soul_weave', 'void_key'],
        'enemies': ['necromancer'],
        'traps': [],
        'bonfire': False,
        'lore': 'The damned linger here, unfreed.',
        'chests': ['void_coffer']
    },
    'cinder_halls': {
        'description': 'Halls of scorched stone, embers glowing in cracks.',
        'exits': {'west': 'lava_chamber', 'north': 'ember_vault'},
        'objects': ['ashen_ember'],
        'enemies': ['ashen_hound'],
        'traps': ['lava_flow'],
        'bonfire': False,
        'lore': 'Fire’s echo haunts these walls.',
        'chests': []
    },
    'ember_vault': {
        'description': 'A vault of smoldering wealth, heat pulsing from within.',
        'exits': {'south': 'cinder_halls', 'east': 'relic_vault'},
        'objects': ['rune_blade', 'fire_tonic'],
        'enemies': ['drake'],
        'traps': [],
        'bonfire': False,
        'lore': 'Treasures burn here, untaken.',
        'chests': ['cinder_box']
    },
    'frosted_depths': {
        'description': 'A frozen expanse, ice cracking underfoot.',
        'exits': {'south': 'frozen_lair', 'north': 'glacial_tomb'},
        'objects': ['frost_glaive'],
        'enemies': ['frost_specter'],
        'traps': ['ice_spikes'],
        'bonfire': False,
        'lore': 'Cold claims all who linger.',
        'chests': []
    },
    'glacial_tomb': {
        'description': 'A tomb of ice, its chill eternal.',
        'exits': {'south': 'frosted_depths', 'west': 'relic_vault'},
        'objects': ['frost_mail', 'ice_draught'],
        'enemies': ['ice_wyrm'],
        'traps': [],
        'bonfire': True,
        'lore': 'A frozen king rests here, unyielding.',
        'chests': []
    },
    'void_chasm': {
        'description': 'A gaping maw of darkness, swallowing light.',
        'exits': {'east': 'deep_cavern', 'north': 'abyssal_rift'},
        'objects': ['abyssal_whip'],
        'enemies': ['void_stalker'],
        'traps': ['false_floor'],
        'bonfire': False,
        'lore': 'The void hungers for more.',
        'chests': []
    },
    'abyssal_rift': {
        'description': 'A tear in reality, shadows writhing within.',
        'exits': {'south': 'void_chasm', 'west': 'relic_vault'},
        'objects': ['spell_scroll_void_pull', 'shadow_essence'],
        'enemies': ['void_stalker'],
        'traps': [],
        'bonfire': False,
        'lore': 'The empire’s end began here.',
        'chests': ['void_coffer']
    }
}

# --- Global State ---
current_room = 'ruined_atrium'
last_bonfire = 'ruined_atrium'
master_enemies = {
    'windy_tunnel': ['shadow_beast'],
    'crystal_cavern': ['skeleton', 'skeleton'],
    'sunken_chamber': ['mage_apprentice'],
    'dark_abyss': ['shadow_beast'],
    'library': ['mage_apprentice'],
    'throne_room': ['guardian'],
    'forge_of_the_ancients': ['golem'],
    'garden_of_shadows': ['shadow_beast', 'shadow_beast'],
    'crypt_of_the_fallen': ['skeleton', 'skeleton'],
    'tower_of_the_mage': ['mage_apprentice', 'mage_apprentice'],
    'labyrinth_of_echoes': ['minotaur'],
    'chamber_of_trials': ['guardian'],
    'shattered_vestibule': ['wraith'],
    'echoing_crypt': ['skeleton', 'wraith'],
    'shadow_vault': ['shadow_beast'],
    'ice_passage': ['ice_wyrm'],
    'frozen_lair': ['ice_wyrm'],
    'lava_chamber': ['drake'],
    'arcane_sanctum': ['necromancer'],
    'mana_well': [],
    'throne_antechamber': ['guardian'],
    'forgotten_mines': ['golem'],
    'deep_cavern': ['drake'],
    'relic_vault': ['relic_warden'],
    'ashen_gorge': ['ashen_hound'],
    'bleak_ruins': [],
    'wraith_spire': ['wraith', 'wraith'],
    'soul_pit': ['necromancer'],
    'cinder_halls': ['ashen_hound'],
    'ember_vault': ['drake'],
    'frosted_depths': ['frost_specter'],
    'glacial_tomb': ['ice_wyrm'],
    'void_chasm': ['void_stalker'],
    'abyssal_rift': ['void_stalker']
}
active_effects: Dict[str, Dict] = {}

# --- Helper Functions ---
def enter_room(room: Dict, player: Dict) -> bool:
    """Original room entry function for compatibility."""
    if 'enemies' in room and room['enemies']:
        for enemy_name in room['enemies']:
            enemy = enemies[enemy_name].copy()
            if not combat(player, enemy):
                handle_death()
                return False
        room['enemies'] = []
    if 'traps' in room and room['traps']:
        if 'poison_gas_trap' in room['traps']:
            print("Poison gas seeps from the cracks!")
            player['health'] -= 10
            print("You take 10 damage.")
            room['traps'].remove('poison_gas_trap')
        elif 'thorny_vines' in room['traps']:
            print("Vines snag and tear at you!")
            player['health'] -= 5
            print("You take 5 damage.")
        elif 'false_floor' in room['traps']:
            print("The floor drops out beneath you!")
            player['health'] -= 20
            print("You take 20 damage.")
            room['traps'].remove('false_floor')
        elif 'magical_runes' in room['traps']:
            print("Runes ignite, burning your flesh!")
            player['health'] -= 15
            print("You take 15 damage.")
            room['traps'].remove('magical_runes')
        if player['health'] <= 0:
            handle_death()
            return False
    print(room['description'])
    return True

def combat(player: Dict, enemy: Dict) -> bool:
    """Original combat function for compatibility."""
    print(f"You face a {enemy['description']}")
    while player['health'] > 0 and enemy['health'] > 0:
        action = input("Attack, cast spell, use item, or flee? ").lower()
        if action == 'attack':
            damage = max(0, player['attack'] - enemy['defense'])
            enemy['health'] -= damage
            print(f"You deal {damage} damage to the {enemy['name']}.")
        elif action == 'cast spell':
            if player['spells']:
                spell = input(f"Choose a spell ({', '.join(player['spells'])}): ").lower()
                if spell in player['spells'] and player['mana'] >= spells[spell]['mana_cost']:
                    player['mana'] -= spells[spell]['mana_cost']
                    if 'damage' in spells[spell]:
                        enemy['health'] -= spells[spell]['damage']
                        print(f"You cast {spell}, dealing {spells[spell]['damage']} damage.")
                    elif 'heal' in spells[spell]:
                        player['health'] = min(player['max_health'], player['health'] + spells[spell]['heal'])
                        print(f"You cast {spell}, healing {spells[spell]['heal']} HP.")
                else:
                    print("Invalid spell or not enough mana.")
            else:
                print("You know no spells.")
        elif action == 'use item':
            if player['inventory']:
                item = input(f"Choose an item ({', '.join(player['inventory'])}): ").lower()
                if item == 'healing_potion' and item in player['inventory']:
                    player['health'] = min(player['max_health'], player['health'] + 30)
                    player['inventory'].remove('healing_potion')
                    print("You drink a healing potion, restoring 30 HP.")
                else:
                    print("That item can’t be used here.")
            else:
                print("Your inventory is barren.")
        elif action == 'flee':
            if random.random() < 0.3:
                print("You flee the fray!")
                return True
            print("You can’t break free!")
        if enemy['health'] > 0:
            damage = max(0, enemy['attack'] - player['defense'])
            player['health'] -= damage
            print(f"The {enemy['name']} strikes for {damage} damage.")
    if player['health'] <= 0:
        print(f"The {enemy['name']} has broken you.")
        return False
    print(f"You vanquish the {enemy['name']}!")
    return True

def handle_death() -> None:
    """Original death handler for compatibility."""
    global current_room
    print("Death takes you. The bonfire’s glow calls you back...")
    current_room = last_bonfire
    player['health'] = player['max_health']
    player['mana'] = player['max_mana']
    for room_name, enemy_list in master_enemies.items():
        rooms[room_name]['enemies'] = enemy_list.copy()

def sarcophagus_puzzle() -> bool:
    """Original sarcophagus puzzle for compatibility."""
    print("Riddle: 'I am taken from a mine, shut in a wooden case, never released, yet used by all. What am I?'")
    answer = input("Answer: ").lower()
    if answer in ['graphite', 'pencil lead']:
        print("The sarcophagus grinds open, revealing a gleaming sword!")
        rooms['crypt_of_the_fallen']['objects'].append('gleaming_sword')
        return True
    print("The riddle stands firm.")
    return False

def enhanced_enter_room(room: Dict, player: Dict) -> bool:
    """Enhanced room entry with new mechanics."""
    player['explored'].add(current_room)
    print(f"\n{room['description']}")
    if 'lore' in room:
        print(f"Lore: {room['lore']}")
    if room.get('bonfire'):
        print("A bonfire flickers, offering solace in the gloom.")
    if 'chests' in room and room['chests']:
        print("Treasures whisper: " + ', '.join(room['chests']))
    if 'crafting_station' in room:
        print("A crafting station hums with potential.")
    if 'enemies' in room and room['enemies']:
        for enemy_name in room['enemies'][:]:
            enemy = enemies[enemy_name].copy()
            if not enhanced_combat(player, enemy, enemy_name):
                handle_death_enhanced(player)
                return False
            room['enemies'].remove(enemy_name)
    if 'traps' in room and room['traps']:
        trap_effects = {
            'poison_gas_trap': (10, "Poison gas chokes the air!", "You take 10 damage."),
            'thorny_vines': (5, "Vines tear at your flesh!", "You take 5 damage."),
            'false_floor': (20, "The floor collapses beneath you!", "You take 20 damage."),
            'magical_runes': (15, "Runes flare, searing your skin!", "You take 15 damage."),
            'ice_spikes': (12, "Ice spikes pierce upward!", "You take 12 damage."),
            'lava_flow': (25, "Lava surges, burning all!", "You take 25 damage."),
            'collapsing_ceiling': (18, "The ceiling rains stone!", "You take 18 damage.")
        }
        for trap in room['traps'][:]:
            damage, message, effect = trap_effects[trap]
            print(message)
            if any(t in player['trinkets'] for t in trinkets if trap == 'poison_gas_trap' and 'dark_resist' in trinkets[t]):
                print("Your trinket wards off the poison!")
                damage = 0
            player['health'] -= damage
            print(effect)
            room['traps'].remove(trap)
            if player['health'] <= 0:
                handle_death_enhanced(player)
                return False
    if 'puzzle' in room:
        solve_puzzle(room, player)
    exits = room['exits']
    if exits:
        print("Paths beckon: " + ', '.join([f"{d} to {dest}" for d, dest in exits.items()]))
    return True

def enhanced_combat(player: Dict, enemy: Dict, enemy_key: str) -> bool:
    """Enhanced combat with dynamic enemy AI and effects."""
    print(f"\nA {enemy['description']} bars your path!")
    turns = 0
    enemy_ai = enemy['ai']
    while player['health'] > 0 and enemy['health'] > 0:
        turns += 1
        print(f"\n=== Turn {turns} ===")
        print(f"{player['name']}: {player['health']}/{player['max_health']} HP | Mana: {player['mana']}")
        print(f"{enemy['name']}: {enemy['health']} HP")
        action = input("Attack, cast spell, use item, or flee? ").lower()
        
        # Player Turn
        if action == 'attack':
            damage = max(0, player['attack'] + active_effects.get('strength', {}).get('bonus', 0) - enemy['defense'])
            if random.random() < 0.15:
                damage *= 2
                print("Critical hit!")
            enemy['health'] -= damage
            print(f"You deal {damage} damage to the {enemy['name']}.")
            apply_weapon_effects(player, enemy)
        elif action == 'cast spell':
            if not player['spells']:
                print("You wield no spells.")
                continue
            spell = input(f"Choose a spell ({', '.join(player['spells'])}): ").lower()
            if spell in player['spells'] and player['mana'] >= spells[spell]['mana_cost']:
                player['mana'] -= spells[spell]['mana_cost']
                apply_spell_effects(player, enemy, spell)
            else:
                print("Not enough mana or invalid spell.")
        elif action == 'use item':
            if not player['inventory']:
                print("Your pack is empty.")
                continue
            item = input(f"Choose an item ({', '.join(player['inventory'])}): ").lower()
            apply_item_effects(player, enemy, item)
        elif action == 'flee':
            flee_chance = 0.3 + (0.3 if player['stealth'] or 'stealth' in active_effects else 0)
            if random.random() < flee_chance:
                print("You slip into the dark!")
                return True
            print("No escape this time!")
        
        # Enemy Turn
        if enemy['health'] > 0:
            defense = player['defense'] + sum(active_effects.get(e, {}).get('bonus', 0) for e in ['barrier', 'endurance'])
            damage = max(0, enemy['attack'] - defense)
            if player['stealth'] or 'blind' in active_effects:
                print(f"The {enemy['name']} flails, missing you!")
            else:
                enemy_action = enemy_ai_behavior(enemy_ai, player, enemy)
                if enemy_action == 'attack':
                    player['health'] -= damage
                    print(f"The {enemy['name']} strikes for {damage} damage.")
                elif enemy_action == 'special':
                    apply_enemy_special(enemy, player)
            
            if enemy['name'] == 'Relic Warden' and random.random() < 0.2:
                player['health'] -= 10
                print("The Warden’s blade hums, sapping 10 more HP!")
        
        update_effects(player)
    
    if player['health'] <= 0:
        print(f"\nThe {enemy['name']} claims your soul.")
        return False
    print(f"\nYou fell the {enemy['name']}!")
    player['xp'] += enemies[enemy_key]['xp']
    player['souls'] += enemies[enemy_key]['souls']
    check_level_up(player)
    check_achievements(player, enemy_key)
    return True

def apply_weapon_effects(player: Dict, enemy: Dict) -> None:
    """Apply special effects from equipped weapons."""
    weapon = weapons.get(player['equipped_weapon'], {})
    if 'fire_damage' in weapon:
        enemy['health'] -= weapon['fire_damage']
        print(f"Flames sear for {weapon['fire_damage']} extra damage!")
    if 'dark_damage' in weapon:
        enemy['health'] -= weapon['dark_damage']
        print(f"Darkness bites for {weapon['dark_damage']} extra damage!")
    if 'bleed' in weapon and random.random() < 0.3:
        active_effects['bleed'] = {'turns': 3, 'damage': 2, 'target': 'enemy'}
        print("The foe begins to bleed!")

def apply_spell_effects(player: Dict, enemy: Dict, spell: str) -> None:
    """Apply effects from cast spells."""
    spell_data = spells[spell]
    bonus = weapons.get(player['equipped_weapon'], {}).get('spell_bonus', 0)
    if 'damage' in spell_data:
        damage = spell_data['damage'] + bonus
        enemy['health'] -= damage
        print(f"You cast {spell}, dealing {damage} damage.")
    if 'heal' in spell_data:
        player['health'] = min(player['max_health'], player['health'] + spell_data['heal'])
        print(f"You cast {spell}, healing {spell_data['heal']} HP.")
    if 'stealth' in spell_data:
        active_effects['stealth'] = {'turns': 2}
        player['stealth'] = True
        print("You fade into shadow!")
    if 'defense_bonus' in spell_data:
        active_effects['barrier'] = {'turns': spell_data['duration'], 'bonus': spell_data['defense_bonus']}
        print(f"You cast {spell}, raising a shield!")
    if 'blind' in spell_data:
        active_effects['blind'] = {'turns': 2, 'target': 'enemy'}
        print("Ash blinds the foe!")

def apply_item_effects(player: Dict, enemy: Dict, item: str) -> None:
    """Apply effects from used items."""
    if item in consumables and item in player['inventory']:
        item_data = consumables[item]
        if 'heal' in item_data:
            player['health'] = min(player['max_health'], player['health'] + item_data['heal'])
            print(f"You use {item}, healing {item_data['heal']} HP.")
        elif 'mana_restore' in item_data:
            player['mana'] = min(player['max_mana'], player['mana'] + item_data['mana_restore'])
            print(f"You use {item}, restoring {item_data['mana_restore']} mana.")
        elif 'attack_bonus' in item_data:
            active_effects['strength'] = {'turns': item_data['duration'], 'bonus': item_data['attack_bonus']}
            print(f"You quaff {item}, strength surging!")
        elif 'defense_bonus' in item_data:
            active_effects['endurance'] = {'turns': item_data['duration'], 'bonus': item_data['defense_bonus']}
            print(f"You use {item}, steeling your guard!")
        elif 'fire_damage' in item_data:
            active_effects['fire'] = {'turns': item_data['duration'], 'damage': item_data['fire_damage']}
            print(f"You imbibe {item}, flames licking your blade!")
        player['inventory'].remove(item)

def enemy_ai_behavior(ai_type: str, player: Dict, enemy: Dict) -> str:
    """Determine enemy actions based on AI type."""
    if ai_type == 'basic':
        return 'attack'
    elif ai_type == 'tank':
        return 'attack' if random.random() < 0.8 else 'special'
    elif ai_type == 'aggressive':
        return 'attack'
    elif ai_type == 'caster':
        return 'special' if random.random() < 0.5 and enemy['health'] > 10 else 'attack'
    elif ai_type == 'stealth':
        return 'special' if random.random() < 0.3 else 'attack'
    elif ai_type == 'boss':
        return 'special' if random.random() < 0.4 else 'attack'
    return 'attack'

def apply_enemy_special(enemy: Dict, player: Dict) -> None:
    """Apply special abilities for enemies."""
    if enemy['ai'] == 'caster':
        player['health'] -= 5
        print(f"The {enemy['name']} casts a dark spell, dealing 5 damage!")
    elif enemy['ai'] == 'tank':
        enemy['defense'] += 2
        print(f"The {enemy['name']} hardens its stance!")
    elif enemy['ai'] == 'stealth':
        enemy['attack'] += 3
        print(f"The {enemy['name']} fades, striking harder next turn!")
    elif enemy['ai'] == 'boss':
        player['mana'] -= 10
        print(f"The {enemy['name']} drains your mana by 10!")

def update_effects(player: Dict) -> None:
    """Update and expire active effects."""
    for effect in list(active_effects.keys()):
        active_effects[effect]['turns'] -= 1
        if 'damage' in active_effects[effect] and active_effects[effect]['target'] == 'enemy':
            'enemy'['health'] -= active_effects[effect]['damage']
            print(f"{effect.capitalize()} deals {active_effects[effect]['damage']} damage!")
        if active_effects[effect]['turns'] <= 0:
            if effect == 'stealth':
                player['stealth'] = False
            del active_effects[effect]
            print(f"Your {effect} fades.")

def handle_death_enhanced(player: Dict) -> None:
    """Enhanced death handler with soul loss."""
    global current_room
    print(f"\n{player['name']} falls, but the bonfire’s embers flare...")
    current_room = last_bonfire
    player['health'] = player['max_health']
    player['mana'] = player['max_mana']
    player['souls'] = player['souls'] // 2  # Lose half souls on death
    active_effects.clear()
    for room_name, enemy_list in master_enemies.items():
        rooms[room_name]['enemies'] = enemy_list.copy()
    print(f"You rise at {last_bonfire}, souls diminished.")

def check_level_up(player: Dict) -> None:
    """Check and handle player level-up."""
    xp_needed = player['level'] * 100
    if player['xp'] >= xp_needed:
        player['level'] += 1
        player['max_health'] += 25
        player['health'] = player['max_health']
        player['max_mana'] += 20
        player['mana'] = player['max_mana']
        player['attack'] += 4
        player['defense'] += 3
        print(f"\n{player['name']} rises to Level {player['level']}! Strength surges within.")

def check_achievements(player: Dict, enemy_key: str) -> None:
    """Check and award achievements."""
    if enemy_key == 'relic_warden' and 'Relic Conqueror' not in player['achievements']:
        player['achievements'].append('Relic Conqueror')
        print("Achievement Unlocked: Relic Conqueror - Vanquished the Relic Warden!")
    if len(player['explored']) >= 20 and 'Explorer of Shadows' not in player['achievements']:
        player['achievements'].append('Explorer of Shadows')
        print("Achievement Unlocked: Explorer of Shadows - Explored 20 realms!")

def solve_puzzle(room: Dict, player: Dict) -> None:
    """Solve room-specific puzzles."""
    if 'puzzle' in room and room['puzzle']:
        puzzle = room['puzzle']
        print(f"\nA riddle bars your way: '{puzzle['riddle']}'")
        answer = input("Answer: ").lower().strip()
        if answer == puzzle['answer']:
            item = puzzle['reward']
            room['objects'].append(item)
            print(f"Stone yields—revealed: {item}!")
            room.pop('puzzle')
        else:
            print("The riddle mocks your folly.")

def open_chest(chest_name: str, player: Dict) -> None:
    """Open a chest with enhanced mechanics."""
    chest = chests[chest_name]
    print(f"\n{chest['desc']}")
    if chest['locked']:
        if chest['key'] in player['inventory']:
            print(f"You unlock the {chest_name} with the {chest['key']}!")
            player['inventory'].remove(chest['key'])
        elif 'teleport' in player['spells'] and player['mana'] >= spells['teleport']['mana_cost']:
            print("You teleport the lock away with a spell!")
            player['mana'] -= spells['teleport']['mana_cost']
        else:
            print(f"The {chest_name} is sealed. You need a {chest['key']} or teleport spell.")
            return
    else:
        print(f"You wrench open the {chest_name}, hinges screaming.")
    for item in chest['contents']:
        player['inventory'].append(item)
        print(f"You claim: {item.capitalize()}")

def save_game(player: Dict) -> None:
    """Save the game state to a file."""
    game_state = {
        'player': player,
        'current_room': current_room,
        'last_bonfire': last_bonfire,
        'rooms': {k: {'enemies': v['enemies'], 'objects': v['objects'], 'chests': v['chests']} for k, v in rooms.items()},
        'active_effects': active_effects
    }
    with open(SAVE_FILE, 'w') as f:
        json.dump(game_state, f)
    print("Your journey is etched into the annals.")

def load_game() -> Tuple[Optional[Dict], str, str, Dict]:
    """Load the game state from a file."""
    if not os.path.exists(SAVE_FILE):
        print("No tale to reclaim from the void.")
        return None, 'ruined_atrium', 'ruined_atrium', {}
    with open(SAVE_FILE, 'r') as f:
        game_state = json.load(f)
    for room, data in game_state['rooms'].items():
        rooms[room]['enemies'] = data['enemies']
        rooms[room]['objects'] = data['objects']
        rooms[room]['chests'] = data['chests']
    print("You rise from the ashes of a past life.")
    return game_state['player'], game_state['current_room'], game_state['last_bonfire'], game_state['active_effects']

def craft_item(player: Dict, item: str) -> None:
    """Craft items at a crafting station."""
    if item not in crafting_recipes:
        print("No such recipe exists.")
        return
    recipe = crafting_recipes[item]
    if player['souls'] < recipe['souls']:
        print(f"Not enough souls. Required: {recipe['souls']}")
        return
    for ingredient, count in recipe['ingredients'].items():
        if player['inventory'].count(ingredient) < count:
            print(f"Missing {count - player['inventory'].count(ingredient)} {ingredient}(s).")
            return
    for ingredient, count in recipe['ingredients'].items():
        for _ in range(count):
            player['inventory'].remove(ingredient)
    player['souls'] -= recipe['souls']
    player['inventory'].append(item)
    print(f"You craft a {item}! {recipe['desc']}")

# --- Game Setup ---
print(f"Bonfire's Echo v{VERSION}")
print_lore()
if os.path.exists(SAVE_FILE):
    choice = input("Load saved game? (yes/no): ").lower()
    if choice.startswith('y'):
        loaded_player, loaded_room, loaded_bonfire, loaded_effects = load_game()
        if loaded_player:
            player = loaded_player
            current_room = loaded_room
            last_bonfire = loaded_bonfire
            active_effects = loaded_effects
    else:
        player = setup_player()
else:
    player = setup_player()
print_ascii_art()

# --- Game Loop ---
while True:
    room = rooms[current_room]
    if not enhanced_enter_room(room, player):
        continue
    if current_room == 'relic_vault' and 'relic_of_ages' in player['inventory']:
        print(f"\n{player['name']} grasps the Relic of Ages, its power a storm in your veins.")
        print("The Underground Empire shudders, light piercing the dark above. Victory is yours—for now.")
        player['achievements'].append('Relic Bearer')
        break
    command = input("> ").lower().split()
    if not command:
        print("The silence deafens.")
        continue
    verb = command[0]

    if verb == 'go' and len(command) > 1:
        direction = command[1]
        if direction in room['exits']:
            current_room = room['exits'][direction]
            print(f"You stagger {direction} into the abyss.")
        else:
            print("That way is barred or lost.")
    elif verb == 'take' and len(command) > 1:
        item = ' '.join(command[1:]).lower()
        if item in room['objects']:
            player['inventory'].append(item)
            room['objects'].remove(item)
            print(f"You take the {item}, another weight on your soul.")
        else:
            print("No such prize lies here.")
    elif verb == 'equip' and len(command) > 1:
        item = ' '.join(command[1:]).lower()
        if item in player['inventory']:
            if item in weapons:
                player['equipped_weapon'] = item
                player['attack'] = weapons[item]['attack']
                print(f"You wield the {item}. {weapons[item]['desc']}")
            elif item in armor:
                if player['equipped_armor']:
                    old_armor = armor[player['equipped_armor']]
                    player['max_mana'] -= old_armor.get('mana_bonus', 0)
                    player['mana'] = min(player['mana'], player['max_mana'])
                player['equipped_armor'] = item
                player['defense'] = armor[item]['defense']
                if 'mana_bonus' in armor[item]:
                    player['max_mana'] += armor[item]['mana_bonus']
                    player['mana'] = min(player['mana'], player['max_mana'])
                print(f"You don the {item}. {armor[item]['desc']}")
            elif item in trinkets:
                player['trinkets'].append(item)
                if 'attack_bonus' in trinkets[item]:
                    player['attack'] += trinkets[item]['attack_bonus']
                if 'defense_bonus' in trinkets[item]:
                    player['defense'] += trinkets[item]['defense_bonus']
                if 'mana_bonus' in trinkets[item]:
                    player['max_mana'] += trinkets[item]['mana_bonus']
                    player['mana'] = min(player['mana'], player['max_mana'])
                player['inventory'].remove(item)
                print(f"You wear the {item}. {trinkets[item]['desc']}")
            else:
                print(f"The {item} serves no purpose here.")
        else:
            print("You don’t possess that.")
    elif verb == 'learn' and len(command) > 1:
        item = ' '.join(command[1:]).lower()
        if item in player['inventory'] and item.startswith('spell_scroll_'):
            spell = item.split('_')[2]
            if spell in spells:
                player['spells'].append(spell)
                player['inventory'].remove(item)
                print(f"You master the {spell} spell. {spells[spell]['desc']}")
            else:
                print("That scroll’s secrets elude you.")
        else:
            print("No such scroll in your grasp.")
    elif verb == 'solve':
        sarcophagus_puzzle()
    elif verb == 'rest' and room.get('bonfire', False):
        player['health'] = player['max_health']
        player['mana'] = player['max_mana']
        last_bonfire = current_room
        print("You rest by the bonfire, its warmth a fleeting balm.")
    elif verb == 'stats':
        print_stats(player)
    elif verb == 'map':
        print_map(player)
    elif verb == 'open' and len(command) > 1:
        chest_name = ' '.join(command[1:]).lower()
        if chest_name in room.get('chests', []):
            open_chest(chest_name, player)
            rooms[current_room]['chests'].remove(chest_name)
        else:
            print("No chest by that name here.")
    elif verb == 'craft' and room.get('crafting_station', False) and len(command) > 1:
        item = ' '.join(command[1:]).lower()
        craft_item(player, item)
    elif verb == 'save':
        save_game(player)
    elif verb == 'help':
        print("Commands: go [direction], take [item], equip [item], learn [spell_scroll], solve, rest, stats, map, open [chest], craft [item], save, help, quit")
    elif verb == 'quit':
        print(f"{player['name']} turns from the dark. The empire waits.")
        save_game(player)
        break
    else:
        print("The shadows ignore your words.")