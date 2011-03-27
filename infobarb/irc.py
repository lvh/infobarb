"""
Low level abstraction layer over IRC.
"""
import panglery

from twisted.words.protocols import irc


class FancyInfobarbPangler(panglery.Pangler):
    def onPrivateMessage(self, _func=None):
        return self.subscribe(_func,
                              event="privateMessage",
                              needs=["user", "message"])


    def onChannelMessage(self, _func=None):
        return self.subscribe(_func,
                              event="channelMessage",
                              needs=["user", "channel", "message"])



class InfobarbClient(irc.IRCClient):
    """
    The IRC client for an infobarb.
    """
    nickname = "infobarb"

    def __init__(self, pangler):
        self.p = pangler


    def privmsg(self, user, channel, message):
        """
        Called when a PRIVMSG is received from the server.
        """
        if channel == self.nickname:
            event = "privateMessage"
        else:
            event = "channelMessage"

        self.p.trigger(event=event,
                       user=user,
                       channel=channel,
                       message=message)
