import os
import psycopg2
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)


def db():
    return psycopg2.connect(os.environ["DATABASE_URL"])


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return {"status": "ok"}


@app.route("/api/polls", methods=["GET"])
def list_polls():
    with db() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, question FROM polls ORDER BY id DESC")
        polls = []
        for pid, q in cur.fetchall():
            cur.execute("SELECT id, text, votes FROM options WHERE poll_id=%s ORDER BY id", (pid,))
            opts = [{"id": i, "text": t, "votes": v} for i, t, v in cur.fetchall()]
            polls.append({"id": pid, "question": q, "options": opts})
    return jsonify(polls)


@app.route("/api/polls", methods=["POST"])
def create_poll():
    data = request.json
    with db() as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO polls(question) VALUES (%s) RETURNING id", (data["question"],))
        poll_id = cur.fetchone()[0]
        for opt in data["options"]:
            cur.execute("INSERT INTO options(poll_id, text) VALUES (%s,%s)", (poll_id, opt))
    return jsonify(id=poll_id), 201


@app.route("/api/vote/<int:option_id>", methods=["POST"])
def vote(option_id):
    with db() as conn, conn.cursor() as cur:
        cur.execute("UPDATE options SET votes = votes + 1 WHERE id=%s", (option_id,))
    return {"message": "vote recorded"}
