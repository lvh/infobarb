"""
Low level abstraction layer over IRC.
"""
import panglery

from twisted.words.protocols import irc


class FancyInfobarbPangler(object):
    """
    Some infobarb-specific event hook shortcuts.
    """
    def __init__(self, boundPangler):
        self.p = boundPangler


    _SHORTCUTS = {
        "onPrivateMessage": {
            "event": "privateMessageReceived",
            "needs": ("user", "message")},

        "onChannelMessage": {
            "event": "channelMessageReceived",
            "needs": ("user", "channel", "message")},

        "onPrivateNotice": {
            "event": "privateNoticeReceived",
            "needs": ("user", "message")},

        "onChannelNotice": {
            "event": "channelNoticeReceived",
            "needs": ("user", "channel", "message")},

        "onUserJoin": {
            "event": "userJoined",
            "needs": ("user", "channel")}
        }


def _buildShortcut(defaultKwargs):
    def shortcut(self, _func=None, **kwargs):
        if any(k in defaultKwargs for k in kwargs):
            raise KeyError("duplicated shortcut kwarg")

        kwargs.update(defaultKwargs)
        return self.p.subscribe(_func, **kwargs)

    return shortcut


for name, defaultKwargs in FancyInfobarbPangler._SHORTCUTS.iteritems():
    setattr(FancyInfobarbPangler, name, _buildShortcut(defaultKwargs))


class InfobarbClient(irc.IRCClient):
    """
    The IRC client for an infobarb.
    """
    nickname = "infobarb"

    def __init__(self, pangler):
        self.p = pangler


    def privmsg(self, user, channel, message):
        if channel == self.nickname:
            event = "privateMessageReceived"
        else:
            event = "channelMessageReceived"

        self.p.trigger(event=event,
                       user=user,
                       channel=channel,
                       message=message)


    def noticed(self, user, channel, message):
        if channel == self.nickname:
            event = "privateNoticeReceived"
        else:
            event = "channelNoticeReceived"

        self.p.trigger(event=event,
                       user=user,
                       channel=channel,
                       message=message)


    def userJoined(self, user, channel):
        self.p.trigger(event="userJoined", user=user, channel=channel)
