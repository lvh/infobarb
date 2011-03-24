==============
 Introduction
==============

The ``#python`` IRC channel on Freenode has had a bot called infobob
for a long time. Although it certainly served its purpose, there were
a few implementation issues that made it unpleasant to work on.
Additionally, some new software came along that we wanted to use in
our new IRC bot.

At its heart, infobarb is little more than an abstraction layer over
IRC. Instead of receiving IRC protocol messages, infobarb components
receive more abstracted events. These events are provided by
Panglery_.

.. _Panglery: https://github.com/habnabit/panglery

Instances of infobarb are supposed to be persistent. This is
accomplished using Axiom_, which uses SQLite_ internally. Each plugin
instance gets its own Axiom store, and gets the same store back every
time it is instantiated.

.. _Axiom: http://pypi.python.org/pypi/Axiom
.. _SQLite: http://www.sqlite.org

The vast majority of behavior in infobarb instances is provided by
individual plugins. These can be reloaded on the fly because of
Exocet_, a novel module system for Python written by Allen Short.

.. _Exocet: https://launchpad.net/exocet
