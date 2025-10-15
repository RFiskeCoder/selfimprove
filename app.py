from flask import Flask, render_template, request, session
from chatbot_core import ChatbotCore
import os

app = Flask(__name__)
# A secret key is required for session management
app.secret_key = os.urandom(24)

# Initialize our chatbot
chatbot = ChatbotCore()

@app.route("/")
def home():
    # Ensure a conversation history exists in the session
    if 'conversation' not in session:
        session['conversation'] = []
    return render_template("index.html", conversation=session['conversation'])

@app.route("/ask", methods=['POST'])
def ask():
    user_message = request.form.get('message')
    if user_message:
        # Get response from the chatbot core
        bot_response = chatbot.get_response(user_message)

        # Add the exchange to our session history
        session['conversation'].append({'user': user_message, 'bot': bot_response})
        # Flask sessions need to be manually marked as modified when changing mutable types
        session.modified = True

    return home()

@app.route("/reset")
def reset():
    # Allow the user to clear their conversation history
    session.clear()
    return home()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
