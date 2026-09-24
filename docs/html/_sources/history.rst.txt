Origin and history of token-utils
=================================

This is likely going to be of very little interest to anyone,
except perhaps for budding programmers who are not sure that
the programming experiments they do are worthwhile. If this is
you, I have a message: **yes**, anything you do for learning
is worthwhile.

.. sidebar:: Note to self?

    As I was writing this documentation, I often felt the need to explain
    why a certain feature of token-utils existed, going into some details
    about the reasoning for it. This lead me, mostly for my own curiosity,
    to try to figure out how it began and evolve. As I was starting to put
    things together, I thought I should write down the full history.

.. error::

    The rest of this document is currently just a "brain dump"
    with various links.

    A coherent text will eventually be written.


Talk about starting to program in 2004, wanting to motivate
my children to learn programming using a desktop application
I created to teach myself Python: `RUR-PLE <https://rur-ple.sourceforge.net/>`_
RUR-PLE eventually supported 8 languages. It has been used (and still is!)
in many schools, including many elementary schools in
Korea with books written by Samsung as
`I reported on my blog <https://aroberge.blogspot.com/2014/03/reeborg-news.html>`_
in 2014. In that same blog post, I announced the creation
of `Reeborg's World <https://reeborg.ca>`_
a significantly improved version of RUR-PLE, running entirely in
a browser, and thus removing the need to install anything on a computer.
Reeborg's World is still very much in use today. Two months later,
I announced the availability of a French version, where the
basic robot commands, such as ``move()``, ``turn_left()``, etc.,
were translated, but the rest was still straight Python.

Somewhere along the way, I added the possibility to write::

    repeat n:
       # code block

as equivalent to::

    for _ in range(n):
       # code block

In 2015, I started to play with import hooks
how to add similar new constructs in Python.

https://aroberge.blogspot.com/2015/10/from-experimental-import-somethingnew.html

In 2018, I started working on `AvantPy <https://aroberge.github.io/avantpy/docs/html/>`_
AvantPy is now defunct as I found out that `Hedy <https://hedy.org/>`_ did such
a much better job at teaching programming using Python-like constructs in
a huge number of human languages.

I wrote token-utils first as a module integrated within
`ideas <https://aroberge.github.io/ideas/docs/html/>`_

Before I completely shelved AvantPy, I started working on
`friendly/friendly-traceback <https://friendly-traceback.github.io/docs/index.html>`_
in 2019.

In 2020, I started working on ideas. I wrote at the time in the readme file

*As I find myself doing a lot of copy/paste/modify on the various import
hooks experiments, including on some published projects such as AvantPy,
I thought it would make sense to create a versatile projects which I could
use as the basis of other projects.  An obvious benefit is that I will
need to fix bugs in a single project.*

I was partly inspired by the following:

In Feb. 21, 2020, on the Python-ideas mailing list,
Andrew Barnert, a Python code developer,
`wrote <https://mail.python.org/archives/list/python-ideas@python.org/message/UNL62EMSNPA5USUS7SCEQZQ63PVP2FDL/>`_:

    *Unfortunately, the boilerplate to write an import hook is more complicated than you’d
    like (and pretty hard to figure out the first time),* **and the support for filtering on the
    token stream (the most obvious way to do this one)**
    *rather than the text stream, AST, or bytecode* **is pretty minimal and clumsy.**
    [emphasis added]


I made some quick progress, and initially created token-utils as a module within it.
When I talked about ideas in a tread on Python-ideas, the same Andrew Barnert

`also wrote <https://mail.python.org/archives/list/python-ideas@python.org/message/2Z2RWUPNBM3BVVL7Q2C3VDRSN5ALDDRB/>`_
to a message writing the following about token-utils
as an existing module within **ideas** :

  *First, one of the parts that always blocked me was coming up with a good way to write
  token-level transformers.
  It looks like you solved that; maybe it’s worth pulling the tokenizer tools out
  into a separate library to post on PyPI separately?*

This motivated me to turn token-utils on its own project available on Pypi.
It quickly become mature and did not change between the end of 2020
and the middle of 2026.


I wrote token-utils first as a module integrated within
`ideas <https://aroberge.github.io/ideas/docs/html/>`_

While **ideas** aims to provide support for all kinds of transformations,
including those that affect the Abstract Syntax Tree or the bytecode,
most transformations deal with exploring alternative syntax that is
not compatible with Python's current syntax defined by its
`grammar <https://docs.python.org/3/reference/grammar.html>`_.
Such alternative syntax cannot be parsed by Python without generating
a ``SyntaxError`` thus preventing the execution of the code.
For this reason, almost all of our examples transform the code
prior to letting Python parse it.  We do this using a set of tools
built upon Python's `tokenize module <https://docs.python.org/3/library/tokenize.html>`_.


In the meantime, I incorporated a version of it (rather than having it as an external requirement)
within friendly/friendly-traceback where I focused on adding methods and functions
not focused on code-transformation, but rather in helping replace the dreaded
``SyntaxError: invalid syntax`` by more appropriate and helpful description of
the exact cause of the problem and offering possible solutions.

