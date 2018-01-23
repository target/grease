from tgt_grease.core import Configuration
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL
from urllib3.exceptions import HTTPError
import requests
import json



class Notifications(object):
    """Notification Router for third party resources

    This is the class to handle all notifications to third party resources

    Attributes:
        _conf (Configuration): Configuration Object
        hipchat_url (str): This is the hipchat API url
        hipchat_token (str): set this to override the config for the auth token
        hipchat_room (str): set this to override the config for the room

    """

    _conf = None
    # HipChat Configuration
    hipchat_url = "https://api.hipchat.com/v2/room/"
    hipchat_token = None
    hipchat_room = None

    def __init__(self, Config=None):
        if Config and isinstance(Config, Configuration):
            self._conf = Config
        else:
            self._conf = Configuration()

    def SendMessage(self, message, level=DEBUG, channel=None):
        """Send Message to configured channels

        This method is the main point of contact with Notifications in GREASE. This will handle routing to all
        configured channels. Use `level` to define what level the message is. This can impact whether a message is
        sent as well as if the message sent will have special attributes (EX: red text). Use `channel` to route
        around sending to multiple channels if the message traditionally would go to multiple, instead going only
        to the selected one.

        Note:
            if you use the channel argument and the channel is not found you will receive False back

        Args:
            message (str): Message to send
            level (int): Level of message to be sent
            channel (str): Specific channel to notify

        Returns:
            bool: Success of sending

        """
        if channel \
                and 'enabled' in self._conf.get('Notifications', channel, {}) \
                and self._conf.get('Notifications', channel, {}).get('enabled'):
            return bool(self._route_notification(channel, message, level))
        else:
            # Capture object for notification channel statuses
            NotificationStatus = []
            NotificationChannels = self._conf.get('Notifications', default={})  # type: dict
            # Loop through those channels
            for Notifier, Config in NotificationChannels.items():
                # ensure channel is enabled
                if 'enabled' in Config and Config.get('enabled'):
                    # loop through the channels
                    NotificationStatus.append(bool(self._route_notification(Notifier, message, level)))
            # make the list unique
            NotificationStatus = list(set(NotificationStatus))
            if len(NotificationStatus) > 1:
                # we got at least one true and at least one false
                return False
            elif len(NotificationStatus) is 1:
                # return what the categorical state was
                return bool(NotificationStatus[0])
            else:
                # nothing was configured to run return true
                return True

    def _route_notification(self, channel, message, level):
        """Handle actual calling of notification channels

        Args:
            channel (str): Channel to notify
            message (str): Message to send
            level (int): Level to send at

        Returns:
            bool: Method success status

        """
        if channel == "HipChat":
            return self.send_hipchat_message(message, level)
        elif channel == "Slack":
            return self.send_slack_message(message)
        else:
            return False

    def send_hipchat_message(self, message, level, color=None):
        """Send a hipchat message

        Args:
            message (str): Message to send to hipchat
            level (int): message level
            color (str): color of message

        Returns:
            bool: API response status

        """
        if not color:
            if level is DEBUG:
                color = 'grey'
            elif level is INFO:
                color = 'purple'
            elif level is WARNING:
                color = 'yellow'
            elif level is ERROR:
                color = 'red'
            elif level is CRITICAL:
                color = 'red'
            else:
                color = 'grey'
        if self.hipchat_room and self.hipchat_token:
            url = "{0}{1}/notification?auth_token={2}".format(
                self.hipchat_url,
                self.hipchat_room,
                self.hipchat_token
            )
        else:
            url = "{0}{1}/notification?auth_token={2}".format(
                self.hipchat_url,
                self._conf.get('Notifications', 'HipChat').get('room'),
                self._conf.get('Notifications', 'HipChat').get('token')
            )
        try:
            response = requests.post(
                url=url,
                data={
                    'message': message,
                    'color': color
                },
                verify=False
                )
            if response.status_code == 204:
                return True
            else:
                return False
        except HTTPError:
            return False

    def send_slack_message(self, message):
        """Send a slack message to slack channel using webhook url in the configuration

        Args:
            message (str): Message to send to Slack

        Returns:
            bool: API response status

        """

        webhook_url = self._conf.get('Notifications', 'Slack').get('webhookURL')
        slack_data = {'text': message}

        try:
            response = requests.post(
                webhook_url, data=json.dumps(slack_data),
                headers={'Content-Type': 'application/json'}
            )
            return True
        except HTTPError:
            return False

