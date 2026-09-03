"""
Smart Parking System - Flask Backend
Updated with AI Assistant using Groq API (Free & Fast)
"""
from flask import Flask, render_template, request, jsonify, session  # type: ignore[import-not-found]
from fuzzy_engine import run_fuzzy, get_membership_curves
import json, random, datetime, requests, os
from dotenv import load_dotenv

load_dotenv()  # reads variables from a local .env file (not committed to git)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "smart_parking_2024")

# ── Your Groq API Key — get free at console.groq.com ────────────
# Set this in a local .env file as GROQ_API_KEY=your_key_here
# NEVER hardcode real keys in source files that get pushed to GitHub.
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL     = "https://api.groq.com/openai/v1/chat/completions"

# ── Simulated parking slots ──────────────────────────────────────
SLOTS = [
    {"id": 1, "zone": "A", "label": "A1", "occupied": False},
    {"id": 2, "zone": "A", "label": "A2", "occupied": True},
    {"id": 3, "zone": "A", "label": "A3", "occupied": False},
    {"id": 4, "zone": "B", "label": "B1", "occupied": True},
    {"id": 5, "zone": "B", "label": "B2", "occupied": False},
    {"id": 6, "zone": "B", "label": "B3", "occupied": True},
    {"id": 7, "zone": "C", "label": "C1", "occupied": False},
    {"id": 8, "zone": "C", "label": "C2", "occupied": False},
    {"id": 9, "zone": "C", "label": "C3", "occupied": True},
]


def suggest_slot(decision):
    """Pick best available slot based on parking decision."""
    available = [s for s in SLOTS if not s["occupied"]]
    if not available:
        return None
    if decision == "Easy":
        for s in available:
            if s["zone"] == "A":
                return s
    elif decision == "Normal":
        for s in available:
            if s["zone"] == "B":
                return s
    return available[0]


def build_ai_system_prompt(context: dict) -> str:
    """
    Build a detailed system prompt for the AI assistant.
    context dict contains the latest fuzzy analysis result.
    """
    score    = context.get("score", "N/A")
    decision = context.get("decision", "N/A")
    risk     = context.get("risk", "N/A")
    distance = context.get("distance", "N/A")
    space    = context.get("space", "N/A")
    speed    = context.get("speed", "N/A")
    exp      = context.get("experience", "N/A")
    weather  = context.get("weather", "N/A")
    slot     = context.get("slot", "N/A")
    act      = context.get("activations", {})

    if exp == "beginner":
        exp_note = (
            "The driver is a BEGINNER. Use very simple, clear language. "
            "Give extra safety warnings. Suggest going slow and using mirrors often. "
            "Be encouraging and patient in tone."
        )
    else:
        exp_note = (
            "The driver is an EXPERT. You can use technical terms. "
            "Keep advice concise and professional."
        )

    if weather == "rainy":
        weather_note = (
            "It is RAINY. Warn about slippery surfaces, reduced visibility, "
            "and longer stopping distances. Suggest extra caution."
        )
    else:
        weather_note = "Weather is clear. Normal driving conditions apply."

    return f"""You are SmartPark AI — a friendly, expert parking assistant embedded in a fuzzy logic parking guidance system.

=== CURRENT PARKING ANALYSIS ===
Fuzzy Logic Score   : {score} / 100
Decision            : {decision}
Risk Level          : {risk}
Suggested Slot      : {slot}

Driver Inputs:
  - Distance from obstacle : {distance} / 10
  - Available space        : {space} / 10
  - Vehicle speed          : {speed} km/h
  - Driver experience      : {exp}
  - Weather                : {weather}

Fuzzy Activations:
  - Tight  : {round(act.get('tight', 0) * 100)}%
  - Normal : {round(act.get('normal', 0) * 100)}%
  - Easy   : {round(act.get('easy', 0) * 100)}%

=== DRIVER PROFILE ===
{exp_note}

=== WEATHER ===
{weather_note}

=== YOUR ROLE ===
1. When asked "should I park?" — give a clear YES or NO first, then explain why based on the score and conditions.
2. When asked for instructions — give numbered step-by-step parking instructions (5-8 steps) tailored to the driver's experience, weather, and score.
3. For beginners: use very simple words, add encouragement, explain each step clearly.
4. For experts: be brief and technical.
5. Always mention the suggested slot ({slot}) when recommending where to park.
6. If risk is High (Tight), strongly warn the driver and suggest waiting or asking for help.
7. If risk is Low (Easy), be positive and encouraging.
8. Keep all responses friendly, clear, and under 200 words unless the user asks for more detail.
9. Never use jargon the driver won't understand.
10. If no analysis has been run yet, ask the user to click "Analyze Parking" first.
"""


# ════════════════════════════════════════════════════════════════
#  EXISTING ROUTES
# ════════════════════════════════════════════════════════════════

@app.route("/")
def index1():
    return render_template("index1.html")


@app.route("/api/analyze", methods=["POST"])
def analyze():
    data       = request.json
    distance   = float(data.get("distance", 5))
    space      = float(data.get("space", 5))
    speed      = float(data.get("speed", 30))
    experience = data.get("experience", "beginner")
    weather    = data.get("weather", "clear")

    result = run_fuzzy(distance, space, speed, experience, weather)
    slot   = suggest_slot(result["decision"])

    history = session.get("history", [])
    entry = {
        "time":       datetime.datetime.now().strftime("%H:%M:%S"),
        "distance":   distance,
        "space":      space,
        "speed":      speed,
        "experience": experience,
        "weather":    weather,
        "decision":   result["decision"],
        "risk":       result["risk"],
        "score":      result["score"],
        "slot":       slot["label"] if slot else "None",
    }
    history.append(entry)
    if len(history) > 10:
        history = history[-10:]
    session["history"] = history

    session["last_analysis"] = {
        "score":       result["score"],
        "decision":    result["decision"],
        "risk":        result["risk"],
        "distance":    distance,
        "space":       space,
        "speed":       speed,
        "experience":  experience,
        "weather":     weather,
        "slot":        slot["label"] if slot else "None",
        "activations": result.get("activations", {}),
    }

    return jsonify({
        **result,
        "suggested_slot": slot,
        "slots": SLOTS,
    })


@app.route("/api/curves")
def curves():
    return jsonify(get_membership_curves())


@app.route("/api/history")
def history():
    return jsonify(session.get("history", []))


@app.route("/api/slots")
def slots():
    return jsonify(SLOTS)


# ════════════════════════════════════════════════════════════════
#  AI ASSISTANT ROUTE — Powered by Groq (Free & Ultra Fast)
# ════════════════════════════════════════════════════════════════

@app.route("/api/chat", methods=["POST"])
def chat():
    """
    AI parking assistant powered by Groq (free tier, ultra fast).

    Expects JSON body:
        { "message": "Should I park now?" }

    Returns JSON:
        { "reply": "YES, you can park safely..." }

    Uses llama-3.3-70b-versatile model via Groq's OpenAI-compatible API.
    """
    data     = request.json or {}
    user_msg = data.get("message", "").strip()

    if not user_msg:
        return jsonify({"reply": "Please type a question."}), 400

    if not GROQ_API_KEY:
        return jsonify({
            "reply": (
                "⚠️ No Groq API key found.\n"
                "Create a .env file with GROQ_API_KEY=your_key_here.\n"
                "Get a free key at: console.groq.com"
            )
        }), 200

    # Get latest fuzzy analysis from session for context
    context       = session.get("last_analysis", {})
    system_prompt = build_ai_system_prompt(context)

    # Build conversation history (OpenAI-compatible format)
    chat_history = session.get("chat_history", [])
    chat_history.append({"role": "user", "content": user_msg})
    if len(chat_history) > 20:
        chat_history = chat_history[-20:]

    # Groq uses OpenAI format: system message + conversation history
    messages = [{"role": "system", "content": system_prompt}] + chat_history

    try:
        response = requests.post(
            GROQ_URL,
            headers={
                "Content-Type":  "application/json",
                "Authorization": f"Bearer {GROQ_API_KEY}",
            },
            json={
                "model":       "llama-3.3-70b-versatile",  # Free & fast on Groq
                "messages":    messages,
                "max_tokens":  512,
                "temperature": 0.7,
            },
            timeout=15
        )

        data_resp = response.json()

        if response.status_code == 401:
            return jsonify({
                "reply": (
                    "❌ Invalid Groq API key.\n"
                    "Please update GROQ_API_KEY in app.py.\n"
                    "Get a free key at: console.groq.com"
                )
            }), 200

        if response.status_code == 429:
            return jsonify({
                "reply": "⏳ Rate limit reached. Please wait a moment and try again."
            }), 200

        if response.status_code != 200:
            error_msg = data_resp.get("error", {}).get("message", "Unknown error")
            return jsonify({"reply": f"Groq error: {error_msg}"}), 200

        reply = (
            data_resp
            .get("choices", [{}])[0]
            .get("message", {})
            .get("content", "Sorry, no response.")
        )

        # Save reply to session history
        chat_history.append({"role": "assistant", "content": reply})
        session["chat_history"] = chat_history

        return jsonify({"reply": reply})

    except requests.Timeout:
        return jsonify({"reply": "⏱️ Request timed out. Please try again."}), 200

    except Exception as e:
        return jsonify({"reply": f"AI error: {str(e)}"}), 200


@app.route("/api/chat/clear", methods=["POST"])
def clear_chat():
    """Clear the chat history from session."""
    session.pop("chat_history", None)
    return jsonify({"status": "cleared"})


# ════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app.run(debug=True, port=5000)