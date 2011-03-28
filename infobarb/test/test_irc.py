"""
Tests for the IRC abstraction.
"""
from twisted.trial import unittest

from infobarb.irc import FancyInfobarbPangler, InfobarbClient


class CallStub(object):
    def __init__(self):
        self.called = False
        self.calledWith = (), {}


    def __call__(self, *args, **kwargs):
        self.called = True
        self.calledWith = args, kwargs



class PanglerCallStubTestCase(unittest.TestCase):
    """
    A test case that verifies if a pangler called a stub.
    """
    p = FancyInfobarbPangler()

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



_SAMPLE_DATA = {
    "user": "lvh",
    "channel": "#python",
    "message": "hi"
}


def _buildEventData(*keys):
    return dict((k, _SAMPLE_DATA[k]) for k in keys)



class FancyInfobarbPanglerTestCase(PanglerCallStubTestCase):
    """
    Tests that the event hook shortcuts provided by FancyInfobobPangler work.
    """
    def _test_fancyShortcut(self, hook, event, eventData):
        hooks = [hook, hook()] # Hook should work directly and as a decorator

        for hook in hooks:
            stub = CallStub()
            hook(stub)
            self.p.trigger(event=event, **eventData)
            self.assertEventFired(stub, eventData)
                

    def test_onPrivateMessage(self):
        hook = self.p.onPrivateMessage
        event = "privateMessageReceived"
        eventData = _buildEventData("user", "message")
        self._test_fancyShortcut(hook, event, eventData)


    def test_onChannelMessage(self):
        hook = self.p.onChannelMessage
        event = "channelMessageReceived"
        eventData = _buildEventData("user", "channel", "message")
        self._test_fancyShortcut(hook, event, eventData)


    def test_onPrivateNotice(self):
        hook = self.p.onPrivateNotice
        event = "privateNoticeReceived"
        eventData = _buildEventData("user", "message")
        self._test_fancyShortcut(hook, event, eventData)


    def test_onChannelNotice(self):
        hook = self.p.onChannelNotice
        event = "channelNoticeReceived"
        eventData = _buildEventData("user", "channel", "message")
        self._test_fancyShortcut(hook, event, eventData)


    def test_onUserJoin(self):
        hook = self.p.onUserJoin
        event = "userJoined"
        eventData = _buildEventData("user", "channel")
        self._test_fancyShortcut(hook, event, eventData)



ALL = object()



class ClientTestCase(PanglerCallStubTestCase):
    def setUp(self):
        super(ClientTestCase, self).setUp()

        self.client = InfobarbClient(self.p)
        self.client.nickname = "testbarb"


    def _test_clientMessage(self, hook, trigger, event, expectedKeys=ALL):
        stub = CallStub()
        hook(stub)

        trigger(**event)

        if expectedKeys == ALL:
            expectedKeys = event.iterkeys()

        expectedData = dict((k, event[k]) for k in expectedKeys)
        self.assertEventFired(stub, expectedData)


    def test_privateMessage(self):
        """
        A direct message from a user fires privateMessageReceived.
        """
        event = _buildEventData("user", "message")
        event["channel"] = self.client.nickname

        self._test_clientMessage(hook=self.p.onPrivateMessage,
                                 trigger=self.client.privmsg,
                                 event=event,
                                 expectedKeys=["user", "message"])


    def test_channelMessage(self):
        """
        A message to a channel fires channelMessageReceived.
        """
        event = _buildEventData("user", "channel", "message")

        self._test_clientMessage(hook=self.p.onChannelMessage,
                                 trigger=self.client.privmsg,
                                 event=event)


    def test_privateNotice(self):
        """
        A direct notice fires privateNoticeReceived.
        """
        event = _buildEventData("user", "message")
        event["channel"] = self.client.nickname

        self._test_clientMessage(hook=self.p.onPrivateNotice,
                                 trigger=self.client.noticed,
                                 event=event,
                                 expectedKeys=["user", "message"])


    def test_channelNotice(self):
        """
        A notice to a channel fires channelNoticeReceived.
        """
        event = _buildEventData("user", "channel", "message")

        self._test_clientMessage(hook=self.p.onChannelNotice,
                                 trigger=self.client.noticed,
                                 event=event)


    def test_userJoined(self):
        """
        A user joining a channel fires userJoined.
        """
        event = _buildEventData("user", "channel")

        self._test_clientMessage(hook=self.p.onUserJoin,
                                 trigger=self.client.userJoined,
                                 event=event)
