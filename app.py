import gradio as gr
import openai
import random
import time

from typing_extensions import Never
from requests import Response

# Set up OpenAI API key
openai.api_key = secretbob

#   Global variable to hold the chat history, initialise with system role
system_message = {"role": "system", "content": "You are a helpful assistant."}
messages = {"role": "system", "content": "You are a helpful assistant."}

conversation = [
        {"role": "system", "content": "You are an intelligent professor."}
        ]

msgfirst = gr.Textbox(label="Texto del Audio")
respuesta = gr.Textbox(label = "Resultado de su consulta")
title = "BOB, Aplicación demostrativa"
description = (
    "BOB es una simple interface demostrativa que utiliza las aplicaciones de OpenAI y prueba sus funcionalidades mostrando como se puede aplicar la tecnología en el día a día"
)

def transcribe(audio):

#   Whisper API

    audio_file = open(audio, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)


#   ChatGPT API

#   append user's inut to conversation
    conversation.append({"role": "user", "content": transcript["text"]})

    response = openai.ChatCompletion.create(
       model="gpt-3.5-turbo",
       messages=conversation
    )

    print(response)

#   system_message is the response from ChatGPT API
    system_message = response["choices"][0]["message"]["content"]

#   append ChatGPT response (assistant role) back to conversation
    conversation.append({"role": "assistant", "content": system_message})


    return transcript["text"], system_message


app1 = gr.Interface(fn=transcribe, inputs=gr.Audio(source="microphone", type="filepath"), outputs=[msgfirst,respuesta] , title=title, description=description,allow_flagging="never")

with gr.Blocks() as demo:

    msg = gr.Textbox(label="Consulta para el Chatbot")
    chatbot = gr.Chatbot()
    clear = gr.Button("Clear")

    state = gr.State([])

    def user(user_message, history):
        return "", history + [[user_message, None]]

    def bot(history, messages_history):
        user_message = history[-1][0]
        bot_message, messages_history = ask_gpt(user_message, messages_history)
        messages_history += [{"role": "assistant", "content": bot_message}]
        history[-1][1] = bot_message
        time.sleep(1)
        return history, messages_history

    def ask_gpt(message, messages_history):
        messages_history += [{"role": "user", "content": message}]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages_history
        )
        return response['choices'][0]['message']['content'], messages_history

    def init_history(messages_history):
        messages_history = []
        messages_history += [system_message]
        return messages_history

    msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot, [chatbot, state], [chatbot, state]
    )

    clear.click(lambda: None, None, chatbot, queue=False).success(init_history, [state], [state])


app2 = demo

final = gr.TabbedInterface([app1, app2], ["Speech to text", "Text to Chatbot"])

if __name__ == "__main__":
    final.launch(auth=(usuario,contra))