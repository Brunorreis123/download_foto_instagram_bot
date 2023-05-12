import telebot
from instaloader import Instaloader, Post
import requests
from io import BytesIO

bot = telebot.TeleBot('Seu Token aqui')
loader = Instaloader()


@bot.message_handler(commands=['start'])
def send_start_message(message):
    start_message = "Insira um link para fazer o download!"
    bot.reply_to(message, start_message)


# Define a função para baixar e enviar cada foto do carrossel.
def download_and_send_carousel_photos(message, post):
    try:
        for index, photo_url in enumerate(post.get_sidecar_nodes()):
            # Baixa a foto
            response = requests.get(photo_url.display_url)
            photo_data = BytesIO(response.content)

            # Envia a foto no chat
            bot.send_photo(message.chat.id, photo_data)

        reply_to_user(message, 'Fotos do carrossel enviadas com sucesso!')
    except Exception as e:
        reply_to_user(message, f"Ocorreu um erro: {str(e)}")


# Define a função para baixar e enviar a foto no chat.
def download_and_send_photo(message, post):
    try:
        if post.is_video or post.get_sidecar_nodes():
            # Se o post for um vídeo ou carrossel de fotos, tratamos de forma diferente
            download_and_send_carousel_photos(message, post)
        else:
            # Baixa a foto
            response = requests.get(post.url)
            photo_data = BytesIO(response.content)

            # Envia a foto no chat
            bot.send_photo(message.chat.id, photo_data)

        reply_to_user(message, 'Foto enviada com sucesso!')
    except Exception as e:
        reply_to_user(message, f"Ocorreu um erro: {str(e)}")

# Define a função para responder ao usuário com uma mensagem.
def reply_to_user(message, text):
    bot.send_message(message.chat.id, text)


# Define a função para lidar com mensagens contendo links.
@bot.message_handler(func=lambda message: message.entities is not None and any(
    entity.type == 'url' for entity in message.entities))
def handle_link_message(message):
    for entity in message.entities:
        if entity.type == 'url':
            post_url = message.text[entity.offset:entity.offset + entity.length]
            post = Post.from_shortcode(loader.context, post_url.split('/')[-2])
            download_and_send_photo(message, post)
            return

    reply_to_user(message, 'Não foi possível encontrar um link válido.')

# Inicia o bot.
bot.polling()
