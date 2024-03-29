from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import base64
import requests

app = Flask(__name__)

API_KEY = 'AIzaSyCq6jd9WCPFLNuEBsQ5k9xiyXJ-THOhiwY'
SEARCH_ENGINE_ID = '83345d27f6d114d7f'

openai_client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")


chat_history = [
  {"role": "system", "content": "you are a personalize ai teacher, your work is to teach student in interactive and easy to understand format"},
  {"role": "user", "content": "you are a childrean of 12 to 16 years and dont like larger responses"},
 
]

@app.route('/')
def index():
    return render_template('index.html', image_url=None)



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
    if user_message.strip():  
        query = user_message.strip()  
        image_url = perform_image_search(query)
    else:
        image_url = None
    

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

    return jsonify({"assistant_response": new_message["content"], "image_url": image_url})
def perform_image_search(query):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={SEARCH_ENGINE_ID}&searchType=image&key={API_KEY}"
    response = requests.get(url)
    data = response.json()
    if 'items' in data and len(data['items']) > 0:
        image_url = data['items'][0]['link']
        return image_url
    else:
        return None


@app.route('/process_image', methods=['POST'])
def process_image():

        
        image = request.files['image'].read()
        question = request.form['question']
        base64_image = base64.b64encode(image).decode("utf-8")

        
        completion = openai_client.chat.completions.create(
            model="local-model",
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
