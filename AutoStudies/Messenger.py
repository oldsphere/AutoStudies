from abc import ABC, abstractmethod

class Notification:

    def __init__(self):
        self.name = ''
        self.etime = 0
        self.status = 0
        self.msg = ''

    def set_name(self, name):
        self.name = name

    def set_etime(self, etime):
        self.etime = etime

    def set_status(self, status):
        self.status = status

    def set_msg(self, msg):
        self.msg = msg

    def set_messeger(self, messenger):
        self._messenger(messenger)

    def _parse_msg(self):
        self.msg.replace('%name', self.name)
        self.msg.replace('%etime', self.etime)
        self.msg.replace('%status', self.status)

    def send(self):
        self._messenger.send(self._parse_msg())

class PushBullentMessenger:

    def __init__(self, configfile):
        self._config = configfile
        self.ApplySettings()
        super().__init__(self)

    def send(self):
        ''' Send the message '''
        self._parse_msg()

    def ApplySettings(self):
        ''' Read the setting files '''
        pass
