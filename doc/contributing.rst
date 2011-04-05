==============
 Contributing
==============

Contributing to infobarb is easy and fun! Well, it should be, at least. If it
wasn't as good for you as it was for us, you should probably tell us what part
of the process made you unhappy so we can fix it.

Style guide
===========

Like most decent projects, infobarb has a mandatory style guide for
contributions. Since it's built on top of Twisted_, the default go-to document
for style matters is the `Twisted coding standard`_. Like the Twisted coding
standard, `PEP 8`_ is the fallback in case something is unclear.

.. _Twisted: http://www.twistedmatrix.com/ 
.. _`Twisted coding standard`: http://twistedmatrix.com/documents/current/core/development/policy/coding-standard.html
.. _`PEP 8`: http://www.python.org/dev/peps/pep-0008/

Tests
=====

This project believes very strongly in tests. The ``master`` should have full
test coverage at all times.

Of course, full test coverage doesn't mean your software doesn't have any bugs
in it. This is why bugs require a failing unit test first, and should /not/
get fixed without one.
