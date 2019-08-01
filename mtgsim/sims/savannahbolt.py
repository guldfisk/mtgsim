from mtgsim import sim
from mtgsim.sim import Game


class Savannah(sim.Card):

    @classmethod
    def on_play(cls, game: Game) -> bool:
        game.player.lands += 1
        return False

    @classmethod
    def each_turn(cls, game: Game) -> None:
        pass


class SavannahLion(sim.Card):

    @classmethod
    def on_play(cls, game: Game) -> bool:
        return True

    @classmethod
    def each_turn(cls, game: Game) -> None:
        game.deal_damage(2)


class LightningBolt(sim.Card):

    @classmethod
    def on_play(cls, game: Game) -> bool:
        game.deal_damage(3)
        return True

    @classmethod
    def each_turn(cls, game: Game) -> None:
        pass


class SavannahStrategy(sim.Strategy):

    @classmethod
    def turn(cls, game: Game):
        if Savannah in game.player.hand:
            cls.play_card(Savannah, game)

        expected_mana = (
            game.player.lands + 1
            if Savannah in game.player.hand else
            game.player.lands
        )

        bolts = game.player.hand.get(LightningBolt, 0)

        if (
            min(
                game.player.lands + expected_mana,
                bolts,
            ) * 3
            + len(game.battlefield) * 4
            + game.damage_dealt
        ) >= 20:
            for _ in range(
                min(
                    bolts,
                    game.player.lands,
                )
            ):
                cls.play_card(LightningBolt, game)

        else:
            lions = game.player.hand.get(SavannahLion, 0)
            for _ in range(
                min(
                    lions,
                    game.player.lands,
                )
            ):
                cls.play_card(SavannahLion, game)

            for _ in range(
                max(
                    min(
                        bolts,
                        game.player.lands - lions
                    ),
                    0,
                )
            ):
                cls.play_card(LightningBolt, game)
