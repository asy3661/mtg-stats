import random
from parser import parse_file
from pprint import pprint

class Color:
    def __init__(self, color: str):
        # U is for blue
        valid_colors = set('BWGRU')
        if color in ['colorless', 'X']:
            self.color = 'colorless'
        elif set(color).issubset(valid_colors):
            self.color = color
        else:
            raise ValueError

    def __str__(self):
        return self.color

class Cost:
    def __init__(self, *cost: tuple):
        self.cost = cost

    def __str__(self):
        strings = []
        for c, n in self.cost:
            strings.append(f'{n} {c}')
        return ', '.join(strings)

    def get_amount(self, color: Color):
        for c, n in self.cost:
            if c == color:
                return n
        raise ValueError

class CombatAbility:
    def __init__(self, power, toughness):
        self.power = power
        self.base_power = power
        self.power_counter = 0
        self.toughness = toughness
        self.base_toughness = toughness
        self.toughness_counter = 0

    def __str__(self):
        if self.power and self.toughness:
            return f'{self.power}/{self.toughness}'
        else:
            return ''

    def add_counter(self, power, toughness):
        self.power_counter += power
        self.toughness_counter += toughness

    def modify_combat_ability(self, power, toughness):
        self.power += power
        self.toughness += toughness

    def get_effective_combat_ability(self):
        return (self.power + self.power_counter, self.toughness +
                self.toughness_counter)

class Card:
    def __init__(self, 
                 name: str,
                 rules: str,
                 type: str,
                 cost: Cost,
                 # *colors: Color,
                 combat_ability: CombatAbility = None,
                 ):
        self.name = name
        self.rules = rules
        self.type = type
        # self.colors = colors
        self.cost = cost
        self.combat_ability = combat_ability

    def __str__(self):
        string = f'{self.name}\n{str(self.cost)}\n{self.type}\n{str(self.combat_ability)}\n{self.rules}'
        return string

    def __lt__(self, other):
        return self.name < other.name

    def __eq__(self, other):
        return self.name == other.name

class Zone:
    def __init__(self, cards: list = None):
        if not cards:
            self.cards = []
        else:
            self.cards = cards

    def __str__(self):
        return str([card.name for card in self.cards])

    def __iter__(self):
        yield from self.cards

    def __getitem__(self, key):
        return self.cards[key]

    def get_card_by_name(self, name):
        for card in self.cards:
            if card.name == name:
                return card
        raise ValueError

    def shuffle(self):
        random.shuffle(self.cards)

    def sort(self):
        self.cards.sort()

    def add_card(self, card):
        if isinstance(card, Card):
            self.cards.append(card)
        elif isinstance(card, str):
            self.cards.append(self.get_card_by_name(card))
        else:
            raise ValueError

    def add_cards(self, cards):
        for card in cards:
            self.add_card(card)

    def remove_card(self, card):
        if isinstance(card, Card):
            self.cards.remove(card)
        elif isinstance(card, str):
            self.cards.remove(self.get_card_by_name(card))
        else:
            raise ValueError

    def remove_cards(self, cards):
        for card in cards:
            self.remove_card(card)

    def pop_n_cards(self, n):
        cards = []
        for _ in range(n):
            cards.append(self.cards.pop(0))
        return cards

    def pop_card(self, card):
        self.remove_card(card)
        return card

class Deck:
    def __init__(self, deck: list = None):
        if not deck:
            self.deck = Zone()
            self.library = Zone()
        else: 
            self.deck = Zone(deck)
            self.library = Zone(deck.copy())
        self.deck.sort()
        self.library.shuffle()
        self.graveyard = Zone()
        self.hand = Zone()
        self.battlefield = Zone()
        self.exile = Zone()

    def __iter__(self):
        yield from self.deck

    def __getitem__(self, key):
        return self.deck[key]

    def __str__(self):
        return str(self.deck)

    def play(self, card):
        if isinstance(card, str):
            card = self.hand.get_card_by_name(card)
        if card.type in ['Instant', 'Sorcery']:
            self.move_card_to_zone(card, self.hand, self.graveyard)
        else:
            self.move_card_to_zone(card, self.hand, self.battlefield)

    def draw(self, n=1):
        self.move_n_cards_to_zone(n, self.library, self.hand)

    def discard(self, card):
        self.move_card_to_zone(card, self.hand, self.graveyard)

    def mill(self, n=1):
        self.move_n_cards_to_zone(n, self.library, self.graveyard)

    def kill_card(self, card):
        self.move_card_to_zone(card, self.battlefield, self.graveyard)

    def exile_card(self, card, zone_from):
        self.move_card_to_zone(card, zone_from, self.exile)

    def move_card_to_zone(self, card: Card, old_zone: Zone, new_zone: Zone):
        c = old_zone.pop_card(card)
        new_zone.add_card(c)

    def move_n_cards_to_zone(self, n: int, old_zone: Zone, new_zone: Zone):
        c = old_zone.pop_n_cards(n)
        new_zone.add_cards(c)

    def import_deck_from_file(self, path):
        deck_dict = parse_file(path)
        self.import_deck_from_dict(deck_dict)

    def import_deck_from_dict(self, dictionary):
        cards = []
        for v in dictionary.values():
            name = v['name']
            rules = v['rules']
            type = v['type']
            combat_ability = self._get_combat_ability(v)
            cost = self._get_cost(v)
            number = v['number']
            card = Card(name, rules, type, cost, combat_ability)
            for _ in range(number):
                cards.append(card)
        self.__init__(cards)

    def _get_combat_ability(self, v: dict):
        combat_ability = CombatAbility(v['power'], v['toughness'])
        return combat_ability

    def _get_cost(self, v: dict):
        costs = []
        for color, cost in v['cost'].items():
            costs.append((Color(color), cost))
        return Cost(*costs)

