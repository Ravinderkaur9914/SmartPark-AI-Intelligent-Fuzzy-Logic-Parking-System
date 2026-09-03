# SmartPark-AI-Intelligent-Fuzzy-Logic-Parking-System
A Flask-based smart parking assistant that uses fuzzy logic to score how easy or risky a parking maneuver is, then suggests the best available slot — complete with a live simulation, membership-function charts, history log, and a Groq-powered AI chat assistant that gives context-aware parking advice.
<img width="1614" height="559" alt="image" src="https://github.com/user-attachments/assets/123b63d1-1342-40b1-8f0f-87eb9b04da36" />
# ✨ Features
📊 Fuzzy Logic Engine — pure NumPy fuzzy inference over distance, space, and speed
🚗 Live Parking Simulation — animated car with a rotating steering wheel reacting to difficulty
🅿️ Smart Slot Suggestion — recommends the best open slot across zones A / B / C
🌦️ Weather & Experience Aware — adjusts risk and advice for rainy conditions and beginner vs. expert drivers
🤖 AI Assistant (Groq / Llama 3.3) — chat with an AI that explains the current analysis and gives step-by-step parking instructions
🔊 Voice Alerts — Web Speech API reads out the decision
💾 History Log — last 10 analyses stored per session
 # 📈 Membership Function Charts — visualize the Near/Medium/Far, Small/Medium/Large, and Tight/Normal/Easy fuzzy sets
📸 Screenshots
<img width="1619" height="340" alt="image" src="https://github.com/user-attachments/assets/f68bd4d6-6c14-4531-b621-16a5a5188981" />
Membership Functions

<img width="1576" height="901" alt="image" src="https://github.com/user-attachments/assets/a28ffecf-ce8a-4b82-90cb-77347790046d" />
AI Chat + History

<img width="1637" height="859" alt="image" src="https://github.com/user-attachments/assets/f4daa55e-87b1-4a15-8b66-06fb31d045e6" />
Live analysis with score, risk, and slot recommendation:
# 📁 Project Structure
parking_system/
├── app.py              ← Flask backend (routes, session, slot logic)
├── fuzzy_engine.py     ← Pure NumPy fuzzy logic engine
├── requirements.txt    ← Python dependencies
├── .env.example         ← Template for required environment variables
├── .gitignore
├── templates/
│   └── index.html      ← Main HTML page
├── static/
│   ├── css/style.css   ← Dark tech UI stylesheet
│   └── js/app.js       ← Frontend: sliders, charts, animation, voice
└── screenshots/         ← README images

 # ⚙️ Setup
1. Clone the repo
bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
2. Create a virtual environment (recommended)
bash
python3 -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate
3. Install dependencies
bash
pip install -r requirements.txt
4. Add your API key
bash
cp .env.example .env

Then open .env and paste in your free Groq API key from console.groq.com.

⚠️ Never commit your real .env file — it's already excluded via .gitignore.

5. Run the app
bash
python app.py
6. Open in your browser
http://localhost:5000

# 🧠 How the Fuzzy Logic Works
Input Parameters
Parameter	Range	Fuzzy Sets
Distance	0 – 10	Near / Medium / Far
Space	0 – 10	Small / Medium / Large
Speed	0 – 100	Slow / Medium / Fast
Experience	Toggle	Beginner / Expert
Weather	Toggle	Clear / Rainy
Output
Score Range	Decision	Risk
60 – 100	Easy	Low
35 – 59	Normal	Medium
0 – 34	Tight	High

# 🔧 Customisation
Add more slots → edit the SLOTS list in app.py
Change fuzzy rules → edit evaluate_rules() in fuzzy_engine.py
Change membership shapes → edit fuzzify_*() functions in fuzzy_engine.py
Change theme colors → edit CSS variables in static/css/style.css
Change the AI's tone/behavior → edit build_ai_system_prompt() in app.py

# 🛠️ Tech Stack
Backend: Flask, NumPy
AI: Groq API (Llama 3.3 70B)
Frontend: HTML/CSS/JS, Chart.js, Web Speech API

# 📄 License
This project is open source — feel free to fork and build on it.
This project is open source — feel free to fork and build on it.

