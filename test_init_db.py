from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import models
from database import Base
from init_db import seed_sample_rosters


def test_seed_sample_rosters_is_idempotent_and_preserves_existing_assignments():
    test_engine = create_engine("sqlite://")
    Base.metadata.create_all(bind=test_engine)

    with Session(test_engine) as db:
        players = [
            models.Player(
                player_id=1001 + index,
                gsis_id=None,
                first_name=f"Player{index}",
                last_name="Sample",
                position="WR",
                last_changed_date=date(2024, 9, 1),
            )
            for index in range(20)
        ]
        league_ids = (5001, 5003, 5004, 5005)
        leagues = [
            models.League(
                league_id=league_id,
                league_name=f"League {league_id}",
                scoring_type="PPR",
                league_size=2,
                last_changed_date=date(2024, 9, 1),
            )
            for league_id in league_ids
        ]
        teams = [
            models.Team(
                team_id=league_id * 10 + team_number,
                team_name=f"Team {league_id}-{team_number}",
                league_id=league_id,
                last_changed_date=date(2024, 9, 1),
            )
            for league_id in league_ids
            for team_number in (1, 2)
        ]
        db.add_all([*players, *leagues, *teams])
        db.commit()
        db.add(
            models.TeamPlayer(
                team_id=50031,
                player_id=1001,
                last_changed_date=date(2024, 9, 1),
            )
        )
        db.add(
            models.TeamPlayer(
                team_id=50011,
                player_id=1002,
                last_changed_date=date(2024, 9, 1),
            )
        )
        db.commit()

    assert seed_sample_rosters(test_engine) == 35
    assert seed_sample_rosters(test_engine) == 0

    with Session(test_engine) as db:
        for league_id in (5003, 5004, 5005):
            league_teams = (
                db.query(models.Team)
                .filter(models.Team.league_id == league_id)
                .order_by(models.Team.team_id)
                .all()
            )
            assert [len(team.players) for team in league_teams] == [1, 7] if league_id == 5003 else [7, 7]
            assigned_player_ids = [
                player.player_id
                for team in league_teams
                for player in team.players
            ]
            assert len(assigned_player_ids) == len(set(assigned_player_ids))

        legacy_team = db.query(models.Team).filter(models.Team.team_id == 50011).one()
        assert [player.player_id for player in legacy_team.players] == [1002]
