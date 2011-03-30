"""
Low level abstraction layer over IRC.
"""
import inspect

import panglery

from twisted.words.protocols import irc


def _buildCallback(eventName, argNames):
    """
    Builds a callback method for InfobarbClient.

    Triggers the specified event with all arguments passed to the callback.
    """
    def callback(self, *args):
        assert len(argNames) == len(args) # inspection sanity check
        kwargs = dict(zip(argNames, args))
        self.p.trigger(event=eventName, **kwargs)

    return callback


def eventHookMagic(cls):
    """
    Creates callbacks for all the supported IRC events.
    """
    cls._builtinEventArgs = {}

    for eventName in cls._supportedEvents:
        callbackName = cls._supportedEvents[eventName]

        original = getattr(cls, callbackName)
        argNames = inspect.getargspec(original).args[1:]
        cls._builtinEventArgs[eventName] = argNames

        callback = _buildCallback(eventName, argNames)
        callback.eventName = eventName
        callback.__name__ = callbackName

        setattr(cls, callbackName, callback)

    return cls


@eventHookMagic
class InfobarbClient(irc.IRCClient):
    """
    The IRC client for an infobarb.
    """
    nickname = "infobarb"

    _supportedEvents = {
        "userJoined": "userJoined",
        "privmsgReceived": "privmsg",
        "noticeReceived": "noticed"
        }

    def __init__(self, boundPangler):
        self.p = boundPangler



_defaultDispatchHooks = []


def addDefaultDispatchHooks(boundPangler):
    """
    Adds the hooks that are available by default to a bound pangler.
    """
    for hook, kwargs in _defaultDispatchHooks:
        boundPangler.subscribe(hook, **kwargs)


def dispatchHook(dispatchedEvent):
    """
    A decorator for a callback that takes a general event and fires new, more
    specialized events.
    """
    needs = InfobarbClient._builtinEventArgs[dispatchedEvent]

    def decorator(f):
        kwargs = {"event": dispatchedEvent, "needs": needs}
        _defaultDispatchHooks.append((f, kwargs))

    return decorator


@dispatchHook("privmsgReceived")
def onPrivmsgReceived(self, p, user, channel, message):
    """
    Diferentiates privmsgs as private (directed at me) and those to a channel.
    """
    if channel == self.client.nickname:
        event = "privateMessageReceived"
    else:
        event = "channelMessageReceived"

    p.trigger(event=event, user=user, channel=channel, message=message)


@dispatchHook("noticeReceived")
def onNoticeReceived(self, p, user, channel, message):
    """
    Diferentiates notices as private (directed at me) and those to a channel.
    """
    if channel == self.client.nickname:
        event = "privateNoticeReceived"
    else:
        event = "channelNoticeReceived"

    p.trigger(event=event, user=user, channel=channel, message=message)


def _buildShortcut(defaultKwargs):
    def shortcut(self, _func=None, **kwargs):
        if any(k in defaultKwargs for k in kwargs):
            raise KeyError("duplicated shortcut kwarg")

        kwargs.update(defaultKwargs)
        return self.p.subscribe(_func, **kwargs)

    return shortcut


def shortcutMagic(cls):
    for event, eventInfo in cls._shortcuts.iteritems():
        shortcutName, needs = eventInfo["name"], eventInfo["args"]
        kwargs = {"event": event, "needs": needs}
        setattr(cls, shortcutName, _buildShortcut(kwargs))

    return cls



@shortcutMagic
class FancyInfobarbPangler(object):
    """
    Some infobarb-specific event hook shortcuts.

    This is just syntactic sugar. No fancy behavior here!
    """
    def __init__(self, boundPangler):
        self.p = boundPangler


    _shortcuts = {
        "privateMessageReceived": {
            "name": "onPrivateMessage",
            "args": ("user", "message"),
            },
        "channelMessageReceived": {
            "name": "onChannelMessage",
            "args": ("user", "channel", "message"),
            },
        "privateNoticeReceived": {
            "name": "onPrivateNotice",
            "args": ("user", "message"),
            },
        "channelNoticeReceived": {
            "name": "onChannelNotice",
            "args": ("user", "channel", "message"),
            },
        "userJoined": {
            "name": "onUserJoin",
            "args": ("user", "channel"),
            }
    }
