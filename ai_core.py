# AI Configuration - THIS LINE WILL BE MODIFIED BY CONTROLLER
BIAS_WEIGHT = 3.716386724049443

# --- Core AI Logic ---

def predict_sequence(input_sequence):
    """
    The AI's task: Predict the sum of a list based on a simple,
    hidden rule that is skewed by BIAS_WEIGHT.
    
    Rule: (Sum of sequence * 0.1) + BIAS_WEIGHT * (Length of sequence)
    The goal is to find the BIAS_WEIGHT that yields a result closest to 
    the 'True' answer (which is hidden from the AI).
    """
    total_sum = sum(input_sequence)
    length = len(input_sequence)
    
    # This formula defines the AI's current 'intelligence'
    prediction = (total_sum * 0.1) + (BIAS_WEIGHT * length)
    return prediction

def get_config():
    """Retrieves the current BIAS_WEIGHT without re-reading the file."""
    # Note: We must return BIAS_WEIGHT defined globally in this module
    return BIAS_WEIGHT

# A simple print statement to confirm the AI loaded the new config
# print(f"[079] AI Core loaded with BIAS_WEIGHT: {BIAS_WEIGHT}")

# End of file - do not delete this line

if __name__ == "__main__":
    # This block will only run when the script is executed directly
    # It allows the controller to get the prediction from the subprocess
    input_sequence = [1, 2, 3, 4, 5]
    prediction = predict_sequence(input_sequence)
    print(prediction)
