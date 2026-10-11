"""Initialize missing SQLAlchemy tables and sample rosters before serving the API."""

from datetime import date

import models  # noqa: F401 - register model tables with SQLAlchemy metadata
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from database import Base, engine


SAMPLE_ROSTER_LEAGUE_IDS = (5003, 5004, 5005)
SAMPLE_ROSTER_SIZE = 7


def create_database_tables(database_engine: Engine = engine) -> None:
    """Create model tables that are missing from the configured database."""
    Base.metadata.create_all(bind=database_engine)


def seed_sample_rosters(database_engine: Engine = engine) -> int:
    """Assign deterministic sample players to unrostered teams in leagues 5003-5005."""
    with Session(database_engine) as db:
        leagues = (
            db.query(models.League)
            .filter(models.League.league_id.in_(SAMPLE_ROSTER_LEAGUE_IDS))
            .order_by(models.League.league_id)
            .all()
        )
        if not leagues:
            return 0

        players = db.query(models.Player).order_by(models.Player.player_id).all()
        teams_by_league = {
            league.league_id: sorted(league.teams, key=lambda team: team.team_id)
            for league in leagues
        }
        if not any(
            not team.players
            for teams in teams_by_league.values()
            for team in teams
        ):
            return 0
        if len(players) < SAMPLE_ROSTER_SIZE:
            raise RuntimeError(
                f"Cannot seed sample rosters: found {len(players)} players; "
                f"at least {SAMPLE_ROSTER_SIZE} are required."
            )

        added_count = 0
        for league_id, teams in teams_by_league.items():
            used_player_ids = {
                player.player_id for team in teams for player in team.players
            }
            player_index = ((league_id - SAMPLE_ROSTER_LEAGUE_IDS[0]) * 100) % len(players)

            for team in teams:
                if team.players:
                    continue
                if len(players) - len(used_player_ids) < SAMPLE_ROSTER_SIZE:
                    raise RuntimeError(
                        f"Cannot seed league {league_id}: not enough unassigned "
                        "players for a complete sample roster."
                    )

                roster = []
                while len(roster) < SAMPLE_ROSTER_SIZE:
                    player = players[player_index]
                    player_index = (player_index + 1) % len(players)
                    if player.player_id not in used_player_ids:
                        roster.append(player)
                        used_player_ids.add(player.player_id)

                db.add_all(
                    models.TeamPlayer(
                        team_id=team.team_id,
                        player_id=player.player_id,
                        last_changed_date=date.today(),
                    )
                    for player in roster
                )
                added_count += len(roster)

        db.commit()
        return added_count


if __name__ == "__main__":
    create_database_tables()
    seed_sample_rosters()
