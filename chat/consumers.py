import json
from .models import Message
from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

User = get_user_model()
class ChatConsumer(WebsocketConsumer):

    def fetch_messages(self, data):
        messages = Message.last_10_messages(self.room_group_name)

        print('dfdf')

        content = {
            'command': 'messages',
            'messages': self.messages_to_json(messages)
        }
        self.send_message(content)

    # Creating json out of multiple messages - used when retrieving messages
    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    # Creating json for one message
    def message_to_json(self, message):
        return {
            'author': message.author.username,
            'content': message.content,
            'timestamp': str(message.timestamp)
        }

    # New message function
    def new_message(self, data):
        print('new message')
        print(data)
        author = data['from']
        if not data['message']:
            print('none')
            return None
        author_user = User.objects.filter(username=author)[0]
        message = Message.objects.create(
            job=self.room_group_name,
            author=author_user,
            content=data['message'],
        )
        print(message)
        content = {
            'command': 'new_message',
            'message': self.message_to_json(message)
        }
        print('sdsds')
        return self.send_chat_message(content)

    # Action when new chat is viewed
    def chat_viewed(self, data):
        print('\nchat\n\n\n\n\n\n\n')
        # Getting msg from db and setting recipient viewed to true
        message = Message.objects.get(message_id=data['message_id'])
        message.recipient_viewed = True
        message.save()
        
        print("data")
        print(data)
        return data

    def read_all(self, data):
        username = data['viewer']
        print('\n\n\n\nsdsdsd')

        user = User.objects.get(username=username)
        # Changing messages that haven't been viewed to viewed  
        print(Message.objects.filter(job=self.room_group_name, recipient_viewed=False))
        past_messages = Message.objects.filter(job=self.room_group_name, recipient_viewed=False).exclude(author=user).update(recipient_viewed=True)

        return data

    # Creating statement for channel
    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message,
        'chat_viewed': chat_viewed,
        'read_all': read_all
    }

    def connect(self):
        
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        print("\n\n\n\n\n\n\n\n\nself.room_group_name\n\n\n\n\n\n\n\n\n\n")
        print(self.room_group_name)
        print(self.channel_name)
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        async_to_sync(self.accept())

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)

    def send_chat_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    def chat_message(self, event):
        message = event['message']

        self.send(text_data=json.dumps(message))

    def send_file(self, event):
        message = event['message']
        print(message)
