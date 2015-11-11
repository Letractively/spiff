# Spiff for End Users #

Spiff is a CMS with desktop integration features that make it easy for Joe User to install and maintain his website, blog, share his calendar with others, and make his media files available on the Internet.

For more information please check our [homepage](http://spiff.debain.org/).

# Spiff for Developers #

Spiff aims to implement a collection of libraries for Python that are generally needed in enterprise (web) environments, as well as tools and libraries for building software development management related applications. As a test case we also implement a CMS on top of those libraries.

  * **We value generalized, componentized software.** Spiff is built out of highly decoupled components and we make our design decisions very carefully.
  * **We build on top of existing solutions and open protocols** if available.
  * **We put the user first.** If an existing product or protocol can not provide the best-possible user experience, we are not afraid to invent our own solution.
  * **We code for fun,** and we code whenever we feel like it. Deadlines are not fun and they have the potential to lower code quality, so we decidedly do not have a roadmap. However, luckily we believe that results are also fun, so you can expect progress. There is also a [TODO file](http://spiff.googlecode.com/svn/trunk/TODO) and some clues on the progress in the tables below.

## Project Help Wanted! ##

Spiff is built by people like you. We simply come and write code, and contribute it for a common cause. We are always looking for people who join our mission to build a really simple and powerful platform and CMS:

  * **Python developers** can [check out the code](http://code.google.com/p/spiff/source) and [submit patches](http://code.google.com/p/spiff/issues/entry),
  * **XHTML writers and Javascript (AJAX) developers** can improve the HTML templates.
  * **Graphic designers** can provide high quality artwork.
  * **Usability engineers** can help to make the user interface even more intuitive.
  * **Testers** can install the software, [tell us about it](http://groups.google.com/group/spiff-devel) or [file bugs](http://code.google.com/p/spiff/issues/entry).

## Architecture ##

  * Spiff stores its data in a database and access is abstracted through the excellent [SQL Alchemy](http://www.sqlalchemy.org/) library. However, we currently test only using MySQL.

  * Spiff-generated HTML output is rendered using [Genshi](http://genshi.edgewall.org/), a stream based output generator. User-entered data is rendered through our own solution for generating HTML from WikiMarkup, using the [Spiff WikiMarkup library](http://spiff.googlecode.com/svn/trunk/libs/WikiMarkup/README).

  * **The center part of Spiff is Spiff Integrator**, a solution that is in some ways comparable to Debian's dpkg. Integrator manages installed components and ensures that dependencies between them are met at any given time. Unlike dpkg however, it also provides a facility over which these components can interact with each other. For more information regarding Spiff Integrator, look [here](http://spiff.googlecode.com/svn/trunk/libs/Integrator/README).

  * Spiff also provides a **very powerful user and group management**. This is implemented in our generic access list library, Spiff Guard. For information regarding Spiff Guard, look [here](http://spiff.googlecode.com/svn/trunk/libs/Guard/README).


## Current Spiff Components ##

| **Component** | **Description** | **Status** |
|:--------------|:----------------|:-----------|
|[Spiff Guard](http://code.google.com/p/spiff-guard/) [[Release](http://www.python.org/pypi/Spiff%20Guard)] [[Docs](http://docs.debain.org/spiff_guard/)]|Generic Access Lists for Python|Completed   |
|[Spiff Constructor](http://spiff.googlecode.com/svn/trunk/libs/Constructor/)|Installing Python applications|Basic functionality ready|
|[Spiff Integrator](http://code.google.com/p/spiff-integrator/) [[Release](http://www.python.org/pypi/Spiff%20Integrator)] [[Docs](http://docs.debain.org/spiff_integrator/)]|Add plugin support to any Python application|Completed   |
|[Spiff WikiMarkup](http://code.google.com/p/spiff-wikimarkup/) [[Release](http://www.python.org/pypi/Spiff%20WikiMarkup)]|A wiki markup 

&lt;-&gt;

 HTML converter|Completed   |
|[Spiff Warehouse](http://spiff.googlecode.com/svn/trunk/libs/Warehouse/) [[Release](http://www.python.org/pypi/Spiff%20Warehouse)]|A database for storing revisioned files|Completed   |
|[Spiff Workflow](http://code.google.com/p/spiff-workflow/) [[Release](http://www.python.org/pypi/Spiff%20Workflow)]|A library for implementing workflows based on [Workflow Patterns](http://www.workflowpatterns.com/)|90% complete|