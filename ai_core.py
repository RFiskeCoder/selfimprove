# AI Configuration - THIS LINE WILL BE MODIFIED BY CONTROLLER
BIAS_WEIGHT = 3.716386724049443

# --- Core AI Logic ---

# The AI's "Brain" - A rewritable formula
# I'm making this formula intentionally suboptimal for testing purposes.
FORMULA = "(sum(input_sequence) * 0.35787093568987915) + (BIAS_WEIGHT * len(input_sequence))"

def predict_sequence(input_sequence):
    """
    The AI's task: Predict the output for a sequence based on a rewritable,
    evolving formula.
    """
    # Using eval() to execute the formula string makes the AI's logic dynamic.
    # Note: In a production environment, eval() can be a security risk if the
    # formula string is not carefully controlled. For this self-contained
    # evolution project, it is a powerful tool.
    try:
        prediction = eval(FORMULA, {
            "input_sequence": input_sequence,
            "BIAS_WEIGHT": BIAS_WEIGHT,
            "sum": sum,
            "len": len
        })
        return prediction
    except Exception as e:
        # If the formula is invalid, return a high-error value
        print(f"Error evaluating formula: {e}")
        return float('inf')


def get_config():
    """Retrieves the current BIAS_WEIGHT without re-reading the file."""
    return BIAS_WEIGHT


if __name__ == "__main__":
    # This block allows the controller to test the AI via subprocess
    import json
    # In a real run, the input would come from a dataset.
    # For direct execution, we can use a sample or read from stdin.
    try:
        input_str = input()
        input_sequence = json.loads(input_str)
        prediction = predict_sequence(input_sequence)
        print(prediction)
    except:
        # Fallback for simple testing
        input_sequence = [1, 2, 3, 4, 5]
        prediction = predict_sequence(input_sequence)
        print(prediction)
