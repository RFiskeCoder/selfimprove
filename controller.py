import json
import re
import subprocess
import os
import sys
import random
import time
import tempfile

# --- Configuration ---
AI_CORE_FILE = "ai_core.py"
TEST_DATASET_FILE = "test_dataset.json"
MUTATION_POOL_SIZE = 10
MUTATION_CHANCE_NUMBER = 0.8
NUMBER_MUTATION_FACTOR = 0.2

# --- Genetic Programming Engine ---

def mutate_formula(formula: str) -> str:
    """Applies a random mutation to the formula string."""
    if random.random() < MUTATION_CHANCE_NUMBER:
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", formula)
        if not numbers: return formula
        number_to_mutate = random.choice(numbers)
        original_value = float(number_to_mutate)
        mutation = original_value * random.uniform(-NUMBER_MUTATION_FACTOR, NUMBER_MUTATION_FACTOR)
        new_value = original_value + mutation
        return formula.replace(number_to_mutate, str(new_value), 1)
    else:
        operators = ["+", "-", "*"]
        found_operators = [op for op in operators if op in formula]
        if not found_operators: return formula
        operator_to_mutate = random.choice(found_operators)
        new_operator = random.choice([op for op in operators if op != operator_to_mutate])
        return formula.replace(operator_to_mutate, new_operator, 1)

def get_current_formula() -> str:
    """Reads the FORMULA string from ai_core.py."""
    with open(AI_CORE_FILE, "r") as f:
        code = f.read()
    match = re.search(r'FORMULA = "(.*)"', code)
    if match:
        return match.group(1)
    raise ValueError("Could not find FORMULA in ai_core.py")

def evaluate_fitness(formula: str, dataset: list) -> float:
    """Evaluates the fitness of a formula by testing it against the dataset."""
    total_error = 0

    # Create a temporary, modified AI core to test the mutant formula
    with open(AI_CORE_FILE, "r") as f:
        original_code = f.read()

    modified_code = re.sub(r'FORMULA = ".*"', f'FORMULA = "{formula}"', original_code)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as temp_f:
        temp_f.write(modified_code)
        temp_ai_core_path = temp_f.name

    for item in dataset:
        input_sequence = item["input"]
        target_output = item["output"]

        process = subprocess.Popen(
            ["python3", temp_ai_core_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=json.dumps(input_sequence))

        if stderr:
            # This formula is invalid and results in a high error
            total_error += 1000 # Penalize errors heavily
            continue

        try:
            prediction = float(stdout.strip())
            error = abs(prediction - target_output)
            total_error += error
        except (ValueError, TypeError):
            total_error += 1000 # Penalize parsing errors

    os.remove(temp_ai_core_path)

    return total_error / len(dataset) if dataset else float('inf')


def self_modify_and_restart(new_formula: str):
    """Rewrites the FORMULA in ai_core.py and restarts the controller."""
    print(f"--- Self-Modifying to adopt new formula: {new_formula} ---")

    with open(AI_CORE_FILE, "r") as f:
        ai_code = f.read()

    # Escape any quotes in the formula to prevent syntax errors
    safe_formula = new_formula.replace('"', '\\"')

    new_ai_code = re.sub(
        r'FORMULA = ".*"',
        f'FORMULA = "{safe_formula}"',
        ai_code,
        count=1
    )

    with open(AI_CORE_FILE, "w") as f:
        f.write(new_ai_code)

    print("Restarting controller to apply evolved AI...")
    os.execv(sys.executable, [sys.executable] + sys.argv)

def main():
    """Main evolutionary loop."""
    print("--- Starting Evolutionary Cycle ---")

    with open(TEST_DATASET_FILE, "r") as f:
        dataset = json.load(f)

    current_formula = get_current_formula()
    print(f"Current Formula: {current_formula}")

    current_fitness = evaluate_fitness(current_formula, dataset)
    print(f"Current Fitness (Average Error): {current_fitness:.4f}")

    print(f"\n--- Generating and Evaluating {MUTATION_POOL_SIZE} Mutants ---")
    best_mutant = None
    best_mutant_fitness = float('inf')

    for i in range(MUTATION_POOL_SIZE):
        mutant_formula = mutate_formula(current_formula)
        mutant_fitness = evaluate_fitness(mutant_formula, dataset)
        print(f"Mutant {i+1} | Formula: {mutant_formula} | Fitness: {mutant_fitness:.4f}")

        if mutant_fitness < best_mutant_fitness:
            best_mutant_fitness = mutant_fitness
            best_mutant = mutant_formula

    print(f"\n--- Cycle Complete ---")
    print(f"Best Mutant found: {best_mutant} (Fitness: {best_mutant_fitness:.4f})")

    if best_mutant_fitness < current_fitness:
        self_modify_and_restart(best_mutant)
    else:
        print("No improvement found in this generation. Continuing with current formula.")


if __name__ == "__main__":
    main()
