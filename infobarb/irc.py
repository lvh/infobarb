"""
Low level abstraction layer over IRC.
"""
import inspect

import panglery

from twisted.words.protocols import irc


_supportedEvents = {
    "userJoined": {
        "callback": "userJoined"
        }
    }



class InfobarbClient(irc.IRCClient):
    """
    The IRC client for an infobarb.
    """
    nickname = "infobarb"

    def __init__(self, pangler):
        self.p = pangler



def _buildCallback(eventName, argNames):
    """
    Builds a callback method for IRCClient.

    Triggers the specified event with all arguments passed to the callback.
    """
    def callback(self, *args):
        assert len(argNames) == len(args) # inspection sanity check
        kwargs = dict(zip(argNames, args))
        self.p.trigger(event=eventName, **kwargs)

    return callback


for eventName in _supportedEvents:
    eventInfo = _supportedEvents[eventName]
    callbackName = eventInfo["callback"]

    original = getattr(InfobarbClient, callbackName)
    eventInfo["args"] = argNames = inspect.getargspec(original).args[1:]
    
    callback = _buildCallback(eventName, argNames)
    setattr(InfobarbClient, callbackName, callback)



_shortcuts = {
    # "privateMessageReceived": "onPrivateMessage",
    # "channelMessageReceived": "onChannelMessage",
    # "privateNoticeReceived": "onPrivateNotice",
    # "channelNoticeReceived": "onChannelNotice",
    "userJoined": "onUserJoin"
    }



class FancyInfobarbPangler(object):
    """
    Some infobarb-specific event hook shortcuts.

    This is just syntactic sugar. No fancy behavior here!
    """
    def __init__(self, boundPangler):
        self.p = boundPangler



def _buildShortcut(defaultKwargs):
    def shortcut(self, _func=None, **kwargs):
        if any(k in defaultKwargs for k in kwargs):
            raise KeyError("duplicated shortcut kwarg")

        kwargs.update(defaultKwargs)
        return self.p.subscribe(_func, **kwargs)

    return shortcut



for event, shortcutName in _shortcuts.iteritems():
    kwargs = {"event": event, "needs": _supportedEvents[event]["args"]}
    setattr(FancyInfobarbPangler, shortcutName, _buildShortcut(kwargs))



# TODO
def privmsgReceived(self, p, user, channel, message):
    if channel == self.nickname:
        event = "privateMessageReceived"
    else:
        event = "channelMessageReceived"

    p.trigger(event=event, user=user, channel=channel, message=message)


def noticeReceived(self, p, user, channel, message):
    if channel == self.nickname:
        event = "privateNoticeReceived"
    else:
        event = "channelNoticeReceived"

    p.trigger(event=event, user=user, channel=channel, message=message)
