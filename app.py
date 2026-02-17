"""
Digital SAT Prep – Python Flask Backend
Kurulum: pip install flask anthropic flask-cors
Çalıştır: python app.py
Sonra tarayıcıda: http://localhost:5000
"""

import os, json, random
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import anthropic

app = Flask(__name__, static_folder=".")
CORS(app)

# API anahtarını buraya yaz ya da ortam değişkeni olarak ver:
# export ANTHROPIC_API_KEY="sk-ant-..."
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", "YOUR_API_KEY_HERE"))

# ─────────────────────────────────────────────────────────────────────────────
# Yardımcı: Claude'a istek gönder
# ─────────────────────────────────────────────────────────────────────────────
def ask_claude(user_prompt: str, system_prompt: str, max_tokens: int = 1200) -> str:
    msg = client.messages.create(
        model="claude-opus-4-5-20251101",
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )
    return msg.content[0].text


# ─────────────────────────────────────────────────────────────────────────────
# 1) Grammar Fix
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/api/grammar", methods=["POST"])
def grammar():
    text = request.json.get("text", "").strip()
    if not text:
        return jsonify({"error": "Boş gönderdin!"}), 400

    system = """You are a precise SAT English grammar teacher.
Respond ONLY with valid JSON (no markdown, no extra text) in this exact format:
{
  "errors": [
    {"original": "wrong phrase", "fixed": "correct phrase", "rule": "brief rule name", "explanation": "why it's wrong"}
  ],
  "corrected_sentence": "The fully corrected sentence here.",
  "error_count": 2
}
If no errors found, return errors as empty array and corrected_sentence as the original."""

    result = ask_claude(f'Check this sentence for ALL grammar errors:\n"{text}"', system)
    try:
        data = json.loads(result)
    except Exception:
        data = {"errors": [], "corrected_sentence": text, "error_count": 0, "raw": result}
    return jsonify(data)


# ─────────────────────────────────────────────────────────────────────────────
# 2) Vocabulary
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/api/vocab", methods=["POST"])
def vocab():
    word = request.json.get("word", "").strip()
    if not word:
        return jsonify({"error": "Kelime girmedin!"}), 400

    system = """You are a vocabulary expert for Digital SAT prep.
Respond ONLY with valid JSON (no markdown, no extra text):
{
  "word": "ephemeral",
  "phonetic": "/ɪˈfem.ər.əl/",
  "part_of_speech": "adjective",
  "definitions": [
    {"meaning": "lasting for a very short time", "example": "The ephemeral beauty of cherry blossoms draws millions of visitors."}
  ],
  "synonyms": ["fleeting", "transient", "momentary"],
  "antonyms": ["permanent", "enduring"],
  "sat_note": "High-frequency SAT word. Often appears in reading passages about art or nature.",
  "memory_tip": "Think: 'ephemera' = things meant to be thrown away after brief use."
}"""

    result = ask_claude(f'Define this word for SAT prep: "{word}"', system)
    try:
        data = json.loads(result)
    except Exception:
        data = {"word": word, "raw": result}
    return jsonify(data)


# ─────────────────────────────────────────────────────────────────────────────
# 3) Pronunciation (phonetic + tips — browser does TTS)
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/api/pronounce", methods=["POST"])
def pronounce():
    text = request.json.get("text", "").strip()
    if not text:
        return jsonify({"error": "Metin girmedin!"}), 400

    system = """You are a phonetics expert.
Respond ONLY with valid JSON (no markdown, no extra text):
{
  "ipa": "/ɪˈfem.ər.əl/",
  "syllables": "e · phem · er · al",
  "stress": "Second syllable (PHEM) gets primary stress",
  "simple_guide": "ih-FEM-er-ul",
  "tips": ["The 'ph' makes an 'f' sound", "Don't say the final 'al' too strongly"],
  "common_mistake": "People often say 'EH-fe-mer-al' — stress the second syllable instead."
}"""

    result = ask_claude(f'Give phonetic pronunciation for: "{text}"', system)
    try:
        data = json.loads(result)
    except Exception:
        data = {"ipa": "", "simple_guide": text, "raw": result}
    return jsonify(data)


# ─────────────────────────────────────────────────────────────────────────────
# 4) Article + Quiz
# ─────────────────────────────────────────────────────────────────────────────
ARTICLE_TOPICS = [
    "the psychology of decision-making under uncertainty",
    "climate adaptation in coastal cities",
    "the economics of open-source software",
    "19th century abolitionist literature",
    "neuroplasticity and language acquisition",
    "the philosophy of consciousness",
    "renewable energy policy debates",
    "the sociology of social media echo chambers",
    "ancient Roman engineering innovations",
    "evolutionary biology and cooperation",
    "the ethics of artificial intelligence",
    "the history of the scientific method",
]

@app.route("/api/article", methods=["GET"])
def article():
    topic = random.choice(ARTICLE_TOPICS)

    system = """You are an SAT Reading passage author. Write exactly like real Digital SAT passages.
Respond ONLY with valid JSON (no markdown, no extra text):
{
  "topic": "topic here",
  "passage": "Full 280-320 word passage here. Use sophisticated vocabulary, complex sentence structures, and academic tone matching the Digital SAT Reading section.",
  "true_main_idea": "The passage argues that X by Y.",
  "key_points": ["point 1", "point 2", "point 3", "point 4"]
}"""

    result = ask_claude(f"Write a Digital SAT reading passage about: {topic}", system, max_tokens=1500)
    try:
        data = json.loads(result)
    except Exception:
        data = {"topic": topic, "passage": result, "true_main_idea": "", "key_points": []}
    return jsonify(data)


@app.route("/api/check_answers", methods=["POST"])
def check_answers():
    body = request.json
    passage = body.get("passage", "")
    true_main = body.get("true_main_idea", "")
    user_main = body.get("user_main_idea", "")
    user_summary = body.get("user_summary", "")
    key_points = body.get("key_points", [])

    system = """You are an SAT Reading teacher evaluating student answers.
Respond ONLY with valid JSON (no markdown, no extra text):
{
  "main_idea_score": 75,
  "main_idea_feedback": "Your main idea captured X but missed Y...",
  "summary_score": 80,
  "summary_feedback": "Good coverage of Z. You missed the author's point about...",
  "missed_points": ["point A", "point B"],
  "overall_score": 77,
  "grade": "B",
  "encouragement": "Great effort! Focus on..."
}"""

    prompt = f"""PASSAGE:\n{passage}

CORRECT MAIN IDEA: {true_main}
KEY POINTS: {json.dumps(key_points)}

STUDENT'S MAIN IDEA: "{user_main}"
STUDENT'S SUMMARY: "{user_summary}"

Evaluate the student's answers."""

    result = ask_claude(prompt, system)
    try:
        data = json.loads(result)
    except Exception:
        data = {"overall_score": 0, "raw": result}
    return jsonify(data)


# ─────────────────────────────────────────────────────────────────────────────
# 5a) SAT Math Questions
# ─────────────────────────────────────────────────────────────────────────────
MATH_TOPICS = [
    "linear equations and inequalities",
    "systems of equations",
    "quadratic functions and equations",
    "exponential growth and decay",
    "statistics: mean, median, standard deviation",
    "probability and data analysis",
    "geometry: circles, triangles, polygons",
    "trigonometry: sine, cosine, tangent",
    "ratios, rates, and proportional reasoning",
    "functions: domain, range, transformations",
    "advanced algebra: complex numbers",
    "word problems: rates and percentages",
]

@app.route("/api/math_question", methods=["GET"])
def math_question():
    topic = random.choice(MATH_TOPICS)

    system = """You create Digital SAT Math questions that are INDISTINGUISHABLE from real College Board questions.
Respond ONLY with valid JSON (no markdown, no extra text):
{
  "topic": "linear equations",
  "difficulty": "Hard",
  "question": "Full question text here with all necessary context.",
  "type": "multiple_choice",
  "choices": {
    "A": "first option",
    "B": "second option",
    "C": "third option",
    "D": "fourth option"
  },
  "correct_answer": "B",
  "solution": "Step 1: ... Step 2: ... Step 3: ... Therefore the answer is B.",
  "concept": "What skill this tests",
  "trap": "Common mistake students make on this question type."
}
For grid-in questions, set type to 'grid_in', choices to null, and correct_answer to the numeric value."""

    result = ask_claude(
        f"Create one Digital SAT Math question about: {topic}. Make it hard difficulty, similar to real SAT Module 2 questions.",
        system, max_tokens=1000
    )
    try:
        data = json.loads(result)
    except Exception:
        data = {"topic": topic, "question": result, "choices": None}
    return jsonify(data)


# ─────────────────────────────────────────────────────────────────────────────
# 5b) SAT Writing & Reading Questions
# ─────────────────────────────────────────────────────────────────────────────
WR_SUBTYPES = [
    "craft and structure: analyzing word choice",
    "information and ideas: identifying the main idea",
    "information and ideas: interpreting data from charts",
    "craft and structure: text structure and purpose",
    "expression of ideas: transitions and cohesion",
    "standard English conventions: punctuation",
    "standard English conventions: sentence structure",
    "cross-text connections: comparing two passages",
    "craft and structure: point of view and purpose",
    "information and ideas: making inferences",
]

@app.route("/api/wr_question", methods=["GET"])
def wr_question():
    subtype = random.choice(WR_SUBTYPES)

    system = """You create Digital SAT Reading and Writing questions identical to real College Board questions.
Respond ONLY with valid JSON (no markdown, no extra text):
{
  "subtype": "craft and structure",
  "skill": "word choice",
  "difficulty": "Medium",
  "passage": "Short passage excerpt (3-6 sentences) with an underlined or bracketed word/phrase if needed.",
  "question": "The full question text exactly as it would appear on the Digital SAT.",
  "choices": {
    "A": "first option",
    "B": "second option",
    "C": "third option",
    "D": "fourth option"
  },
  "correct_answer": "C",
  "explanation": "C is correct because... A is wrong because... B is wrong because... D is wrong because...",
  "strategy": "On questions like this, always look for..."
}"""

    result = ask_claude(
        f"Create one Digital SAT Reading & Writing question about: {subtype}. Mirror real College Board style exactly.",
        system, max_tokens=1200
    )
    try:
        data = json.loads(result)
    except Exception:
        data = {"subtype": subtype, "question": result, "choices": None}
    return jsonify(data)


# ─────────────────────────────────────────────────────────────────────────────
# 6) English Grammar Exercises (YENI EKLENDI)
# ─────────────────────────────────────────────────────────────────────────────
GRAMMAR_TOPICS = [
    "subject-verb agreement",
    "pronoun-antecedent agreement",
    "parallel structure",
    "dangling and misplaced modifiers",
    "punctuation: commas with nonrestrictive clauses",
    "punctuation: semicolons and colons",
    "verb tense consistency",
    "active vs passive voice",
    "articles: a, an, the",
    "countable vs uncountable nouns",
    "conditional sentences (if-clauses)",
    "relative clauses: who, which, that",
    "gerunds vs infinitives",
    "comparative and superlative adjectives",
    "prepositions of time and place",
]

@app.route("/api/grammar_exercise", methods=["GET"])
def grammar_exercise():
    topic = random.choice(GRAMMAR_TOPICS)

    system = """You create English grammar exercises for SAT prep students.
Respond ONLY with valid JSON (no markdown, no extra text):
{
  "topic": "subject-verb agreement",
  "instruction": "Choose the option that correctly completes the sentence.",
  "sentence": "The committee _____ unable to reach a consensus on the proposed budget changes.",
  "choices": {
    "A": "were",
    "B": "was",
    "C": "are",
    "D": "have been"
  },
  "correct_answer": "B",
  "rule": "Collective nouns like 'committee', 'team', 'jury' take singular verbs in American English.",
  "explanation": "'Was' is correct because 'committee' is a collective noun treated as singular in American English. 'Were' would be used in British English. 'Are' is present tense plural. 'Have been' is plural.",
  "more_examples": ["The jury has reached its verdict.", "The team is practicing."],
  "tip": "When in doubt with collective nouns on the SAT, use singular verbs — the test follows American English conventions."
}"""

    result = ask_claude(
        f"Create an English grammar exercise about: {topic}. Make it SAT-level difficulty.",
        system, max_tokens=900
    )
    try:
        data = json.loads(result)
    except Exception:
        data = {"topic": topic, "question": result, "choices": None}
    return jsonify(data)


# ─────────────────────────────────────────────────────────────────────────────
# Static files
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(".", "index.html")


if __name__ == "__main__":
    print("\n🎓 Digital SAT Prep başlatılıyor...")
    print("👉 http://localhost:5000 adresini aç\n")
    app.run(debug=True, port=5000)
