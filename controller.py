import json
import random
import re
import os
import sys
import time
from chatbot_core import ChatbotCore
from Levenshtein import distance as levenshtein_distance

# --- Configuration ---
RULES_FILE = "rules.json"
EVALUATION_DATASET_FILE = "evaluation_dataset.json"
MUTATION_POOL_SIZE = 10
MUTATION_RATE = 0.2
EVOLUTION_LOOP_DELAY_SECONDS = 30 # Wait 30 seconds between cycles

# --- Genetic Programming Engine for Language ---

def mutate_rules(rules: list) -> list:
    """Applies random mutations to a copy of the rule set."""
    mutated_rules = [dict(rule) for rule in rules]

    for rule in mutated_rules:
        if random.random() < MUTATION_RATE:
            mutation_type = random.choice(["add_pattern", "mutate_response"])
            if mutation_type == "add_pattern" and rule.get('patterns'):
                pattern_to_modify = random.choice(rule['patterns'])
                words = pattern_to_modify.split()
                if len(words) > 1:
                    random.shuffle(words)
                    new_pattern = " ".join(words)
                    if new_pattern not in rule['patterns']:
                        rule['patterns'].append(new_pattern)
            elif mutation_type == "mutate_response" and rule.get('responses'):
                response_index = random.randint(0, len(rule['responses']) - 1)
                words = rule['responses'][response_index].split()
                if words:
                    word_to_replace = random.choice(words)
                    rule['responses'][response_index] = rule['responses'][response_index].replace(
                        word_to_replace, word_to_replace[::-1], 1
                    )
    return mutated_rules

def evaluate_fitness(rules: list, dataset: list) -> float:
    """Evaluates the fitness of a rule set."""
    temp_bot = ChatbotCore()
    temp_bot.rules = rules
    temp_bot.default_responses = temp_bot._get_default_responses()

    total_distance = 0
    for item in dataset:
        user_input = item['input']
        ideal_response = item['ideal_response']
        bot_response = temp_bot.get_response(user_input)
        distance = levenshtein_distance(bot_response.lower(), ideal_response.lower())
        total_distance += distance

    return total_distance / len(dataset) if dataset else float('inf')


def self_modify_rules(new_rules: list):
    """Overwrites the main rules.json with the new, superior rule set."""
    print("--- Self-Modifying: Adopting superior rule set ---")
    with open(RULES_FILE, 'w') as f:
        json.dump({"rules": new_rules}, f, indent=2)


def main():
    """Main evolutionary loop for the chatbot."""
    print("--- Starting Chatbot Evolutionary Controller ---")

    with open(EVALUATION_DATASET_FILE, 'r') as f:
        dataset = json.load(f)

    while True:
        print("\n--- Starting New Evolutionary Cycle ---")

        try:
            with open(RULES_FILE, 'r') as f:
                current_rules = json.load(f).get('rules', [])
        except (FileNotFoundError, json.JSONDecodeError):
            print("Could not load rules.json. Starting with an empty rule set.")
            current_rules = []

        current_fitness = evaluate_fitness(current_rules, dataset)
        print(f"Current Fitness (Avg. Levenshtein Distance): {current_fitness:.4f}")

        print(f"Generating and evaluating {MUTATION_POOL_SIZE} mutants...")
        best_mutant = None
        best_mutant_fitness = float('inf')

        for i in range(MUTATION_POOL_SIZE):
            mutant_rules = mutate_rules(current_rules)
            mutant_fitness = evaluate_fitness(mutant_rules, dataset)
            print(f"Mutant {i+1} fitness: {mutant_fitness:.4f}")
            if mutant_fitness < best_mutant_fitness:
                best_mutant_fitness = mutant_fitness
                best_mutant = mutant_rules

        print(f"\n--- Cycle Complete ---")
        print(f"Best mutant fitness: {best_mutant_fitness:.4f}")

        if best_mutant_fitness < current_fitness:
            print(f"Improvement found! Adopting new rule set.")
            self_modify_rules(best_mutant)
        else:
            print("No improvement found in this generation.")

        print(f"Waiting for {EVOLUTION_LOOP_DELAY_SECONDS} seconds before next cycle...")
        time.sleep(EVOLUTION_LOOP_DELAY_SECONDS)


if __name__ == "__main__":
    main()
