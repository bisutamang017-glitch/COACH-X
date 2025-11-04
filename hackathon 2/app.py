from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
# Import the necessary Google GenAI library
from google import genai
from google.genai.errors import APIError

app = Flask(__name__)
CORS(app)

# ==============================
# 🔑 API KEY & GEMINI CONFIGURATION
# ==============================

# 🛑 ACTION REQUIRED: Replace this placeholder with your actual Gemini API Key.
# It is best practice to use environment variables (e.g., os.getenv("GEMINI_API_KEY"))
# but for simplicity, we'll use a direct placeholder.
GEMINI_API_KEY = "AIzaSyA9fSiZbQqRQf9cGS66xZshNXtVdDUUPtU" 

# Initialize the Gemini client
try:
    client = genai.Client(api_key=GEMINI_API_KEY)
    # Use a faster, general-purpose model for chat replies
    MODEL = 'gemini-2.5-flash' 
except Exception as e:
    print(f"Error initializing Gemini Client: {e}")
    client = None

# ==============================
# 🤖 AI Chat Knowledge Base (DEPRECATED - Replaced by Gemini)
# ==============================
# The old 'responses' dictionary is no longer needed. 
# We'll use a local fallback function just in case the API call fails.

def get_local_reply(message):
    """Provides a simple fallback response if the Gemini API fails."""
    local_responses = {
        "hi": "Hello there! 👋 I’m Coach X — your AI mentor. How can I help you today?",
        "hello": "Hi! 👋 How are you doing today?",
        "who are you": "I’m Coach X — your personal AI mentor built to help you grow smarter and stronger every day.",
        "who won the womens cricket worldcup 2025":"The champion of the 2025 ICC Women’s Cricket World Cup is India women’s national cricket team. They defeated South Africa women’s national cricket team in the final by 52 runs.",
    }
    for key, reply in local_responses.items():
        if key in message:
            return reply
    return "I’m powered by Gemini AI, but it seems I'm currently unable to connect. Can you try again shortly?"


# ==============================
# 💬 Chat Endpoint (Updated to use Gemini)
# ==============================
@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"reply": "Please say or type something."})

        # --- 1. Use the Gemini API ---
        if client:
            # We set a system instruction to define the AI's persona (Coach X)
            system_instruction = (
                "You are Coach X, a friendly and motivational personal AI mentor for career "
                "growth and skill development. Be concise, helpful, and supportive. Use relevant emojis."
            )
            
            # Generate the content using the Gemini model
            response = client.models.generate_content(
                model=MODEL,
                contents=user_message,
                config=genai.types.GenerateContentConfig(
                    system_instruction=system_instruction
                )
            )
            reply = response.text
        else:
            # --- 2. Fallback to Local Reply ---
            reply = get_local_reply(user_message.lower())

        return jsonify({"reply": reply})

    except APIError as e:
        print(f"Gemini API Error: {e}")
        # Fallback if there's an issue with the API key or quota
        return jsonify({"reply": "⚠️ API Error: Couldn't connect to Gemini. Check your API key or connection."})
    
    except Exception as e:
        print("General Server Error:", e)
        return jsonify({"reply": "⚠️ Server error. Please try again."}), 500


# ==============================
# 👨‍🏫 Mentor Data (Unchanged)
# ==============================
@app.route("/mentors", methods=["GET"])
def mentors():
    # This endpoint is now used by JavaScript in mentors.html to fetch data
    mentors_data = [
        {
            "id": "m1",
            "name": "Bishwash",
            "subject": "Mathematics",
            "description": "Expert in problem-solving, calculus, and logical reasoning. Loves helping students simplify complex concepts.",
            "contact": "7033771446",
            "sessions": [
                {"day": "Monday", "time": "10:00 AM - 11:00 AM", "price": 100},
                {"day": "Thursday", "time": "3:00 PM - 4:00 PM", "price": 100},
                {"day": "Saturday", "time": "5:00 PM - 6:00 PM", "price": 100}
            ]
        },
        {
            "id": "m2",
            "name": "Abhishek",
            "subject": "Physics",
            "description": "Passionate about mechanics and electricity. Breaks down difficult topics into easy-to-understand lessons.",
            "contact": "7848021451",
            "sessions": [
                {"day": "Tuesday", "time": "9:00 AM - 10:00 AM", "price": 150},
                {"day": "Friday", "time": "2:00 PM - 3:00 PM", "price": 180}
            ]
        },
        {
            "id": "m3",
            "name": "Akib",
            "subject": "Computer Science",
            "description": "Specialist in algorithms, Python, and problem-solving. Makes programming fun and practical.",
            "contact": "6202160937",
            "sessions": [
                {"day": "Wednesday", "time": "1:00 PM - 2:00 PM", "price": 200},
                {"day": "Saturday", "time": "10:00 AM - 11:00 AM", "price": 180}
            ]
        },
        {
            "id": "m4",
            "name": "Sabteen",
            "subject": "Chemistry",
            "description": "Experienced in organic and inorganic chemistry, focuses on real-world applications and conceptual clarity.",
            "contact": "9798177611",
            "sessions": [
                {"day": "Monday", "time": "4:00 PM - 5:00 PM", "price": 160},
                {"day": "Thursday", "time": "11:00 AM - 12:00 PM", "price": 190}
            ]
        }
    ]
    return jsonify(mentors_data)

# ==============================
# 🌐 Routes to Serve HTML Pages (Added Mentor & Payment)
# ==============================

@app.route("/")
def index():
    # Renders the main chat page
    return render_template("index.html")

@app.route("/login.html")
def login_page():
    return render_template("login.html")

@app.route("/features.html")
def features_page():
    return render_template("features.html")

@app.route("/mentors.html") # NEW ROUTE for Mentor List
def mentors_page():
    return render_template("mentors.html")

@app.route("/payment.html") # NEW ROUTE for Payment Step
def payment_page():
    # payment.html uses request arguments to show session details
    return render_template("payment.html")


# ==============================
# 🚀 Run the App
# ==============================
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
