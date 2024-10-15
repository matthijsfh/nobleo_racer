#!/usr/bin/env python3
from argparse import ArgumentParser, Namespace

import optuna

# import racer.bots.rein.lib as rein

import racer.bots.matthijsfh.bot as matthijs

from racer.constants import framerate
from racer.game_state import GameState
from racer.track import Track
from racer.tracks import track1, track2


def main():
    study = optuna.create_study(
        storage="sqlite:///db.sqlite3",  # Specify the storage URL here.
        study_name="caravan racer",
        load_if_exists=True,
    )
    study.optimize(objective, n_trials=1000, n_jobs=1)

    print(study.best_params)


def objective(trial):
    # config = Namespace(
    #     curvature_clustering_distance=trial.suggest_float(
    #         "curvature_clustering_distance", 100, 500
    #     ),
    #     curvature_velocity_scaling=trial.suggest_float(
    #         "curvature_velocity_scaling", 1, 5
    #     ),
    #     max_velocity=trial.suggest_float("max_velocity", 100, 500),
    #     distance_offset=trial.suggest_float("distance_offset", 0, 100),
    #     acceleration=trial.suggest_float("acceleration", 50, 150),
    # )

    config = Namespace(
        QuadraticGainA=trial.suggest_float("QuadraticGainA", 0.1, 2),
        LinearGainB=trial.suggest_float("LinearGainB", 5, 20),
        fullSpeed=trial.suggest_float("fullSpeed", 500, 550),
    )

    return single_game(config, Track(track1)) + single_game(
        config, Track(track2)
    )


def single_game(config, track: Track):
    rounds = 3
    min_frames = 12000

    game_state = GameState(track)

    # rein.CURVATURE_CLUSTERING_DISTANCE = config.curvature_clustering_distance
    # rein.CURVATURE_VELOCITY_SCALING = config.curvature_velocity_scaling
    # rein.MAX_VELOCITY = config.max_velocity
    # rein.DISTANCE_OFFSET = config.distance_offset
    # rein.ACCELERATION = config.acceleration

    matthijs.Kwadratic = config.QuadraticGainA
    matthijs.Linear = config.LinearGainB
    matthijs.fullSpeed = config.fullSpeed

    finishing = False
    for _ in range(0, min_frames):
        game_state.update(1 / framerate)

        for bot, car_info in game_state.bots.items():
            if car_info.round >= rounds:
                finishing = True
                break
        if finishing:
            break

    finish_index = rounds * len(game_state.track.lines) - 1
    for bot, car_info in game_state.bots.items():
        if finish_index < len(car_info.waypoint_timing):
            finish_time = car_info.waypoint_timing[finish_index]
            print(f"{bot.name} finished in {finish_time:.2f} seconds")
            return finish_time
        else:
            print(f"{bot.name} did not finish")
            return float("inf")

    return float("nan")


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Run a tournament of the coding challenge racer"
    )
    args = parser.parse_args()

    try:
        main(**vars(args))
    except KeyboardInterrupt:
        pass
