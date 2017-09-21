import requests
import os
from urllib3.exceptions import HTTPError


class Notifier:

    def __init__(self):
        #Make sure we have the appropriate keys
        self._auth_token = os.getenv('GREASE_HIPCHAT_TOKEN', '')
        self._hipchat_room = os.getenv('GREASE_HIPCHAT_ROOM', '')
        self._base_url = 'https://api.hipchat.com/v2/room/'
        self._response = None

    def get_response(self):
        # type: () -> requests.Response
        return self._response

    def set_hipchat_room(self, room, token):
        #Each HipChat room has a unique auth token, so we have to change both.
        self._auth_token = token
        self._hipchat_room = room

    def send_hipchat_message(self, message):
        url = self._base_url + self._hipchat_room + '/notification?auth_token=' + self._auth_token 
        request_data = {
            'message': message
        }

        try:
            self._response = requests.post(
                url=url,
                data=request_data,
                verify=False
            )
            if self.get_response().status_code == 204:
                return True
            else:
                return False
        except HTTPError, e:
            return False

