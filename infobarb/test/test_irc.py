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
        eventData = {"user": "lvh", "message": "hi"}
        self._test_fancyShortcut(hook, event, eventData)


    def test_onChannelMessage(self):
        hook = self.p.onChannelMessage
        event = "channelMessageReceived"
        eventData = {"user": "lvh", "channel": "#python", "message": "hi"}
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
            expectedKeys = event.keys()

        expectedData = dict((k, event[k]) for k in expectedKeys)
        self.assertEventFired(stub, expectedData)


    def test_privateMessage(self):
        """
        A privmsg IRC message from a user fires a privateMessage event.
        """
        event = {
            "user": "lvh",
            "channel": "testbarb",
            "message": "hello, testbarb!"
        }

        self._test_clientMessage(hook=self.p.onPrivateMessage,
                                 trigger=self.client.privmsg,
                                 event=event,
                                 expectedKeys=["user", "message"])


    def test_channelMessage(self):
        """
        A privmsg IRC message from a channel fires a channelMessage event.
        """
        event = {
            "user": "lvh",
            "channel": "#python",
            "message": "Use Twisted."
        }

        self._test_clientMessage(hook=self.p.onChannelMessage,
                                 trigger=self.client.privmsg,
                                 event=event)
