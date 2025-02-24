from flask import Flask, request, jsonify
import sqlite3
import openai

app = Flask(__name__)

openai.api_key = ""  # Replace with your actual OpenAI API key

# Initialize database
def init_db():
    conn = sqlite3.connect("chatbot.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS interactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        query TEXT UNIQUE,
                        response TEXT
                      )''')
    conn.commit()
    conn.close()

init_db()

# Function to get chatbot response (now includes AI logic)
def get_response(query):
    conn = sqlite3.connect("chatbot.db")
    cursor = conn.cursor()
    
    # Check if query exists in database
    cursor.execute("SELECT response FROM interactions WHERE query = ?", (query,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]  # Return stored response
    else:
        return get_ai_response(query)  # Get response from AI if not found

# Function to generate AI-based response when no match in DB
def get_ai_response(query):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": query}]
        )
        ai_response = response["choices"][0]["message"]["content"]

        # Store AI-generated response in the database for future use
        conn = sqlite3.connect("chatbot.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO interactions (query, response) VALUES (?, ?)", (query, ai_response))
        conn.commit()
        conn.close()

        return ai_response
    except Exception as e:
        return "I'm still learning! Please try again later."

# Homepage Route to Fix 404 Error
@app.route("/")
def home():
    return "Chatbot API is running!"

# Store new user queries and responses
@app.route("/train-chatbot", methods=["POST"])
def train_chatbot():
    data = request.json
    query = data.get("query")
    response = data.get("response")

    if query and response:
        conn = sqlite3.connect("chatbot.db")
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO interactions (query, response) VALUES (?, ?)", (query, response))
        conn.commit()
        conn.close()
        return jsonify({"message": "Training data added!"})
    else:
        return jsonify({"error": "Missing query or response"}), 400

# API to fetch chatbot responses
@app.route("/chatbot-response", methods=["GET"])
def chatbot_response():
    query = request.args.get("query")
    response = get_response(query)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)
