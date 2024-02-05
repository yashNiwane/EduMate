from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import pyttsx3

app = Flask(__name__)

# Initialize OpenAI client
openai_client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Chat history
chat_history = [
    {"role": "system", "content": "You are an intelligent assistant. You always provide well-reasoned answers that are both correct and helpful."},
    {"role": "user", "content": "Hello, introduce yourself to someone opening this program for the first time. Be concise."},
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    user_message = request.form['user_message']

    # Display user message in the chat history
    chat_history.append({"role": "user", "content": user_message})

    # Generate assistant's response using OpenAI
    completion = openai_client.chat.completions.create(
        model="local-model",
        messages=chat_history,
        temperature=0.7,
        stream=True,
    )

    new_message = {"role": "assistant", "content": ""}

    for chunk in completion:
        if chunk.choices[0].delta.content:
            new_message["content"] += chunk.choices[0].delta.content

    # Display assistant's response in the chat history
    chat_history.append(new_message)

    # Output the assistant's response vocally
    engine.say(new_message["content"])
    engine.runAndWait()

    return jsonify({"assistant_response": new_message["content"]})

@app.route('/get_chat_history', methods=['GET'])
def get_chat_history():
    return jsonify({"chat_history": chat_history})

if __name__ == '__main__':
    app.run(debug=True)
