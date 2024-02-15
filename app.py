from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import base64

app = Flask(__name__)

openai_client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")


chat_history = [
  {"role": "system", "content": "You are an AI science tutor. Your goal is to facilitate learning in a questioning and answering format for students. The subject is Science, covering various topics."},
  {"role": "user", "content": "You are a student eager to learn. Begin by asking the AI tutor a question related to any science topic. The AI will provide a detailed and comprehensible answer. After receiving the answer, try to summarize the information in your own words and ask a follow-up question to deepen your understanding. The learning goal is to ensure that you not only grasp the concept but can also explain it to someone else."},
  {"role": "system", "content": "Provide a clear and concise question related to science to start the learning interaction."}
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    user_message = request.form['user_message']


    image_input = request.files.get('image_input')
    if image_input:
        image_data = base64.b64encode(image_input.read()).decode("utf-8")
        user_message_data = [{"type": "text", "text": user_message}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}]
    else:
        user_message_data = [{"type": "text", "text": user_message}]


    chat_history.append({"role": "user", "content": user_message_data})


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


    chat_history.append(new_message)

    return jsonify({"assistant_response": new_message["content"]})


@app.route('/process_image', methods=['POST'])
def process_image():

        # Read the image and question from the form
        image = request.files['image'].read()
        question = request.form['question']
        base64_image = base64.b64encode(image).decode("utf-8")

        # Make a request to OpenAI
        completion = openai_client.chat.completions.create(
            model="local-model",  # not used
            messages=[
                {
                    "role": "system",
                    "content": "This is a chat between a user and an assistant. The assistant is helping the user to describe an image.",
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": question},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                        },
                    ],
                },
            ],
            max_tokens=1000,
        )
        return jsonify({"result": "Image processed successfully"})






@app.route('/save-message', methods=['POST'])
def save_message():
    content = request.form['content']
    with open('templates/messages.html', 'a') as file:
        file.write(content + '<br>')  
    return 'Message saved successfully!'

if __name__ == '__main__':
    app.run(debug=True)
