from django.test import TestCase
from django.urls import reverse
from .models import *

broadcaster_permissions = ['True', 'False', 'False']
moderator_permissions = ['False', 'True', 'False']
subscriber_permissions = ['False', 'False', 'True']
everyone_permissions = ['False', 'False', 'False']

def create_test_command(text, permissions):
    simple_output = SimpleOutput(output_text=text)
    simple_output.save()
    command = Command(command='!' + text, permissions=permissions, cooldown=False, output=simple_output)
    command.save()

def create_test_commands():
    create_test_command('disabled', DISABLED)
    create_test_command('broadcaster', BROADCASTER_ONLY)
    create_test_command('moderator', MODERATOR_ONLY)
    create_test_command('subscriber', SUBSCRIBER_ONLY)
    create_test_command('everyone', EVERYONE)

class PermissionsTests(TestCase):
    urls = 'dashboard.urls'

    def verify_response(self, command, permissions, expected_response):
        args = {'is_broadcaster': permissions[0], 'is_moderator': permissions[1], 'is_subscriber': permissions[2], 'username': 'test', 'line': command}
        response = self.client.get(reverse('drfujibot'), data=args)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, expected_response)

    def test_disabled_permissions(self):
        create_test_commands()
        self.verify_response('!disabled', broadcaster_permissions, '')
        self.verify_response('!disabled', moderator_permissions, '')
        self.verify_response('!disabled', subscriber_permissions, '')
        self.verify_response('!disabled', everyone_permissions, '')

    def test_broadcaster_permissions(self):
        create_test_commands()
        self.verify_response('!broadcaster', broadcaster_permissions, 'broadcaster')
        self.verify_response('!broadcaster', moderator_permissions, 'Sorry')
        self.verify_response('!broadcaster', subscriber_permissions, 'Sorry')
        self.verify_response('!broadcaster', everyone_permissions, 'Sorry')

    def test_moderator_permissions(self):
        create_test_commands()
        self.verify_response('!moderator', broadcaster_permissions, 'moderator')
        self.verify_response('!moderator', moderator_permissions, 'moderator')
        self.verify_response('!moderator', subscriber_permissions, 'Sorry')
        self.verify_response('!moderator', everyone_permissions, 'Sorry')

    def test_subscriber_permissions(self):
        create_test_commands()
        self.verify_response('!subscriber', broadcaster_permissions, 'subscriber')
        self.verify_response('!subscriber', moderator_permissions, 'subscriber')
        self.verify_response('!subscriber', subscriber_permissions, 'subscriber')
        self.verify_response('!subscriber', everyone_permissions, 'Sorry')

    def test_everyone_permissions(self):
        create_test_commands()
        self.verify_response('!everyone', broadcaster_permissions, 'everyone')
        self.verify_response('!everyone', moderator_permissions, 'everyone')
        self.verify_response('!everyone', subscriber_permissions, 'everyone')
        self.verify_response('!everyone', everyone_permissions, 'everyone')
