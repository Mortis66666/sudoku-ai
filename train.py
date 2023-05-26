import os
import sys
import random

from stable_baselines3.common.logger import TensorBoardOutputFormat
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import SubprocVecEnv
from stable_baselines3.common.callbacks import CheckpointCallback, BaseCallback


from sb3_contrib import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker

from sudoku_env import SudokuEnv

NUM_ENV = 1
LOG_DIR = "logs"


class LogCallback(BaseCallback):
    def __init__(self, env, verbose=0):
        super(LogCallback, self).__init__(verbose)
        self.env = env

    def _on_training_start(self):
        output_formats = self.logger.output_formats
        # Save reference to tensorboard formatter object
        # note: the failure case (not formatter found) is not handled here, should be done with try/except.
        self.tb_formatter = next(formatter for formatter in output_formats if isinstance(formatter, TensorBoardOutputFormat))
    
    def _on_rollout_end(self) -> bool:
        # env = self.training_env

        # self.tb_formatter.writer.add_scalar("episode_reward", env.reward)
        # self.tb_formatter.writer.add_scalar("episode_length", env.steps)

        self.logger.record('reward', self.env.reward)
        self.logger.record('steps', self.env.steps)
 
        return True
    
    def _on_step(self) -> bool:
        return super()._on_step()


def linear_schedule(initial_value, final_value=0.0):

    if isinstance(initial_value, str):
        initial_value = float(initial_value)
        final_value = float(final_value)
        assert (initial_value > 0.0)

    def scheduler(progress):
        return final_value + progress * (initial_value - final_value)

    return scheduler

def make_env(seed=0):
    def _init():
        env = SudokuEnv(seed=seed)
        env = ActionMasker(env, SudokuEnv.get_action_mask)
        env = Monitor(env)
        # env.seed(seed)
        return env
    return _init

def main():
    seed_set = set()
    while len(seed_set) < NUM_ENV:
        seed_set.add(random.randint(0, 1e9))

    # env = SubprocVecEnv([make_env(seed=s) for s in seed_set])
    env = make_env(random.randint(0, 1e9))()

    lr_schedule = linear_schedule(2.5e-4, 2.5e-6)
    clip_range_schedule = linear_schedule(0.150, 0.025)

    model = MaskablePPO(
        "MlpPolicy",
        env,
        device="cpu",
        verbose=1,
        n_steps=2048,
        batch_size=512,
        n_epochs=4,
        gamma=0.94,
        learning_rate=lr_schedule,
        clip_range=clip_range_schedule,
        tensorboard_log=LOG_DIR
    )

    # Set the save directory
    save_dir = "model"
    os.makedirs(save_dir, exist_ok=True)

    log_callback = LogCallback(env)

    checkpoint_interval = 15625 # checkpoint_interval * num_envs = total_steps_per_checkpoint
    checkpoint_callback = CheckpointCallback(save_freq=checkpoint_interval, save_path=save_dir, name_prefix="ppo_sudoku")

    # Writing the training logs from stdout to a file
    original_stdout = sys.stdout
    log_file_path = os.path.join(save_dir, "training_log.txt")
    with open(log_file_path, 'w') as log_file:
        sys.stdout = log_file

        model.learn(
            total_timesteps=int(100000000),
            callback=[checkpoint_callback, log_callback]
        )
        env.close()

    # Restore stdout
    sys.stdout = original_stdout

    # Save the final model
    model.save(os.path.join(save_dir, "ppo_sudoku_final.zip"))

if __name__ == "__main__":
    main()
