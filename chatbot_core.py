import json
import random
import re

RULES_FILE = 'rules.json'

class ChatbotCore:
    def __init__(self, rules_file=RULES_FILE):
        self.rules = self._load_rules(rules_file)
        self.default_responses = self._get_default_responses()

    def _load_rules(self, rules_file):
        try:
            with open(rules_file, 'r') as f:
                return json.load(f).get('rules', [])
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _get_default_responses(self):
        for rule in self.rules:
            if 'default' in rule.get('patterns', []):
                return rule.get('responses', [])
        return ["I'm not sure how to respond to that."]

    def get_response(self, user_input):
        """
        Finds the best response to a user's input based on the loaded rules.
        """
        user_input_lower = user_input.lower()

        for rule in self.rules:
            for pattern in rule.get('patterns', []):
                # Use regex to match whole words to avoid partial matches
                if re.search(r'\b' + re.escape(pattern) + r'\b', user_input_lower):
                    return random.choice(rule.get('responses', []))

        # If no specific rule is found, return a default response
        return random.choice(self.default_responses)

if __name__ == '__main__':
    # A simple example of how to use the chatbot core
    chatbot = ChatbotCore()

    print("Chatbot is ready. Type 'quit' to exit.")
    while True:
        user_message = input("You: ")
        if user_message.lower() == 'quit':
            break
        response = chatbot.get_response(user_message)
        print(f"Bot: {response}")
