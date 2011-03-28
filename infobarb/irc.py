"""
Low level abstraction layer over IRC.
"""
import panglery

from twisted.words.protocols import irc


class FancyInfobarbPangler(panglery.Pangler):
    """
    A Pangler with some infobarb-specific hook shortcuts.
    """
    def onPrivateMessage(self, _func=None):
        return self.subscribe(_func,
                              event="privateMessageReceived",
                              needs=["user", "message"])


    def onChannelMessage(self, _func=None):
        return self.subscribe(_func,
                              event="channelMessageReceived",
                              needs=["user", "channel", "message"])


    def onPrivateNotice(self, _func=None):
        return self.subscribe(_func,
                              event="privateNoticeReceived",
                              needs=["user", "message"])


    def onChannelNotice(self, _func=None):
        return self.subscribe(_func,
                              event="channelNoticeReceived",
                              needs=["user", "channel", "message"])


    def onUserJoin(self, _func=None):
        return self.subscribe(_func,
                              event="userJoined",
                              needs=["user", "channel"])



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
