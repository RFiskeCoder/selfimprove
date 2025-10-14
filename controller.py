import json
import re
import subprocess

# --- Configuration ---
AI_MODULE_NAME = "ai_core"
PERFORMANCE_LOG_FILE = "performance_log.json"
ITERATIONS = 10
INITIAL_BIAS_WEIGHT = 5.0
BIAS_WEIGHT_INCREMENT = 0.5

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
    """Logs the performance of the AI."""
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

def main():
    """Main controller loop."""
    current_bias_weight = INITIAL_BIAS_WEIGHT

    for i in range(ITERATIONS):
        print(f"--- Iteration {i+1}/{ITERATIONS} ---")

        # 1. Read the AI code
        ai_code = read_ai_code()

        # 2. Modify the BIAS_WEIGHT
        modified_code = modify_bias_weight(ai_code, current_bias_weight)

        # 3. Write the modified code back
        write_ai_code(modified_code)

        # 4. Run the AI as a subprocess and capture the output
        result = subprocess.run(
            ["python3", f"{AI_MODULE_NAME}.py"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"Error running AI core: {result.stderr}")
            continue

        prediction = float(result.stdout.strip())
        print(f"BIAS_WEIGHT: {current_bias_weight}, Prediction: {prediction}")

        # 5. Log the performance
        log_performance(current_bias_weight, prediction)

        # 6. Update the bias weight for the next iteration
        current_bias_weight += BIAS_WEIGHT_INCREMENT

    print("Self-improvement cycle complete.")

if __name__ == "__main__":
    main()
