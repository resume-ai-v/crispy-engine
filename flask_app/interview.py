# flask_app/interview.py

from flask import Blueprint, render_template, request, jsonify
import openai
import os

interview_bp = Blueprint("interview", __name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@interview_bp.route("/interview", methods=["GET", "POST"])
def interview():
    if request.method == "POST":
        role = request.json.get("role", "Software Engineer")
        user_input = request.json.get("question", "")
        prompt = f"You are an expert {role} interviewer. Ask or answer questions professionally. Candidate: {user_input}"

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            answer = response.choices[0].message.content
            return jsonify({"response": answer})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return render_template("interview.html")
