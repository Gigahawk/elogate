from datetime import datetime
from collections import defaultdict

from tortoise.expressions import Q

from elogate.models import Game, Player, PlayerRank, Match


def teams_list_to_player_ids(teams: list[list[Player]]) -> list[list[int]]:
    return [[p.id for p in t] for t in teams]


async def player_ids_list_to_teams(player_ids: list[list[int]]) -> list[list[Player]]:
    out = []
    for t in player_ids:
        team_out = []
        for id in t:
            player = await Player.filter(id=id).first()
            if not player:
                # TODO: specific error
                raise ValueError(f"Could not find player with id {id}")
            team_out.append(player)
        out.append(team_out)
    return out


async def create_match(game: Game, teams: list[list[Player]], timestamp: datetime):
    match = Match(
        timestamp=timestamp, game=game, participants=teams_list_to_player_ids(teams)
    )
    await match.save()

    await update_rankings(match)


# async def get_next_match(match: Match) -> Match | None:
#    out = (
#        await Match.filter(game=match.game, timestamp__gt=match.timestamp)
#        .order_by("timestamp")
#        .first()
#    )
#    return out


async def _update_rankings_one_game(game: Game, root_timestamp: datetime):
    matches = await game.all_matches.filter(timestamp__gte=root_timestamp)

    for match in matches:
        teams = await player_ids_list_to_teams(match.participants)
        model = game.ranking_model.value(**game.ranking_model_args)

        ranked_teams = []
        rank_idxs = {}
        player_map = {}
        for rank_idx, t in enumerate(teams):
            team = []
            for player in t:
                rank_idxs[player.name] = rank_idx
                player_map[player.name] = player
                last_rank = (
                    await PlayerRank.filter(
                        # Filter for matches of the same game
                        game=game,
                        # Filter for matches older than current timestamp
                        match__timestamp__lt=match.timestamp,
                        player=player,
                    )
                    .order_by("-match__timestamp")
                    .first()
                )
                if last_rank is None:
                    player_rank = model.rating(name=player.name)
                else:
                    mu = last_rank.mu
                    sigma = last_rank.sigma
                    player_rank = model.rating(name=player.name, mu=mu, sigma=sigma)
                team.append(player_rank)
            ranked_teams.append(team)
        ranked_teams = model.rate(ranked_teams)
        for t in ranked_teams:
            for player in t:
                db_player = player_map[player.name]
                update_items = {
                    "rank_idx": rank_idxs[player.name],
                    "mu": player.mu,
                    "sigma": player.sigma,
                }
                # Check if rank has already been created
                rank = await match.ranks.filter(game=game, player=db_player).first()
                if not rank:
                    rank = PlayerRank(
                        match=match,
                        game=game,
                        player=db_player,
                    )
                rank.update_from_dict(update_items)
                await rank.save()


async def update_rankings(root_match: Match):
    root_timestamp = root_match.timestamp
    game = root_match.game
    while True:
        await _update_rankings_one_game(game, root_timestamp)

        # Technically we only support one layer of recursion but whatever
        if game.parent:
            game = game.parent
        else:
            break


async def update_all_rankings():
    root_timestamp = datetime.fromtimestamp(0)
    for game in await Game.all():
        await _update_rankings_one_game(game, root_timestamp)
