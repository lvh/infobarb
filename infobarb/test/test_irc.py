"""
Tests for the IRC abstraction.
"""
import panglery

from twisted.trial import unittest

from infobarb import irc


class CallStub(object):
    def __init__(self):
        self.called = False
        self.calledWith = (), {}


    def __call__(self, *args, **kwargs):
        self.called = True
        self.calledWith = args, kwargs



class MockClient(object):
    @classmethod
    def fromNickname(cls, nickname):
        c = cls()
        c.nickname = nickname
        return c
        


class PanglerCallStubTestCase(unittest.TestCase):
    """
    A test case that verifies if a pangler called a stub.
    """
    p = panglery.Pangler()

    def setUp(self):
        irc.addDefaultDispatchHooks(self.p)


    def assertStubCalled(self, stub, *args, **kwargs):
        """
        Asserts that the stub has been called with some positional arguments
        and some keyword arguments.
        """
        self.assertTrue(stub.called)

        calledArgs, calledKwargs = stub.calledWith
        self.assertEqual(calledArgs, args)
        self.assertEqual(calledKwargs, kwargs)


    def assertEventFired(self, stub, eventData):
        """
        Asserts that a stub got called with:
         - bound instance (a test case)
         - pangler (for firing new events)
         - event data
        """
        self.assertStubCalled(stub, self, self.p, **eventData)


NICKNAME = "testbarb"

_SAMPLE_DATA = {
    "user": "lvh",
    "channel": "#python",
    "message": "hi",
    "quitMessage": "bye",
    "nickname": "testbarb",
    "kicker": "lvh",
    "kickee": "cheater"
}

_KEY_MASK = {
    "nickname": "channel",
}


def _buildEventData(*keys):
    return dict((_KEY_MASK.get(k, k), _SAMPLE_DATA[k]) for k in keys)



class DefaultDispatchHookTestCase(PanglerCallStubTestCase):
    def setUp(self):
        super(DefaultDispatchHookTestCase, self).setUp()

        irc.addDefaultDispatchHooks(self.p)

        self.client = MockClient.fromNickname("testbarb")


    def _test_dispatchHook(self, sourceEvent, targetEvent, eventData):
        stub = CallStub()
        self.p.subscribe(stub, event=targetEvent, needs=eventData)
        self.p.trigger(event=sourceEvent, **eventData)        

        self.assertEventFired(stub, eventData)


    def test_privmsgReceived_privateMessage(self):
        eventData = _buildEventData("user", "message")
        eventData["channel"] = self.client.nickname

        sourceEvent = "privmsgReceived"
        targetEvent = "privateMessageReceived"

        self._test_dispatchHook(sourceEvent, targetEvent, eventData)


    def test_privmsgReceived_channelMessage(self):
        eventData = _buildEventData("user", "channel", "message")

        sourceEvent = "privmsgReceived"
        targetEvent = "channelMessageReceived"

        self._test_dispatchHook(sourceEvent, targetEvent, eventData)


    def test_noticeReceived_privateNotice(self):
        eventData = _buildEventData("user", "message")
        eventData["channel"] = self.client.nickname

        sourceEvent = "noticeReceived"
        targetEvent = "privateNoticeReceived"

        self._test_dispatchHook(sourceEvent, targetEvent, eventData)


    def test_noticeReceived_channelNotice(self):
        eventData = _buildEventData("user", "channel", "message")

        sourceEvent = "noticeReceived"
        targetEvent = "channelNoticeReceived"

        self._test_dispatchHook(sourceEvent, targetEvent, eventData)



class FancyInfobarbPanglerTestCase(PanglerCallStubTestCase):
    """
    Tests that the event hook shortcuts provided by FancyInfobobPangler work.
    """
    def setUp(self):
        super(FancyInfobarbPanglerTestCase, self).setUp()
        self.f = irc.FancyInfobarbPangler(self.p)


    def test_raiseOnMissingAttribute(self):
        self.assertRaises(AttributeError, getattr, self.f, "nonexistentHook")


    def test_raiseOnOverriddenKwarg(self):
        """
        Tests that if you use the fancy shortcut with a keyword that would get
        overridden by the shortcut, an exception gets raised.
        """
        decorator = self.f.onUserJoin
        self.assertRaises(KeyError, decorator, event="whatever")


    def _test_fancyShortcut(self, hook, event, eventData):
        hooks = [hook, hook()] # Hook should work directly and as a decorator

        for hook in hooks:
            stub = CallStub()
            hook(stub)
            self.p.trigger(event=event, **eventData)
            self.assertEventFired(stub, eventData)


    def test_onPrivateMessage(self):
        hook = self.f.onPrivateMessage
        event = "privateMessageReceived"
        eventData = _buildEventData("user", "message")
        self._test_fancyShortcut(hook, event, eventData)


    def test_onChannelMessage(self):
        hook = self.f.onChannelMessage
        event = "channelMessageReceived"
        eventData = _buildEventData("user", "channel", "message")
        self._test_fancyShortcut(hook, event, eventData)


    def test_onPrivateNotice(self):
        hook = self.f.onPrivateNotice
        event = "privateNoticeReceived"
        eventData = _buildEventData("user", "message")
        self._test_fancyShortcut(hook, event, eventData)


    def test_onChannelNotice(self):
        hook = self.f.onChannelNotice
        event = "channelNoticeReceived"
        eventData = _buildEventData("user", "channel", "message")
        self._test_fancyShortcut(hook, event, eventData)


    def test_onUserJoin(self):
        hook = self.f.onUserJoin
        event = "userJoined"
        eventData = _buildEventData("user", "channel")
        self._test_fancyShortcut(hook, event, eventData)


    def test_onUserLeave(self):
        hook = self.f.onUserLeave
        event = "userLeft"
        eventData = _buildEventData("user", "channel")
        self._test_fancyShortcut(hook, event, eventData)


    def test_onUserKicked(self):
        hook = self.f.onUserKick
        event = "userKicked"
        eventData = _buildEventData("kickee", "channel", "kicker", "message")
        self._test_fancyShortcut(hook, event, eventData)



ALL = object()



class ClientTestCase(PanglerCallStubTestCase):
    def setUp(self):
        super(ClientTestCase, self).setUp()
        self.f = irc.FancyInfobarbPangler(self.p)

        self.client = irc.InfobarbClient(self.p)
        self.client.nickname = NICKNAME


    def _test_clientMessage(self, eventData, hook, trigger, expectedKeys=ALL):
        stub = CallStub()
        hook(stub)

        argSpec = self.client._builtinEventArgs[trigger.eventName]
        triggerArgs = [eventData[name] for name in argSpec]

        trigger(*triggerArgs)

        if expectedKeys is ALL:
            expectedKeys = eventData.iterkeys()

        expectedData = dict((k, eventData[k]) for k in expectedKeys)
        self.assertEventFired(stub, expectedData)


    def test_privateMessage(self):
        """
        A direct message from a user fires privateMessageReceived.
        """
        eventData = _buildEventData("user", "nickname", "message")

        self._test_clientMessage(eventData=eventData,
                                 hook=self.f.onPrivateMessage,
                                 trigger=self.client.privmsg,
                                 expectedKeys=["user", "message"])


    def test_channelMessage(self):
        """
        A message to a channel fires channelMessageReceived.
        """
        eventData = _buildEventData("user", "channel", "message")

        self._test_clientMessage(eventData=eventData,
                                 hook=self.f.onChannelMessage,
                                 trigger=self.client.privmsg)


    def test_privateNotice(self):
        """
        A direct notice fires privateNoticeReceived.
        """
        eventData = _buildEventData("user", "nickname", "message")

        self._test_clientMessage(eventData=eventData,
                                 hook=self.f.onPrivateNotice,
                                 trigger=self.client.noticed,
                                 expectedKeys=["user", "message"])


    def test_channelNotice(self):
        """
        A notice to a channel fires channelNoticeReceived.
        """
        eventData = _buildEventData("user", "channel", "message")

        self._test_clientMessage(eventData=eventData,
                                 hook=self.f.onChannelNotice,
                                 trigger=self.client.noticed)


    def test_userJoined(self):
        """
        A user joining a channel fires userJoined.
        """
        eventData = _buildEventData("user", "channel")

        self._test_clientMessage(eventData=eventData,
                                 hook=self.f.onUserJoin,
                                 trigger=self.client.userJoined)


    def test_userLeft(self):
        """
        A user leaving a channel fires userLeft.
        """
        eventData = _buildEventData("user", "channel")

        self._test_clientMessage(eventData=eventData,
                                 hook=self.f.onUserLeave,
                                 trigger=self.client.userLeft)


    def test_userQuit(self):
        """
        A user quitting fires userQuit.
        """
        eventData = _buildEventData("user", "quitMessage")

        self._test_clientMessage(eventData=eventData,
                                 hook=self.f.onUserQuit,
                                 trigger=self.client.userQuit)


    def test_userKicked(self):
        """
        A user being kicked fires userKicked.
        """
        eventData = _buildEventData("kickee", "channel", "kicker", "message")

        self._test_clientMessage(eventData=eventData,
                                 hook=self.f.onUserKick,
                                 trigger=self.client.userKicked)
