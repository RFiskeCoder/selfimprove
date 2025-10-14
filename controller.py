import json
import re
import subprocess
import os
import sys
import random
import math
import time

# --- Configuration ---
AI_MODULE_NAME = "ai_core"
PERFORMANCE_LOG_FILE = "performance_log.json"
ITERATIONS_PER_GENERATION = 20
INITIAL_BIAS_WEIGHT = 5.0
TARGET_NUMBER = 42.0
BIAS_WEIGHT_INCREMENT = 0.5
RANDOM_SEARCH_RANGE = (0.0, 20.0)

# --- Self-Modification Configuration ---
CURRENT_STRATEGY = "strategy_simple_increment"

# --- Learning Strategies ---
STRATEGIES = [
    "strategy_simple_increment",
    "strategy_hill_climbing",
    "strategy_random_search"
]

def read_ai_code():
    """Reads the content of the AI core file."""
    with open(f"{AI_MODULE_NAME}.py", "r") as f:
        return f.read()

def write_ai_code(code):
    """Writes the modified code back to the AI core file."""
    with open(f"{AI_MODULE_NAME}.py", "w") as f:
        f.write(code)

def modify_bias_weight(code, new_bias_weight):
    """Modifies the BIAS_WEIGHT in the AI core code."""
    return re.sub(
        r"BIAS_WEIGHT = .*",
        f"BIAS_WEIGHT = {new_bias_weight}",
        code
    )

def log_performance(bias_weight, prediction):
    """Appends a performance record to the log file."""
    log_entry = {
        "bias_weight": bias_weight,
        "prediction": prediction
    }
    try:
        with open(PERFORMANCE_LOG_FILE, "r") as f:
            logs = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logs = []
    logs.append(log_entry)
    with open(PERFORMANCE_LOG_FILE, "w") as f:
        json.dump(logs, f, indent=4)

def run_ai_subprocess():
    """Runs the AI core as a subprocess and returns the prediction."""
    result = subprocess.run(["python3", f"{AI_MODULE_NAME}.py"], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running AI core: {result.stderr}")
        return None
    try:
        return float(result.stdout.strip())
    except (ValueError, TypeError):
        print(f"Error parsing AI output: {result.stdout}")
        return None

# --- Strategy Implementations ---
def strategy_simple_increment():
    print(f"--- Running Generation with Strategy: Simple Increment ---")
    current_bias_weight = INITIAL_BIAS_WEIGHT
    for i in range(ITERATIONS_PER_GENERATION):
        ai_code = read_ai_code()
        modified_code = modify_bias_weight(ai_code, current_bias_weight)
        write_ai_code(modified_code)
        prediction = run_ai_subprocess()
        if prediction is not None:
            log_performance(current_bias_weight, prediction)
        current_bias_weight += BIAS_WEIGHT_INCREMENT

def strategy_hill_climbing():
    print(f"--- Running Generation with Strategy: Hill Climbing ---")
    current_bias_weight = INITIAL_BIAS_WEIGHT
    step_size = BIAS_WEIGHT_INCREMENT
    ai_code = read_ai_code()
    modified_code = modify_bias_weight(ai_code, current_bias_weight)
    write_ai_code(modified_code)
    last_prediction = run_ai_subprocess()
    if last_prediction is None: return
    last_score = abs(last_prediction - TARGET_NUMBER)
    log_performance(current_bias_weight, last_prediction)
    for i in range(1, ITERATIONS_PER_GENERATION):
        next_bias_weight = current_bias_weight + step_size
        modified_code = modify_bias_weight(ai_code, next_bias_weight)
        write_ai_code(modified_code)
        prediction = run_ai_subprocess()
        if prediction is None: continue
        score = abs(prediction - TARGET_NUMBER)
        if score < last_score:
            current_bias_weight = next_bias_weight
            last_score = score
        else:
            step_size *= -1
        log_performance(next_bias_weight, prediction)

def strategy_random_search():
    print(f"--- Running Generation with Strategy: Random Search ---")
    for i in range(ITERATIONS_PER_GENERATION):
        random_bias_weight = random.uniform(RANDOM_SEARCH_RANGE[0], RANDOM_SEARCH_RANGE[1])
        ai_code = read_ai_code()
        modified_code = modify_bias_weight(ai_code, random_bias_weight)
        write_ai_code(modified_code)
        prediction = run_ai_subprocess()
        if prediction is not None:
            log_performance(random_bias_weight, prediction)

# --- Analysis and Self-Modification ---
def analyze_performance(log_start_index=0):
    """
    Analyzes the performance log to find the best prediction from a certain point.
    """
    try:
        with open(PERFORMANCE_LOG_FILE, "r") as f:
            logs = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return float('inf')

    generation_logs = logs[log_start_index:]
    if not generation_logs:
        return float('inf')

    best_score = float('inf')
    for record in generation_logs:
        score = abs(record["prediction"] - TARGET_NUMBER)
        if score < best_score:
            best_score = score
    return best_score

def self_modify_and_restart(best_strategy):
    """Modifies the controller's code to use the best strategy and restarts."""
    print(f"--- Self-Modifying to use '{best_strategy}' for the next cycle ---")

    with open(__file__, "r") as f:
        controller_code = f.read()

    new_code = re.sub(
        r'^CURRENT_STRATEGY = ".*"',
        f'CURRENT_STRATEGY = "{best_strategy}"',
        controller_code,
        count=1,
        flags=re.MULTILINE
    )

    with open(__file__, "w") as f:
        f.write(new_code)

    print("Restarting script to apply changes...")
    os.execv(sys.executable, [sys.executable] + sys.argv)

def main():
    """Main controller loop for self-improvement."""
    while True:
        print(f"--- Starting Self-Improvement Cycle with Strategy: {CURRENT_STRATEGY} ---")

        strategy_map = {
            "strategy_simple_increment": strategy_simple_increment,
            "strategy_hill_climbing": strategy_hill_climbing,
            "strategy_random_search": strategy_random_search,
        }

        best_strategy = None
        best_overall_score = float('inf')

        # Run each strategy and find the best one
        for strategy_name in STRATEGIES:
            try:
                with open(PERFORMANCE_LOG_FILE, "r") as f:
                    log_start_index = len(json.load(f))
            except (FileNotFoundError, json.JSONDecodeError):
                log_start_index = 0

            strategy_func = strategy_map.get(strategy_name)
            if strategy_func:
                strategy_func()
                score = analyze_performance(log_start_index)
                print(f"Strategy '{strategy_name}' finished with best score: {score:.2f}")
                if score < best_overall_score:
                    best_overall_score = score
                    best_strategy = strategy_name

        print(f"\n--- Cycle Complete ---")
        print(f"Best strategy found: {best_strategy} with score {best_overall_score:.2f}")

        if best_strategy and best_strategy != CURRENT_STRATEGY:
            self_modify_and_restart(best_strategy)
        else:
            print("Current strategy is already optimal or no improvement found. Continuing with current strategy.")

        print("Waiting before starting next cycle...")
        time.sleep(10)


if __name__ == "__main__":
    main()
