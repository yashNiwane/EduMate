import os
import openai
from flask import Flask, render_template, request

# Load environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")


# Initialize OpenAI client
openai_client = openai


# Initialize Flask app
app = Flask(__name__)

# Global variable to hold the conversation
conversation = []

@app.route("/")
def index():
    global conversation
    conversation = []  # Clear the conversation when user starts a new conversation
    return render_template("index.html")

@app.route("/get_response", methods=["GET", "POST"])
def get_response():
    global conversation
    message = request.args.get("message")
    conversation.append({"role": "user", "content": message})
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation
    )
    response = completion["choices"][0]["message"]["content"]
    conversation.append({"role": "assistant", "content": response})
    return response

if __name__ == "__main__":
    app.run(debug=True)
