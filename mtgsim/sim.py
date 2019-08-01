from __future__ import annotations

import typing as t

from abc import ABC, abstractmethod
import random

import numpy as np

from yeetlong.multiset import Multiset, FrozenMultiset


class Card(ABC):

    @classmethod
    @abstractmethod
    def on_play(cls, game: Game) -> bool:
        pass

    @classmethod
    @abstractmethod
    def each_turn(cls, game: Game) -> None:
        pass


class Deck(object):

    def __init__(self, cards: t.Iterable[t.Type[Card]]):
        self._cards = cards if isinstance(cards, FrozenMultiset) else FrozenMultiset(cards)

    @property
    def cards(self) -> FrozenMultiset[t.Type[Card]]:
        return self._cards


class Library(object):

    def __init__(self, deck: Deck):
        self._deck = deck
        self._library = random.sample(self._deck.cards, len(self._deck.cards))

    def draw(self) -> t.Optional[t.Type[Card]]:
        try:
            return self._library.pop()
        except IndexError:
            return None

    def shuffle(self) -> Library:
        self._library = random.shuffle(self._library)
        return self


class Player(object):

    def __init__(self, library: Library, strategy: t.Type[Strategy]):
        self._library = library
        self._strategy = strategy
        self.lands = 0

        self._hand = Multiset() #type: Multiset[t.Type[Card]]

    @property
    def hand(self) -> Multiset[t.Type[Card]]:
        return self._hand

    def turn(self, game: Game) -> Player:
        self._strategy.turn(game)
        return self

    def draw(self) -> Player:
        card = self._library.draw()
        if card:
            self._hand.add(card)
        return self

    def draw_hand(self) -> Player:
        for _ in range(7):
            self.draw()
        return self


class Game(object):

    def __init__(self, player: Player, on_the_play: bool = False):
        self._player = player
        self._damage_dealt = 0

        self._on_the_play = on_the_play
        self._turns = 0

        self._battlefield = Multiset() #type: Multiset[t.Type[Card]]

    @property
    def player(self) -> Player:
        return self._player

    @property
    def battlefield(self) -> Multiset[t.Type[Card]]:
        return self._battlefield

    @property
    def damage_dealt(self) -> int:
        return self._damage_dealt

    def deal_damage(self, amount: int) -> None:
        self._damage_dealt += amount

    def take_turn(self) -> Game:
        self._turns += 1

        if not ( self._on_the_play and self._turns == 0):
            self._player.draw()

        # print('turn', self._turns, {card.__name__: multiplicity for card, multiplicity in self._player.hand.items()})


        for card in self._battlefield:
            card.each_turn(self)

        self._player.turn(self)

        # print('damage dealt: ', self._damage_dealt)

        return self

    def goldfish(self) -> int:
        self._player.draw_hand()
        while self._damage_dealt < 20:
            self.take_turn()

        return self._turns


class Strategy(ABC):

    @classmethod
    @abstractmethod
    def turn(cls, game: Game):
        pass

    @classmethod
    def play_card(cls, card: t.Type[Card], game: Game) -> None:
        # print('play', card.__name__)
        game.player.hand.remove(card, 1)
        if card.on_play(game):
            game.battlefield.add(card)


class Session(object):

    def __init__(self, deck: Deck, strategy: t.Type[Strategy]):
        self._deck = deck
        self._strategy = strategy
        self._results = [] #type: t.List[int]

    def game(self) -> int:
        # print('new game')
        return Game(
            player = Player(
                library = Library(
                    self._deck
                ),
                strategy = self._strategy,
            )
        ).goldfish()

    def simulate(self, takes: int = 100) -> Session:
        self._results = [
            self.game()
            for _ in
            range(takes)
        ]
        return self

    def mean(self) -> float:
        return np.mean(self._results)