# A Practical Introduction to Databases

Author: Christopher Painter-Wakefield
License: CC BY-SA 4.0


## Chapter: sql-basics.rst

.. _basics-chapter:

======
Basics
======

Part 1 of this book is all about SQL, the most popular language used for interacting with *relational databases*, the main focus of the book. The goal of this chapter is to introduce the most simple features of relational databases and SQL.  You will learn how to get data out of the database, and how to get data into the database, and how to use this textbook's interactive features.


.. index::
    single: database; defined
    single: database management system
    single: DBMS
    single: database system

Databases and database systems
::::::::::::::::::::::::::::::

Before we start, we should define these two terms:

database
    An organized collection of data.

database management system (DBMS)
    The software that manages the storage of data in a database and provides facilities for searching, retrieving, and modifying data in a database.

The word "database" is frequently used as shorthand to mean both a database and the DBMS managing it, and both usages can be found in this textbook.  Also, "database system" is generally used as a synonym for DBMS.


.. index::
    single: table; defined
    single: column; defined
    single: row

Tables
::::::

While relational databases can contain many types of *objects*, the object type that stores data is the *table*.  Each table in the database has a name, which usually provides some indication of what kind of data can be found in the table.  The table structure is defined by the table's *columns*, each of which has a name and an associated data type.  The actual data is contained in the *rows* of the table; each row is one data point and has a value for each column of the table.

We can visualize a simple table as, well, a table:

.. image:: table_illustration.svg
    :alt: Illustration of a table

The illustration above shows a table named "fruit_stand" with three columns named "item", "price", and "unit".  Although the illustration does not show the data types, we might infer that the **item** and **unit** columns contain text and the **price** column contains decimal numbers.  Each row of **fruit_stand** contains information about one kind of fruit sold at the fruit stand.


.. index:: SQL, Structured Query Language, query language, statement, query

Structured Query Language (SQL)
:::::::::::::::::::::::::::::::

An important characteristic of modern databases is that they abstract low-level operations on files, tables, indexes and so forth into high-level requests to the database management system.  Requests to the database are typically expressed in a *query language*.  Query languages are a type of programming language, but are different from most in that query languages tend to be declarative rather than imperative.  Whereas imperative languages require the programmer to specify exactly what steps to take to perform a task, declarative languages simply describe a desired outcome.

Structured query language (SQL) is the most popular query language for relational databases, and is an example of a declarative language.  SQL was developed by engineers at IBM in the 1970s and was standardized by standards organizations ANSI and ISO in 1986, with regular updates following.  New features continue to be added to SQL as relational database technology and applications evolve.

Even though a standard exists for SQL, relational databases have slightly different implementations of the relational model, and similarly different "dialects" of SQL.  Despite these differences, most SQL dialects share enough in common that, with care, highly portable SQL code can be written.  Examples in this textbook use the SQLite database engine, and thus the dialect of SQL used by SQLite.  To the extent possible, however, examples will be portable to other dialects; differences between implementations will be noted where significant.  Due to the large number of relational DBMSes available, only a few highly popular DBMSes are included:  SQLite, PostgreSQL, MySQL, Oracle, and Microsoft SQL Server.

SQLite examples can be run directly inside this online textbook (more on this below).  :ref:`Appendix A <appendix-a>` provides SQL scripts to create the database used in this book for each of the database engines listed above.

..
  .. index::
      see: DQL; data query language
      single: data query language
      see: DML; data manipulation language
      single: data manipulation language
      see: DDL; data definition language
      single: data definition language
      see: DCL; data control language
      single: data control language

  SQL is sometimes subdivided into smaller languages focused on particular tasks: a data query language (DQL) for retrieving data, a data manipulation language (DML) for modifying data, a data definition language (DDL) for defining and modifying database objects, and a data control language (DCL) for managing authorization and access to data.  These distinctions are largely unimportant, and will not be used in this textbook.

The basic element of SQL is the *statement* or *query*.  While a distinction can be made between these two (statements act to change the state of the database, while queries act to retrieve data), it is common to use the terms interchangeably.  Statements in SQL read much like English sentences, although with very strict rules.

SQL is often pronounced as "sequel", although it is equally valid to simply say each letter.


.. index:: SELECT, FROM, clause, data; retrieving

Retrieving data using SELECT
::::::::::::::::::::::::::::

In its simplest form, the **SELECT** statement can be used to retrieve all data from a table.  We just need to know the table name:

::

    SELECT * FROM fruit_stand;

Here, **fruit_stand** is the name of the table.  The **\*** is a special symbol used with **SELECT** statements to mean "all columns in the table".  The table **fruit_stand** is one table in the example database for this textbook. The interactive example below will let you query this database; the query above is already set up for you - click on "Run" to see its results.  The column names for the table are shown across the top of the result table.

.. activecode:: sql_basics_example_select
    :language: sql
    :dburl: /_static/textbook.sqlite3

    SELECT * FROM fruit_stand;

The statement (or query) above is said to have two *clauses*; a clause is a part of a SQL statement, usually starting with a SQL keyword.  The two clauses in the statement above are the **SELECT** clause, "SELECT \*" and the **FROM** clause, "FROM fruit_stand".  Most clauses are optional in the sense that they are not required in every query, although they will be necessary to produce certain desired results.

Retrieving specific columns
---------------------------

Above, we retrieved all columns of a table, which may not be the desired result.  We can specify the columns we wish to retrieve, and in what order, by replacing the **\*** in our **SELECT** clause with a comma-separated list of columns:

::

    SELECT price, item FROM fruit_stand;

You can paste this new query into the interactive tool above to see its result.

Looking ahead
-------------

There is a lot more we can do with a **SELECT** query, which will be explored in future chapters.  In :numref:`Chapter {number} <data-retrieval-chapter>`, we will discuss basic usage of **SELECT**, including how to retrieve specific subsets of rows and how to sort rows.  In :numref:`Chapter {number} <expressions-chapter>`, we will delve deeper into the types of values and expressions you can use in SQL queries.  In :numref:`Chapter {number} <joins-chapter>`, we look at connecting multiple tables in a query to retrieve more complex results.  Even more advanced topics will be explored in later chapters.


Creating tables and adding data
:::::::::::::::::::::::::::::::

Of course, before you can retrieve data from a database, you need to put data into it.  First, we need to define a table structure.  We do this with a **CREATE TABLE** statement.  The **fruit_stand** table above was created using this statement:

::

    CREATE TABLE fruit_stand (
      item TEXT,
      price NUMERIC,
      unit TEXT
    );

When defining a table in SQL, you list the columns you want, giving the name and the data type of the column.  Try creating a new table, **my_purchase**, in the database using the interactive tool below:

.. activecode:: sql_basics_example_create
    :language: sql
    :dburl: /_static/textbook.sqlite3

    CREATE TABLE my_purchase (
      item TEXT,
      quantity NUMERIC,
      total_price NUMERIC
    );

As soon as you create this table, you can query it using **SELECT**.  However, there will not be any data in the table yet.  To add data to the table, use **INSERT** statements:

::

    INSERT INTO my_purchase VALUES ('apple', 2, 6.98);
    INSERT INTO my_purchase VALUES ('melon', 1, 0.89);

Try adding some data to the **my_purchase** table, and then retrieve it using **SELECT**.  You can also add data to the **fruit_stand** table, or try creating your own tables and adding data to them.  Be sure to use single quotes around any string values you put into a table.

We should note, at this point, that the data types we have used here are not standard SQL.  They are supported by SQLite, the database implementation used in this online textbook. We have used them here for simplicity, but a full discussion of SQL data types and table creation will have to wait until :numref:`Chapter {number} <table-creation-chapter>`.

Looking ahead
-------------

Table definitions can include much more than simple lists of columns.  We will discuss the complexities of table construction in :numref:`Chapter {number} <table-creation-chapter>`.  Likewise, above we only showed the most basic form of the **INSERT** statement.  We will discuss **INSERT** in more detail in :numref:`Chapter {number} <data-modification-chapter>`; in the same chapter, we will discuss how to remove rows from a table and how to modify row data.


SQL statement rules and conventions
:::::::::::::::::::::::::::::::::::

First, note that SQL statements are properly terminated by semicolons.  In some software tools, single statements are allowed to be unterminated - this is true in our interactive examples, in fact.  However, we will always show the semicolon in our examples, as they become very important in settings where you want to send a list of statements to the database at one time.

One implication of this is that it is entirely permissible and (in many cases preferable, as in our **CREATE TABLE** examples) to write statements on multiple lines.  The query below is correct, and equivalent to the same query expressed all on one line:

::

    SELECT *
    FROM fruit_stand;

Next, SQL keywords are case-insensitive.  That is, we can write:

::

    select * from fruit_stand;
    Select * From fruit_stand;
    select * FROM fruit_stand;

and get the same result for each query.  In the examples in this book, the convention is that SQL keywords will be capitalized.

To some extent, the names of things (tables, columns, functions, etc.) also act as if they are case-insensitive.  However, the behavior here varies among databases.  We will explore more on this topic in :numref:`Chapter {number} <joins-chapter>`.  A fairly common convention is to always put the names of things in lowercase.  The examples in this book will follow that convention, which will help distinguish keywords from things that exist in the database.

Note that the conventions used in this textbook may be different from those used by your teacher, at your place of work, or in code found on the internet!

.. index:: comments


Comments
::::::::

SQL provides for two types of comments, which we will occasionally use to annotate queries in this book.  Any text between `/*` and `*/` forms a multi-line comment.  Single-line comments start with two dashes.  Here is a query using both types of comment:

::

    SELECT *
    /* here is a
       multi-line comment */
    FROM      -- single-line comment
      fruit_stand;


Interactive examples
::::::::::::::::::::

The interactive tools in this chapter are all connected to the same database, which is the example database that will be used throughout the book. If you make a table, or modify data, you can see the result of the changes in any interactive tool on the same page.  It is important to note, however, that you are just working with a copy of the database that is created and loaded into your web browser whenever you view the page.  Any changes you make will disappear as soon as you go to another chapter in the book or close your web browser.

The good news is that this means you can experiment as much as you want with the book's database - you cannot harm anything.  We strongly encourage you to try all of the examples, as well as to try out your own ideas.  The more time you spend "playing" in the database, the more you will learn.

The bad news is that any queries you create will disappear when you leave the page.  If you work on anything complex, or anything that you want to return to, you may want to copy it to a separate document on your computer.  You can also save code in the "Scratch ActiveCode" tool - click on the pencil at the top of the page to get to the tool.  Note that the scratch tool is not connected to the same database, but instead uses an empty database.

As you work through this textbook, there will be frequent interactive examples based on various tables in the database.  The available tables are described in more detail in :ref:`Appendix A <appendix-a>`.  You can also query the database to learn about its tables.  To get a list of available tables, execute the query:

.. activecode:: sql_basics_example_catalog
    :language: sql
    :dburl: /_static/textbook.sqlite3

    SELECT name FROM sqlite_master WHERE type = 'table';

You can see the table definition in addition to the name if you do

::

    SELECT name, sql FROM sqlite_master WHERE type = 'table';

|chapter-end|

|license-notice|



## Chapter: data-retrieval.rst

.. _data-retrieval-chapter:

==============
Data retrieval
==============

In this chapter, you will learn more about **SELECT** queries, including how to retrieve specific rows and how to sort the output.


Tables used in this chapter
:::::::::::::::::::::::::::

We will be working with the **simple_books** and **simple_authors** tables for this chapter.  As the names suggest, these are smaller, simplified versions of other tables we will work with later in the book, and the data concerns books and their authors.  You can read a full explanation of these tables in :ref:`Appendix A <appendix-a>`, but for now we recommend simply using a **SELECT** query to view all of the data in these two tables.  Here is an interactive tool you can use for that purpose:

.. activecode:: data_retrieval_example_tables
    :language: sql
    :dburl: /_static/textbook.sqlite3

    SELECT * FROM simple_books;

Remember from the previous chapter that you can **SELECT** \* to retrieve all columns, or you can specify the columns you want:

::

    SELECT author, title FROM simple_books;


.. index:: WHERE

Filtering rows: the WHERE clause
::::::::::::::::::::::::::::::::

Retrieving all of the data from a table is useful, but often not what we want, especially if the table is very large (and tables can get very, very large!)  To see just a subset of rows, we include a **WHERE** clause in our query.  The **WHERE** clause consists of the keyword **WHERE** followed by an *expression* that evaluates to true or false (a Boolean expression). [#]_  The **WHERE** clause is placed after the **FROM** clause.  Expressions are discussed more in :numref:`Chapter {number} <expressions-chapter>`, but for now, let's see some simple examples:

.. activecode:: data_retrieval_example_where
    :language: sql
    :dburl: /_static/textbook.sqlite3

    SELECT * FROM simple_books WHERE author = 'Isabel Allende';

    SELECT author, title, genre
    FROM simple_books
    WHERE publication_year > 1999;

    SELECT birth, death
    FROM simple_authors
    WHERE name = 'Ralph Ellison';

Note that character string literals in SQL are enclosed with single quotes - not double quotes.  Double quotes are used in SQL for a different purpose, which we'll see in :numref:`Chapter {number} <joins-chapter>`.

Queries can return zero, one, or many rows.  If no rows match the **WHERE** condition, zero rows are returned (try pasting this in one of the interactive tools above):

::

    SELECT * FROM simple_books WHERE genre = 'romance';


.. index:: ORDER BY, DESC, ASC

Ordering data: the ORDER BY clause
::::::::::::::::::::::::::::::::::

One surprising fact about relational databases is that the rows in a table are not necessarily ordered in any particular fashion.  In fact, relational DBMSes (RDBMSes) are permitted to store data in whatever fashion is most convenient or efficient, as well as to retrieve data however is most convenient.  For example, in many RDBMSes, data may be initially in the order in which it was added to the table, but a subsequent data modification statement results in the data being re-ordered.

SQL provides a mechanism by which we can put rows in order by whatever criteria we wish.  This is accomplished via the **ORDER BY** clause, which always comes last in any query.  The key phrase **ORDER BY** is followed by a comma-separated list of expressions, which must evaluate to some type that can be put in order: numbers, character strings, dates, etc.  By default, numbers are sorted from smallest to largest, and dates from earliest to latest.  Character strings are a bit trickier, because different databases order them differently. [#]_ SQLite, the dialect we are using, defaults to `lexicographic ordering <https://en.wikipedia.org/wiki/Lexicographic_order>`_ based on `ASCII <https://en.wikipedia.org/wiki/ASCII>`_ values.

Here are some simple queries to try:

.. activecode:: data_retrieval_example_order_by
    :language: sql
    :dburl: /_static/textbook.sqlite3

    SELECT * FROM simple_books ORDER BY publication_year;

    SELECT * FROM simple_authors ORDER BY birth;


Ordering is initially applied using the first expression after the **ORDER BY** keyword.  If any two rows are equal according to that first expression, and there are additional expressions in the **ORDER BY** clause, the next expression is then applied to groups of rows that have equal values for the first expression, and so forth.  For example, suppose you are organizing books for a library or bookstore where books are grouped by genre and then alphabetized by title.  You could write the following query to help with this task:

::

    SELECT author, title, genre
    FROM simple_books
    ORDER BY genre, title;

It is also possible to reverse the ordering for any or all of the criteria using the **DESC** ("descending") keyword.  (You can also use **ASC** for "ascending", but, as that is the default, it is usually omitted.)  If we want to see all books listed from most recent to least recent, we can write:

::

    SELECT * FROM simple_books ORDER BY publication_year DESC;


.. index:: DISTINCT, uniqueness

Retrieving unique rows: the DISTINCT keyword
::::::::::::::::::::::::::::::::::::::::::::

As we will see in later chapters, it is usually good practice to set up database tables in such as way that each record in the table is unique; that is, for each row, there will be no other row in the table that contains exactly the same data in every column.

However, queries that **SELECT** a subset of the columns of a table can easily end up with duplicate results; this may or may not be desired.  Suppose you were interested in browsing the books in our database for particular genres of books, but you weren't sure what genres the database puts books into - that is, you need to determine what would be valid choices given the data.

You could simply run the query:

.. activecode:: data_retrieval_example_distinct
    :language: sql
    :dburl: /_static/textbook.sqlite3

    SELECT genre FROM simple_books;

For this small collection of books, that would probably be fine - there are duplicate values, but we can pretty quickly come up with a unique set.  However, a real database of books could contain many thousands of books.  You wouldn't want to browse that many rows to discover the possible genres!

SQL provides a keyword, **DISTINCT**, that can be added after the **SELECT** keyword and tells SQL that we only want unique results, and if there are duplicates, it should discard them.  This will give us the desired result, a unique set of genres that we can choose from:

::

    SELECT DISTINCT genre FROM simple_books;


Self-check exercises
::::::::::::::::::::

This section contains some simple exercises using the **simple_books** and **simple_authors** tables used in the text above.  If you get stuck, click on the "Show answer" button below the exercise to see a correct answer.

.. activecode:: data_retrieval_self_test_select
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Modify the SQL statement below to retrieve author names only.
    ~~~~
    SELECT * FROM simple_authors;

.. reveal:: data_retrieval_self_test_select_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT name FROM simple_authors;


.. activecode:: data_retrieval_self_test_where1
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query to find all books in the science fiction genre.
    ~~~~


.. reveal:: data_retrieval_self_test_where1_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT * FROM simple_books WHERE genre = 'science fiction';


.. activecode:: data_retrieval_self_test_where2
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query to find the publication year and author for the book *Bodega Dreams*.
    ~~~~


.. reveal:: data_retrieval_self_test_where2_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT publication_year, author
        FROM simple_books
        WHERE title = 'Bodega Dreams';


.. activecode:: data_retrieval_self_test_where3
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query to find all books published prior to 1950.
    ~~~~


.. reveal:: data_retrieval_self_test_where3_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT * FROM simple_books WHERE publication_year < 1950;


.. activecode:: data_retrieval_self_test_order
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query to get books in order by title.
    ~~~~


.. reveal:: data_retrieval_self_test_order_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT * FROM simple_books ORDER BY title;


.. activecode:: data_retrieval_self_test_challenge1
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query to get the authors publishing since 1980, in order by author name.
    ~~~~


.. reveal:: data_retrieval_self_test_challenge1_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT author
        FROM simple_books
        WHERE publication_year > 1979
        ORDER BY author;


.. activecode:: data_retrieval_self_test_challenge2
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query to get the unique publication years for the books in our database published since 1980, ordered latest to earliest.
    ~~~~


.. reveal:: data_retrieval_self_test_challenge2_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT DISTINCT publication_year
        FROM simple_books
        WHERE publication_year > 1979
        ORDER BY publication_year DESC;


|chapter-end|

----

**Notes**

.. [#] There is actually a third possible value, ``NULL``, which may occur in expressions used in the **WHERE** clause of a query.  ``NULL`` is a complex topic which will be covered in :numref:`Chapter {number} <expressions-chapter>`.  For now, assume a normal Boolean result of true or false.

.. [#] You can change the sort order for strings by applying the **COLLATE** operator. **COLLATE** is out of scope for this textbook, and varies with the dialect of SQL.  Please see the documentation for your particular DBMS.


|license-notice|



## Chapter: expressions.rst

.. _expressions-chapter:

===========
Expressions
===========

.. index:: expression

An *expression* in SQL is a thing that can be *evaluated* - anything that results in a value.  Some examples include literal values, operator expressions, and function call expressions.  Expressions are used in most clauses of a SQL query; for example, in the **SELECT** clause, expressions result in the values we see returned from the query, while in the **WHERE** clause, expressions determine whether or not a row is returned from the query.  You can also **ORDER BY** expressions, and later we will see other uses for expressions.  This chapter will explore some of the most common expression types; additional expressions will be introduced in later chapters.

Tables used in this chapter
:::::::::::::::::::::::::::

We will again be working with the **simple_books** and **simple_authors** tables for this chapter.  Reminder: you can read a full explanation of these tables in :ref:`Appendix A <appendix-a>`.


.. index:: column expression

Column expressions
::::::::::::::::::

The use of a column name in a SQL statement produces a special expression which evaluates to the value stored in that column for the current row being processed.  So, when we run

.. activecode:: expressions_example_column
    :language: sql
    :dburl: /_static/textbook.sqlite3

    SELECT *
    FROM simple_books
    WHERE author = 'J.R.R. Tolkien';

the query execution examines each row of the table **simple_books** in turn to evaluate the expression ``author = 'J.R.R. Tolkien'``.  This expression compares the value of the **author** column to the literal value ``'J.R.R. Tolkien'`` using the **=** operator.  If the two are the same, the overall expression evaluates to ``True``, and the row is included in the output; otherwise, the row is excluded.


.. index:: literal; number, literal; character string, literal; Boolean

Literals
::::::::

Literals are simple values expressed in a form that the database recognizes and understands.  There are only a few basic types of literals in SQL, although these can be converted to many different types within a database.  We will discuss SQL data types further in :numref:`Chapter {number} <table-creation-chapter>`.  The main literals you will encounter are:

- Numbers: these are expressed in the usual fashion, for example, ``-1``, ``3.14159``, ``0.0008``. Depending on the database, you may also be able to use numeric literals in scientific notation or other formats, for instance, ``6.02e23`` (which stands for :math:`6.02 \times 10^{23}`).
- Character strings: these are strings of characters enclosed in single quotes, for example, ``'apple'``.  If you need to express a literal character string which contains a single quote, you simply write the single quote twice; this is tricky to read, but produces the desired result.  This is shown in the following query:

.. activecode:: expressions_example_literal
    :language: sql
    :dburl: /_static/textbook.sqlite3

    SELECT author FROM simple_books
    WHERE title = 'The Handmaid''s Tale';

- Boolean values: ``True`` or ``False``.  Note, however, that not all SQL implementations support Boolean literals.
- Date and time values. The accepted notations for dates and times vary widely among different SQL implementations.
- The special value ``NULL``. We will talk more about ``NULL`` below.

You can ask for literal expressions in the **SELECT** clause - this is sometimes useful.  In this case, the literal is evaluated as itself for each row in the table you are querying.  For example:

::

    SELECT 42, 'hello', author FROM simple_books;

If you try this query in the interactive tool above, note that the output provides column names based on the literal expressions selected.  Later we will see how to change the names of columns in the output if we want to make them more meaningful.


Operators and functions
:::::::::::::::::::::::

SQL defines a number of useful operations on its various types.  Some of these use simple operators, as in mathematical expressions, while others take the form of functions.  :ref:`Appendix B <appendix-b>` provides extensive lists of the operators and functions defined by the SQL standard, but we will discuss some of the most commonly used ones here, along with examples of their use.


.. index:: operator; comparison

Comparison operators
--------------------

We've already seen the equality operator (**=**) used to test if some column is equal to a literal value in the **WHERE** clause of queries.  We could instead test for inequality using the (**<>**) operator:

.. activecode:: expressions_example_comparison
    :language: sql
    :dburl: /_static/textbook.sqlite3

    SELECT * FROM simple_books WHERE genre <> 'fantasy';

Though it is non-standard, most databases also recognize **!=** as an inequality operator.  (Note that SQL does not use **==**, which is used to test for equality in many programming languages.  While SQLite does recognize it as an equality comparison operator, **do not use it**, as it will be a difficult habit to break.)

We can also test to see if a value is less than (**\<**), greater than (**\>**), less than or equal to (**\<=**), or greater than or equal to (**\>=**) some other value.  There is also a ternary operator, **BETWEEN**, that tests if a value is between two other values (see Appendix B - :ref:`appendix-b-comparison-operators` for details).


.. index:: operator; mathematics, function; mathematics

Mathematics
-----------

You can expect the basic arithmetic operators to work with any numeric values: addition (**+**), subtraction (**-**), multiplication (**\***), and division (**/**) are standard.  Your database may implement others, but make sure you read the documentation for your database to ensure other operators do what you think they do.  You can actually use your database as a simple calculator!  Try running these:

.. activecode:: expressions_example_math
    :language: sql
    :dburl: /_static/textbook.sqlite3

    SELECT 4 + 7;
    SELECT 302.78 * 14;

(Note for Oracle users: Oracle requires all **SELECT** queries to have a **FROM** clause, so the special table **dual** is provided for queries that use no columns and return one row.  Thus, use ``SELECT 4 + 7 FROM dual;`` in Oracle.)

The SQL standard additionally provides functions for many useful mathematical operations, such as logarithms (**log**, **ln**, **log10**), exponentials (**exp**), square root (**sqrt**), modulus (**mod**), floor and ceiling (**floor**, **ceiling** or **ceil**), trigonometric functions (**sin**, **cos**, etc.), and more.  Some examples:

::

    SELECT sqrt(3);
    SELECT log10(1e5);
    SELECT cos(0);

You will most likely find yourself using mathematical operators in SQL if you are working with numerical data such as financial or scientific records.  In :numref:`Chapter {number} <table-creation-chapter>` we will discuss some of the different data types available for storing numbers: integers, decimal numbers, and floating point values.  Each has applications to various problems.

As a somewhat contrived example of applying mathematical operators to an actual table, consider the problem of finding out which century a book was published in.  In the English language, the 1st century is traditionally considered to be the years numbered 1 - 100.  Each subsequent 100 years adds 1 to the century, so the 20th century included the years 1901 - 2000.

With a little math, we can extract the century in which each book in our database was published:

::

    SELECT
      title,
      floor((publication_year + 99) / 100) AS century
    FROM simple_books;

Note the use of parentheses to enforce an order of operations: the addition operation occurs before the division, and then the result of the division is provided to the **floor()** function.  We have also introduced something new - a renaming operation to give our result column a more informative name. The **AS** keyword lets us rename a column in the output of our query.  We will learn more about using **AS** in :numref:`Chapter {number} <joins-chapter>`.

See Appendix B - :ref:`appendix-b-math-operators` for a complete list of standard operators and functions.


.. index:: operator; character string, function; character string, string concatenation, LIKE, pattern matching

Character string operators and functions
----------------------------------------

SQL provides two very useful string operators. The operator **||** (two vertical bars) is used for string concatenation.  There are many instances in which we want to append one string to another.  For example, if we do not like the multi-column output from our **simple_books** table, we could use string concatenation to produce a more familiar representation of the data:

.. activecode:: expressions_example_string
    :language: sql
    :dburl: /_static/textbook.sqlite3

    SELECT title || ', by ' || author FROM simple_books;

(Note about implementations: in SQL Server, you will need to use **+** instead of **||**; in MySQL, you will need to use the MySQL **concat** function, e.g. ``SELECT concat(title, ', by ', author) FROM simple_books;``.)

The **LIKE** operator is a Boolean operator that is used almost exclusively in the **WHERE** clause.  **LIKE** provides very simple pattern matching capabilities in SQL.  A *pattern* is just a string that can contain regular text and special *wildcard* characters, which can match one or many unspecified characters.  The two wildcards are **%**, which can match any string of zero or more characters, and **_**, which can match exactly one of any character. Normal text matches itself exactly.  (If you are familiar with standard *regular expression* syntax, the **%** wildcard corresponds to ".*" as used in a regular expression, and the **_** wildcard corresponds to ".".)

Consider the case in which we recall the first name of an author, but not the full name, and wish to look up authors with that first name.  The **%** wildcard can be used here to stand in for the unknown part of the name:

::

    SELECT name FROM simple_authors WHERE name LIKE 'Isabel %';

Since the **%** can match any string, the pattern ``'Isabel %'`` would match "Isabel Allende", "Isabel Granada", or "Isabel del Puerto" for example (only one of these is in our **simple_authors** table, though).

Similarly, if we remember the last part of the name, but not the start, we can use the **%** wildcard again:

::

    SELECT name FROM simple_authors WHERE name LIKE '% Ginsberg';

We can even use the wildcard more than once:

::

    SELECT title FROM simple_books WHERE title LIKE '%Earth%';

Now, suppose we are interested in authors who use an initial instead of their full first name.  An initial looks like some single character followed by a period - both are required.  Here's what the query would look like, using both the **%** and **_** wildcards:

::

    SELECT name FROM simple_authors WHERE name LIKE '_.%';

In addition to these operators, SQL provides a number of useful functions that act on character strings.  The functions **upper** and **lower** convert strings to all uppercase or lowercase characters, respectively.  Not all languages distinguish between uppercase and lowercase, of course, so these functions may not be applicable in certain locales.  You can use **upper** or **lower** whenever you want to get back strings in all uppercase or lowercase:

::

    SELECT upper(title), author FROM simple_books;

You can also use them when pattern matching if you aren't sure of the capitalization of the strings in your database:

::

    SELECT * FROM simple_books WHERE lower(title) LIKE '%love%';

SQL also provides functions for tasks such as substring extraction or replacement, finding the location of a substring, trimming whitespace (or other characters) from the front and/or back of a string, and many more.  See Appendix B - :ref:`appendix-b-string-operators` for these.


.. index:: operator; Boolean, AND, OR, NOT

Boolean operators
-----------------

As discussed in :numref:`Chapter {number} <data-retrieval-chapter>`, the **WHERE** clause of a **SELECT** query expects a Boolean expression after the **WHERE** keyword.  Some expressions that are Boolean in SQL include expressions using comparison operators, or an expression using the **LIKE** operator.  Many functions also result in a Boolean value.

SQL provides logical operators that operate on Boolean values.  These operators are **AND**, **OR**, and **NOT**, which perform the logical operations that their names imply.  For example, if we have an expression of the form ``expr1 AND expr2``, the result is ``True`` if and only if both ``expr1`` and ``expr2`` evaluate to ``True``.  Similarly, ``expr1 OR expr2`` evaluates to ``True`` if at least one of ``expr1`` and ``expr2`` are ``True``.  Finally, ``NOT`` inverts the truth value:  ``NOT True`` results in ``False``, and ``NOT False`` results in ``True``.

These logical operators allow us to build up complex Boolean expressions from simpler Boolean expressions to express the particular logical conditions we want for our **WHERE** clause.  So, for example, we might be interested in fantasy books published since the year 2000:

.. activecode:: expressions_example_boolean
    :language: sql
    :dburl: /_static/textbook.sqlite3

    SELECT *
    FROM simple_books
    WHERE genre = 'fantasy' AND publication_year > 2000;

Or, we might be interested in books in either the fantasy or science fiction genres:

::

    SELECT * FROM simple_books
    WHERE genre = 'fantasy' OR genre = 'science fiction';

If we simply hate science fiction, we might write

::

    SELECT * FROM simple_books WHERE NOT genre = 'science fiction';

which gives the same result as

::

    SELECT * FROM simple_books WHERE genre <> 'science fiction';

For more complex expressions involving combinations of **AND**, **OR**, and **NOT**, we may need to use parentheses to make our meaning clear.  In SQL, **NOT** is applied before **AND**, and **AND** is applied before **OR**. For example, perhaps we are interested in any books other than fantasy books published after the year 2000.  We might be tempted to write

::

    SELECT * FROM simple_books
    WHERE NOT genre = 'fantasy' AND publication_year > 2000;

However, this isn't quite right (try it!).  Since the **NOT** is applied first, this query returns books that a) are not fantasy and b) were published since the year 2000.  The expression ``NOT genre = 'fantasy' AND publication_year > 2000`` is equivalent to ``(NOT genre = 'fantasy') AND (publication_year > 2000)``.  To get what we originally wanted, we need to use parentheses explicitly:
::

    SELECT * FROM simple_books
    WHERE NOT (genre = 'fantasy' AND publication_year > 2000);

You can see that the above query only excludes books in the list:

::

    SELECT * FROM simple_books
    WHERE genre = 'fantasy' AND publication_year > 2000;

Similarly, we might be interested in either science fiction or fantasy books, but only if they were published after 2000.  Compare the two queries below:

::

    SELECT *
    FROM simple_books
    WHERE genre = 'science fiction' OR genre = 'fantasy'
    AND publication_year > 2000;

    SELECT *
    FROM simple_books
    WHERE
        (genre = 'science fiction' OR genre = 'fantasy')
        AND publication_year > 2000;

The first of these queries returns *any* science fiction books, along with fantasy books published after 2000.  The second returns the desired result: books published after 2000 in either the fantasy or science fiction genres.

For a fuller discussion of Boolean operators, we need to know more about ``NULL`` values, which will be discussed below.  See Appendix B - :ref:`appendix-b-boolean-operators` for complete documentation on the SQL Boolean operators.


.. index:: operator; date and time, function; date and time, CURRENT_DATE, CURRENT_TIME, CURRENT_TIMESTAMP

Date and time operators and functions
-------------------------------------

Date and time data are extremely important in many database applications, such as those supporting governmental or financial institutions.  SQL provides extensive functionality for managing dates and times.  Unfortunately, this is an area where different SQL implementations vary widely in their conformance to the SQL standard. See Appendix B - :ref:`appendix-b-datetime-operators` for a fuller discussion, and consult your database implementation's documentation to see what capabilities it offers with respect to date and time handling.

One useful SQL function that most databases implement is the **CURRENT_DATE** function (also try **CURRENT_TIME** and **CURRENT_TIMESTAMP**):

.. activecode:: expressions_example_datetime
    :language: sql
    :dburl: /_static/textbook.sqlite3

    SELECT CURRENT_DATE;

We will see in :numref:`Chapter {number} <table-creation-chapter>` how this function can be used to automatically record the date in a newly created row.


.. index:: NULL - SQL, three value logic - SQL

NULL
::::

In many database applications, it is sometimes necessary to record the *absence of information* on some aspect of a piece of data.  For example, in querying our **authors** table, we can see that some entries in the **death** column are blank.  This probably means that the author for that row had not yet died at the time the data was entered, and thus the column was simply not applicable for that author; there is no death date.  Additionally, some **birth** dates are blank; in this case, the column certainly applies to the author - they were clearly born at some point!  However, that information was unknown to the person entering the data into the table, so nothing was entered.

These notions of data entries that are *not applicable* or *unknown* are captured with a special value in SQL:  ``NULL``. [#]_ ``NULL`` values represent the absence of information.  When we query the **authors** table, the blanks in our result do not indicate that empty strings are in the database.  Instead, ``NULL`` values stand in for the missing information.  Unfortunately, ``NULL`` does not tell us the *reason* the data is missing - whether it is not applicable or simply unknown.  If this distinction is important for your database, you will need to use extra columns to indicate the meaning of the ``NULL``, or use some value other than ``NULL``.

Because ``NULL`` is truly an absence of information, ``NULL`` values used in expressions usually result in ``NULL`` when the expression is evaluated.  For example, what is the result of ``2 + NULL``?  We simply cannot know - the ``NULL`` is not telling us anything, so the result is unknown, or ``NULL``.

A very important consequence of this behavior is that ``NULL`` values cannot be usefully compared with anything, even other ``NULL`` values!  That is, an expression like ``x = NULL`` is never ``True`` even if *x* itself contains ``NULL``.  This might seem counterintuitive, but if you think of the expression ``NULL = NULL`` as asking the question, "Is this unknown thing the same as this other unknown thing?", you can see that the answer should be "unknown", or ``NULL``. [#]_

To find out if a value is ``NULL`` or not ``NULL`` requires special operators: **IS NULL** and **IS NOT NULL**.  For example, if we want to discover authors for whom we have no death date, we would execute the query:

.. activecode:: expressions_example_null
    :language: sql
    :dburl: /_static/textbook.sqlite3

    SELECT * FROM simple_authors WHERE death IS NULL;

You can discover authors for whom we do have death dates by replacing **IS NULL** with **IS NOT NULL** in the above query.

What happens if we instead write the following query?

::

    SELECT * FROM simple_authors WHERE death = NULL;

In this case, the expression ``death = NULL`` will evaluate to ``NULL`` for every row in the table.  The **WHERE** clause will filter these out, because it only accepts expressions that evaluate to ``True``, and ``NULL`` is not the same as ``True``.

``NULL`` values can sometimes lead us astray.  Consider the question of finding all authors who were alive in the year 2000 or later.  It might be tempting to write a query such as

::

    SELECT * FROM simple_authors
    WHERE birth <= '2000-12-31'
    AND death >= '2000-01-01';

This is a perfectly valid query - dates in this standard format can be compared in this fashion in our database.  However, if you run the query, you will see that not all of our living authors are in the result.  This happened, again, because the **death** column in those rows contained ``NULL`` values: comparing these to ``'2000-01-01'`` also yielded ``NULL``, and the **WHERE** clause therefore filtered them out.

In this case, we need to use more logic, and query the database thus:

::

    SELECT * FROM simple_authors
    WHERE birth <= '2000-12-31' AND
        (death >= '2000-01-01' OR death IS NULL);

This works correctly, but you might be wondering why.  We said that ``NULL`` used in expressions usually results in ``NULL``, but here we have a compound Boolean expression using the operators **AND** and **OR**.  So why are we not again losing all living authors?  Well, it turns out that Boolean operators are an exception.  This is because, when used in Boolean expressions, ``NULL`` means that we simply cannot know if the value is ``True`` or ``False``; the value is unknown.  However, the **OR** expression only requires one operand to evaluate to ``True`` in order to return ``True``: ``True OR True`` is ``True``, and so is ``True OR False`` in Boolean logic.  Either way, we get ``True``, so not knowing which it might be doesn't matter.  Therefore the expression in the parentheses is ``True`` if either one of the two conditions within it is true.

On the other hand, ``False OR NULL`` will give us ``NULL``.  In this case, whether the ``NULL`` is standing in for ``True`` or ``False`` actually matters, because each gives a different outcome. Since we do not know the outcome, the result is ``NULL``.

Because Boolean expressions can result in ``True``, ``False``, or ``NULL``, we say that SQL has *three-valued logic* (not truly Boolean logic).  Appendix B - :ref:`appendix-b-boolean-operators` provides truth tables for this three-valued logic, but as shown above, you can usually work out the answer by simply thinking of ``NULL`` as meaning "unknown".

Ordering and NULLs
------------------

Given that you cannot meaningfully compare ``NULL`` with other values, what happens when we **ORDER BY** a column containing ``NULL`` values?  Unfortunately, it depends on which database implementation you are working with.  You will need to consult your database documentation (or simply try an experiment) to see what its default behavior is.  The standard does provide a way to specify whether ``NULL`` values should sort to the top or bottom.  Compare these two queries:

::

    SELECT * FROM simple_authors ORDER BY death NULLS FIRST;

    SELECT * FROM simple_authors ORDER BY death NULLS LAST;

(Note: the **NULLS FIRST** and **NULLS LAST** modifiers are not supported in MySQL or SQL Server.)

.. index:: conditional expressions

Conditional expressions
:::::::::::::::::::::::

SQL provides expressions for doing simple conditional logic.  The basic conditional expression in SQL is the **CASE** expression, which comes in two forms.  In the most general form, **CASE** lets you specify what the expression should evaluate to depending on a list of conditions.  The effect is similar to using if/else or switch/case statements in some programming languages.

The basic form of the **CASE** expression is

::

    CASE WHEN condition1 THEN result1
         [WHEN condition2 THEN result2]
         ...
         [ELSE result]
    END

The **CASE** keyword comes first, followed by one or more **WHEN** clauses giving a condition and the desired result if the condition is true.  The first true condition determines the result that will be returned.  If none of the conditions evaluate to ``True``, then the **ELSE** result is used, if provided, or ``NULL`` if there is no **ELSE** clause.  The expression is finished with the **END** keyword.

For example, we could put our books into different categories, maybe for different sections in a library, using **CASE**:

.. activecode:: expressions_example_case
    :language: sql
    :dburl: /_static/textbook.sqlite3

    SELECT
        author, title,
        CASE WHEN genre = 'fantasy' THEN 'speculative fiction'
             WHEN genre = 'science fiction' THEN 'speculative fiction'
             WHEN genre = 'poetry' THEN 'poetry'
             WHEN genre = 'history' THEN 'non-fiction'
             ELSE 'general fiction'
        END
        AS category
    FROM simple_books;

Here we have included tests for some genres not present in our current dataset.  A library application might have many categories, each encompassing multiple genres.  Using a **CASE** expression would be one way to output books with their categories, although it depends on knowledge of all the possible genres in our database.  A more data-driven way would be to look up categories in another database table using a *join*, a technique we will discuss in :numref:`Chapter {number} <joins-chapter>`.

Another form of **CASE** matches an expression to possible values.  The above query can be rewritten using this form:

::

    SELECT
        author, title,
        CASE genre
            WHEN 'fantasy' THEN 'speculative fiction'
            WHEN 'science fiction' THEN 'speculative fiction'
            WHEN 'poetry' THEN 'poetry'
            WHEN 'history' THEN 'non-fiction'
            ELSE 'general fiction'
        END
        AS category
    FROM simple_books;

Additionally, there are two functions that perform specialized conditional logic.  The **COALESCE** function takes a variable number of arguments.  The result of the function is the first non-``NULL`` expression in the argument list, or ``NULL`` if all arguments are ``NULL``.  This can be useful for replacing ``NULL`` values with more descriptive values:

::

    SELECT name, COALESCE('died: ' || death, 'living')
    FROM simple_authors;

Finally, the **NULLIF** function takes two arguments: if the arguments are equal, the function results in ``NULL``, otherwise it results in the first argument.  This can be used to replace specific values with ``NULL``.  For example,

::

    SELECT title, author, NULLIF(genre, 'science fiction')
    FROM simple_books;



Self-check exercises
::::::::::::::::::::

This section contains some exercises using the same books and authors database used in the text above.  If you get stuck, click on the "Show answer" button below the exercise to see a correct answer.

.. activecode:: expressions_self_test_comparison
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query to find all books published from the year 1980 through the year 2000, in order by publication year.
    ~~~~

.. reveal:: expressions_self_test_comparison_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    There are usually many ways to achieve the same goal in SQL.  Here are two solutions:

    ::

        SELECT * FROM simple_books
        WHERE publication_year >= 1980 AND publication_year <= 2000
        ORDER BY publication_year;

        SELECT * FROM simple_books
        WHERE publication_year BETWEEN 1980 AND 2000
        ORDER BY publication_year;


.. activecode:: expressions_self_test_pattern
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query to find the authors whose name starts with the letter "J".
    ~~~~

.. reveal:: expressions_self_test_pattern_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT name FROM simple_authors WHERE name LIKE 'J%';


.. activecode:: expressions_self_test_boolean1
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query to find books written between 1950 and 1999, excluding poetry.
    ~~~~

.. reveal:: expressions_self_test_boolean1_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT * FROM simple_books
        WHERE publication_year >= 1950 AND publication_year <= 1999
        AND genre <> 'poetry';


.. activecode:: expressions_self_test_boolean2
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query to find books written before 1950 or after 1999, excluding science fiction.
    ~~~~

.. reveal:: expressions_self_test_boolean2_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT * FROM simple_books
        WHERE (publication_year < 1950 OR publication_year > 1999)
        AND genre <> 'science fiction';


.. activecode:: expressions_self_test_boolean3
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query to find books with a title beginning with the letters "T" or "I", in the fiction, fantasy, or poetry genres.
    ~~~~

.. reveal:: expressions_self_test_boolean3_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT * FROM simple_books
        WHERE (title LIKE 'T%' OR title LIKE 'I%')
        AND (genre = 'fiction' OR genre = 'fantasy' OR genre = 'poetry');


.. activecode:: expressions_self_test_null1
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query to find authors for whom we have no birth date.
    ~~~~

.. reveal:: expressions_self_test_null1_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT name FROM simple_authors WHERE birth IS NULL;


.. activecode:: expressions_self_test_null2
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query to find deceased authors born after 1915.
    ~~~~

.. reveal:: expressions_self_test_null2_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT name FROM simple_authors
        WHERE death IS NOT NULL
        AND birth > '1915-12-31';


.. activecode:: expressions_self_test_conditional
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query giving book titles and authors together with the century in which they were written, spelled out like 'Twentieth Century' (you only need to worry about the 20th - 21st centuries).
    ~~~~

.. reveal:: expressions_self_test_conditional_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT title, author,
            CASE WHEN publication_year > 1900 AND publication_year <= 2000
                   THEN 'Twentieth Century'
                 WHEN publication_year > 2000 AND publication_year <= 2100
                   THEN 'Twenty-first Century'
            END
            AS century
        FROM simple_books;


|chapter-end|

----

**Notes**

.. [#] Database scholars frequently reject calling ``NULL`` a *value*.  If ``NULL`` were truly a value, then it should be comparable to itself and other values.  One alternative is to say that a column is in a ``NULL`` *state*, rather than that it contains a ``NULL`` value.  However, this distinction breaks down in other SQL settings, such as grouping and aggregation (discussed in :numref:`Chapter {number} <grouping-chapter>`).  Because of this and other concerns, the inclusion of ``NULL`` in SQL is controversial.

.. [#] This results in an unfortunate logical inconsistency in SQL: the expression ``x = x`` evaluates to ``NULL`` when *x* is ``NULL``.  Logically, the answer should be ``True``, regardless of what *x* is.

|license-notice|



## Chapter: multiple-tables.rst

.. _joins-chapter:

==========================
Queries on multiple tables
==========================

In past chapters, we saw how to retrieve data from individual tables, filter data on different criteria, order the data, and format the data with various expressions.  Now we turn to the question of how to retrieve data from more than one table in a single query.  For example, using the tables **simple_books** and **simple_authors**, we might like to see book titles together with author's name and birth date. The author's name is in both tables, but book titles are in **simple_books**, while author birth dates are in **simple_authors**.  How can we get these together in one result?  This chapter will explain how to retrieve data from multiple tables using *joins*, and explore various issues that arise when working with multiple tables.


Tables used in this chapter
:::::::::::::::::::::::::::

We will use several collections of tables in this chapter, starting with some abstract tables used to illustrate joins.  These abstract tables are illustrated below, but are also available in the database for your own experimentation.  Also new to this chapter is a synthetic dataset simulating the database for a used book store, as well as a more complex set of tables about books and authors.  We will also continue to use the **simple_books** and **simple_authors** tables from previous chapters.  Brief explanations of newly introduced tables can be found below, and a full explanation of all of the datasets can be found in :ref:`Appendix A <appendix-a>`.

You may wish to spend some time doing **SELECT** queries on each new table as it is introduced, to get a sense of what the data looks like.  Understanding your database is key!


.. index:: join - SQL, JOIN, join - sql; inner, join condition

Simple joins
::::::::::::

To start with, we will consider an abstract example with a small amount of data.  Specifically, we will work with the two tables shown below, named **s** and **t**:

.. image:: joins1.svg
    :alt: Tables s and t

There is no real meaning to this data, but you might notice that the table data suggests a relationship: table **s** has a column **sy** containing small integers and table **t** has a column **ty** similarly containing small integers.  What we want to accomplish is to connect rows from table **s** with rows from table **t** when the values in the **sy** and **ty** columns are the same.  The desired result looks like this:

.. image:: joins1_result.svg
    :alt: The desired result of connecting s and t

When rows from one table are paired with rows from another table, we call the result a *join* of the tables.  Here is a query that joins **s** and **t** to produce the result shown above:

.. activecode:: joins_example_simple_join
    :language: sql
    :dburl: /_static/textbook.sqlite3

    SELECT *
    FROM
      s
      JOIN t ON sy = ty
    ;

We start our **FROM** clause with table **s**, then use the **JOIN** keyword to bring in table **t**, followed by the **ON** keyword, and finally a Boolean condition explaining to SQL which rows from **s** go with which rows from **t**.  The Boolean condition after **ON** is known as a *join condition*.  Join conditions always compare an expression on one table with an expression on another table.

To understand what happens when you run this query, consider each row in **s** in turn.  For each row in **s**, look at each row in **t** and apply the join condition.  If the join condition evaluates to ``True``, then make a new row by concatenating the row from **s** with the row from **t**, and add it to the result.  (This can be likened to performing nested **for** loops in a programming language like Python or Java; the outer loop is over the rows in **s**, and the inner loop is over the rows in **t**.)

So, for example, we start by looking at the first row in **s**, which we can write as ``('one', 1)``.  The value of **sy** in this row is 1.  Now, we look at each row in **t** to see which ones have **ty** also equal to 1.  The first row in **t** is ``(1, 'green')``, which has a **ty** value of 1, so we make the row ``('one', 1, 1, 'green')`` and add it to the output.  No other rows in **t** match, so we move on to the next row in **s**, ``('two', 2)``.  Again, we consider each row in **t**, this time looking for a **ty** value equal to 2; this time we match the row ``(2, 'blue')``, and we add ``('two', 2, 2, 'blue')`` to the output.  This process continues until we have processed every row in **s**.

In the first example, each row in **s** matched exactly one row in **t**, and each row in **t** matched exactly one row in **s**.  What happens if this is not the case?  First, consider tables **s2** and **t2** below, in which one row in each table fails to match any rows in the other table:

.. image:: joins2.svg
    :alt: Tables s2 and t2

Joining **s2** and **t2** using the same equality condition on columns **sy** and **ty** now gives us:

.. image:: joins2_result.svg
    :alt: The join of s2 and t2

This result can again be understood by examining each row of **s2** and looking for matches in **t2**.  If there is no match, no row gets output.

We can also have the case where more than one row in one table matches some row in the other table.  Here are two more tables to consider:

.. image:: joins3.svg
    :alt: Tables s3 and t3

This time, the **s3** row ``('two', 2)`` matches *two* different rows in **t3**, so we will produce two combined rows where **sy** and **ty** both equal 2:

.. image:: joins3_result.svg
    :alt: The join of s3 and t3


Tables **s2**, **t2**, **s3** and **t3** are also in the database accessible in the interactive tool above.

Two tables can be related via multiple columns rather than just one in each table.  To join them, you would use a compound join condition using **AND**.  In fact, join conditions do not have to be equality (although they usually are); any logical expression relating rows in one table with rows in another can be used.  The conceptual model of examining each row in the first table and comparing with each row in the second table still works.  See if you can figure out what this query will produce (and then try it in the interactive tool above):

::

    SELECT *
    FROM
      s
      JOIN t ON sy = ty OR sy > ty
    ;

**JOIN** clauses are considered to be sub-clauses of the **FROM** clause.  We are, of course, free to add other clauses as normal to the query, such as a **WHERE** clause:

::

    SELECT *
    FROM
      s
      JOIN t ON sy = ty
    WHERE tz = 'blue';

Think of the **FROM** clause as being the first part of the query processed by the database.  The result is some collection of rows, which we can then filter with a **WHERE** clause, or put in a particular order with an **ORDER BY** clause, and so forth.

We have a lot more to talk about with joins, but before moving on, let us see how to answer the question raised earlier, where we would like to obtain both book titles and author birth dates in one query result using **simple_books** and **simple_authors**.  Here is the solution:

::

    SELECT title, author, birth
    FROM
      simple_books
      JOIN simple_authors ON author = name
    ;

Note here that we are choosing specific columns to return as part of our result, using our **SELECT** clause.  The column **name**, used in the join condition, is the column containing author names in the **simple_authors** table.  We compare this column to the **author** column in **simple_books** for our join, but we don't include it in the columns we retrieve; otherwise we would have the same author name showing in two different columns.


Names of things
:::::::::::::::

We have (mostly) not worried about the *names* of things in our discussion so far.  We have said that we can use a column name as an expression representing the value in the column for some row under consideration, but we now need to consider some scenarios in which a column's name by itself is not sufficiently specific.  We have also given some examples where we renamed the output columns for a **SELECT** query, but we deferred discussion of that technique.  This section will go into more detail regarding both of these topics and more.

.. index:: name; collision, ambiguity

Name collisions and ambiguity
-----------------------------

In all of our examples so far, all of the columns in the tables we queried had unique names.  For example, the join of **s** and **t** contained columns named **sx**, **sy**, **ty**, and **tz**.  However, we will often not be so lucky as to have distinct column names when working with multiple tables.  When two columns from tables involved in a join have the same name, we say that the column names *collide*.  When a naming collision occurs, we cannot use the column name by itself as an expression in any part of our query, because the database will not know which table's column you mean; the database will give an error message that the column name is *ambiguous*.

.. index:: name; qualified

Qualified names
---------------

Fortunately, there is an easy way to specify a particular column in a particular table: simply give the table name first, followed by a period, or dot (".") and then the column name.  You can do this even if names are not ambiguous. For example, the last query above could be expressed as:

.. activecode:: joins_example_qualified_names
    :language: sql
    :dburl: /_static/textbook.sqlite3

    SELECT
      simple_books.title,
      simple_books.author,
      simple_authors.birth
    FROM
      simple_books
      JOIN simple_authors
        ON simple_books.author = simple_authors.name
    ;

This has the added benefit of making clear where each column is coming from for anyone reading the query who is not familiar with the database.

You can also use the asterisk shortcut to mean all columns in a specific table by prefixing with the table name and a dot:

::

    SELECT simple_books.*, simple_authors.birth
    FROM
      simple_books
      JOIN simple_authors ON simple_books.author = simple_authors.name
    ;

Such expressions using both the table name and the column name are known as *qualified* column names, and can be used with any database.  In some database implementations, tables can be grouped together into larger containers; in those databases, it is possible to have multiple tables of the same name (in different containers), which now must be qualified using the container name.  Each database implementation is different, so you will need to learn about your particular database system's rules for qualifying names.

When doing a join, it is good practice to qualify all of your column names.  This will make it easier for anyone reading or maintaining your code to understand what your query is doing.

.. index:: aliasing, AS

Aliasing
--------

SQL provides facilities to change the names of tables and columns within the context of a single query.  This can be useful, and at times, necessary.  In a previous chapter, we used column renaming to get nicer column headers in our output.  For example, consider this query:

::

    SELECT
      title,
      floor((publication_year + 99) / 100) AS century
    FROM simple_books;

We supplied the name "century" for the second output column (which otherwise would have a header that looked like the mathematical expression we computed).  This technique is known as *aliasing*, and is accomplished with the **AS** keyword.  Aliasing for columns is most often used for the purpose of giving a helpful name for the column in the output, although it can be applied for other reasons that we shall see.

Aliasing can also be used with tables.  This is often used to shorten table names to keep qualified names short and readable.  Here, the **AS** keyword is used in the **FROM** clause after each table that should be renamed.  The alias can then be used in the **SELECT**, **WHERE**, and other clauses in place of the table name.  Here is an earlier query, rewritten using table aliasing:

::

    SELECT b.title, b.author, a.birth
    FROM
      simple_books AS b
      JOIN simple_authors AS a ON b.author = a.name
    ;

When working with large queries using many tables, aliasing can make the query significantly smaller and more readable.

One instance where table aliasing is *required* is when joining a table to itself.  This can be done when there is some kind of relationship between rows within the same table, which happens more often than you might guess.  As an example of a query we might do with our simple books and authors data, consider the question, "What books were published in the same year as *The Three-Body Problem*?".  Here is one way to answer that question with a query:

::

    SELECT b2.*
    FROM
      simple_books AS b1
      JOIN simple_books AS b2
        ON b1.publication_year = b2.publication_year
    WHERE
      b1.title = 'The Three-Body Problem';

If this seems confusing, think about it as using two tables, **b1** and **b2**, each containing the same data as **simple_books**.  Work through what happens if you join **b1** and **b2** applying the join condition ``b1.publication_year = b2.publication_year``; then, filter that result with the condition ``b1.title = 'The Three-Body Problem'``; finally, output just the columns from **b2**.  If you have trouble visualizing what the result should be at each step, remember that you can query the database using the interactive tool above.

When using table aliasing, you should qualify all of your column names using the aliases as a matter of good style.  Some databases allow you to use original table names instead of aliases, but mixing aliases with original table names is inconsistent and confusing, and in some cases that can result in incorrect code that is difficult to debug.

Just remember, aliasing only affects the query in which the renaming occurs; a new query will know nothing about any previous aliasing applied to tables or columns.

As a final note, the **AS** keyword is actually optional in SQL - you can create an alias with this keyword omitted.  Simply put a valid identifier string after the name of a table or after a column expression:

::

  SELECT b.title, b.author, a.birth
  FROM
    simple_books b
    JOIN simple_authors a ON b.author = a.name
  ;

Leaving out a keyword may seem strange, but you are likely to read code at some point using this form of aliasing, so be aware.  There is no consensus on which style is better; for this textbook, we will consistently use **AS** for additional clarity.

(Note for Oracle users: the **AS** keyword is optional for columns, but is not supported for table aliases - you must omit the **AS** in Oracle queries when aliasing a table.)

.. index:: double quotes

Reserved names, names with spaces, or mixed-case names
-------------------------------------------------------
Usually, names of things are case-insensitive and do not contain spaces.  Also, the case used when displaying the output headers for a query may be all uppercase or all lowercase, depending on the database (for this textbook, lowercase is the norm).  It is possible, however, to use names which are case-sensitive and which contain spaces.  To do this, put the name within double quotes.  For example, the header for the output column of in the following query will be mixed-case as well as having spaces:

::

    SELECT 42 AS "The Answer";

Reserved names (such as SQL keywords) may also need to be put inside double quotes when used as column or table names.

Very rarely, you may encounter a database where table or column names are mixed-case or contain spaces.  This can occur if the database creator used double quotes in the SQL code when creating the tables.  In general, this is not a good practice, as it forces the use of double quotes for any future queries using the table.  Reserved words should also be avoided in general, although this can be difficult when working with multiple databases, as an allowed word in one database may be a reserved word in another database.

(Note for MySQL users: use backticks instead of double quotes.  The backtick character looks like an apostrophe, but slanting in the opposite direction.)


.. index::
    single: column; identity
    single: id column
    single: universally unique identifier
    single: UUID

Identity columns
::::::::::::::::

If we want to make a connection between data in one table and data in another using a join, we need the tables to share some data elements in common.  In our simple books dataset, the common element was the author's name, which was present in both the **simple_books** and **simple_authors** tables; this let us join the two tables with the join condition ``simple_books.author = simple_authors.name``.  We can be confident in our result because we know the author's name uniquely identifies the authors in our simple database.  But what if author names were not unique?  Then we might join authors to books they did not actually write!

For some types of data, some element of the data is unique for every possible data item and can be used as an identifier for the data in a database.  For example, international travel to many countries requires the traveler to have a passport, and the issuing country together with the passport number uniquely identifies any traveler.  However, this only works for international travel; most countries do not require passports for travel within the country's own borders, and therefore there are many people who have no passport at all.  A database trying to track domestic travelers, then, cannot use passport information as a unique identifier.

Author names might seem like a good identifier for authors, but, in fact, we have to be careful here as well due to multiple authors sharing the same name.  For example, there are two novelists named Richard Wright, and both a novelist and a poet named David Diop.  We could further distinguish between these authors using their birth dates, or perhaps we could consider their birthplace or other attributes.  That only works, of course, if we *know* the birth date and so forth of each author in our database. In any case it begins to be an unsatisfactory solution due to the complexity of having to store so many pieces of information about each author for any tables we want to join to our table of authors.

This type of problem comes up a lot.  The solution we will adopt, which is widely used in practice, is to create an artificial unique identifier, or *id*, for each author in our database.  Unique identifiers can take different forms.  The most common scheme is to keep a counter in the database and increment it each time a row is added to a table.  This counter value is then used as the id value for the new row (we will discuss how to do this in :numref:`Chapter {number} <table-creation-chapter>`).

Another popular scheme is to use a very large integer generated at random - a *universally unique identifier*, or UUID.  In this scheme, due to the large number of possible UUIDs, each new id value is very likely to be different from any other previously id in the table. It is also easy to detect if there is a duplicate, in which case another value can be generated.

In our database, there is a table named **authors** which has an **author_id** column holding a unique value for each row.  There is also a **books** table, which does not have a column to store the author's name.  Instead, it also has the column **author_id**.  Each unique **author_id** in **books** is equal to some **author_id** value in **authors**.

To get the author's name together with their books, we will need to join **books** to **authors** using the common id value:

.. activecode:: joins_example_books_join
    :language: sql
    :dburl: /_static/textbook.sqlite3

    SELECT authors.name, books.title
    FROM
      books
      JOIN authors ON authors.author_id = books.author_id
    ;

Note that this query requires the use of qualified column names, at least for the two **author_id** columns - if we simply try the query

::

    SELECT name, title
    FROM
      books
      JOIN authors ON author_id = author_id
    ;

we will get an error message that the **author_id** name is ambiguous.


Table relationships
:::::::::::::::::::

One of the strengths of relational databases compared to earlier database systems is that relationships are not explicitly stored in the database.  This provides a number of advantages regarding database design and software complexity, which are mostly beyond the scope of this book.  One important advantage of the relational approach is that you can easily express queries concerning relationships which were not anticipated by the designer of the database; for example, our earlier query looking for books published in the same year as another book.  However, this flexibility also means that when you encounter a new relational database, you may not immediately understand the structure and relationships in the database, or how (or why) you should join two tables together.

A well structured database usually gives some indication of likely places to join tables together.  One indication may be in the names of columns - e.g., **book_id** in a table strongly suggests a column that links to the identity column of the **books** table.  Another indication can come in the form of *foreign key constraints*, a topic we will discuss in :numref:`Chapter {number} <constraints-chapter>`.  Exploring the database to find these implicit relationships is an important first step in learning any new database.

Your database might also come with a data model diagram, discussed in :numref:`Part {number} <data-modeling-part>` of this book.  (Data models for the data sets in our database can be found in :ref:`Appendix A <appendix-a>`.)  The data model will typically make the relationships between tables explicit.  While data can be related to each other in very complex ways, there are some basic relationship types that capture the important aspects of most relationships.  These relationships are commonly called "one-to-one", "one-to-many", and "many-to-many".  Below, we discuss these common relationships and where they appear in our database.

.. index::
    single: relationship - tables; one-to-one
    single: one-to-one relationship - tables

One-to-one
----------

*One-to-one* describes a relationship between two types of data.  If we think of each data type as having its own table, then each row in one table has a well-defined relationship with *at most* one row in the other table, and vice versa.  Sometimes each row in a table has exactly one corresponding row in the other table, and vice versa; other times, some rows in one or both tables may not have corresponding rows in the other table.  When there is a true one-to-one correspondence between tables, it is sometimes desirable to combine the tables into one larger table (whether or not to do this is a design decision).

An example of a one-to-one relationship might appear in a database for a seller of used books.  Some example data for this fictional bookstore can be found in our database in the tables **bookstore_inventory** and **bookstore_sales**.  Each of the seller's books is recorded in **bookstore_inventory**, listing the book's author, title, condition, and current price.  The table **bookstore_sales** records the sale of a book, the date it was sold, the payment type, and a receipt number.  These two tables can be joined by the common column **stock_number**, which functions as the id column for **bookstore_inventory**.  Every record in the **bookstore_sales** table corresponds to exactly one record in the **bookstore_inventory** table; however, any unsold books still in the seller's possession will not have a corresponding **bookstore_sales** record.

A few rows from each table are illustrated below.

.. figure:: one_to_one.svg

    Some example rows from the **bookstore_inventory** and **bookstore_sales** tables: two inventory items have corresponding sales records, but the third has not been sold yet.

.. index::
    single: relationship - tables; one-to-many
    single: one-to-many relationship - tables
    single: relationship - tables; many-to-one
    single: many-to-one relationship - tables

One-to-many
-----------

*One-to-many* refers to the case when rows in one table correspond to some number of rows in another table, but rows in the second table only correspond to at most one row in the first table.  In some cases, rows in the first table always have at least one corresponding row; other times, rows can have zero or more corresponding rows.

In our database, we have a one-to-many relationship between **authors** and **books** - each author has one or more books, but each book has exactly one author.  (This is not reflective of the real world - many books exist that were written by two or more authors working together!  However, for simplicity our database only contains single-author books.)  Note that we can also talk of *many-to-one* relationships, which are just the symmetric equivalent of one-to-many; we can say that the **authors** table is in a one-to-many relationship with **books**, or that the **books** table is in a many-to-one relationship with **authors**.

To connect rows from one table to rows in another table where a one-to-many relationship exists between them, the simplest approach is to include a column on the "many" side that stores id values from the "one" side.  As we saw above, this strategy is used with **books** and **authors**; the **authors** table has the **author_id** column, which is unique for every row, and the **books** table has the corresponding column **author_id**.

.. figure:: one_to_many.svg

    Some example rows from the **authors** and **books** tables (not all columns shown): each book has one author, some authors have written multiple books.

Similarly, the **books** table has a one-to-many relationship with the **editions** table in our database.  In this case, the **editions** table has a **book_id** column, which, as you might guess, contains values from the **book_id** column of **books**.  (The **editions** table contains information about the printed editions of books: publisher information, title as printed, year printed, and so forth. [#]_)

.. index::
    single: relationship - tables; many-to-many
    single: many-to-many relationship - tables
    single: table; cross-reference
    single: cross-reference table

Many-to-many
------------

*Many-to-many*, you can probably guess, implies that rows in one table may correspond to multiple rows in the other table, and vice versa.  In our database, our examples of many-to-many relationships will involve book and author awards.  For example, the Hugo Award is given out each year to a book in the science fiction genre.  In our database, there are many books that have won a Hugo Award; therefore the row for the Hugo Award in the **awards** table relates to multiple rows in the **books** table.  Especially good science fiction books might win both a Hugo Award and a Nebula Award; so rows in the **books** table can correspond to multiple **awards** rows.

How do you connect rows from one table to rows in another table when there is a many-to-many relationship?  If you try the trick we used with one-to-many relationships, you quickly run into trouble.  For example, suppose we try to store id values from **books** in the **awards** table; since many books have won the Hugo Award, we need to store many book ids, so we would have many rows for the Hugo Award, all identical except for the book id. On the other hand, if we try to store award ids in the **books** table, books that have won multiple awards will need multiple rows, all identical except for the award ids. [#]_  Having multiple nearly identical rows creates a number of problems, some of which we will explore in :numref:`Chapter {number} <normalization-chapter>`.

The solution is to use a third table, known as a *cross-reference* table, as a connector.  At minimum, a cross-reference table will have one column for each of the unique id columns in the two tables being connected.  For example, the **books_awards** table in our database has a column **book_id** referring to the **book_id** column of **books** and an **award_id** column referring to the **award_id** column of **awards**.  The existence of a (book id, award id) pair in the **books_awards** table means that the given book has won the stated award.

We can store other information in the cross-reference table as well.  In the case of **books_awards**, we also have a **year** column storing the year in which the award was given to the book.  Note that the cross-reference table is really the only place we can store this information; the year doesn't properly "belong" to the award, as an award is given out in many years; and it doesn't properly belong to the book, as books can win awards in different years.

.. figure:: many_to_many.svg

    Some example rows from **books**, **books_awards**, and **awards** (not all columns shown).  Each row in **books_awards** connects a book to an award that the book has won.  The year of the award is stored in **books_awards** as well.

To use the cross-reference table, we will need to join together *three* tables.  The basic principles for joining three tables are the same as for two; start by joining two tables, then join that result with the third table.  The finished query looks like this:

.. activecode:: joins_example_many_to_many
    :language: sql
    :dburl: /_static/textbook.sqlite3

    SELECT b.title, a.name AS award, ba.year
    FROM
      books AS b
      JOIN books_awards AS ba ON b.book_id = ba.book_id
      JOIN awards AS a ON a.award_id = ba.award_id
    ;

Looking at the query above, think of the first join as adding award ids from the cross-reference table to the rows from the books table, and think of the second join as then bringing in the award information matching those award ids.  (Again, you can break this query down into smaller pieces and try them in the interactive tool to help build your intuition about how SQL works.)

In addition to winning awards for specific books, an author can win awards for their entire body of work.  Awards of this type are also stored in the **awards** table; however, we need another table to connect authors with these awards (since the **books_awards** table connects to specific books only).  The cross-reference table **authors_awards** exists for this purpose.

.. index:: join - SQL; outer, outer join, INNER JOIN, RIGHT [OUTER] JOIN, LEFT [OUTER] JOIN, FULL [OUTER] JOIN

Inner and outer joins
:::::::::::::::::::::

When relational database programmers use the word "join" without any qualifiers, they almost always mean the type of join we have been describing above, in which the result only contains rows that match on both sides of the join.  This type of join is more formally known as an *inner join*.  In fact, you can optionally use the keyword **INNER** in front of **JOIN** if you want to make clear what type of join you are doing; however, **INNER** is commonly dropped simply because the default without **INNER** is still an inner join.

What if you want to retrieve *all* rows from one table in a join, even if there are no matching rows on the other side of the join?  For example, we might want a list of books, together with any awards the books have won.  Since not all books have won awards, the inner join of the **books**, **books_awards**, and **awards** shown above only returns some of the books in our database.  To get all books, and awards where present, we want an *outer join*.

There are three types of outer join: *left*, *right*, and *full*.  These are implemented with the key phrases **LEFT [OUTER] JOIN**, **RIGHT [OUTER] JOIN**, and **FULL [OUTER] JOIN**.  (The square brackets mean that the **OUTER** keyword is optional; that is, **LEFT JOIN** means the same thing as **LEFT OUTER JOIN**.)  In an outer join, all rows from one or both tables are returned, depending on the type of outer join.  In a left outer join, all of the rows from the table on the left-hand side of the **LEFT JOIN** key phrase are returned, but only matching rows are returned from the right-hand side table.  **RIGHT JOIN** does the opposite, while **FULL JOIN** returns all rows from both tables involved in the join.

When the join specifies that all rows from a table should be returned, and a row has no match in the other table, what should the row contain for the missing data from the other table?  A logical choice is to fill in those columns with ``NULL`` values, which is exactly what happens.  Here is one query to retrieve all books, as well as awards where relevant:

.. activecode:: joins_example_outer_join
    :language: sql
    :dburl: /_static/textbook.sqlite3

    SELECT b.title, a.name AS award, ba.year
    FROM
      books AS b
      LEFT JOIN books_awards AS ba ON b.book_id = ba.book_id
      LEFT JOIN awards AS a ON a.award_id = ba.award_id
    ;

Note that we have to do two outer joins in the above query.  The first outer join between **books** and **books_awards** is necessary because books without awards will have no matching records in the **books_awards** cross reference table.  The result of that join, then, will have ``NULL`` values for the **award_id** column coming from the **books_awards** table.  So, when we join with **awards** we again need an outer join, because the ``NULL`` **award_id** values will not match any rows in the **awards** table.

In most databases, we could instead write the query using one right outer join. (Note: at the time this book was written, SQLite did not yet support right or full outer joins, so this query may not work in the interactive tool above):

::

    SELECT b.title, a.name AS award, ba.year
    FROM
      awards AS a
      JOIN books_awards AS ba
        ON a.id = ba.award_id
      RIGHT JOIN books AS b
        ON b.id = ba.book_id
    ;

Here, the **awards** and **books_awards** tables can use a regular join, as we only care about awards that are referenced in the **books_awards** table, and all rows in the **books_awards** table have a matching entry already in the **awards** table.  However, a right outer join would have worked equally well - an outer join is equivalent to an inner join if all rows match.

The above queries do exhibit one behavior which may be unwanted, which is that we have multiple rows for books that have won multiple awards.  Some databases provide a way to produce a list of awards after each book, rather than multiple rows; see the **LISTAGG** aggregate function in Appendix B - :ref:`appendix-b-aggregate-functions` (we discuss the use of aggregate functions in :numref:`Chapter {number} <grouping-chapter>`).

Here is one more example of the use of an outer join, this time using our bookstore tables - see if you can figure out what this query is doing:

::

    SELECT
      inv.*,
      CASE WHEN sales.stock_number IS NULL THEN 'in stock'
           ELSE 'sold'
      END
        AS status
    FROM
      bookstore_inventory AS inv
      LEFT JOIN bookstore_sales AS sales
        ON inv.stock_number = sales.stock_number
    ;

.. index:: join - SQL; implicit, cross product - SQL, CROSS JOIN

Implicit join syntax
::::::::::::::::::::

The ability to do inner joins existed in SQL long before the **JOIN** keyword and related key phrases.  Prior to the introduction of this *explicit* join syntax, joins used an *implicit* join syntax, which is described in this section.  You may prefer the explicit syntax above, and it is considered by many practitioners to be best practice to use it for the clarity it provides.  However, the implicit syntax is supported by all databases and you are very likely to encounter it in practice. Additionally, most databases reduce the explicit syntax to the implicit syntax internally, which has implications for understanding how the database processes join queries.  For these reasons, it is important that you understand the implicit join syntax.

Returning to our abstract examples from the start of this chapter:

.. image:: joins1.svg
    :alt: Tables s and t

In the implicit join syntax, the first step is to simply list all tables involved in the join after the **FROM** clause.  In SQL, this implies a *cross product* of the tables.  In a cross product of two tables, *every* row in one table is paired with *every* row from the other table.  You can see this in action in the query below:

.. activecode:: joins_example_implicit_join
    :language: sql
    :dburl: /_static/textbook.sqlite3

    SELECT * FROM s, t;

Given this result, how do we apply join conditions to get the rows we actually want?  We simply put our join conditions into the **WHERE** clause:

::

    SELECT * FROM s, t
    WHERE sy = ty;

This is equivalent in all respects to:

::

    SELECT *
    FROM
      s
      JOIN t ON sy = ty
    ;

That is, all conditions that would normally be put after the **ON** keyword in a **JOIN** clause should be put into the **WHERE** clause when using the implicit join syntax.  If you consider the cross product of **s** and **t**, it is easy to see how applying the join condition to filter the cross product produces the desired result. [#]_

One danger in using the implicit join syntax is that it separates join conditions from the part of the query that actually joins the tables, making it easy to accidentally leave out a join condition.  The join conditions instead are put into the **WHERE** clause together with any other single-table conditions needed.

If you are joining together *n* tables using the implicit syntax, then always remember that you need *n - 1* join conditions to ensure that all of the tables are linked in.  It is important that all of the tables connect to each other either directly or through a path of other tables (if you are familiar with data structures, the tables must be the nodes of a *connected graph*, generally in the shape of a *free tree*, with the edges represented by join conditions).  Remember that *n - 1* join conditions may mean more than *n - 1* **WHERE** clause conditions, if any of the join conditions are compound.  If you add a join condition to your **WHERE** clause for each new table you add to the **FROM** clause as you are writing your query, you can systematically create the proper join structure.

A good clue that you have omitted a join condition is if you suddenly get many more rows than you expected.  If you look more closely at the data (you may need to include more columns in your **SELECT** clause to see it), you can see that you have created a cross product.  Consider an implicit join of **books**, **books_awards**, and **awards** with a missing join condition:

.. activecode:: joins_example_missing_join_condition
    :language: sql
    :dburl: /_static/textbook.sqlite3

    SELECT b.title, a.name AS award, ba.year
    FROM books AS b, awards AS a, books_awards AS ba
    WHERE b.book_id = ba.book_id
    -- missing: AND a.award_id = ba.award_id
    ;

It looks like every book that has won an award has won *every* award!  That is due to the cross product resulting from the missing join condition.

Implicit join syntax is standard only for inner joins.  Some database implementations do provide non-standard ways of doing outer joins using the implicit form, and you may see older queries using these.  Since notations vary, we will not include any examples here.

As a final note, cross products are seldom a desired result on their own.  However, if you actually need a cross product and wish to be explicit about it, SQL provides the **CROSS JOIN** key phrase for the purpose:

::

    SELECT * FROM s CROSS JOIN t;


Self-check exercises
::::::::::::::::::::

This section contains some exercises using the books data set (reminder: you can get full descriptions of all tables in :ref:`Appendix A <appendix-a>`).  If you get stuck, click on the "Show answer" button below the exercise to see a correct answer.  For each of these, try writing the answer using explicit join syntax first, and then using the implicit syntax (where possible).

.. activecode:: joins_self_test_two_way_join
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query listing all of the editions (publisher, year, and published title) for the book titled "The Hobbit",
    ~~~~

.. reveal:: joins_self_test_two_way_join_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    Explicit:

    ::

        SELECT e.publisher, e.publication_year, e.title
        FROM
          books AS b
          JOIN editions AS e ON b.book_id = e.book_id
        WHERE b.title = 'The Hobbit';

    Implicit:

    ::

        SELECT e.publisher, e.publication_year, e.title
        FROM books AS b, editions AS e
        WHERE b.book_id = e.book_id
        AND   b.title = 'The Hobbit';

.. activecode:: joins_self_test_two_way_join2
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query listing the distinct titles under which the book 'The Fellowship of the Ring' was published.
    ~~~~

.. reveal:: joins_self_test_two_way_join2_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT DISTINCT e.title
        FROM
          books AS b
          JOIN editions AS e ON b.book_id = e.book_id
        WHERE b.title = 'The Fellowship of the Ring';

        SELECT DISTINCT e.title
        FROM books AS b, editions AS e
        WHERE b.book_id = e.book_id
        AND   b.title = 'The Fellowship of the Ring';

.. activecode:: joins_self_test_two_way_join3
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query listing editions (title, corresponding book title, publisher, and publisher location) that were published since 2005 under a different name than the book.
    ~~~~

.. reveal:: joins_self_test_two_way_join3_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT e.title, b.title, e.publisher, e.publisher_location
        FROM
          books AS b
          JOIN editions AS e
            ON b.book_id = e.book_id AND b.title <> e.title
        WHERE e.publication_year > 2005;

        SELECT e.title, b.title, e.publisher, e.publisher_location
        FROM books AS b, editions AS e
        WHERE b.book_id = e.book_id
        AND   b.title <> e.title
        AND   e.publication_year > 2005;

.. activecode:: joins_self_test_three_way_join
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query listing author, book title, edition title, and publisher for editions published since 2010.
    ~~~~

.. reveal:: joins_self_test_three_way_join_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT a.name, b.title, e.title, e.publisher
        FROM
          authors AS a
          JOIN books AS b ON a.author_id = b.author_id
          JOIN editions AS e ON b.book_id = e.book_id
        WHERE e.publication_year > 2010;

        SELECT a.name, b.title, e.title, e.publisher
        FROM authors AS a, books AS b, editions AS e
        WHERE a.author_id = b.author_id
        AND   b.book_id = e.book_id
        AND   e.publication_year > 2010;

.. activecode:: joins_self_test_cross_reference1
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query returning the author who won the Neustadt International Prize for Literature in 1996. Note: this is an *author* award, not a *book* award.
    ~~~~

.. reveal:: joins_self_test_cross_reference1_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT au.name
        FROM
          authors AS au
          JOIN authors_awards AS aa ON aa.author_id = au.author_id
          JOIN awards AS aw ON aa.award_id = aw.award_id
        WHERE aw.name = 'Neustadt International Prize for Literature'
        AND   aa.year = 1996;

        SELECT au.name
        FROM authors AS au, authors_awards AS aa, awards AS aw
        WHERE aa.author_id = au.author_id
        AND   aa.award_id = aw.award_id
        AND   aw.name = 'Neustadt International Prize for Literature'
        AND   aa.year = 1996;

.. activecode:: joins_self_test_cross_reference2
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query to list the authors who have won author awards, together with their awards and the year of the award. Give the output descriptive headers (not just "name" and "name").  Order by author name.
    ~~~~

.. reveal:: joins_self_test_cross_reference2_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT au.name AS author, aw.name AS award, aa.year
        FROM
          authors AS au
          JOIN authors_awards AS aa ON aa.author_id = au.author_id
          JOIN awards AS aw ON aa.award_id = aw.award_id
        ORDER BY au.name;

        SELECT au.name AS author, aw.name AS award, aa.year
        FROM authors AS au, authors_awards AS aa, awards AS aw
        WHERE aa.author_id = au.author_id
        AND   aa.award_id = aw.award_id
        ORDER BY au.name;

.. activecode:: joins_self_test_outer_join1
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query listing all authors, together with their (author) awards, if any.
    ~~~~

.. reveal:: joins_self_test_outer_join1_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

      SELECT au.name AS author, aw.name AS award, aa.year
      FROM
        authors AS au
        LEFT JOIN authors_awards AS aa ON aa.author_id = au.author_id
        LEFT JOIN awards AS aw ON aa.award_id = aw.award_id
      ORDER BY au.name;

.. activecode:: joins_self_test_outer_join2
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query listing authors who have *not* won any of the author awards listed in our database. Hint: how might you detect the absence of an award in the query above?
    ~~~~

.. reveal:: joins_self_test_outer_join2_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

      SELECT au.name
      FROM
        authors AS au
        LEFT JOIN authors_awards AS aa ON aa.author_id = au.author_id
      WHERE aa.author_id IS NULL;


.. activecode:: joins_self_test_recursive_join1
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query listing all the books by the author of "Interpreter of Maladies".
    ~~~~

.. reveal:: joins_self_test_recursive_join1_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT b1.title
        FROM
          books AS b1
          JOIN books AS b2 ON b2.author_id = b1.author_id
        WHERE b2.title = 'Interpreter of Maladies';

        SELECT b1.title
        FROM books AS b1, books AS b2
        WHERE b1.author_id = b2.author_id
        AND   b2.title = 'Interpreter of Maladies';


.. activecode:: joins_self_test_recursive_join2
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Same as above, but show the author's name as well.
    ~~~~

.. reveal:: joins_self_test_recursive_join2_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT b1.title, a.name
        FROM
          books AS b1
          JOIN authors AS a ON b1.author_id = a.author_id
          JOIN books AS b2 ON b2.author_id = a.author_id
        WHERE b2.title = 'Interpreter of Maladies';

        SELECT b1.title, a.name
        FROM books AS b1, books AS b2, authors AS a
        WHERE b1.author_id = a.author_id
        AND   b2.author_id = a.author_id
        AND   b2.title = 'Interpreter of Maladies';


.. activecode:: joins_self_test_recursive_join3
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Using the **books** and **authors** tables, find all books (author and title) published in the same year as *The Three-Body Problem*, excluding *The Three-Body Problem* itself.
    ~~~~

.. reveal:: joins_self_test_recursive_join3_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT a.name, b2.title
        FROM
          books AS b1
          JOIN books AS b2
            ON
              b1.publication_year = b2.publication_year
              AND b2.book_id <> b1.book_id
          JOIN authors AS a ON a.author_id = b2.author_id
        WHERE b1.title = 'The Three-Body Problem';

        SELECT a.name, b2.title
        FROM books AS b1, books AS b2, authors AS a
        WHERE b1.publication_year = b2.publication_year
        AND   b2.book_id <> b1.book_id
        AND   a.author_id = b2.author_id
        AND   b1.title = 'The Three-Body Problem';


.. activecode:: joins_self_test_challenge1
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query to list books (author, name, and title) that have won the Nebula Award. Show the year of the award and list the most recent awards first.
    ~~~~

.. reveal:: joins_self_test_challenge1_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT au.name AS author, b.title, ba.year
        FROM
          authors AS au
          JOIN books AS b ON au.author_id = b.author_id
          JOIN books_awards AS ba ON b.book_id = ba.book_id
          JOIN awards AS aw ON aw.award_id = ba.award_id
        WHERE aw.name = 'Nebula Award'
        ORDER BY ba.year DESC;

        SELECT au.name AS author, b.title, ba.year
        FROM authors AS au, books AS b, books_awards AS ba, awards AS aw
        WHERE au.author_id = b.author_id
        AND   b.book_id = ba.book_id
        AND   aw.award_id = ba.award_id
        AND   aw.name = 'Nebula Award'
        ORDER BY ba.year DESC;

.. activecode:: joins_self_test_challenge2
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query giving a distinct list of book awards won by authors who have also won the Nobel Prize in Literature (an author award).
    ~~~~

.. reveal:: joins_self_test_challenge2_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT DISTINCT aw1.name
        FROM
          books AS b
          JOIN books_awards AS ba ON b.book_id = ba.book_id
          JOIN awards AS aw1 ON aw1.award_id = ba.award_id  -- book awards
          JOIN authors_awards AS aa ON b.author_id = aa.author_id
          JOIN awards AS aw2 ON aw2.award_id = aa.award_id  -- author awards
        WHERE aw2.name = 'Nobel Prize in Literature';

        SELECT DISTINCT aw1.name
        FROM
          books AS b,
          books_awards AS ba,
          awards AS aw1,         -- book awards
          authors_awards AS aa,
          awards AS aw2          -- author awards
        WHERE b.book_id = ba.book_id
        AND   aw1.award_id = ba.award_id
        AND   b.author_id = aa.author_id
        AND   aw2.award_id = aa.award_id
        AND   aw2.name = 'Nobel Prize in Literature';


|chapter-end|

----

**Notes**

.. [#] Because the database would be rather large (for use in your web browser) if we included all the known editions of all of the books in our database, the **editions** table only contains editions for books by author J.R.R. Tolkien.  The **editions** data is particularly "dirty", in the sense that there are many missing pieces of information, and the accuracy and completeness of the data are questionable. You can read more about the data and how it was collected in :ref:`Appendix A <appendix-a>`.

.. [#] You could argue that the **books** table should store an *array* of award ids, instead of just a single award id, thus solving the dilemma.  This is actually possible in a few database implementations that support array-valued columns.  However, the use of such columns is not without controversy.  For this textbook, we will take the more common approach of using cross-reference tables.

.. [#] Because a cross product has a number of rows equal to the number of rows in one table times the number of rows in the other table, the product is very large when the tables involved are large.  Even though databases typically convert explicit joins to their implicit equivalents internally, when database systems process joins they generally do not create the cross product and then apply the **WHERE** clause conditions, as that would be very slow and require a lot of memory or temporary storage.  However, the conceptual model is helpful in understanding the end result.

|license-notice|



## Chapter: data-modification.rst

.. _data-modification-chapter:

==============
Modifying data
==============

This chapter will explain the basic mechanisms for adding data to tables, removing data from tables, and modifying data.

Tables used in this chapter
:::::::::::::::::::::::::::

For this chapter, we will work with the tables **bookstore_inventory** and **bookstore_sales**, which simulate a simple database that a seller of used books might use.  The **bookstore_inventory** table lists printed books that the bookstore either has in stock or has sold recently, along with the condition of the book and the asking price.  The column **stock_number** is a unique identifier for each book.

When the bookstore sells a book, a record is added to the **bookstore_sales** table.  This table lists the **stock_number** of the book sold, the date sold, and the type of payment.  The column **receipt_number** is a unique identifier for the sale.  (This may not be a very good database design; it assumes we only sell one book at a time!)

A full description of these tables can be found in :ref:`Appendix A <appendix-a>`.

.. index:: INSERT INTO, INSERT, data; adding

Adding data using INSERT
::::::::::::::::::::::::

To add rows to a table in the database, we use a statement starting with the keyword **INSERT**.  In its simplest form, **INSERT** lets you add a single row to a table by providing a value for each column in the table as defined.  As an example, suppose a customer at our bookstore purchases our copy of *One Hundred Years of Solitude* by Gabriel García Márquez.  This book is listed in our inventory with a stock number of 1455.  The customer purchases the book on August 14, 2021 and pays cash.  Finally, we provide a receipt to the customer with receipt number 970.

In the database, the table **bookstore_sales** is defined with these columns:  **receipt_number**, **stock_number**, **date_sold**, and **payment**.

We could record the sale using this statement:

.. activecode:: data_modification_example_insert
    :language: sql
    :dburl: /_static/textbook.sqlite3

    INSERT INTO bookstore_sales
    VALUES (970, 1455, '2021-08-14', 'cash');

Try the above statement in the interactive tool, then use a **SELECT** query to verify that the new data has been added.  Note that the order in which the values are listed matches the order in which columns are defined for the **bookstore_sales** table.


Specifying columns
------------------

Performing the insert as we did above works fine when we know for certain how a table has been defined in a database.  However, tables change over time in practice, which may result in columns appearing in a different order, or in more columns being added to the table.  If this happens, old SQL code that makes assumptions about the table structure will break.  So it is a better practice to provide not only the data, but the names of the columns in which we want to put the data.  To do this, we simply list the column names in parentheses after the table name:

::

    INSERT INTO bookstore_sales (receipt_number, stock_number, date_sold, payment)
    VALUES (971, 1429, '2021-08-15', 'trade in');

As described in :numref:`Chapter {number} <table-creation-chapter>`, it is possible to have some of our columns be automatically generated by the database.  For example, if we add a new book to our inventory, we want to generate a new, unique stock number.  The **bookstore_inventory** table is set up to do this.  When the database generates values like this for us, we should not provide a value for the generated column.  Specifying column names lets us insert data for only the non-generated columns.

The **bookstore_sales** table is likewise set up to generate unique **receipt_number** values; above we provided values for the receipt number, which only works as long as the values we provide are not already used.  The **bookstore_sales** table also has a default setting for the **date_sold** column - it will put in today's date for you if you do not provide a value for the column.  Here is how the **bookstore_sales** table might be used in practice:

::

    INSERT INTO bookstore_sales (stock_number, payment)
    VALUES (1460, 'cash');

Inserting multiple rows
-----------------------

While it is perfectly valid to do multiple **INSERT** statements to add multiple rows of data, SQL also lets you provide multiple rows in a single **INSERT** statement.  Perhaps we wish to enter all of a day's sales in one statement.  We can enter this query:

::

    INSERT INTO bookstore_sales (stock_number, payment)
    VALUES
      (1444, 'credit card'),
      (1435, 'cash'),
      (1453, 'credit card')
    ;

(Note for Oracle users: Oracle does not permit multiple rows in an **INSERT**.)

.. index:: INSERT INTO ... SELECT

Inserting query results
-----------------------

SQL also provides the capability of providing values via a **SELECT** query.  As a somewhat contrived example, suppose we create another table named **bookstore_recent_sales** with columns named **author** and **title**. We will store data in this table about books we sold recently (perhaps to see what books and authors are popular, to inform our purchasing).  We might want to fill this table with the unique books that have been sold in the past month.

The syntax is the same as a regular **INSERT**, but with the **VALUES** clause replaced by a **SELECT** query (which must return columns of the same type and in the same order as the columns we are inserting into).  Try the statements below to see this in action.

::

    CREATE TABLE bookstore_recent_sales (author TEXT, title TEXT);

    INSERT INTO bookstore_recent_sales (author, title)
    SELECT DISTINCT i.author, i.title
    FROM
      bookstore_inventory AS i
      JOIN bookstore_sales AS s ON s.stock_number = i.stock_number
    WHERE s.date_sold BETWEEN '2021-08-01' AND '2021-08-31';

.. index:: DELETE, data; removing

Removing data with DELETE
:::::::::::::::::::::::::

Removing rows from a table is accomplished using **DELETE** statements.  **DELETE** statements are generally very simple, requiring only a **FROM** clause and optionally a **WHERE** clause.  You can delete data from only one table at a time.  As an example, if we want to remove all sales from **bookstore_sales** prior to August 1, 2021, we could write:

.. activecode:: data_modification_example_delete
    :language: sql
    :dburl: /_static/textbook.sqlite3

    DELETE FROM bookstore_sales
    WHERE date_sold < '2021-08-01';

This is probably a bad idea unless we first delete the data from **bookstore_inventory** for the books we are deleting - otherwise we might think that we still have those sold books.  Since we cannot delete data from multiple tables in one query (e.g., using a join) it may be tricky to see how to get rid of the appropriate rows from **bookstore_inventory**. The information about what rows we want to delete is actually in **bookstore_sales** (in the **date_sold** column).  The technique we need will be covered in :numref:`Chapter {number} <subqueries-chapter>` - using a subquery.  Here is the necessary query, given without explanation for now:

::

    DELETE FROM bookstore_inventory
    WHERE stock_number IN
      (SELECT stock_number FROM bookstore_sales
       WHERE date_sold < '2021-08-01')
    ;

In :numref:`Chapter {number} <constraints-chapter>` we will discuss other techniques for keeping multiple tables consistent with each other.

If the **WHERE** clause is omitted in a **DELETE** query, then all data from the table is removed.

As with any data modification statement, the effects of a **DELETE** statement are immediate and permanent.  To some extent, you can undo the result of an **INSERT** with a **DELETE** if you know which rows you inserted; however, it is impossible to restore deleted rows unless you have a backup of the data.  Thus, it is very important to be sure you are deleting only what you want to delete.  A simple way to test this before you perform a delete is to replace **DELETE** with **SELECT \*** in your statement - this will show you exactly the rows that your statement would delete.

Remember that with our interactive examples, any changes you make to this book's database only last for the current viewing session, so if you wish to restore the deleted data, you may do so by refreshing the page in your browser.

.. index:: UPDATE, SET, data; modifying

Modifying data with UPDATE
::::::::::::::::::::::::::

One of the most powerful capabilities SQL provides is data modification using **UPDATE** statements.  The form of an **UPDATE** is:

::

    UPDATE tablename
    SET
      column1 = expression1,
      column2 = expression2,
      ...
    [WHERE expressions]
    ;

Often, we may want to update a single row in our database.  For example, perhaps we examine one of the books in our bookstore inventory and decide that its condition is better than we initially thought.  Our copy of *Slow River* by Nicola Griffith (stock number 1460) is listed as in fair condition, with a price of 2 (in some unit of currency).  We want to upgrade the condition to "good" and raise the price to 2.50 at the same time:

.. activecode:: data_modification_example_update
    :language: sql
    :dburl: /_static/textbook.sqlite3

    UPDATE bookstore_inventory
    SET
      condition = 'good',
      price = 2.50
    WHERE stock_number = 1460;

We can also update multiple rows at a time.  Perhaps we mistakenly put in all sales for August 1, 2021 as July 31 instead.  We can fix these in one query:

::

    UPDATE bookstore_sales
    SET date_sold = '2021-08-01'
    WHERE date_sold = '2021-07-31';

Of course, this only works if none of the sales marked as July 31 were correct; we might have to be more clever with our **WHERE** clause if not.

The real power of **UPDATE**, though, is that the right hand side of the assignments in the **SET** clause can be expressions, and these expressions are based on the row being updated.  Hence, we can do something like the following:

::

    UPDATE bookstore_inventory
    SET price = price + 0.25;

This would raise the price of every book by 0.25.

.. index:: TRUNCATE, MERGE

Other data modification statements
::::::::::::::::::::::::::::::::::

SQL provides some other data modification statement types, which may or may not be supported in your database.  **TRUNCATE TABLE** removes all rows from a table, and is typically faster than **DELETE** (but can only be used to remove *all* rows).  **MERGE** is a somewhat complex operation that combines inserts, updates, and deletes, allowing synchronization of a table with another table or join of tables.  Neither of these operations is strictly necessary, given that the same results can be accomplished with **INSERT**, **UPDATE**, and **DELETE**.  We will not cover them further in this book.

Self-check exercises
::::::::::::::::::::

This section contains exercises on **INSERT**, **UPDATE**, and **DELETE**, using the **bookstore_inventory** and **bookstore_sales** tables. Keep in mind that the database we are using for these exercises is shared with the interactive examples above, so any changes you have applied in an interactive tool above are reflected in the database you use below.  If the results you get are not what you are expecting, you may need to reload this page in your browser to get a fresh copy of the database.

If you get stuck, click on the "Show answer" button below the exercise to see a correct answer.

.. activecode:: data_modification_self_test_insert
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a statement to add the book *House Made of Dawn* by N. Scott Momaday to the **bookstore_inventory** table.  Use 1471 for the stock number, 'like new' for the condition, and 4.75 for the price.
    ~~~~

.. reveal:: data_modification_self_test_insert_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        INSERT INTO bookstore_inventory (stock_number, author, title, condition, price)
        VALUES (1471, 'N. Scott Momaday', 'House Made of Dawn', 'like new', 4.75);


.. activecode:: data_modification_self_test_insert_as_select
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a statement to add all books by John Steinbeck (from our **books** table) into **bookstore_inventory** with a condition of 'new' and a price of 4.00.  Note that there is no good way to provide unique stock numbers for each of these books, but if you omit the **stock_number** column entirely, the **bookstore_inventory** table is set up to provide unique values automatically.
    ~~~~

.. reveal:: data_modification_self_test_insert_as_select_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        INSERT INTO bookstore_inventory (author, title, condition, price)
        SELECT a.name, b.title, 'new', 4.00
        FROM
          authors AS a
          JOIN books AS b ON a.author_id = b.author_id
        WHERE a.name = 'John Steinbeck';


.. activecode:: data_modification_self_test_delete
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a statement to remove all books from **bookstore_inventory** that are in 'fair' condition.
    ~~~~

.. reveal:: data_modification_self_test_delete_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        DELETE FROM bookstore_inventory
        WHERE condition = 'fair';


.. activecode:: data_modification_self_test_update_1
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a statement to change the payment type to 'cash' for the sale with receipt number 963.
    ~~~~

.. reveal:: data_modification_self_test_update_1_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        UPDATE bookstore_sales
        SET payment = 'cash'
        WHERE receipt_number = 963;


.. activecode:: data_modification_self_test_update_2
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a statement to set the price (in our bookstore inventory) for all books by Clifford Simak to a special sale price of 1.0.
    ~~~~

.. reveal:: data_modification_self_test_update_2_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        UPDATE bookstore_inventory
        SET price = 1.0
        WHERE author = 'Clifford Simak';


.. activecode:: data_modification_self_test_update_3
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a statement to double the price of all books in 'new' condition.
    ~~~~

.. reveal:: data_modification_self_test_update_3_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        UPDATE bookstore_inventory
        SET price = price * 2
        WHERE condition = 'new';



|chapter-end|


|license-notice|



## Chapter: table-creation.rst

.. _table-creation-chapter:

=============================
Data types and table creation
=============================

.. index:: table; creation

This chapter will discuss basic table creation, starting with an explanation of SQL data types.

.. index:: data; types, data type

Data types
::::::::::

The SQL standard defines several basic data types with which columns can be associated.  While most of the basic types exist in all relational database systems, actual implementation of the types varies quite a bit.  Most database systems define additional, non-standard types for various uses.  Unusually, SQLite is dynamically typed, and you can store values of any type in any column no matter how the column is defined.  For all of these reasons, you will want to consult your database system's documentation to understand the types available to you.  In this section we survey the major data types, without discussion of database compatibility; for more information, see Appendix B - :ref:`appendix-b-data-types`.

Numbers
-------

SQL provides support for several different types of numbers, each with different applications and limitations.  However, actual implementation of the standard varies quite a bit; see Appendix B - :ref:`appendix-b-number-types` for a full discussion of number types.

.. index:: data type; integer, INTEGER, INT, SMALLINT, BIGINT

Integers
########

SQL defines three integer types: **INTEGER**, **SMALLINT**, and **BIGINT**.  Implementations of these types vary, but it is not uncommon for **INTEGER** (often abbreviated as **INT**) to store 32-bit integers, **SMALLINT** 16-bit integers, and **BIGINT** 64-bit integers.  Not all databases recognize all of these types, but **INTEGER** is recognized by all of the databases considered for this book.  Additional integer types may be available for your database system.

.. index:: data type; exact decimal number, NUMERIC, DECIMAL, precision, scale

Exact decimal numbers
#####################

Decimal number types allow for exact storage of numbers that have digits to the right of the decimal point, e.g., 1234.56789.  These numbers are exact (unlike the floating point types described below) and permit exact mathematical operations where possible (addition, subtraction, and multiplication).  The two defined types for SQL are **NUMERIC** and **DECIMAL**, which are synonyms of each other.  These types may be defined with parameters representing *precision* and *scale*, where precision is the number of significant digits that can be stored, and scale is the number of digits following the decimal point.  If the precision is given, but not the scale, the scale defaults to zero.

For example, in most implementations:

- **NUMERIC(3, 2)** defines a type that can store the values between -999.99 and 999.99, with a maximum of 2 digits past the decimal point.
- **NUMERIC(4)** defines a type that can store integers between -9999 and 9999.
- **NUMERIC** defines a type that can exactly store decimal values with implementation-defined precision and scale.

Different implementations behave differently when an attempt is made to store values with more digits than are allowed by the specified precision and scale.  This may result in an error, or (in the case of too many digits to the right of the decimal point), it may result in rounding or truncation of the value.

Decimal number types are particularly important for the storage of monetary data, where exact addition, subtraction, and multiplication is necessary.

.. index:: data type; floating point number, FLOAT, REAL, DOUBLE, DOUBLE PRECISION

Floating point numbers
######################

Floating point number types allow for a possibly inexact storage of real numbers, similar (or sometimes identical to) the `IEEE 754`_ specification.  The SQL standard defines the types **FLOAT**, **REAL**, and **DOUBLE PRECISION** (often abbreviated **DOUBLE**), but implementation of these types vary.  These types can support extremely large and extremely small numbers, and are most useful in scientific and mathematical applications.

.. _`IEEE 754`: https://en.wikipedia.org/wiki/IEEE_754

.. index:: data type; character string, CHARACTER, CHAR, CHARACTER VARYING, VARCHAR, TEXT

Character string types
----------------------

There are several data types for storing character data in SQL; again, actual implementations vary.  See Appendix B - :ref:`appendix-b-string-types` for a full discussion of character string types.

The type **CHARACTER**, usually abbreviated as **CHAR**, is used for fixed-length strings.  The type **CHAR** is followed by parentheses enclosing the length of the string.  All values in a column of type **CHAR(4)**, for example, must contain exactly 4 characters.  In practice, many databases relax the "exactly" part of the definition and allow for shorter strings to be stored, although they may pad the value with trailing space characters.  Attempting to store strings longer than *n* usually results in an error.

**CHARACTER VARYING** is usually abbreviated as **VARCHAR**, and is used for strings of varying length up to some maximum, which must be specified just as with the **CHAR** type.  It is usually an error to attempt to store strings longer than the maximum.  (Note for Oracle users: Oracle strongly recommends using their **VARCHAR2** type rather than **VARCHAR**, although both types are recognized.)

Examples:

- **CHAR(5)** can store the strings ``'apple'``, ``'1 2 3'``, or ``'x    '`` (with four trailing spaces), but not ``'x'`` or ``'this is too long'``.
- **VARCHAR(5)** can store the strings ``'hello'``, ``'a b'`` or ``'y'``, but not ``'also too long'``.

One disadvantage to **VARCHAR** is the need to predict the maximum length of string that you might need to store.  Many databases now implement some type of arbitrary-length character string type, often named **TEXT**.  Some databases impose limitations on this type (such as not allowing its use for indexed columns).  Be sure to read your database implementation's documentation to understand these limitations before using **TEXT**; if you need portability between databases, it may be best to use **VARCHAR** with a generous size allocation.

.. index:: data type; date, data type; time, data type; timestamp

Date and time types
-------------------

Management of date and time data is a very complicated affair.  Calendars change over time and differ among cultures, time zones vary geographically, and "leap" adjustments to the calendar and clock occur irregularly.  SQL provides very robust date and time types along with operations on these types that allow for very precise storage and management of these values.  However, here again implementations vary, and you should read your database system's documentation to understand the fine points.  See Appendix B - :ref:`appendix-b-datetime-types` for a full discussion.

There is no standard syntax for date and time literals in SQL.  In most cases, strings in some implementation-defined format(s) are used to represent dates and times.  Internally, the values may be stored as decimal numbers - offsets from some fixed reference.  In this book we will simply use character strings conforming to the `ISO 8601`_ standard.  Using this format, dates can be usefully compared - ``'2001-04-10'`` is correctly less than ``'2014-01-22'`` - which also means we can put data in order by date columns.  Time values can be trickier due to the possible inclusion of time zones, but we will avoid these complications by simply ignoring them (there are no examples of time values in our database).

.. _`ISO 8601`: https://en.wikipedia.org/wiki/ISO_8601

.. index:: data type; Boolean, BOOLEAN, True, False

Additional data types
---------------------

Below is a list of some other data types you might encounter or wish to use in a SQL setting.  These are not supported by all database implementations.

- SQL defines a Boolean data type (**BOOLEAN**) which can store the literal values **True** and **False**, however, not all databases support this type.
- SQL also defines types designed to hold binary data.  This can sometimes be useful, although binary data such as images or music files take up a great deal of space. Thus, it is often preferable to store them externally, and only record the information needed to retrieve the files in the database  (e.g., a file path or URL).
- SQL provides for user-defined types; that is, custom data types created by the database user for specific applications.
- Many databases support types not defined in the SQL standard, or defined as optional extensions, such as types for storing and working with JSON and XML documents, geometric objects, geographical or spatial coordinates, arrays, and more.


Types in SQLite
---------------

As mentioned earlier, SQLite (used in the interactive examples in this book) allows the storage of arbitrary types of data into any column; no type checking is performed.  Essentially, a value in SQLite can be ``NULL``, an integer, a floating point number, or a character string.  However, SQLite supports standard SQL syntax for table creation, including specifying data types for columns; this type information can be viewed as a hint to the database user as to what kind of data should be stored.  We will consistently use types that you might find in other databases, and store data appropriate to those types in our examples.

.. index:: CREATE TABLE

Creating tables
:::::::::::::::

Once we have chosen the types for our columns, we can create a table using a **CREATE TABLE** statement.  For our first example, we will create something simple just for demonstration purposes.  You do not need to worry that we are changing the database - we are only working with a copy of the database that is created each time you load the textbook into your browser.  You can reload this page anytime you want to start fresh!

Creating a table from scratch
-----------------------------

Use the **CREATE TABLE** command to create a table.  For now, we will create a simple table by defining the columns in the table.  Later, we will add additional details to the table in the form of *constraints* and *defaults*.  The **CREATE TABLE** command looks like this:

::

    CREATE TABLE (
      column1 type1,
      column2 type2,
      ...
    );

Where "column*n*" is the name of a column, and "type*n*" is a data type that your database supports.  Here is some code to try out:

.. activecode:: table_creation_example_create
    :language: sql
    :dburl: /_static/textbook.sqlite3

    CREATE TABLE test (
      id INTEGER,
      x  VARCHAR(20),
      y  DATE,
      z  NUMERIC(10,2)
    );

    INSERT INTO test VALUES
      (0, 'this is a test', '2021-06-14', 1234.56),
      (1, 'apple', '2021-01-01', 10.10)
    ;

    SELECT * FROM test;

All database tools provide some mechanism for seeing the definition of tables in the database.  In SQLite, you can see the definition of tables by querying the special table **sqlite_master**:

::

    SELECT sql FROM sqlite_master WHERE name = 'test';

.. index:: table; removal, DROP TABLE

Dropping tables
---------------

We cannot **CREATE** a table when it already exists, so if you try to run the above example more than once (without reloading this page in your browser), you will get an error message.  We need to remove the object before re-creating it.  Removing an object from the database is called *dropping* the object, and is accomplished with a **DROP** statement:

::

    DROP TABLE test;

This statement will cause an error if you do it when there is no table named **test**, however.  This can be inconvenient, because we might want to drop and recreate the table many times when we are developing a database-modifying program, or *script*, but we may not always know the current state of the database.  Fortunately, most databases implement an extension to **DROP** that lets us remove the table if and only if it exists, without an error if it does not exist:

::

    DROP TABLE IF EXISTS test;

(Note for Oracle users: Oracle does not recognize this syntax.)

Note that dropping a table also destroys all data stored in the table, and this action is irrevocable (there is no "undo" operation).  This is one reason that database-modifying programs are usually developed and thoroughly tested by using a copy of a database before they are ever used on the "real" database.

.. index:: CREATE TABLE ... AS SELECT

Creating a table from a query
-----------------------------

From the perspective of SQL, the result of a **SELECT** query is essentially the same thing as a table.  The difference is that the **SELECT** result is not named and exists only temporarily.  SQL provides a way for us to save the result of a query as a named table, with the table columns defined implicitly based on the result columns.  Any **SELECT** query can be used.  Here is an example making a table from our **books** and **authors** tables:

.. activecode:: table_creation_example_create_as_select
    :language: sql
    :dburl: /_static/textbook.sqlite3

    -- good practice to always start with this
    DROP TABLE IF EXISTS recent_books;

    CREATE TABLE recent_books AS
      SELECT
        a.name AS author,
        b.title,
        b.publication_year
      FROM
        authors AS a
        JOIN books AS b ON a.author_id = b.author_id
      WHERE b.publication_year >= 2010
    ;

    SELECT sql FROM sqlite_master WHERE name = 'recent_books';

    SELECT * FROM recent_books;

(Note for SQL server users: SQL server does not support the above syntax.  The equivalent statement in SQL server looks like: ``SELECT ... INTO new_table FROM ... WHERE ...;``.)

.. index:: default, auto increment, sequence, DEFAULT, GENERATED ... AS IDENTITY

Defaults and auto increments
----------------------------

Table columns can be defined with additional properties that can enhance usage of the database in different ways.  In :numref:`Chapter {number} <constraints-chapter>`, we will talk about various *constraints* that can be used to restrict data to help ensure the validity of the database as a whole.  Another property we can add to a column is a *default* expression - an expression producing a value that will be provided by the database only when we do not provide a value.

Here is an example, showing the usage of the **DEFAULT** keyword:

.. activecode:: table_creation_example_default
    :language: sql
    :dburl: /_static/textbook.sqlite3

    DROP TABLE IF EXISTS test2;

    CREATE TABLE test2 (
      id INTEGER,
      greeting VARCHAR(15) DEFAULT 'Hello'
    );

    INSERT INTO test2 (id, greeting) VALUES (1, 'Good morning');
    INSERT INTO test2 (id, greeting) VALUES (2, NULL);
    INSERT INTO test2 (id) VALUES (3);

    SELECT * FROM test2;

As you can see, when we provided a value (or ``NULL``) for the column **greeting**, what we provided was stored.  When we did not provide the value, the default ``'Hello'`` was used.

In the simplest case, as above, we can provide a literal value for a column.  More commonly, we will use an expression, typically calling a function of some sort.  A common usage for this is to record the date and time when a record is added to the database.  Here we will use the **CURRENT_TIMESTAMP** function for this purpose:

::

    DROP TABLE IF EXISTS test3;

    CREATE TABLE test3 (
      purchase VARCHAR(10),
      created_at VARCHAR(20) DEFAULT CURRENT_TIMESTAMP
    );

    INSERT INTO test3 (purchase) VALUES ('apple');

    SELECT * FROM test3;

Default columns are also commonly used in combination with a special kind of database object called a *sequence*, which simply generates sequential integers.  This can be used, for example, to create unique identifiers for every row in a table.  This usage is so common that the SQL standard provides syntax that both creates the necessary sequence and sets up the default for the table; not all databases support this syntax, but most provide some mechanism for the generation of sequential values for a column.  The SQL standard syntax does not work in SQLite, so you will not be able to test it in an interactive tool in this book, but the column definition using this syntax is

::

    column_name type GENERATED BY DEFAULT AS IDENTITY

or

::

    column_name type GENERATED ALWAYS AS IDENTITY

The first form allows values to be provided by the user when inserting a row, just like a regular value.  The second form requires that the value always be provided by the database - it cannot be overridden by the user.

(Note: of the databases considered for this book, only PostgreSQL and Oracle support the standard syntax; they also provide equivalent mechanisms using different syntax.  For MySQL, see documentation on the AUTO_INCREMENT property of the INTEGER data type, and for SQL Server, see the IDENTITY option under CREATE TABLE.  For SQLite, see below.)

SQLite provides a mechanism which is similar to, but different from the standard.  In SQLite, we can create an integer column that automatically provides a new value using the **AUTOINCREMENT** keyword. If the user does not provide a value, the database supplies a value of 1 (if the table is empty) or 1 greater than the maximum value already stored.  To create a column of this type, the column must also be declared to be a primary key, a topic covered in :numref:`Chapter {number} <constraints-chapter>`.  Here is an example to try out:

::

    DROP TABLE IF EXISTS test4;

    CREATE TABLE test4 (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      greeting VARCHAR(15)
    );

    INSERT INTO test4 (greeting) VALUES ('Hello');
    INSERT INTO test4 (id, greeting) VALUES (4, 'Good day');
    INSERT INTO test4 (greeting) VALUES ('Good afternoon');

    SELECT * FROM test4;

In our database, the tables **bookstore_inventory** and **bookstore_sales** use auto increment columns; **bookstore_sales** also uses the **DEFAULT** property.

Self-check exercises
::::::::::::::::::::

This section contains exercises on table creation.  If you get stuck, click on the "Show answer" button below the exercise to see a correct answer.

.. activecode:: table_creation_self_test_create
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a statement to create a table named **my_table** with columns **a**, **b**, **c**, and **d**.  Column **a** will contain strings of at most 100 characters; **b** will contain dates; **c** will contain numbers with at most 15 digits, three of which come after the decimal point; and **d** will contain strings of exactly two characters.
    ~~~~

.. reveal:: table_creation_self_test_create_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        CREATE TABLE my_table (
          a VARCHAR(100),
          b DATE,
          c NUMERIC(15,3),
          d CHAR(2)
        );

.. activecode:: table_creation_self_test_drop
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a statement to remove **my_table**.
    ~~~~

.. reveal:: table_creation_self_test_drop_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        DROP TABLE my_table;

    or

    ::

        DROP TABLE IF EXISTS my_table;

.. activecode:: table_creation_self_test_create_as_select
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a statement to create a table named **a_authors** containing just authors whose names start with the letter 'A'.
    ~~~~

.. reveal:: table_creation_self_test_create_as_select_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        CREATE TABLE a_authors AS
          SELECT * FROM authors
          WHERE name LIKE 'A%'
        ;


|chapter-end|

----

..
 **Notes**

 .. [#] Relational databases allow operations to be wrapped in something called a *transaction*, which does provide a way to undo work.  We will study transactions more in chapter XXX.


|license-notice|



## Chapter: constraints.rst

.. _constraints-chapter:

====================
Keys and constraints
====================

In this chapter, we explore the different ways in which data may be constrained in order to help preserve the correctness of our data.

Tables used in this chapter
:::::::::::::::::::::::::::

Some examples in this chapter will use the **books** table and related tables (see :ref:`Appendix A <appendix-a>` for a full description of these tables).  Other examples will use tables created just for the example, then discarded.

.. index:: constraint, constraint; domain

Constraints
:::::::::::

As data is critical to so many organizations and applications, it is worth doing everything possible to ensure the correctness and consistency of the data in databases.  This can be achieved in many ways: application software can do checks to ensure data is entered and maintained correctly, separate programs can test and report on data consistency, and databases can enforce correctness using constraints and triggers.  (Triggers are actions the database can perform when certain events, such as an update to a row, occur; in some databases, the actions can even be complete small programs using implementation-specific programming languages.  This book does not cover triggers.)  We focus in this chapter on database constraints.

Constraints are properties of the database that restrict data in various ways.  One of the simplest types of constraints are *domain* constraints: data entered into a column is constrained to be of the type defined for the column.  (Domain constraints are not enforced in SQLite, so we cannot demonstrate using the book's database.)  Below we discuss constraints that enforce data properties for entire tables - primary and foreign key constraints - and those that apply to individual rows: not null, uniqueness, and check constraints.

.. index:: primary key - SQL, key - SQL; primary, constraint; primary key

Primary keys
::::::::::::

A *primary key* is a column or set of columns of a table which are required to contain unique values for each row stored in the table.  Controlling for uniqueness ensures that we can associate a specific, single item of data with data in another table by storing the key value in the other table. It also prevents unnecessary duplication of data that could result in incorrect statistics (for example, when taking counts or sums).  The id columns discussed in :numref:`Chapter {number} <joins-chapter>` - special columns used specifically to ensure each row can be uniquely identified - are commonly used as primary keys.  A table can have only one primary key.

Some examples can be found in our books database.  The table **authors**, for example, has **author_id** as a primary key.  The database will enforce the uniqueness property of the **author_id** column by preventing any data modification queries which would result in a duplicate primary key.  Deleting rows can never violate a primary key constraint, but inserts and updates can.  Either of the following queries will result in an error because there already exists a row in the database with **author_id** = 1:

.. activecode:: constraints_example_primary_key
    :language: sql
    :dburl: /_static/textbook.sqlite3

    INSERT INTO authors (author_id, name)
    VALUES (1, 'Charles Dickens');

    UPDATE authors SET author_id = 1 WHERE author_id = 2;

Because we need to compare primary key values to ensure uniqueness, it is also forbidden to insert ``NULL`` values into a primary key column.  (SQLite varies from this standard behavior, though. If you insert a ``NULL`` into an integer primary key column, SQLite will generate a unique value for you.  For other primary key column types, or multi-column primary keys, ``NULL`` values are permitted in SQLite.)

An example of a multi-column primary key can be found in the table **authors_awards**.  For this table, the primary key is the pair (**author_id**, **award_id**).  This does not mean that each column is a primary key, e.g., that each column is independently unique.  Instead, it is the pair of values which must be unique.  That is, you may not insert the pair ``(4, 10)`` twice, but you may insert all of ``(4, 10)``, ``(4, 11)``, and ``(5, 10)`` (assuming none of those pairs is already in the table).

.. index:: PRIMARY KEY, ALTER TABLE

Creating a primary key
-----------------------

There are a few ways to create a primary key on a table.  It is easiest to create a primary key when creating the table.  If the primary key is a single column, then you may simply put the phrase **PRIMARY KEY** at the end of the column definition:

::

      DROP TABLE IF EXISTS test;
      CREATE TABLE test (
        x VARCHAR(10) PRIMARY KEY
      );

You can also create the primary key as a separate entry in the table definition; you must use this form when creating a multi-column primary key.  The first definition below is equivalent to the one above, while the second creates a multi-column primary key:

::

    DROP TABLE IF EXISTS test2;
    DROP TABLE IF EXISTS test3;

    CREATE TABLE test2 (
      x VARCHAR(10),
      PRIMARY KEY (x)
    );

    CREATE TABLE test3 (
      x INTEGER,
      y INTEGER,
      PRIMARY KEY (x, y)
    );

Some database systems also allow the addition of a primary key to an existing table using the **ALTER TABLE** command, as long as the existing data would conform to the constraint.  **ALTER TABLE** can also be used to remove (drop) constraints from a table.  (SQLite does not support this usage.)

.. index:: foreign key, key - SQL; foreign, constraint; foreign key - SQL, constraint; referential integrity, referential integrity constraint, table; referencing, table; referenced


Foreign keys
::::::::::::

We are also interested in the relationships between data in different tables.  For example, every row in the **books** table has an **author_id** value which lets us look up author information in the **authors** table.  How can we ensure that the **author_id** value is valid, that is, that it always has a corresponding row in the **authors** table?  For a relational database, the solution is a *foreign key* constraint.

A foreign key constraint applies to a column or list of columns in one table (the *referencing* table), and references a column or list of columns in another table (the *referenced* table).  The constraint requires that one of two things be true:

- The values in the column or columns in the referencing table exist in the referenced column or columns
- The values in the column or columns in the referencing table are ``NULL``

The column or columns in the referenced table must be constrained to be unique, either by making them the primary key (the usual case), or through a uniqueness constraint (see below).

Our database defines a foreign key between **books** and **authors**.  The foreign key constraint is on the **author_id** column of **books** and references the **author_id** column of **authors**.  If we want to add a new book to **books**, we must add it with an **author_id** value, which must be a valid **author_id** from the **authors** table.  The foreign key by itself would allow a ``NULL`` **author_id** value, but we have further constrained the **author_id** column to not be null (using the **NOT NULL** constraint defined later on).

For example, the code below will fail due to the foreign key constraint on **books** referencing **authors**.  (Note that, unlike other database systems, SQLite will not enforce foreign keys unless you specifically tell it to - that is what the line of code below starting with the keyword **PRAGMA** is doing.  The **PRAGMA** keyword is not part of the SQL standard, and is only needed in SQLite.)

.. activecode:: constraints_example_foreign_key
    :language: sql
    :dburl: /_static/textbook.sqlite3

    PRAGMA foreign_keys = ON;

    INSERT INTO books (author_id, title)
    VALUES (99, 'Unknown');   -- 99 is not a valid author id

We also cannot do operations which would destroy existing relationships.  For example, there exist records in the **books** table for which the **author_id** = 1.  If we were to delete the author with this id value, we would violate the foreign key constraint on the **books** table.  We would also violate a similar foreign key constraint on **authors_awards**.  This code therefore produces an error:

::

    PRAGMA foreign_keys = ON;

    DELETE FROM authors WHERE author_id = 1;

However, if we first remove all books and awards for this author, we can successfully remove the author:

::

    PRAGMA foreign_keys = ON;

    DELETE FROM books WHERE author_id = 1;
    DELETE FROM authors_awards WHERE author_id = 1;
    DELETE FROM authors WHERE author_id = 1;

We similarly cannot drop the **authors** table without first dropping any referencing tables.

The **books** and **authors** examples demonstrate a common pattern, which is that foreign key constraints relate columns that we are likely to want to use in a join query (:numref:`Chapter {number} <joins-chapter>`).  This does not mean that a foreign key is a necessary condition for a join; one of the strengths of a relational database is that relationships between data do not have to be predetermined.  However, the presence of a foreign key is an indication that there exists a natural relationship between the data in the referencing and referenced tables.

Foreign key constraints are also known as *referential integrity constraints*.

.. index:: REFERENCES, FOREIGN KEY

Creating a foreign key constraint
---------------------------------

As with primary keys, there are multiple ways to create a foreign key constraint.  If the foreign key constrains a single column, then we can add it in the column definition for a table using the **REFERENCES** keyword:

::

    DROP TABLE IF EXISTS referencing;
    DROP TABLE IF EXISTS referenced;

    CREATE TABLE referenced (
      x INTEGER PRIMARY KEY
    );

    CREATE TABLE referencing (
      xx INTEGER REFERENCES referenced (x)
    );

Note that although the foreign key constraint only appears in the referencing table definition, the constraint affects both tables.  The code above ensures that values in the **xx** column of **referencing** are either ``NULL`` or contained in the **x** column of **referenced**.

(Note for MySQL users: MySQL does not recognize the single column syntax for creating foreign keys.  Use instead the explicit constraint syntax below.)

We can also create a foreign key constraint with a separate **FOREIGN KEY** entry in the table definition.  This form must be used for multi-column foreign keys:

::

    DROP TABLE IF EXISTS referencing2;
    DROP TABLE IF EXISTS referenced2;

    CREATE TABLE referenced2 (
      a VARCHAR(10),
      b VARCHAR(20),
      PRIMARY KEY (a, b)
    );

    CREATE TABLE referencing2 (
      c INTEGER PRIMARY KEY,
      aa VARCHAR(10),
      bb VARCHAR(10),
      FOREIGN KEY (aa, bb) REFERENCES referenced2 (a, b)
    );

In the above example, the *pair* (**aa**, **bb**) in **referencing2** must match a corresponding (**a**, **b**) pair in **referenced2**; the columns are not constrained independently.

Note that it is possible (and sometimes useful) to create a foreign key constraint in which the referencing and referenced tables are the same table.  For example, a company might have a table of employees that references itself:

::

    CREATE TABLE employees (
      id INTEGER PRIMARY KEY,
      name VARCHAR(100),
      supervisor_id INTEGER REFERENCES employees (id)
    );

As with primary keys, some database systems allow the addition or removal of foreign key constraints using the **ALTER TABLE** command.  (This usage is not supported by SQLite.)

.. index:: constraint; violation, ON [UPDATE|DELETE] CASCADE, ON [UPDATE|DELETE] SET NULL, ON [UPDATE|DELETE] RESTRICT

Enforcement mechanisms
----------------------

The default behavior for a foreign key constraint is to reject any attempt to modify data in a way that would violate the constraint.  However, SQL provides additional options that can be applied for **DELETE** or **UPDATE** queries.  Adding the phrase **ON DELETE SET NULL** to the foreign key constraint indicates that a deletion of a referenced table row should result in setting corresponding referencing key values to ``NULL`` (if permitted).  The phrase **ON DELETE CASCADE** indicates that referencing rows should be deleted along with the referenced row.  Similarly, **ON UPDATE SET NULL** results in setting referencing key values to ``NULL`` if the referenced key value is changed; **ON UPDATE CASCADE** changes the referencing key values to match the changed referenced key value.  Finally, if you want to use the default behavior explicitly, you can use **ON DELETE RESTRICT** and **ON UPDATE RESTRICT**.

Here is an example to try, using **CASCADE** for both deletions and updates (modify to try different settings):

::

    PRAGMA foreign_keys = ON;

    DROP TABLE IF EXISTS works;
    DROP TABLE IF EXISTS composers;

    CREATE TABLE composers (
      id INTEGER PRIMARY KEY,
      name VARCHAR(30)
    );

    INSERT INTO composers VALUES
      (1, 'Beethoven'),
      (2, 'Mozart')
    ;

    CREATE TABLE works (
      title VARCHAR(50),
      composer_id INTEGER REFERENCES composers (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
    );

    INSERT INTO works VALUES
      ('Symphony No. 1', 1),
      ('Symphony No. 2', 1),
      ('String Quartet No. 1', 2)
    ;

    DELETE FROM composers WHERE name = 'Beethoven';

    UPDATE composers SET id = 4 WHERE name = 'Mozart';

    SELECT * FROM composers;
    SELECT * FROM works;


Other constraints
:::::::::::::::::

SQL provides some additional constraints you may find useful, which are described in this section.

.. index:: constraint; uniqueness, UNIQUE

UNIQUE
------

Occasionally you may need to ensure that a column or set of columns contains unique values, but you do not want to set the column or columns as a primary key (for example, when some other set of columns is already the primary key).  The **UNIQUE** constraint can be used for this purpose; simply add the **UNIQUE** keyword as part of the column definition.  One difference between a **UNIQUE** constraint and a primary key constraint is that the **UNIQUE** constraint does not prevent ``NULL`` values. However, databases deal with ``NULL`` values in a unique column in different ways; some allow multiple rows to contain ``NULL``, and others allow only a single ``NULL`` row (effectively treating ``NULL`` as a comparable value).  Note that the final statement below will fail due to a violation of the **UNIQUE** constraint on column **x**.

.. activecode:: constraints_example_other
    :language: sql
    :dburl: /_static/textbook.sqlite3

    DROP TABLE IF EXISTS test4;
    CREATE TABLE test4 (
      x INTEGER UNIQUE
    );

    INSERT INTO test4 VALUES (1);
    INSERT INTO test4 VALUES (2);
    INSERT INTO test4 VALUES (1);

You can also create a **UNIQUE** constraint as a separate entry in the table definition (this is required for a multi-column constraint):

::

      DROP TABLE IF EXISTS test5;
      CREATE TABLE test5 (
        x INTEGER,
        y INTEGER,
        UNIQUE (x, y)
      );

Note that a primary key constraint on a set of columns already implies something stronger than **UNIQUE**, thus there is no need to specify **UNIQUE** if **PRIMARY KEY** is already in place.

.. index:: constraint; not null, NOT NULL

NOT NULL
--------

``NULL`` values can be a source of many data errors.  If some bug in your software incorrectly inserts ``NULL`` values into your database, the data becomes corrupt, and queries against the data may produce wrong answers. Also, since ``NULL`` values are not comparable, they tend to be "invisible" when querying, unless looked for specifically using **IS NULL**.   This combination of factors can result in many lost hours of work trying to resolve differences between what you believe is true and what your queries are telling you.

It can be valuable, then, to constrain columns to not allow ``NULL`` values at all, using the **NOT NULL** constraint.  In our database, one example is the **authors** table, which has a **NOT NULL** constraint on the **name** column - we always want a value in the **name** column [#]_.  You can find other examples in the books-related tables.

Note that **NOT NULL** is implied on all columns in a primary key, so there is no need to specify **NOT NULL** for those columns.

.. index:: constraint; check, CHECK

CHECK
-----

SQL provides a general constraint form that you can use to apply simple Boolean conditions on your data.  The **CHECK** constraint can be an expression involving a single column or multiple columns of the table.  This expression is typically limited in what else it can incorporate; for example subqueries are typically not allowed, and some databases do not allow function calls (implementations vary).

Here is an example, showing both single column and table constraint forms:

::

    DROP TABLE IF EXISTS test6;
    CREATE TABLE test6 (
      a INTEGER CHECK (a BETWEEN 0 AND 100),
      b INTEGER,
      CHECK (b > a)
    );

    INSERT INTO test6 VALUES (42, 200);
    INSERT INTO test6 VALUES (-1, 6);   -- error
    INSERT INTO test6 VALUES (10, 5);   -- error


..
  Behind the scenes
  :::::::::::::::::

  While **NOT NULL** and **CHECK** constraints affect single rows of data and can easily be verified when an **INSERT** or **UPDATE** is performed, key constraints and **UNIQUE** constraints require checks against entire tables.  In these cases, the constraint test fails (primary keys and **UNIQUE**) or succeeds (foreign keys) if a set of values matches some row in some table.  You might wonder how these checks can be performed efficiently in situations where the table to be tested contains very many rows.

  A full answer will have to wait until chapter XXX, but the short answer is that the data values we need to search to test our constraint are *indexed* - stored in a special data structure that allows us to find a particular value very fast, without having to examine every row.  Primary keys and columns constrained to be unique are automatically indexed by the database.  Using the index, the database can quickly detect if a duplicate value is about to be created.  To test a foreign key constraint, the database has to determine whether the data we are putting into the referencing table exists in the referenced table.  Since the referenced columns must either form a primary key or be constrained with **UNIQUE**, the data to be searched is indexed once again.

  Indexes are also very important in speeding up queries and statements of all kinds.  We can add additional indexes to the ones implied by our constraints in order to speed up specific searches or modifications.  We will discuss how to use indexes to improve the performance of queries and statements in chapter XXX.


|chapter-end|

----

**Notes**

.. [#] It is possible that we might wish to record some book for whom the author is unknown (or anonymous), which might seem like an instance in which we would want ``NULL``; after all, one possible meaning of ``NULL`` is "unknown".  However, what does it mean for an unknown author to have an entry in the **authors** table in the first place?   What meaning would we give, if any, to the birth and death date fields for the ``NULL`` author?  And what does it mean if multiple books relate to that author record?  Are they all by the same, unknown author, or by different authors, all of whom are unknown?  A slightly better choice for a book with no known author may be to allow ``NULL`` values in the **author_id** column in **books** - this is closer to the desired meaning.  However, this introduces problems of its own, such as the fact that an inner join of **books** and **authors** will now leave out any books with unknown authors, so we would need to be very careful in writing our queries.  None of this is to say that ``NULL`` is never the right choice, only that it introduces complexity and therefore more opportunity for software bugs and data corruption.  Consider your options carefully.


|license-notice|



## Chapter: subqueries.rst

.. _subqueries-chapter:

==========
Subqueries
==========

.. index:: subquery, subquery expression, nested query

A subquery is simply a **SELECT** query enclosed with parentheses and nested within another query or statement.  This *subquery expression* evaluates to a scalar, a row, a column, or a table, depending on the query results and the context in which the subquery appears.  In this chapter we discuss the many ways in which we can use the result of a query within another query.


Tables used in this chapter
:::::::::::::::::::::::::::

For this chapter we will be using the books dataset (tables **books**, **authors**, etc.), described in :ref:`Appendix A <appendix-a>`.

.. index:: scalar value, row value, row value constructor, table value

Scalars, rows, and tables
:::::::::::::::::::::::::

Before we discuss the uses of subqueries, it is useful to talk about some additional types of data that come up in SQL.  So far we have assumed that all expressions evaluate to a *scalar* value.  Scalar values are simple values of a single type, such as ``42`` or ``'hello'``.  We can also work with *row* values in SQL.  A row is just an ordered list of values.  We can write down a literal row (SQL calls these "row value constructors") by putting a comma-separated list of expressions between parentheses:

::

    (1, 'hello', 3.1415)

In most databases (but not SQLite), you can **SELECT** the above expression as a literal, with the result showing as a single column.

Rows can be used in comparison expressions. The two queries below are equivalent (although the second is probably preferred as a matter of style):

.. activecode:: subqueries_example_row_expressions
    :language: sql
    :dburl: /_static/textbook.sqlite3

    SELECT b.title
    FROM
      books AS b
      JOIN authors AS a ON a.author_id = b.author_id
    WHERE
      (a.name, b.publication_year) = ('V. S. Naipaul', 1961);

    SELECT b.title
    FROM
      books AS b
      JOIN authors AS a ON a.author_id = b.author_id
    WHERE a.name = 'V. S. Naipaul'
    AND b.publication_year = 1961;


We will see more useful applications of row expressions in the following sections.

Beyond rows, we can also think in terms of *tables* as values.  Here we are using "tables" to mean a collection of rows, not necessarily the named object living in the database.  The result from a **SELECT** query is a table in this sense.

.. index:: subquery; used in Boolean expression

Boolean expressions using subqueries
::::::::::::::::::::::::::::::::::::

To start with, we will examine Boolean expressions using subqueries.  These are appropriate for use within the **WHERE** clause of another query or statement.

Scalar or row result
--------------------

We can use a subquery in place of a scalar expression as long as we know the subquery will return a single row and column.  Let us return to an example from :numref:`Chapter {number} <joins-chapter>` using our **books** table: how can we find all books published in the same year as *The Three-Body Problem*?  We will use a subquery (the **SELECT** query inside the parentheses below) to first obtain the **publication_year** of *The Three-Body Problem*, and then we will use that result to get our list of books:

.. activecode:: subqueries_example_single_row
    :language: sql
    :dburl: /_static/textbook.sqlite3

    SELECT * FROM books WHERE publication_year =
      (SELECT publication_year
       FROM books
       WHERE title = 'The Three-Body Problem')
    ;

To see what is happening in this query, first execute the subquery on its own:

::

    SELECT publication_year
    FROM books
    WHERE title = 'The Three-Body Problem';

Since this particular query returns exactly one row and one column, we treat the result (the integer ``2008``) as a scalar value, and simply substitute the scalar in place of the subquery:

::

    SELECT * FROM books WHERE publication_year = 2008;

Note that this only works because we only have one book with the title *The Three-Body Problem*.  In general, it is not a good idea to assume a query will return a single row unless you use a **WHERE** clause condition on a column known to hold unique values, or unless you are computing an aggregate statistic over a set of rows (we will discuss aggregates in :numref:`Chapter {number} <grouping-chapter>`).  If multiple rows are returned by the subquery, the query will result in an error.  However, if zero rows are returned from the subquery, the result is considered to be ``NULL``, rather than an error.

This same approach works with row expressions, although the syntax is perhaps a bit inconsistent.  If a subquery would return multiple columns, then you need to use a row expression on the left-hand side of your comparison only.  That is, the below is correct SQL:

::

    SELECT * FROM books
    WHERE (author_id, publication_year) =
      (SELECT author_id, publication_year
       FROM books
       WHERE title = 'The Hundred Thousand Kingdoms')
    ;

Putting parentheses around the columns in the **SELECT** clause of the subquery will cause an error.

Comparisons with scalar results do not have to be equality; you can use any comparison operator instead:

::

    SELECT * FROM books
    WHERE publication_year >
      (SELECT publication_year FROM books
       WHERE title = 'Americanah')
    ;


Table or column result
----------------------

When a query can return multiple rows (a column or table), we have a different set of operators to work with.  In this section, we discuss the **IN** operator and the use of comparison operators with **ALL**, **ANY**, and **SOME**.  Another Boolean operator, **EXISTS**, will wait until we discuss correlated subqueries later in the chapter.  All of the operators that work with multiple rows also work on subqueries which return zero rows or one row.

.. index:: IN, NOT IN

IN
####

The **IN** operator lets us compare some expression to every row returned from a subquery.  If the expression equals any result from the subquery, then the **IN** expression evaluates to ``True``.  For example, we can ask our database for a list of books which have won awards (books with book ids matching some book id in the **books_awards** table):

.. activecode:: subqueries_example_multiple_rows
    :language: sql
    :dburl: /_static/textbook.sqlite3

    SELECT * FROM books WHERE book_id IN
      (SELECT book_id FROM books_awards)
    ;

SQL also provides the **NOT IN** operator as simply the Boolean inverse of **IN**.  We can get a list of books that did not win any of the awards listed in our database by a simple modification of the above query:

::

    SELECT * FROM books WHERE book_id NOT IN
      (SELECT book_id FROM books_awards)
    ;

The **IN** operator also works with row expressions, when we want to compare against multiple column subquery results.  Here is a query that asks for books published in the same year as the author's death.  (We are using the **substring** function as implemented by SQLite to get just the first four characters of each author's death date.  Although the substring is a character string and book publication years are stored as integers, SQLite is able to do an appropriate type conversion to make the comparison.)

::

    SELECT a.name AS author, b.title, b.publication_year
    FROM
      authors AS a
      JOIN books AS b ON a.author_id = b.author_id
    WHERE
      (a.author_id, b.publication_year) IN
        (SELECT author_id, substring(death, 1, 4) FROM authors)
    ;

As always, it can be helpful to execute the subquery separately to see what values it returns in order to better understand what the entire query is doing.

**IN** also has a useful application that does not involve a subquery.  If we follow **IN** with a comma-separated list of expressions inside parentheses, the operator will test the expression to the left of **IN** against every expression listed in the parentheses. Note that while the expression list looks like a row expression, it is very different; every expression in the list after **IN** should have a type compatible with the expression being compared.

For example, we might be interested in books by a few different authors:

::

    SELECT a.name AS author, b.title
    FROM
      books AS b
      JOIN authors AS a ON a.author_id = b.author_id
    WHERE author IN
      ('Virginia Woolf', 'Kazuo Ishiguro', 'Iris Murdoch');


If we want to compare multiple values (i.e., row expressions), we must use parentheses for each expression.  In this case, the general form of the expression is

::

    (expr1, expr2, ...) IN ((test11, test12, ...), (test21, test22, ...), ...)

.. index:: ALL, ANY, SOME

ALL, ANY, and SOME
##################

We can alternately use comparison operators in conjunction with the **ALL** or **ANY** or **SOME** keywords to compare an expression against the results of a subquery.  For example, we can ask again for books which have won awards by using the equality operator together with the **ANY** keyword as follows (note that the **ALL**/**ANY**/**SOME** keywords are not supported by SQLite, so you cannot test this within the textbook's interactive tools):

::

    SELECT * FROM books WHERE book_id = ANY
      (SELECT book_id FROM books_awards);

**SOME** is just a synonym for **ANY**.  The **IN** operator when used with subqueries is equivalent to **= ANY**.  However, **ANY** cannot be used with an expression list in the same way **IN** can.

In contrast, **ALL** requires that every row returned the subquery passes the comparison test.  For example, to find books published before all books by the author Willa Cather:

::

    SELECT * FROM books WHERE publication_year < ALL
      (SELECT publication_year FROM books WHERE author_id =
        (SELECT author_id FROM authors WHERE name = 'Willa Cather')
      )
    ;

Note here we have used a subquery inside another subquery!  We can nest subqueries in this fashion; we can also use multiple subqueries within a compound Boolean expression.

The **NOT IN** operator is equivalent to **<> ALL**.

.. index:: subquery; used in statement

Use in statements
-----------------

Subqueries do not have to be used only within other **SELECT** queries.  The use of subqueries within the **WHERE** clause of **DELETE** or **UPDATE** statements can be very powerful, often making up for the fact that we cannot do joins within those types of statements.  For example, we could use a subquery to remove any authors from our database for whom we have no books:

::

    DELETE FROM authors
    WHERE author_id NOT IN
      (SELECT author_id FROM books);

There are no rows matching this condition in the database (unless you add them), so the above query does not remove any rows, although it runs successfully.

.. index:: correlated subquery, subquery; correlated

Correlated subqueries
:::::::::::::::::::::

In all of our examples so far, we used subqueries which are executable on their own as separate **SELECT** queries.  The subquery can be executed once, with the result of the subquery substituted in its place in the outer query.  It is possible, however, to construct subqueries that are dependent on the outer query.  When a subquery references some attribute from the outer query in an expression, we say that the subquery is *correlated* with the outer query.

For example, consider the problem of finding books published after the author's death (posthumous books).  We previously saw a way of using a subquery to get books published in the same year as the author's death:

::

    SELECT a.name AS author, b.title, b.publication_year
    FROM
      authors AS a
      JOIN books AS b ON a.author_id = b.author_id
    WHERE
      (a.author_id, b.publication_year) IN
        (SELECT author_id, substring(death, 1, 4) FROM authors)
    ;

It is not clear how we can modify this query's **WHERE** clause to find books published *after* the author's death.  We want the author ids to match (equality), but we need a different operator (greater than) to compare the publication year with the author's death year.  What we want to do is, for each book in the outer query, compare its publication year to the death year of *its author only*.  To do this, we need our subquery to only return results relevant for the current row in the outer query - in this case, the subquery should return the scalar value representing the book's author's death year.

Here is the solution:

.. activecode:: subqueries_example_correlated
    :language: sql
    :dburl: /_static/textbook.sqlite3

    SELECT
      a1.name AS author, a1.death, b.title, b.publication_year
    FROM
      authors AS a1
      JOIN books AS b ON a1.author_id = b.author_id
    WHERE b.publication_year >
      (SELECT substring(death, 1, 4)
       FROM authors AS a2
       WHERE a2.author_id = a1.author_id)
    ;

Note that we have a situation where ambiguity must be resolved using aliasing - we have two instances of the **authors** table, one used in the outer query and one in the subquery.  If we simply refer to **author_id** in the subquery, SQL assumes we mean the subquery's **authors** table.  To refer to the outer query's **authors** table, we must give it an alias (**a1**) to distinguish it.  While not necessary, we have chosen to alias the subquery's table (**a2**) as well, to avoid any chance of confusion.

As you can see, we can no longer run the subquery independent of the outer query.  In effect, we are running the subquery over and over again, once for each row we encounter in the outer query.

As in this example, correlated subqueries tend to be most useful when both the outer query and the subquery work with the same table.  When the outer query and subquery work with different tables, it is typically possible to write the query as uncorrelated.

.. index:: EXISTS, NOT EXISTS

EXISTS
------

The **EXISTS** operator precedes a subquery, which is the only operand.  An **EXISTS** expression evaluates to ``True`` only if the subquery returns one or more rows.  The actual data from the subquery is ignored, so you can put anything you want in the **SELECT** clause.  We will use a constant ``1`` in our examples, just to emphasize that the data we are returning is unimportant.

Many uncorrelated subqueries can be rewritten as correlated subqueries using **EXISTS**.  For example, to find all books that have won awards, we can either write

::

    SELECT * FROM books WHERE book_id IN
      (SELECT book_id FROM books_awards)
    ;

as we did earlier, or, using **EXISTS**:

::

    SELECT * FROM books AS b WHERE EXISTS
      (SELECT 1
       FROM books_awards AS ba
       WHERE ba.book_id = b.book_id)
    ;

You can also use **NOT EXISTS**, which evaluates to the Boolean inverse of **EXISTS**.

Subqueries in other clauses
:::::::::::::::::::::::::::

We have seen numerous examples of subqueries used in **WHERE** clauses.  However, subquery expressions can be used in other contexts.  In particular, subqueries returning scalars can be useful in **SELECT** clauses and in the **SET** clauses of **UPDATE** statements.  Subqueries returning tables can also be used in place of named tables in the **FROM** clause of a **SELECT** clause.

.. index:: subquery; used in SELECT clause

SELECT
------

Used in a **SELECT** clause, subqueries can be used to retrieve values that are not easily obtained from the tables used in the outer query.  Used in this way, the subquery must return a scalar.  These subqueries are almost always correlated, as we want to return a value that is specific to each row.

For example, in a listing of books, we might want to include the total number of books written by the author.  For this we will use the aggregate expression **COUNT(\*)**, which simply counts the number of rows matching the **WHERE** clause in a **SELECT** query [#]_.  (Aggregates are discussed fully in :numref:`Chapter {number} <grouping-chapter>`.)

.. activecode:: subqueries_example_other_clauses
    :language: sql
    :dburl: /_static/textbook.sqlite3

    SELECT
      a.name AS author,
      (SELECT COUNT(*) FROM books AS b2 WHERE b2.author_id = a.author_id)
        AS author_total,
      b1.title
    FROM
      authors AS a
      JOIN books AS b1 ON b1.author_id = a.author_id
    ;


.. index:: subquery; used in update

SET
---

Used in the **SET** clause of an **UPDATE** statement, subqueries provide a way to work around the issue that we cannot use joins in an **UPDATE**.  If we want to update rows in some table with data from a second table, we can simply use a subquery to obtain the proper value.

As an example, in preparation of this book's database, a statement was run to populate the **publication_year** column of **books** using book edition information.  (The **editions** table in the database only has entries for a few books, to keep the size manageable, but the original database had complete data.)  This statement uses another aggregate expression to obtain the earliest publication year from the editions table for each book:

::

    UPDATE books
    SET publication_year =
      (SELECT MIN(publication_year)
       FROM editions
       WHERE books.book_id = editions.book_id)
    ;

Note: if you run the statement above, you will update most books to have a ``NULL`` publication year - when the subquery returns zero rows, the result is interpreted as ``NULL``.  (Do not worry if you executed this statement - changes are only made to a copy of the data.  You can obtain an unmodified copy of the database by refreshing your browser window.)  You can modify the statement to only update rows for which we have editions data using another subquery:

::

    UPDATE books
    SET publication_year =
      (SELECT MIN(publication_year)
       FROM editions
       WHERE books.book_id = editions.book_id)
    WHERE EXISTS
      (SELECT 1 FROM editions WHERE books.book_id = editions.book_id)
    ;

.. index:: subquery; used in FROM clause

FROM
----

Subqueries can also be used within the **FROM** clause of a **SELECT** query, in which case the subquery result acts like a table containing exactly the data returned by the subquery.  In this usage, the subquery expression *must* be given a name using aliasing.  The subquery cannot be correlated!  The subquery expression can be used to obtain computed data not available in any table in the database.  For example, above we used a correlated subquery to retrieve author's book counts on a row-by-row basis to go with each book title.  We could instead compute all author totals using an uncorrelated subquery, and then join each to the result as if it were a table.  (Here the subquery uses both grouping and aggregation, covered in :numref:`Chapter {number} <grouping-chapter>`.)

::

    SELECT
      a.name AS author,
      c.count AS author_total,
      b.title
    FROM
      authors AS a
      JOIN books AS b ON b.author_id = a.author_id
      JOIN
        (SELECT author_id, COUNT(*) AS count
         FROM books
         GROUP BY author_id) AS c
        ON c.author_id = a.author_id
    ;

.. index:: subquery; compared to join, join; compared to subquery

Comparison with joins
:::::::::::::::::::::

Subqueries are comparable to joins in the sense that they both involve multiple tables.  There are many cases in which a subquery can substitute for a join or vice-versa.  However, there are some subtle differences.

First, of course, is that short of using **SELECT** clause subqueries, you can only return data that actually appears in the outer query's tables.  If you need your result to contain data contained in multiple tables, it is generally best to join the tables rather than using **SELECT** clause subqueries.  (The example used above of a **SELECT** clause subquery is an exception, since the data we pulled in was not actually stored in any table.)  Using a separate subquery for each column needed is unwieldy, hard to read, and probably inefficient.

On the other hand, if you are retrieving data from one table only, it is sometimes advantageous to use a subquery.  Consider these two queries to retrieve books that have won awards:

.. activecode:: subqueries_example_comparison
    :language: sql
    :dburl: /_static/textbook.sqlite3

    SELECT * FROM books WHERE book_id IN
      (SELECT book_id FROM books_awards)
    ORDER BY title;

    SELECT b.*
    FROM
      books AS b
      JOIN books_awards AS ba ON ba.book_id = b.book_id
    ORDER BY b.title;

Both queries return the same data, but the second query has duplicate rows - each book appears once for each award it has won.  In the first query, the **IN** operator merely tests for the presence of a book in the awards table, not how many times it appears, so duplicates are avoided.

The **NOT EXISTS** and **NOT IN** operators are particularly interesting in that they can provide clean solutions to questions that otherwise require an outer join, such as listing the books which have *not* won awards.

In many cases, though, you have choices in how you approach a query.  Which you use depends on your personal preference and style.  Here are three different queries for finding books published in the same year as the author's death - one using an uncorrelated subquery (repeated from above), one using a correlated subquery with **EXISTS**, and one using a join:

::

    SELECT a.name AS author, b.title, b.publication_year
    FROM
      authors AS a
      JOIN books AS b ON a.author_id = b.author_id
    WHERE
      (a.author_id, b.publication_year) IN
        (SELECT author_id, substring(death, 1, 4) FROM authors)
    ;

    SELECT a1.name AS author, b.title, b.publication_year
    FROM
      authors AS a1
      JOIN books AS b ON a1.author_id = b.author_id
    WHERE EXISTS
      (SELECT 1
       FROM authors AS a2
       WHERE a2.author_id = a1.author_id
       AND substring(a2.death, 1, 4) = b.publication_year)
    ;

    SELECT a1.name AS author, b.title, b.publication_year
    FROM
      authors AS a1
      JOIN books AS b ON a1.author_id = b.author_id
      JOIN authors AS a2 ON
        a2.author_id = a1.author_id
        AND substring(a2.death, 1, 4) = b.publication_year
    ;


Self-check exercises
::::::::::::::::::::

This section contains some exercises using the books data set (reminder: you can get full descriptions of all tables in :ref:`Appendix A <appendix-a>`).  If you get stuck, click on the "Show answer" button below the exercise to see a correct answer.  There are many ways to answer these questions; try to use at least one subquery for each.

.. activecode:: subqueries_self_test_scalar_1
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query to list books (title, publication_year) by the author Viet Thanh Nguyen.
    ~~~~

.. reveal:: subqueries_self_test_scalar_1_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT title FROM books WHERE author_id =
          (SELECT author_id FROM authors WHERE name = 'Viet Thanh Nguyen')
        ;


.. activecode:: subqueries_self_test_scalar_2
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query giving the author of *How We Became Human*.
    ~~~~

.. reveal:: subqueries_self_test_scalar_2_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT name FROM authors WHERE author_id =
          (SELECT author_id FROM books WHERE title = 'How We Became Human')
        ;


.. activecode:: subqueries_self_test_scalar_3
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query to list authors born after the death of author Albert Camus.
    ~~~~

.. reveal:: subqueries_self_test_scalar_3_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT name FROM authors WHERE birth >
          (SELECT death FROM authors WHERE name = 'Albert Camus')
        ;


.. activecode:: subqueries_self_test_in_1
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query to list books for which we have editions information.
    ~~~~

.. reveal:: subqueries_self_test_in_1_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT * FROM books WHERE book_id IN
          (SELECT book_id FROM editions)
        ;


.. activecode:: subqueries_self_test_in_2
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query to list the titles of books by living authors (assume a ``NULL`` death date means the author is living).
    ~~~~

.. reveal:: subqueries_self_test_in_2_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT title FROM books WHERE author_id IN
          (SELECT author_id FROM authors WHERE death IS NULL)
        ;


.. activecode:: subqueries_self_test_challenge_1
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query to list the authors who have won the Nobel Prize in Literature (an author award).
    ~~~~

.. reveal:: subqueries_self_test_challenge_1_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT name FROM authors WHERE author_id IN
          (SELECT author_id FROM authors_awards WHERE award_id =
            (SELECT award_id FROM awards WHERE name = 'Nobel Prize in Literature'))
        ;


.. activecode:: subqueries_self_test_challenge_2
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query to list the authors whose books have won any kind of Pulitzer prize (a book award starting with the string 'Pulitzer').
    ~~~~

.. reveal:: subqueries_self_test_challenge_2_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT name FROM authors WHERE author_id IN
          (SELECT author_id FROM books WHERE book_id IN
            (SELECT book_id FROM books_awards WHERE award_id IN
              (SELECT award_id FROM awards WHERE name LIKE 'Pulitzer%')))
        ;


.. activecode:: subqueries_self_test_challenge_3
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query to list authors who have won book awards but not author awards.
    ~~~~

.. reveal:: subqueries_self_test_challenge_3_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT name
        FROM authors
        WHERE author_id IN
          (SELECT author_id FROM books WHERE book_id IN
            (SELECT book_id FROM books_awards))
        AND author_id NOT IN
          (SELECT author_id FROM authors_awards)
        ;


.. activecode:: subqueries_self_test_challenge_4
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query to find books by authors with only one book (according to our database).  *Hint*: one way is to ask, for each book, whether there exist *other* books by the same author.
    ~~~~

.. reveal:: subqueries_self_test_challenge_4_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT a.name, b1.title
        FROM
          authors AS a
          JOIN books AS b1 ON a.author_id = b1.author_id
        WHERE NOT EXISTS
          (SELECT 1
           FROM books AS b2
           WHERE b2.author_id = b1.author_id
           AND b2.book_id <> b1.book_id)
        ORDER BY a.name;  -- to make it easier to verify


.. activecode:: subqueries_self_test_challenge_5
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query to list all awards (either author awards or book awards) won by author J. M. Coetzee.
    ~~~~

.. reveal:: subqueries_self_test_challenge_5_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT name
        FROM awards
        WHERE award_id IN
          (SELECT award_id FROM authors_awards WHERE author_id =
            (SELECT author_id FROM authors WHERE name = 'J. M. Coetzee'))
        OR award_id IN
          (SELECT award_id FROM books_awards WHERE book_id IN
            (SELECT book_id FROM books WHERE author_id =
              (SELECT author_id FROM authors WHERE name = 'J. M. Coetzee')))
        ;



|chapter-end|

----

**Notes**

.. [#] For this particular problem, we could instead use something called a *window function*, which will be discussed briefly in :numref:`Chapter {number} <advanced-sql-chapter>`.



|license-notice|



## Chapter: grouping-and-aggregation.rst

.. _grouping-chapter:

========================
Grouping and aggregation
========================

Previous chapters have focused on mechanisms for storing and retrieving data.  SQL also provides facilities for simple analyses of the data.  In this chapter, we discuss methods of partitioning data and computing simple statistics on the partitions.


Tables used in this chapter
:::::::::::::::::::::::::::

For this chapter, we will primarily work with the tables **bookstore_inventory** and **bookstore_sales**, which simulate a simple database that a seller of used books might reference.  The **bookstore_inventory** table lists printed books that the bookstore either has in stock or has sold recently, along with the condition of the book and the asking price.  When the bookstore sells a book, a record is added to the **bookstore_sales** table.  This table lists the **stock_number** of the book sold, the date sold, and the type of payment.  The column **stock_number** is a unique identifier for each book in the inventory, and can be used to join the tables.

We will also use the **authors** table to illustrate the interaction of ``NULL`` with aggregate functions.

A full description of these tables can be found in :ref:`Appendix A <appendix-a>`.

.. index:: aggregate statistic, aggregate function, COUNT, SUM, AVG, MIN, MAX

Aggregate statistics
::::::::::::::::::::

*Aggregate statistics* are values computed on entire sets of data.  Counts, sums, and averages are examples of aggregate statistics.  SQL provides a number of aggregate functions for computing such statistics.  This section will cover some of the most commonly used functions; for documentation on all of the aggregate functions defined by SQL, see Appendix B - :ref:`appendix-b-aggregate-functions`.

We start by using the **COUNT** aggregate function to illustrate the basic rules for aggregate functions.  At its simplest, **COUNT** can be used to return the number of rows in a table:

.. activecode:: grouping_example_aggregate
    :language: sql
    :dburl: /_static/textbook.sqlite3

    SELECT COUNT(*) FROM bookstore_sales;

If you add a **WHERE** clause, **COUNT** will only consider rows matching the **WHERE** clause:

::

    SELECT COUNT(*)
    FROM bookstore_sales
    WHERE payment = 'cash';

The use of **\*** within the aggregate function is unique to **COUNT**; it simply means that we want to count rows, rather than any particular column.  Other aggregate functions require application to a column or expression.  When applied to a column or expression, **COUNT** and the other aggregate functions ignore ``NULL`` values.  For example, observe the result when applying **COUNT** to different columns of the **authors** table:

::

    SELECT COUNT(*), COUNT(author_id), COUNT(birth), COUNT(death)
    FROM authors;

In each of the results above, we obtain a single number for each function in the **SELECT** clause.  Only one row is returned, because we are (at the moment) applying the aggregate function to all rows matching the (optional) **WHERE** clause.  This row represents a *summary* of the data.  As a summary, details of the data cannot be included; it is an error to try to retrieve any expressions on the columns other than aggregates, when any aggregate function is used.  The following query will result in an error in every database except SQLite:

::

    SELECT title, COUNT(*) FROM bookstore_inventory;

While SQLite does not give us an error, the data returned demonstrates why this is an error in most databases; the returned **title** value represents just one row of the table, while the **COUNT(\*)** value is a summary of the whole table.  These two things do not match.

In addition to **COUNT**, the most common aggregate functions implemented by SQLite are **SUM**, **AVG**, **MIN**, and **MAX**.  SQL defines a number of other aggregate functions as well, including statistical functions such as variance and standard deviation.  As with **COUNT**, the argument of the function is a column or expression, which is evaluated for every row; ``NULL`` values are discarded.  For all aggregates except **COUNT**, if the argument evaluates to ``NULL`` for every row, then the result is ``NULL`` (for **COUNT** the result is zero).

You can probably guess the meaning of these aggregate functions:

- **SUM** computes the sum, and can only be applied to numbers
- **AVG** computes the average, and can only be applied to numbers
- **MIN** finds the minimum value according to the normal sort order for the value type
- **MAX** finds the maximum value according to the normal sort order for the value type

We can apply all of these to the **price** column of **bookstore_inventory**:

::

    SELECT COUNT(price), SUM(price), AVG(price), MIN(price), MAX(price)
    FROM bookstore_inventory;

In addition to ignoring ``NULL`` values, it is possible to indicate that duplicate values should be ignored by putting the **DISTINCT** keyword before the argument of the aggregate function.  This is mostly useful when combined with **COUNT**.  For example, if we want to know the total number of books versus the number of unique titles in our inventory, we could write:

::

    SELECT COUNT(title), COUNT(DISTINCT title) FROM bookstore_inventory;

.. index:: grouping, GROUP BY

Grouping
::::::::

Aggregates can be very useful when applied to an entire table or to a set of rows matching a **WHERE** clause.  Sometimes, though, we want more than one count, or sum, or average from a table; we may want these statistics over some subsets of rows, organized by some common attribute.  For example, our **bookstore_inventory** table includes books in different conditions; we might be interested in the average price we are charging for books in "good" condition separately from books in "fair" condition, and so forth.

SQL provides the **GROUP BY** clause for this purpose.  **GROUP BY** lets us specify an attribute, such as the condition of a book, by which to organize a table into *groups*.  Membership in a specific group is based on the **GROUP BY** expression; all members of a group share the same value for the expression.  The groups form a *partition* of the data; every row (matching the optional **WHERE** clause, if used) is assigned to a group, and no row is assigned to more than one group.

With **GROUP BY** in effect, we can now retrieve information about each group as a whole; each row of our output will represent information about one group.  If we put an aggregate function expression in our **SELECT** clause, the aggregate is applied to each group's rows separately.  In addition to aggregates, we can **SELECT** the **GROUP BY** expression - this is allowed (and makes sense) because all of the rows in each group will have the same value for the expression. You usually want to include the grouping expression as a label for the group - otherwise you will not know what group each aggregate expression belongs to!

The **GROUP BY** clause comes immediately after the **WHERE** clause, or after **FROM** if there is no **WHERE** clause.  Here is an example of grouping on our bookstore inventory by book condition:

.. activecode:: grouping_example_grouping
    :language: sql
    :dburl: /_static/textbook.sqlite3

    SELECT condition, COUNT(*), AVG(price)
    FROM bookstore_inventory
    GROUP BY condition;

If we want to exclude books that have already been sold, we could add a **WHERE** clause (here we use a subquery as discussed in :numref:`Chapter {number} <subqueries-chapter>`):

::

    SELECT condition, COUNT(*), AVG(price)
    FROM bookstore_inventory
    WHERE stock_number NOT IN
      (SELECT stock_number FROM bookstore_sales)
    GROUP BY condition;

It is also possible to group by more than one expression, in which case each group is defined by a unique setting for all of the expressions.  Our **bookstore_sales** table contains information about the date in which a book was sold, as well as the type of payment used in the purchase.  We might be very interested in knowing sales totals by month, or by type of payment, or both.  To get the price that was paid, we will have to join in the **bookstore_inventory** table.

To start with, let's retrieve sales totals by month (here we will use SQLite's substring() function to extract the 2-digit month number; in other databases it may be possible to extract a month by name):

::

    SELECT
      substring(s.date_sold, 6, 2) AS month,
      SUM(i.price) AS total_sales
    FROM
      bookstore_sales AS s
      JOIN bookstore_inventory AS i ON s.stock_number = i.stock_number
    GROUP BY month;

Note that we can use the alias "month" defined in our **SELECT** clause in our **GROUP BY** clause without having to rewrite the function expression.

Now, let's break down our total sales by type of month *and* type of payment:

::

    SELECT
      substring(s.date_sold, 6, 2) AS month,
      s.payment,
      SUM(i.price) AS total_sales
    FROM
      bookstore_sales AS s
      JOIN bookstore_inventory AS i ON s.stock_number = i.stock_number
    GROUP BY month, s.payment
    ORDER BY month, s.payment;

Here we have sorted by our grouping expressions as well, just to ensure that our groups come out in a consistent fashion.

.. index:: HAVING

Filtering grouped data
----------------------

When we group, we are generating a new set of rows representing the groups present in our data.  If we include a **WHERE** clause in our query, it is applied to the data *before* grouping.  The **WHERE** clause, then, cannot be used to filter the set of rows produced by grouping.  If we want to filter the grouped data, we must do so using a **HAVING** clause.

The **HAVING** clause works just like the **WHERE** clause, but applies to the set of rows generated by grouping.  Using **HAVING**, we can filter by expressions available to us after grouping: any expressions that we grouped by (our group labels), or aggregate functions on the groups.  The **HAVING** clause comes after the **GROUP BY** clause.

Here we use **HAVING** to list books for which we have more than one copy in our bookstore inventory, in order by the number of copies:

::

    SELECT author, title, COUNT(*)
    FROM bookstore_inventory
    GROUP BY author, title
    HAVING COUNT(*) > 1
    ORDER BY COUNT(*) DESC;

We can, of course, use both **WHERE** and **HAVING** in the same query - here we group books that have not been sold by author and title; then we report  the titles (groups) with multiple copies:

::

    SELECT author, title, COUNT(*)
    FROM bookstore_inventory
    WHERE stock_number NOT IN
      (SELECT stock_number FROM bookstore_sales)
    GROUP BY author, title
    HAVING COUNT(*) > 1;


Self-check exercises
::::::::::::::::::::

This section contains exercises on grouping and aggregation, using the **bookstore_inventory** and **bookstore_sales** tables.  If you get stuck, click on the "Show answer" button below the exercise to see a correct answer.

.. activecode:: grouping_self_test_count
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query to count the number of books in our inventory by the author Toni Morrison.
    ~~~~

.. reveal:: grouping_self_test_count_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT COUNT(*) FROM bookstore_inventory WHERE author = 'Toni Morrison';


.. activecode:: grouping_self_test_statistics
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query to find the minimum, maximum, and average price of a book in 'good' condition.
    ~~~~

.. reveal:: grouping_self_test_statistics_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT MIN(price), MAX(price), AVG(price)
        FROM bookstore_inventory
        WHERE condition = 'good';


.. activecode:: grouping_self_test_distinct
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query to find out how many different authors have written books in our inventory.
    ~~~~

.. reveal:: grouping_self_test_distinct_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT COUNT(DISTINCT author) FROM bookstore_inventory;


.. activecode:: grouping_self_test_grouping_1
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query to get the average price of a book, by author; sort by highest average price first.
    ~~~~

.. reveal:: grouping_self_test_grouping_1_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT author, AVG(price)
        FROM bookstore_inventory
        GROUP BY author
        ORDER BY AVG(price) DESC;


.. activecode:: grouping_self_test_grouping_2
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query to get the average price of a book, by author and condition; sort by author and condition.
    ~~~~

.. reveal:: grouping_self_test_grouping_2_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT author, condition, AVG(price)
        FROM bookstore_inventory
        GROUP BY author, condition
        ORDER BY author, condition;


.. activecode:: grouping_self_test_grouping_3
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query to give the number of books sold and the total sales from those books, grouped by condition.  Exclude books for the payment type 'trade in'.
    ~~~~

.. reveal:: grouping_self_test_grouping_3_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT i.condition, COUNT(*) AS books_sold, SUM(i.price) AS sales
        FROM
          bookstore_inventory AS i
          JOIN bookstore_sales AS s ON s.stock_number = i.stock_number
        WHERE s.payment <> 'trade in'
        GROUP BY i.condition;


.. activecode:: grouping_self_test_having
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query to find which authors' books have an average price less than 3 units of currency.
    ~~~~

.. reveal:: grouping_self_test_having_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT author, AVG(price)
        FROM bookstore_inventory
        GROUP BY author
        HAVING AVG(price) < 3;


.. activecode:: grouping_self_test_challenge_1
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query to get the difference between the maximum and minimum price of a book for each possible book condition.
    ~~~~

.. reveal:: grouping_self_test_challenge_1_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT condition, MAX(price) - MIN(price)
        FROM bookstore_inventory
        GROUP BY condition;


.. activecode:: grouping_self_test_challenge_2
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query to find the maximum price of any book in our inventory and list the books with that price.  *Hint*: you will need to use a subquery for this one.
    ~~~~

.. reveal:: grouping_self_test_challenge_2_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT * FROM bookstore_inventory WHERE price =
          (SELECT MAX(price) FROM bookstore_inventory);




|chapter-end|


|license-notice|



## Chapter: set-operations.rst

.. _sets-chapter:

==============
Set operations
==============
.. index:: set operation - SQL

Relational database theory is based on mathematical set theory.  Even though relational database implementations stray from the theory in some important regards, the notion of sets remains important.  In this chapter, we examine the three set operations available to us in SQL.

Tables used in this chapter
:::::::::::::::::::::::::::

For this chapter we will be using the books dataset (tables **books**, **authors**, etc.), which is described in :ref:`Appendix A <appendix-a>`.

.. index:: set; defined

Sets refresher
::::::::::::::

If you are already familiar with sets, and with basic operations on sets (union, intersection, and set difference), then you can skip this section.  Otherwise, please continue reading for some very basic background.

A *set* is a mathematical object that represents a collection of distinct values.  For a given set and any value, we can ask whether or not the set contains the value.  Sets can be defined by some property that values have in common, or simply by listing all of the values in the set.  For example, in the figure below, the blue circle (including the overlapping portion) represents a set containing the numbers 0, 2, 4, 6, 8, and 10.  More succinctly, this set contains the multiples of 2 between 0 and 10.  The figure also contains a yellow circle containing the multiples of 3 between 0 and 10.

.. figure:: venn_diagram.svg

    A Venn diagram illustrating set operations.  The left (blue) circle contains multiples of 2 in the range [0, 10].  The right (yellow) circle contains multiples of 3 in the same range.

This type of diagram is known as a Venn diagram, and it is frequently used to illustrate sets and operations on them.  We will use it to discuss three binary operations on sets: *union*, *intersection*, and *set difference*.

The union of two sets is another set: the set containing all values that are in either set.  In the diagram above, the union of the two sets contains the values 0, 2, 3, 4, 6, 8, 9, and 10.  In the diagram, this is every number that is contained in either circle.  Note that we do not duplicate values; even though 6 is in both sets, the union of the sets does not contain 6 twice.  A number is either in the set once, or it is not in the set at all.  A union of values is related to the Boolean **OR** operator: the union of these two sets contains integers between 0 and 10 which are multiples of 2 OR multiples of 3.

The intersection of two sets is again a set, this time containing only values which appear in both of the original sets.  In the diagram above, the intersection is represented by the overlap between the two circles, containing the values 0 and 6.  Intersection is related to the Boolean **AND** operation; the intersection of these two sets contains integers between 0 and 10 which are multiples of 2 AND multiples of 3.

While union and intersection are commutative - the sets involved in an operation can be exchanged and get the same result - set difference is not.  In set difference, you are "subtracting" one set from another to obtain a new set.  The result is all values in the first set excluding any values also in the second set.  The diagram above shows the two possible set differences we can obtain using our two sets.  These are the portions of the circles that are outside the intersection.  For example, if we subtract the set of multiples of 3 from the set of multiples of 2, we get the numbers in the left circle which are not in the right circle, that is, the values 2, 4, 8, and 10.  Set difference does not correspond directly to a basic Boolean operation, but we can approximate set difference using **NOT** and **AND**:  the set difference above (multiples of 2 minus multiples of 3) is the set of integers between 0 and 10 inclusive which are multiples of 2 AND NOT multiples of 3.

It may be difficult to imagine all of the amazing applications of sets in both mathematics and computer science from this simple example.  However, set theory is a very powerful tool.  As we will discuss in :numref:`Part {number} <relational-theory-part>`, relational databases resulted from the application of set theory to the problems of data management.

.. index:: multiset

Tables as sets
::::::::::::::

Mathematically, sets are collections of distinct values.  In the original conception of relational databases, tables and the results of data retrieval queries were intended to be true sets; that is, collections of rows, with no two rows being exactly the same.  For performance reasons, SQL databases allow duplicate rows in both tables and in the results of queries.  For example, if we run the following query, we get some duplicate rows.

::

    SELECT publication_year FROM books;

The term used to describe tables and query results in SQL is *multiset*.  A multiset is a collection of values from the same domain of values, but values can appear more than once in the set.  This difference between relational databases in practice and in theory results in some complications, as we will soon see.

The three basic set operations that SQL supports are union, intersection, and set difference.

.. index:: UNION, set operation - SQL; union

Union
-----

Set union in SQL is an operation on two **SELECT** queries.  The query is written as one **SELECT** query, followed by the keyword **UNION**, followed by another **SELECT** query.  The two query results must be compatible in the sense that they must both return the same number of columns, and the columns should have compatible types.  The union of the queries contains every distinct row that is returned from either query.  As a very simple example, we can use a **UNION** query in place of a Boolean **OR** condition.  Compare these two queries:

.. activecode:: sets_example_aggregate
    :language: sql
    :dburl: /_static/textbook.sqlite3

    SELECT * FROM books WHERE title LIKE 'W%'
    UNION
    SELECT * FROM books WHERE publication_year = 1995;

    SELECT *
    FROM books
    WHERE title LIKE 'W%'
    OR publication_year = 1995;

In this case, the queries return the same results.  However, there is a subtle difference between them.  When we use **UNION**, SQL treats it as a true set operation and returns a set of distinct rows - any duplicates are removed.  To be completely equivalent, we should use the **DISTINCT** keyword in the second query.

There is no particular reason to choose a union query over the **OR** expression in this case; it is merely used for illustration.  **UNION** may be a more preferable alternative in other scenarios, such as those involving complex conditional logic.  As a simple example, consider providing a column labeling authors as "living", "dead" (giving the date of death), or "unknown" (where the birth and death dates are unknown).  We could do this with a **CASE** expression, or with a **UNION** of three queries (think of a union of the first two queries, then a union of the result with the third query):

::

    SELECT name, 'living' AS status
    FROM authors
    WHERE death IS NULL AND birth IS NOT NULL
    UNION
    SELECT name, 'died ' || death
    FROM authors
    WHERE death IS NOT NULL AND birth IS NOT NULL
    UNION
    SELECT name, 'unknown'
    FROM authors
    WHERE birth IS NULL;

    SELECT
      name,
      CASE
        WHEN death IS NULL AND birth IS NOT NULL
          THEN 'living'
        WHEN death IS NOT NULL AND birth IS NOT NULL
          THEN 'died ' || death
        WHEN birth IS NULL
          THEN 'unknown'
      END AS status
    FROM authors;

If you run the union query above, you will see that column names for the result of the whole query come from the first **SELECT** query when using set operations.

In some cases, **UNION** may be your only choice - such as when you are combining results from different tables.  One example of this might occur when a company wishes to create an email list for everyone related to the company in some way: the company's database might contain one table for employees, another for customers, and a third for vendors  A union query would easily create one mailing list from these three tables, and eliminate duplicates (since, for example, employees might also be customers).

.. index:: UNION ALL

Multiset complication
#####################

Used by itself, **UNION** results in the removal of all duplicates from the result set of the query.  There may be occasions when this is not the desired behavior; if you wish to retain duplicate records (keeping all rows returned by either query), simply add the keyword **ALL** after **UNION**.  The query below will result in duplicate records:

::

    SELECT * FROM books WHERE title LIKE 'W%'
    UNION ALL
    SELECT * FROM books WHERE publication_year = 1995;

.. index:: INTERSECT, set operation - SQL; intersection

Intersection
------------

Set intersection in SQL is accomplished by the keyword **INTERSECT**.  The rules for using **INTERSECT** are the same as for using **UNION**, but its result contains only every distinct row that is contained in *both* query results:

::

    SELECT * FROM books WHERE title LIKE 'W%'
    INTERSECT
    SELECT * FROM books WHERE publication_year = 1995;

This result is similar to that achieved by using an **AND** expression in the **WHERE** clause of a single query:

::

    SELECT DISTINCT *
    FROM books
    WHERE title LIKE 'W%'
    AND publication_year = 1995;

However, as with **UNION**, you can use **INTERSECT** to perform queries against multiple tables.

The SQL standard allows the keyword **ALL** after **INTERSECT**, but most databases (including SQLite) do not support this usage.

(Note for MySQL users: MySQL does not implement **INTERSECT**.)

.. index:: EXCEPT, set operation - SQL; difference

Set difference
--------------

Set difference in SQL is accomplished by the keyword **EXCEPT**.  The rules for using **EXCEPT** are again the same as for **UNION** and **INTERSECT**, but note that **EXCEPT** is not commutative - the order of the queries matters.  Here is our same example again, using **EXCEPT**:

::

    SELECT * FROM books WHERE title LIKE 'W%'
    EXCEPT
    SELECT * FROM books WHERE publication_year = 1995;

This result is similar to that achieved by requiring one condition **AND NOT** the other condition in the **WHERE** clause of a single query:

::

    SELECT DISTINCT *
    FROM books
    WHERE title LIKE 'W%'
    AND NOT publication_year = 1995;

However, as with **UNION** and **INTERSECT**, you can use **EXCEPT** to perform queries against multiple tables.

The SQL standard allows the keyword **ALL** after **EXCEPT**, but most databases (including SQLite) do not support this usage.

One application of the **EXCEPT** operator is determining if two query results are identical; if you take the set difference in both directions, your result should be empty if the two queries return the same distinct rows (there could be a difference in the counts of duplicate rows).  An alternate approach is to see if the union and intersection of the two queries contain the same count of rows.

(Note for MySQL users: MySQL does not implement **EXCEPT**.)

(Note for Oracle users: Oracle uses the keyword **MINUS** rather than **EXCEPT**.)

Chaining operations
-------------------

As we saw with **UNION**, it is possible to do more than one set operation in a single query.  For queries just involving **UNION**, the order of queries does not matter, as **UNION** is both commutative and associative.  The same is true for a query just involving **INTERSECT**.  For queries involving **EXCEPT**, or queries mixing set operations, the situation is more complicated.  **EXCEPT** is neither commutative nor associative.  Queries that chain mixed operators do not behave the same in all databases, so be cautious when attempting this; some databases allow you to use parentheses to force the order in which you want operations to be performed.



Self-check exercises
::::::::::::::::::::

This section contains some exercises using the books data set (reminder: you can get full descriptions of all tables in :ref:`Appendix A <appendix-a>`).  If you get stuck, click on the "Show answer" button below the exercise to see a correct answer.  There are many ways to answer these questions; try to use a set operation to solve each.

.. activecode:: sets_self_test_union
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query to find all of the awards won by poet Allen Ginsberg, either as an author or for a book.  Your output should have three columns: the name of the award, the year of the award, and what the award was won for - the book title for book awards, or "body of work" for author awards.
    ~~~~

.. reveal:: sets_self_test_union_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT aw.name, ba.year, bo.title AS "Awarded For"
        FROM
          awards AS aw
          JOIN books_awards AS ba ON ba.award_id = aw.award_id
          JOIN books AS bo ON bo.book_id = ba.book_id
          JOIN authors AS au ON au.author_id = bo.author_id
        WHERE au.name = 'Allen Ginsberg'
        UNION
        SELECT aw.name, aa.year, 'body of work'
        FROM
          awards AS aw
          JOIN authors_awards AS aa ON aa.award_id = aw.award_id
          JOIN authors AS au ON au.author_id = aa.author_id
        WHERE au.name = 'Allen Ginsberg';


.. activecode:: sets_self_test_intersection
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query to find a list of awards that have been given for either books or an author's body of work (i.e., the award(s) should show up in both **authors_awards** and **books_awards**).
    ~~~~

.. reveal:: sets_self_test_intersection_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT * FROM awards WHERE award_id IN
          (SELECT award_id FROM books_awards)
        INTERSECT
        SELECT * FROM awards WHERE award_id IN
          (SELECT award_id FROM authors_awards)
        ;


.. activecode:: sets_self_test_difference
    :language: sql
    :dburl: /_static/textbook.sqlite3

    Write a query to find a list of authors who won author awards but no book awards.
    ~~~~

.. reveal:: sets_self_test_difference_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    ::

        SELECT name FROM authors WHERE author_id IN
          (SELECT author_id FROM authors_awards)
        EXCEPT
        SELECT name FROM authors WHERE author_id IN
          (SELECT author_id FROM books WHERE book_id IN
            (SELECT book_id FROM books_awards))
        ;


|chapter-end|


|license-notice|



## Chapter: advanced-topics.rst

.. _advanced-sql-chapter:

===============
Advanced topics
===============

This chapter provides brief coverage of some advanced SQL capabilities that did not fit neatly into previous chapters: views, common table expressions, and window functions.  These topics are not thoroughly covered (particularly common table expressions and window functions).  It is hoped that this introduction will suffice to give you some understanding of the additional possibilities within SQL.

Tables used in this chapter
:::::::::::::::::::::::::::

For this chapter we will be using the books dataset (with tables **books**, **authors**, etc.), a description of which can be found in :ref:`Appendix A <appendix-a>`.

.. index:: view, CREATE VIEW, DROP VIEW

Views
:::::

A *view* is a database object that acts as a saved **SELECT** query, the result of which can be queried directly as if it were a table.  The data itself is not stored; the query that the view represents must be executed each time the view is queried, ensuring that up-to-date data is returned [#]_.  Views are particularly useful for saving complex queries that must be executed frequently, or that will be used by people with minimal SQL skills; the complex parts of the query can be written once, tested, and saved, reducing errors in later usage.

To create a view, use the **CREATE VIEW** statement:

.. activecode:: advanced_example_view
    :language: sql
    :dburl: /_static/textbook.sqlite3

    CREATE VIEW book_editions AS
    SELECT
      a.name AS author,
      b.title,
      e.publication_year,
      e.publisher,
      e.publisher_location,
      e.title AS published_title,
      e.pages,
      e.isbn10,
      e.isbn13
    FROM
      editions AS e
      JOIN books AS b ON b.book_id = e.book_id
      JOIN authors AS a ON a.author_id = b.author_id
    ;

    SELECT author, published_title, publication_year, publisher
    FROM book_editions
    WHERE title = 'The Two Towers';

To remove a view, use the **DROP VIEW** statement:

::

    DROP VIEW book_editions;

.. index:: common table expression, CTE, WITH

Common table expressions
::::::::::::::::::::::::

Related to both views and subqueries, *common table expressions* (CTEs) let us define a **SELECT** query and assign it a name for use within the context of a larger **SELECT** query.  Multiple CTEs may be used within a query.  Unlike views, CTEs only exist for the lifetime of the query in which they are defined.  Unlike subqueries, CTEs may not be correlated with the main query (unless used itself in a subquery).  A common use of CTEs is in place of subqueries used in the **FROM** clause of the main query; the CTE effectively moves the subquery out of the body of the main query, which makes it easier to read.  In addition, one CTE can refer to another CTE defined earlier in the query, which eliminates the need to nest subqueries of this type.

CTEs are defined prior to the main **SELECT** clause, using a **WITH** clause:

::

    WITH
      name1 AS
        (select query 1),
      name2 AS
        (select query 2),
      ...
    SELECT ...

Here is an example listing books along with some additional pieces of information: the number of awards the book has won, and the number of printed editions of the book (keeping in mind that we only have edition information for books by J.R.R. Tolkien).  We could easily provide either one of these pieces of information simply using joins and grouping and aggregation, but providing both in the same query would require writing at least one subquery or using window functions (which are discussed in the next section).  Here we use CTEs to do our grouping and aggregation steps separately, then we join those results in the main query.

.. activecode:: advanced_example_cte
    :language: sql
    :dburl: /_static/textbook.sqlite3

    WITH
      ec AS
        (SELECT book_id, COUNT(*) AS count
         FROM editions
         GROUP BY book_id),
      ac AS
        (SELECT b.book_id, COUNT(ba.book_id) AS count
         FROM
          books AS b
          LEFT JOIN books_awards AS ba ON b.book_id = ba.book_id
        GROUP BY b.book_id)
    SELECT
      au.name AS author,
      ac.count AS "awards won",
      ec.count AS "editions in print",
      b.title
    FROM
      authors AS au
      JOIN books AS b ON b.author_id = au.author_id
      JOIN ac ON ac.book_id = b.book_id
      LEFT JOIN ec ON ec.book_id = b.book_id
    ;

.. index:: window function, PARTITION BY

Window functions
::::::::::::::::

As we saw in :numref:`Chapter {number} <grouping-chapter>`, grouping and aggregation let us report aggregate statistics on groups of data, along with attributes common to the group (typically, attributes that we grouped by).  However, the individual elements of the group are not visible.  *Window functions* provide a mechanism for reporting information related to some grouping of data while also listing all individual rows.  In general, all aggregate functions are available as window functions, and there are additional functions that relate a row to its membership in the group (such as its rank within the group according to some ordering).

As an example, suppose we wish to list all books, along with the number of books by the same author, and the ordinal number of the book as part of the author's body of work, in order by publication year (e.g., was this the author's first, second, or third book?).  We can do this with window functions:

.. activecode:: advanced_example_window
    :language: sql
    :dburl: /_static/textbook.sqlite3

    SELECT
      a.name AS author,
      COUNT(*) OVER
        (PARTITION BY b.author_id)
        AS author_count,
      ROW_NUMBER() OVER
        (PARTITION BY b.author_id ORDER BY b.publication_year)
        AS book_rank,
      b.title,
      b.publication_year
    FROM
      authors AS a
      JOIN books AS b ON b.author_id = a.author_id
    ORDER BY a.name, book_rank;

Note that windowing occurs *after* application of any **WHERE** conditions, and even after grouping and application of **HAVING** conditions.  This makes window functions useful in application to already grouped data, for example, but it also means that you cannot apply **WHERE** or **HAVING** conditions to the window function result itself.

Window functions have a number of additional options allowing for fairly complex processing, which we do not cover here.



|chapter-end|

----

**Notes**

.. [#] Some databases also provide *materialized views*, which store actual data; these are used when executing the query for a view would take too long.  Such views do become out of date and must be refreshed periodically.

|license-notice|



## Chapter: index.rst

.. _sql-part:

===
SQL
===

Part 1 of this book is all about SQL, the most popular language used for interacting with *relational databases*, the main focus of the book.  The chapters in this section have been organized to allow topics to be introduced in somewhat different orders according to the instructor's desired approach.  The diagram below shows the strong dependencies between chapters; chapters will assume knowledge introduced in earlier chapters as implied by the graph.  Chapters without a strong dependency may still refer to other chapters in passing, with a link to the chapter explaining the reference; these weak dependencies are not critical for understanding the referencing chapter.

.. figure:: chapter_dependencies.svg

    Chapter dependency graph for Part 1

**Table of contents for Part 1**

.. toctree::
    :maxdepth: 3

    01-sql-basics/sql-basics
    02-data-retrieval/data-retrieval
    03-expressions/expressions
    04-multiple-tables/multiple-tables
    05-data-modification/data-modification
    06-table-creation/table-creation
    07-constraints/constraints
    08-subqueries/subqueries
    09-grouping-and-aggregation/grouping-and-aggregation
    10-set-operations/set-operations
    11-advanced-topics/advanced-topics


|license-notice|



## Chapter: introduction.rst

.. _data-modeling-intro-chapter:

=============================
Introduction to data modeling
=============================

.. index:: data; modeling, data model, analysis, database; design

When beginning a project that requires a database, it is useful to expend some effort thinking about an appropriate database structure.  Unless your database will be very small (involving only one or two tables), if you simply sit down and start creating tables, you will likely run into trouble fairly quickly.  It is quite easy to create a database that - even though it stores the necessary data - is difficult to understand, update, and query.

Much like software creation, database creation benefits from the activities of *analysis* and *design*.  Analysis can include discussions with people who have a thorough understanding of the data to be stored, discussions with the intended users of the database, and an examination of representative data.  Design uses the insights gained from analysis to produce a database structure that can correctly store the necessary data and meet user requirements.  Analysis and design are complementary activities; analysis informs design, which in turn uncovers new questions for further analysis.  The back-and-forth interaction between analysis and design works to eliminate the kinds of problems that otherwise result from partial understanding and incorrect assumptions.

Analysis and design may be facilitated using a variety of graphical and non-graphical documents.  *Data models* are one type of document that are most useful when creating a database.  At minimum, a data model must capture the various types of data and how these types relate to each other.  Some data models go further in detail, capturing specific programming elements or even aspects of the physical computer systems or networks on which the database will be deployed.

We can use data models to reason about data, abstracted from the details of SQL or a programming language.  While it may seem that there are very many types and notations for data models, in practice there are only a few important underlying concepts to learn.  There are many benefits to working with a data model: better realization of users' needs, a database structure that allows easy querying and consistent updates, and documentation of the system for new users, to list a few.  If an existing database lacks documentation in the form of a data model, you may find value in creating one to better understand the system.

This part of the book examines graphical data models at varying levels of abstraction.  In :numref:`Chapter {number} <erd-chapter>`, we discuss the *entity-relationship diagram* (ERD), a high-level model of data.  ERDs are particularly useful at the intersection of analysis and design, facilitating discussion with users and domain experts.  :numref:`Chapter {number} <erd-to-relational-chapter>` explains how to transition from an ERD into a relational database.  This transition may be mediated by less abstract models which have closer correspondence with the relational database, discussed in :numref:`Chapter {number} <other-notations-chapter>`.  :numref:`Chapter {number} <other-notations-chapter>` also discusses some of the many variations in notation in common usage.



|chapter-end|


|license-notice|



## Chapter: ERD.rst

.. _erd-chapter:

============================
Entity-relationship diagrams
============================

.. index:: entity-relationship diagram, ERD, Chen notation

This chapter introduces *entity-relationship diagrams*, or ERDs.  ERDs define a graphical language for data modeling at a high level of abstraction.  ERDs map well to relational databases at a high level, but can also be used as a precursor to building non-relational databases.

ERDs were conceived of by Peter Chen and described in a :ref:`1976 paper <data-modeling-references>`.  While various approaches to data modeling existed before the ERD, Chen's ERD has stood the test of time to become one of the preferred methods and is in wide use today.  Many authors have expanded upon Chen's basic model, extending the notation in different directions.  As a result, there are many different ERD notations in use.  For this book, we adopt the notation of :ref:`Elmasri and Navathe <data-modeling-references>`.

As we cover the various elements of the ERD notation, our examples will build pieces of a data model for a fictional computer manufacturer.  The complete model is given in :numref:`Section {number} <complete-model-section>` below. In :ref:`appendix-a`, you can also find ERDs for some of the datasets that we used in :numref:`Part {number} <sql-part>`.

Basic model
:::::::::::

As the name suggests, ERDs are concerned with *entities* and the *relationships* between them.  Each of these elements and its related elements are denoted using simple shapes containing text labels and connected with straight lines.

.. index:: entity, entity; regular

Entities
--------

Entities represent things or objects with independent existence; persons, products, and companies are some examples.  Entities act much like the "nouns" of our visual modeling language.  Entities are denoted by rectangles; the rectangle is labeled with a name indicative of the concept being modeled:

.. image:: entity.svg
    :alt: A rectangle containing the word "employee"

It is important to distinguish between an entity, which represents the type of the thing or object being modeled, and instances of the entity, e.g., a particular thing or object.  The entity **employee** models all employees, not a specific employee of a company.

.. index:: entity attribute

Attributes
----------

Entities are further described by their properties, or *attributes*.  Attributes are denoted by ovals and attached to their entities with straight lines.  For example, employees have names:

.. image:: attribute.svg
    :alt: An oval containing the word "name" connected to the employee entity

You can attach as many attributes as necessary to an entity.

.. index:: entity attribute; key

Keys
----

Every entity has at least one attribute that uniquely identifies instances of the entity.  These *key attributes* are indicated by underlining the attribute label.  For our computer company, each employee is given an ID number for unique identification:

.. image:: key_attribute.svg
    :alt: An oval containing the word "ID", underlined, connected to the employee entity

ERDs allow for multiple key attributes: for example, we might wish to also store a government issued identification number (such as the SSN used in the United States) for each employee.  In this case, we would have two attributes with underlined labels.  Note that this is not the same as a key attribute composed of multiple parts!  An employee can be uniquely identified by either their company ID or by their government issued identification number - you do not need to know both.  Composite keys will be discussed in a later section.

.. index:: relationship - ERD

Relationships
-------------

Two or more entities may participate in a relationship.  Relationships act like the "verbs" in our modeling language.  Relationships are denoted by diamonds and are connected to the participating entities by straight lines:

.. image:: relationship_with_entities.svg
    :alt: A diamond containing the words "works at", connected to the entities employee and factory

This diagram reads like a sentence: "employee works at factory".  Note that no direction is implied by the layout of the diagram; you have to use your knowledge of the data domain to know that the diagram probably does not mean "factory works at employee".

.. index:: relationship - ERD; cardinality ratio, relationship - ERD; participation, cardinality ratio, relationship - ERD; one-to-one, relationship - ERD; one-to-many, relationship - ERD; many-to-one, relationship - ERD; many-to-many, one-to-one relationship - ERD, one-to-many relationship - ERD, many-to-one relationship - ERD, many-to-many relationship - ERD, participation, participation; total, participation; partial, partial participation, total participation

Cardinality ratios and participation
-------------------------------------

How many employees work at a factory, and how many factories can an employee work at?  This is important information for our model (and for the database we will create from it).

*Cardinality ratios* let us indicate the general number of instances of an entity that map to another entity on the other side of the relationship, and vice versa.  The cardinalities defined by the basic model are **1** and **N** (or **n**).  A cardinality of **1** actually means "zero or one"; a cardinality of **N** means "zero, one, or many".  As most relationships are binary (involving only two participating entities), there are a small number of commonly occurring cardinality ratios:

- 1:1, read as "one-to-one"
- 1:N, read as "one-to-many" (equivalently, N:1, or "many-to-one")
- N:M (or N:N), read as "many-to-many"

We show the cardinalities on our model next to the line connecting the relationship to the entity:

.. image:: relationship_with_cardinalities.svg
    :alt: The works at relationship, annotated with an "N" on the employee side and a "1" on the factory side

This diagram's cardinality ratio implies two statements about the relationship between employees and factories.  First, "each employee works at zero or one factory".  Second, "each factory has zero or more employees working at it".

*Participation* is a closely related topic.  An entity is said to have *total participation* in a relationship if every instance of the entity must be matched with instances of the other entity in the relationship.  In effect, this provides a minimum cardinality for the entity on the other side of the relationship.  Here is an example - note that this is a second relationship between **employee** and **factory**:

.. image:: relationship_with_participation.svg
    :alt: The manages relationship connecting employee and factory, annotated with a "1" on both sides; employee is connected with a single line, while factory is connected with a double line

The double line between **factory** and **manages** says that **factory** has total participation in the relationship.  This diagram's cardinality ratio and participation imply two subtly different statements: "each employee manages *zero or one* factories" and "each factory has *exactly one* employee managing it".  That is, every factory is expected to have a manager, but only some employees manage a factory.

The alternative to total participation, denoted using a single line, is *partial participation*.

While indicating total participation on an ERD provides useful information, it is not as critical as cardinality ratios.  As we will see in :numref:`Chapter {number} <erd-to-relational-chapter>`, total participation can influence some decisions when converting our diagram to a relational database (particularly for 1:1 relationships), but its absence is generally not harmful.

Putting it together
-------------------

Below is a diagram incorporating the examples above, with some additional attributes to fill out the entities:

.. image:: subset_of_ERD.svg
    :alt: The employee and factory entities with their attributes, and the works at and manages relationships; the employee entity has attributes ID, name, position, pay rate, and pay type; the factory entity has the attribute city.

Note that the **factory** entity does not use a generated key, but a "natural" one - the city in which the factory is located.  (This only works if our company has no more than one factory in a city!)

While this is only part of the complete model that we will ultimately develop, it is a valid ERD from which we could build a database.  All of the necessary detail is in place.

There is also no unnecessary duplication of information in our model.  It is tempting to add attributes or other features that anticipate the database to come; for example, we might think that employees should have an attribute indicating at which factory they work.  However, the fact that (at least some) employees work at a factory is already implicit in the relationship **works at**.  This relationship will give rise to the necessary database structures connecting employees to factories.


More complex modeling options
:::::::::::::::::::::::::::::

This section will look at some cases not covered in the examples above, and will also reveal some additional notation covering situations not addressed by the basic model above.

.. index:: relationship - ERD; recursive, recursive relationship

Recursive relationships
-----------------------

Relationships can exist between an entity and itself.  This is frequently useful, especially in modeling hierarchical relationships.  In our fictional computer company, each employee (except for the head of the company) has a supervisor, who is another employee.  This is easily modeled as a one-to-many relationship connecting **employee** to **employee**:

.. image:: recursive_relationship.svg
    :alt: The one-to-many relationship supervises connecting twice to employee

For added clarity, we have annotated the lines connecting the relationship with the roles that employees play in the relationship: one supervisor supervises many supervisees.

.. index:: entity; weak, weak entity, identifying relationship, partial key, weak key

Weak entities
-------------

In some situations, we may want to model an entity for which we do not have a unique identifier, but which can be uniquely identified in relationship with another entity.  As an example, each of the factories of our computer manufacturer will contain assembly lines.  We wish to track certain information about each assembly line in our database, such as the daily *throughput* of the assembly line (the number of computers it can produce in a day).  We wish to model these as an entity in our data model, but it is not immediately clear what property of an assembly line would make a good identifier.

We could, of course, give every assembly line a generated unique identifier, but there is a more natural way to identify assembly lines.  In each factory, assembly lines are simply numbered starting from 1, most likely in order by their position on the factory floor.  To identify a particular assembly line, we first state which factory it is in, and then its number within the factory.

When an entity is dependent on another entity for full identification, the dependent entity is called a *weak entity*, and we notate it using a rectangle with doubled outline.  The weak entity has only a partial, or weak, key - in our example, this is the number of the assembly line within the factory.  We note the weak key using a dashed underline.  We also call out the relationship that the weak entity depends on for its identity, to distinguish it from any other relationships the weak entity participates in.  We call this relationship the *identifying relationship*, and draw it as a diamond with a doubled outline.  The key of the parent entity together with the weak key of the weak entity constitutes a unique identifier for instances of the weak entity.

Here is the diagram of our assembly line example:

.. image:: weak_entity.svg
    :alt: The weak entity assembly line and the entity factory and their attributes, connected by the one-to-many relationship contains; assembly line has attributes number and throughput

.. index:: entity attribute; composite

Composite attributes
--------------------

We may sometimes wish to model an attribute that is naturally composed of multiple parts.  For example, the address of a person or company may be composed of a street address, city, postal code, and so forth.  To indicate that these attributes work together as part of a larger property of the entity, we can use a *composite attribute*, which is drawn as a regular attribute with its component attributes attached.

The use of a composite attribute is essential in cases where our key is itself composed of multiple attributes.  We cannot simply underline each component of the key, as this would indicate that each is a key by itself.  Instead, we must create a composite attribute; we underline the composite, but not the component attributes.

In our computer manufacturer example, each type of computer (or "model") that the company builds is identified by a name (indicating some line of computers), and a number (indicating the version of that line of computers).  For lack of a better name, we group these as a composite labeled "designation":

.. image:: composite_attribute.svg
    :alt: Ovals containing the words "name" and "number" connecting to the key attribute designation of the entity model

.. index:: entity attribute; multivalued

Multivalued attributes
----------------------

Some properties of entities are not simple values, but lists or sets of values.  As these will need special handling when we create a database from the data model, we differentiate these *multivalued attributes* from regular attributes using a doubled outline:

.. image:: multivalued_attribute.svg
    :alt: A double outlined oval containing the word "application" connected to the entity model

In our example, computer models may be designed or marketed for particular applications, such as gaming, multimedia, or business.  As computers may fit into more than one of these categories, we model it above as a multivalued attribute.

An alternative to making a multivalued attribute is modeling the possible attribute values as a separate entity, which is connected to the original entity with a many-to-many relationship.  The separate entity would have only the single attribute, and its instances would represent the possible values that can be associated with the original entity.

.. index:: entity attribute; derived

Derived attributes
------------------

Entities may have important properties that we want to note on our data model, but which we would prefer to compute from other values in the data model, rather than store in our database.  For example, the age of a person is an important property for many applications, but storing this value in the database is generally a poor choice, as a person's age changes over time, necessitating regular updates to the data.  Instead, we might store the person's birth date, and calculate the person's age each time we need it.

In our computer manufacturer example, we are interested in the total throughput of each factory.  While we could make this an attribute of **factory**, we note that a factory's throughput can be calculated by summing up the throughputs of the factory's assembly lines.  We model these calculated properties as *derived attributes*, using a dashed outline:

.. image:: derived_attribute.svg
    :alt: The weak entity assembly line and the entity factory and their attributes, connected by the relationship contains; the diagram now shows a dashed outline oval containing the word "throughput" connected to the factory entity

.. index:: relationship - ERD; attribute

Relationship attributes
-----------------------

While most attributes are attached to entities, we can also attach attributes to relationships.  We do this when an attribute properly applies to a combination of entities, rather than to a single entity.  This most frequently occurs with many-to-many relationships.

Our fictional computer manufacturer buys computer parts from multiple vendors.  The manufacturer considers certain parts that have similar properties to be a single "part".  For example, the database might contain an entry for the part "8TB 7200RPM hard drive", regardless of brand.  However, at any given time, one vendor's price for a given part may be different from another vendor's price for the same part.  This price therefore cannot belong to the **part** entity - it depends on **vendor**, too.  Similarly, vendors supply many different parts, so the price cannot belong to the **vendor** entity.  Instead, it belongs to the relationship between these entities:

.. image:: relationship_attribute.svg
    :alt: The entities vendor and part connected by the man-to-many relationship supplies; supplies has a price attribute; vendor has attributes part number (key) and description, while vendor has the key attribute name

.. index:: relationship - ERD; higher-arity

Higher-arity relationships
--------------------------

We stated that two *or more* entities could participate in a relationship.  While most relationships are binary, you may run into cases where you need to relate three (or more) entities.  We do not have an example of this in our model.  However, a classic example arises in the context of large organizations or government agencies with many projects involving complex contracts with parts suppliers.  Projects use many parts, and parts may be used in multiple projects; additionally, the same part might be available from different vendors.  Normally this might be modeled using two many-to-many relationships (very much like what is in our computer manufacturer model).  However, if the company has legal agreements that, for a certain project, a certain type of part must come from a certain vendor, while for a different project, the same type of part must come from a different vendor, the situation is not easily modeled using binary relationships.  What we need is a relationship that connects parts, projects, and vendors.

In this example, the relationship is many-to-many-to-many, which may be notated as M:N:P (or N:N:N):

.. image:: ternary_relationship.svg
    :alt: Entities project, vendor, and part connected by the relationship requires

.. _complete-model-section:


Complete example
::::::::::::::::

Below is our completed example; most parts of the diagram have been explained above.  Now that you know what the different elements mean, the rest of the diagram should be self-explanatory:

.. image:: complete_ERD.svg
    :alt: The complete ERD; in addition to pieces shown above, the diagram includes a many-to-many relationship can use between model and part, and a one-to-many relationship builds between factory and model

Using ERD to design a database
:::::::::::::::::::::::::::::::

While an ERD has many applications, we emphasize its use as an analysis and design tool.  ERDs facilitate communication between database developers, programmers, domain experts, and database users.  An ERD produces an abstract model of the data.  Although we will examine how to turn our ERD into a relational database in :numref:`Chapter {number} <erd-to-relational-chapter>`, the ERD contains no details specific to SQL or relational databases.  Especially in the early stages of analysis, thinking ahead to such details can actually be counterproductive; your focus should be on creating a shared understanding of the data.

In a similar vein, we encourage you to avoid spending effort on perfect conformance to the ERD notation.  In the interest of improved communication, you should feel free to adapt the notation to your needs.  You can (and perhaps should) add text explanations wherever they are helpful - designing a large database is a complex endeavor, and it can be easy to forget the reasons for particular design decisions.  Notational details will become more important in the later stages of design, however, as you begin to test your design with actual database construction.

The actual process you use to create a database for a project may be dictated by your project group or organization, but some general advice is provided below.

Analysis
--------

A crucial first step in the design of any software is understanding the requirements of your project.  In regards to your database, requirements may be dictated by:

- the data domain, e.g., facts which impose structure and relationships on the data
- user needs, e.g., the answers or insights they want to obtain from the data
- data sources, e.g., the data values that are actually available to be stored
- application requirements, e.g., how other software will view or manipulate the data

You may therefore need to talk with domain experts (people who have deep knowledge about the area the data applies to), end users, data providers, and software developers to determine these requirements.  Brainstorming entities, attributes, and relationships is a great starting point for these discussions.  List data elements on a whiteboard or piece of paper where everyone can see.  Some of these are potential entities, some are attributes, and some may even be relationships.  Have people propose relationships between the data elements, and write these as simple "subject verb object" sentences.  It is not necessary to be exhaustive in your brainstorming; additional entities, attributes, and relationships will be discovered in later steps.

Once you have a good set of data elements and relationships, you can begin working on an ERD.  Focus at first on basic model elements - entities, attributes, and relationships.  Identify potential key attributes for all of your entities.  Consider cardinality ratios; examine whether these make sense by the statements they imply about the entities involved, e.g., "each instance of this entity has this relationship with *x* number of instances of the other entity".  Question all assumptions!  For example, if you identify some attribute as a key for an entity, ask if every instance of the entity actually has that attribute.

It may take significant time and multiple discussions to build an ERD that is satisfactory to everyone involved.  This process is messy and may seem chaotic at first.  Be patient, try different options, and make incremental improvements.  It is not necessary to solve every disagreement before moving on to next steps; you may need to revisit the ERD multiple times as you uncover questions and issues in later steps.

Design, implementation, and beyond
----------------------------------

You can build a database as the next step once you have an ERD, or you can engage in further design activities.  You may wish to build a lower level data model, such as a *logical model* (discussed in :numref:`Chapter {number} <other-notations-chapter>`) as an intermediate step.  Some of this will depend on interactions with other systems that are being built (e.g., software).  As will be discussed in :numref:`Chapter {number} <erd-to-relational-chapter>`, the ERD does not fully dictate how your database will be built; for instance, you need to choose table and column names (for a relational database), as well as data types for the different values represented by attributes in your ERD.

Regardless of your next step, you are likely to run into problems of some sort: assumptions that do not hold, new questions, or other issues in translating the ERD into a more concrete form.  As part of your process, expect to revisit the design with your domain experts and project stakeholders to resolve these problems.  This will probably happen yet again when you start trying to put data into your new database, when software is written to interact with the database, and when users start testing the database and/or software.

Whether you resolve issues at each stage with the ERD or at some lower level, it can be valuable to keep the ERD aligned with the database as implemented as part of your documentation of the system.  Systems change over time; when it is time to modify your database, you will want some documentation of the design decisions that went into the earlier database, and the ERD may play a part in designing the updates to your system.  An up-to-date ERD will also help new database users or software developers become acquainted with the system more quickly.


Self-check exercises
::::::::::::::::::::

This section has some questions you can use to check your understanding of entity-relationship diagrams and data modeling.

.. fillintheblank:: erd_self_test_elements_1

   Which data element models a thing or object with independent existence, such as a person, product, or company?

   - :entity: Correct.  Entities act as the "nouns" of our data model.
     :.*: Try again.  Be sure your answer is in all lowercase.

.. reveal:: erd_self_test_elements_1_hint
     :showtitle: Show answer
     :hidetitle: Hide answer

     The answer is "entity".

.. fillintheblank:: erd_self_test_elements_2

    An |blank| describes a property of an entity.

    - :attribute:   Correct.
      :.*: Try again.  Be sure your answer is in all lowercase.

.. reveal:: erd_self_test_elements_2_hint
    :showtitle: Show answer
    :hidetitle: Hide answer

    The answer is "attribute".

.. fillintheblank:: erd_self_test_elements_3

   Which data element connects two or more entities and acts as a "verb" in our data model?

   - :relationship:   Correct.
     :.*: Try again.  Be sure your answer is in all lowercase.

.. reveal:: erd_self_test_elements_3_hint
     :showtitle: Show answer
     :hidetitle: Hide answer

     The answer is "relationship".

.. dragndrop:: erd_self_test_shapes
    :match_1: rectangle|||entity
    :match_2: oval|||attribute
    :match_3: diamond|||relationship

    Drag the shape to the corresponding model element.


.. mchoice:: erd_self_test_keys

    Suppose you are designing a database to store information about movies.  What might be a good key attribute for your **movie** entity?

    -   Lead actor

        - Many actors, especially lead actors, have worked on many movies.  Lead actor is unlikely to be a unique identifier.

    -   Title

        - Many movies have been remade under the same title (and some movies share a title with unrelated films), so this is not a good unique identifier.

    -   First line of dialogue

        - Probably not.  It might be unique for most films, but probably not all films, and it is a fairly large piece of data to use as key.

    -   Title and year of release (composite)

        + This is the best of the choices given here.  Alternately, you might use an artificially generated id value.


.. mchoice:: erd_self_test_cardinality_1

    Consider the entities and relationship shown here:

    .. image:: self_test_relationship_1.svg
        :alt: Entities A and B connected to an unnamed relationship by single lines, labeled N and M

    Which statement most accurately describes the relationship?

    -   Each instance of A is associated with zero or one instance of B; each instance of B is associated with zero or one instance of A.

        - Incorrect.  What does the label "N" imply about maximum cardinality?

    -   Each instance of A is associated with zero or more instances of B; each instance of B is associated with zero or more instances of A.

        + Correct.  The relationship is many-to-many, with partial participation on both sides.

    -   Each instance of A is associated with one or more instances of B; each instance of B is associated with one or more instances of A.

        - Incorrect.  What is the participation of A and B in the relationship?  What does that imply about the minimum cardinality?

.. mchoice:: erd_self_test_cardinality_2

    Consider the entities and relationship shown here:

    .. image:: self_test_relationship_2.svg
        :alt: Entities C and D connected to an unnamed relationship.  C is connected by a single line labeled 1.  D is connected by a double line labeled N.

    Which statement most accurately describes the relationship?

    -   Each instance of C is associated with zero or one instance of D; each instance of D is associated with one or more instances of C.

        - Incorrect.  Each cardinality label describes the entity on the same side of the relationship.

    -   Each instance of C is associated with zero or more instances of D; each instance of D is associated with exactly one instance of C.

        - Incorrect.  Reconsider the participation on each side of the relationship, and what that implies about minimum cardinality.

    -   Each instance of C is associated with one or more instances of D; each instance of D is associated with zero or one instance of C.

        + Correct.


.. fillintheblank:: erd_self_test_elements_4

   Some entities have instances that cannot be uniquely identified based solely on their attributes, but must be associated with a parent entity instance for full identification.  We call these |blank| entities.

   - :weak:   Correct.
     :.*: Try again.  Be sure your answer is in all lowercase.

.. reveal:: erd_self_test_elements_4_hint
     :showtitle: Show answer
     :hidetitle: Hide answer

     The answer is "weak".


.. mchoice:: erd_self_test_elements_5

     Suppose we are modeling a simple database about books.  For each book we want to include information about the genres the book belongs to.  Many books can belong to more than one genre.  What kind of attribute should we use for genre?

     -  Multivalued

        + Correct.

     -  Derived

        - Probably not, unless genre information can be deduced from some other information stored in the database.

     -  Composite

        - Probably not, although you could make a case for storing a general genre category and a more specific sub-genre.

     -  Key

        - Definitely not.  Many books belong to the same genre, so genre is not a unique identifier for a book.




|chapter-end|


|license-notice|



## Chapter: ERD-to-relational.rst

.. _erd-to-relational-chapter:

====================================
Converting ERD to a relational model
====================================

.. |right-arrow| unicode:: U+2192

.. index:: ERD; conversion to SQL

In this chapter we explain the process of creating a relational database from an entity-relationship model.  While many steps are largely mechanical, a number of decisions need to be made along the way.  We will explore the trade-offs for each decision.  We will use the computer manufacturer data model from :numref:`Chapter {number} <erd-chapter>` as our example.

This chapter assumes you are familiar with the basics of the relational model of the database, including tables and primary and foreign key constraints.  The necessary foundations are covered in either Part I (Chapters :numref:`{number} <basics-chapter>` and :numref:`{number} <constraints-chapter>`) or Part III (:numref:`Chapter {number} <relational-model-chapter>`).

There are many ways to represent the relational database: logical or physical data models (:numref:`Chapter {number} <other-notations-chapter>`), text or tabular descriptions, or SQL code.  Which you use will depend on your development process and needs.  In this chapter, we will provide simple text descriptions in tabular format.

We start with the basic conversion rules, converting pieces of our example data model as we go.  The full set of tables resulting from our conversion is given at the end of the chapter.

Entities
::::::::

The first step in building a relational database from an ERD is creating a table from each entity in the data model.  Weak entities need slightly different handling than regular entities, so we will address them separately, starting with regular entities.

Regular entities
-----------------

First, decide on a name for the table - this does not have to be the same as the entity name!  There are many naming schemes for tables.  If you are building a database for a company or organization that has naming standards, you will of course want to follow those.  Otherwise, choose a basic approach and be consistent.  For example, some databases use plural nouns for tables, while others use singular nouns.  In our data model from :numref:`Chapter {number} <erd-chapter>`, the entity **employee** might become a table named **employee** or **employees**.  Another naming issue arises with table names containing multiple words; some databases choose to run these together, while others employ underscore characters.  For example, the entity **assembly line** could become a table named **assemblyline** or **assembly_line**.  In our examples below, we will use singular nouns and underscores.

Most attributes for the entity should be converted to columns in the new table.  Do not create columns for derived attributes, as these values are not intended to be stored.  Do not create columns for multivalued attributes; we will address these later.  For composite attributes, create columns only for the component attributes, not the composite itself.  As with entities, you will need to decide on a name for each new column, which does not have to be the same as the attribute name.  You will also need to specify a type and any constraints for the column.  Determining appropriate types for some columns may require consultation with your data domain experts.  Constraints may be added as appropriate.  In the descriptions below, we will use simple type and constraint descriptions, rather than SQL syntax.

Choose a key attribute (every regular entity should have at least one) and use the column created from it as the primary key for the new table.  If the entity has multiple key attributes, you will need to decide which one makes most sense as a primary key.  Simpler primary keys are usually preferred over more complex ones.  If desired, you can constrain the columns resulting from other keys to be not null and unique similar to primary key columns.  For example, an employee table might use a company generated ID number as its primary key, and also include a column for a government issued ID number which we would want to constrain to prevent duplicates.

Here is our ERD depiction of the **employee** entity:

.. image:: employee.svg
    :alt: The employee entity and its attributes

Here is a preliminary conversion of the **employee** entity into a relational table named **employee**:

.. table:: Table **employee** (preliminary)
    :class: lined-table

    +---------------+----------+--------------+-----------------------------+
    | Column name   | Type     | Constraints  | Notes                       |
    +===============+==========+==============+=============================+
    | id            | integer  | not null     |                             |
    +---------------+----------+--------------+-----------------------------+
    | name          | text     | not null     |                             |
    +---------------+----------+--------------+-----------------------------+
    | position      | text     |              |                             |
    +---------------+----------+--------------+-----------------------------+
    | pay_rate      | currency |              |                             |
    +---------------+----------+--------------+-----------------------------+
    | pay_type      | character| 's' or 'h'   | s = salaried, h = hourly    |
    +---------------+----------+--------------+-----------------------------+
    | **Keys**                                                              |
    |                                                                       |
    | Primary key: id                                                       |
    +---------------+----------+--------------+-----------------------------+

This is not yet the final **employee** table!  We will add additional columns to the table when we address the relationships that the **employee** entity participates in.

Weak entities
-------------

Weak entities are converted into tables in nearly the same way as regular entities.  However, recall that a weak entity has no identifying key attribute.  Instead, it has a partial key, which must be combined with the key of the parent entity.  In our example, the **assembly line** entity is weak.  Its partial key, the number of the assembly line within a particular factory, must be combined with the factory identity for full identification.

The table created from a weak entity must therefore incorporate the key from the parent entity as an additional column.  The primary key for the new table will be composed of the columns created from the parent key and from the partial key.  Additionally, the column created from the parent key should be constrained to always match some key in the parent table, using a foreign key constraint.

Here is the ERD of **assembly line** and its parent entity, **factory**:

.. image:: assembly_line.svg
    :alt:  The assembly line and factory entities, their attributes, and the contains relationship connecting them

Using the above guidelines, we should create tables **factory** and **assembly_line**, and include a column in **assembly_line** for values from the **city** column of **factory**.  A good choice of name for these "borrowed" columns is to concatenate the original table and column names together; in our case, this gives us the column **factory_city**.  (We will use the term "borrow" in reference to this process of inserting a column in one table to hold values from the primary key column of a related table.)  Here is the preliminary conversion of **factory** and the final conversion of **assembly line**:

.. table:: Table **factory** (preliminary)
    :class: lined-table

    +---------------+----------+--------------+-----------------------------+
    | Column name   | Type     | Constraints  | Notes                       |
    +===============+==========+==============+=============================+
    | city          | text     | not null     |                             |
    +---------------+----------+--------------+-----------------------------+
    | **Keys**                                                              |
    |                                                                       |
    | Primary key: city                                                     |
    +---------------+----------+--------------+-----------------------------+

.. table:: Table **assembly_line**
    :class: lined-table

    +---------------+----------+--------------+-----------------------------+
    | Column name   | Type     | Constraints  | Notes                       |
    +===============+==========+==============+=============================+
    | factory_city  | text     | not null     |                             |
    +---------------+----------+--------------+-----------------------------+
    | number        | integer  | not null     |                             |
    +---------------+----------+--------------+-----------------------------+
    | throughput    | real     |              |                             |
    +---------------+----------+--------------+-----------------------------+
    | **Keys**                                                              |
    |                                                                       |
    | Primary key: factory_city, number                                     |
    |                                                                       |
    | Foreign key: factory_city |right-arrow| factory (city)                |
    +---------------+----------+--------------+-----------------------------+


Relationships
:::::::::::::

Relationships can be handled using a few different approaches, depending on the cardinality ratio of the relationship.  Most generally, we can create a table to represent the relationship.  This kind of table is known as a *cross-reference* table, and acts as an intermediary in a three-way join with the two (or more) tables whose entities participate in the relationship.  As we will see, some cardinality ratios permit simpler solutions.

Many-to-many
------------

Many-to-many relationships are the most general type of relationship; a database structure accommodating a many-to-many relationship can also accommodate one-to-many or one-to-one relationships, as "one" is just a special case of "many".  The challenge for many-to-many relationships is how to represent a connection from a record in one table to multiple records in the other table.  While modern SQL allows array valued columns in tables, not all databases support them.  The traditional solution is to create a cross-reference table.

Given a table **A** and a table **B**, we create a cross-reference table with columns corresponding to the primary keys of **A** and **B**.  Each row in the cross-reference table stores one unique pairing of a primary key value from **A** with a primary key value from **B**.  Each row thus represents a single connection between one row in **A** with one row in **B**.  If a row in **A** is related to multiple rows in **B**, then there will be multiple entries with the same **A** primary key value, paired with each related **B** primary key value.

For example, our ERD indicates a many-to-many relationship between the entities **vendor** and **part**.  A computer part (such as an 8TB hard drive) can come from multiple sellers, while sellers can sell multiple different computer parts:

.. image:: supplies.svg
    :alt: The vendor and part entities, their attributes, and the supplies relationship connecting them

We create tables **vendor** and **part** following the guidelines above, and then create the cross-reference table **vendor_part**.  (It is common to name a cross-reference table using the names of the two tables being related, although other schemes can of course be used.)  Note that the **supplies** relationship also has a relationship attribute, **price**, which we can incorporate into the cross-reference table.  The result, with some fictional data, is pictured below:

.. image:: vendor_part_xref.svg
    :alt: The tables vendor, part, and vendor_part with sample data

Data in the cross-reference table is constrained in several ways.  First, we only want to store the relationship between rows once, so we make the combination of primary keys from the related tables into a primary key for the cross-reference table.  In our example, the primary key is the combination of **vendor_name** and **part_number**.  Second, each of the borrowed primary key columns should be constrained to only hold values that are present in the original tables, using foreign key constraints.

Table descriptions for **vendor**, **part**, and the **vendor_part** cross-reference table are given below:

.. table:: Table **vendor**
    :class: lined-table

    +---------------+----------+--------------+-----------------------------+
    | Column name   | Type     | Constraints  | Notes                       |
    +===============+==========+==============+=============================+
    | name          | text     | not null     |                             |
    +---------------+----------+--------------+-----------------------------+
    | email         | text     |              |                             |
    +---------------+----------+--------------+-----------------------------+
    | phone         | text     |              |                             |
    +---------------+----------+--------------+-----------------------------+
    | **Keys**                                                              |
    |                                                                       |
    | Primary key: name                                                     |
    +---------------+----------+--------------+-----------------------------+

.. table:: Table **part**
    :class: lined-table

    +---------------+----------+--------------+-----------------------------+
    | Column name   | Type     | Constraints  | Notes                       |
    +===============+==========+==============+=============================+
    | part_number   | text     | not null     |                             |
    +---------------+----------+--------------+-----------------------------+
    | description   | text     |              |                             |
    +---------------+----------+--------------+-----------------------------+
    | **Keys**                                                              |
    |                                                                       |
    | Primary key: part_number                                              |
    +---------------+----------+--------------+-----------------------------+

.. table:: Table **vendor_part**
    :class: lined-table

    +---------------+----------+--------------+-----------------------------+
    | Column name   | Type     | Constraints  | Notes                       |
    +===============+==========+==============+=============================+
    | vendor_name   | text     | not null     |                             |
    +---------------+----------+--------------+-----------------------------+
    | part_number   | text     | not null     |                             |
    +---------------+----------+--------------+-----------------------------+
    | price         | currency |              |                             |
    +---------------+----------+--------------+-----------------------------+
    | **Keys**                                                              |
    |                                                                       |
    | Primary key: vendor_name, part_number                                 |
    |                                                                       |
    | Foreign key: vendor_name |right-arrow| vendor (name)                  |
    |                                                                       |
    | Foreign key: part_number |right-arrow| part (part_number)             |
    +---------------+----------+--------------+-----------------------------+


One-to-many
-----------

As a special case of many-to-many relationships, one-to-many relationships can be implemented in the database using a cross-reference table as above.  We have another choice, however.  Observing that rows on the "many" side of the relationship can be associated with at most one row from the "one" side, we can choose to capture the relationship by storing the primary key of the "one" side table in the "many" side table.

In our ERD, the **employee** entity participates in one-to-many relationships with both **factory** and itself:

.. image:: one_to_many.svg
    :alt: The employee and factory entities and their attributes, and the supervises, manages, and works at relationships

There is also a one-to-one relationship between **employee** and **factory**, which we will deal with in the next section.

Considering first the **works at** relationship, we see that each employee works at no more than one factory.  Therefore, we can include a column for the factory's city in the **employee** table.  For consistency with previous choices, we will call this column **factory_city**.  This column should be constrained by a foreign key referencing the **factory** table.

We also have the **supervises** relationship to deal with.  In the same fashion as above, we should include a column in the **employee** table containing primary keys from the **employee** table.  However, we should give careful consideration to the name we give this added column; **employee_id** would be a very misleading choice!  A better choice is to consider the role of the employee whose id will be stored, and call the column **supervisor_id**.

With these changes, the **employee** table now looks like:

.. table:: Table **employee**
    :class: lined-table

    +---------------+----------+--------------+-----------------------------+
    | Column name   | Type     | Constraints  | Notes                       |
    +===============+==========+==============+=============================+
    | id            | integer  | not null     |                             |
    +---------------+----------+--------------+-----------------------------+
    | name          | text     | not null     |                             |
    +---------------+----------+--------------+-----------------------------+
    | position      | text     |              |                             |
    +---------------+----------+--------------+-----------------------------+
    | pay_rate      | currency |              |                             |
    +---------------+----------+--------------+-----------------------------+
    | pay_type      | character|   's' or 'h' | s = salaried, h = hourly    |
    +---------------+----------+--------------+-----------------------------+
    | factory_city  | text     |              |                             |
    +---------------+----------+--------------+-----------------------------+
    | supervisor_id | integer  |              |                             |
    +---------------+----------+--------------+-----------------------------+
    | **Keys**                                                              |
    |                                                                       |
    | Primary key: id                                                       |
    |                                                                       |
    | Foreign key: factory_city |right-arrow| factory (city)                |
    |                                                                       |
    | Foreign key: supervisor_id |right-arrow| employee (id)                |
    +---------------+----------+--------------+-----------------------------+

Using a cross-reference table instead of the above scheme is a perfectly valid choice, and may be preferable if there is any chance the data model might change such that the one-to-many relationship becomes many-to-many.  In our example ERD, a given computer model is built at only one factory (while factories can build multiple different models); however, it would not be surprising if, at some point, we want to allow for models to be built at multiple locations.  We might choose to use a cross-reference table for the relationship between **factory** and **model** in anticipation of this possibility.

One-to-one
----------

One-to-one relationships can be considered a special case of one-to-many relationships, so you can utilize either approach suitable for one-to-many relationships.  In most cases, it will be preferable to borrow the primary key from one table as a foreign key in the other table.  Using this approach, you could borrow from either side; however, one choice is often preferable to another.

In our example, we have a one-to-one relationship, **manages**, between **employee** and **factory**.  We could therefore add another column to the **employee** table, this time for the city of the factory that the employee manages.  However, most employees do not manage factories, so the column will end up containing many ``NULL`` values.

On the other hand, every factory should have a manager (implied by the total participation of **factory** in the relationship). It makes perfect sense, then, to add a column to the **factory** table for the employee managing the factory.  This is another situation in which it makes sense to name the column for the role of the employee in this relationship, so we will call the new column **manager_id**.

Here is the completed **factory** table:

.. table:: Table **factory**
    :class: lined-table

    +---------------+----------+--------------+-----------------------------+
    | Column name   | Type     | Constraints  | Notes                       |
    +===============+==========+==============+=============================+
    | city          | text     | not null     |                             |
    +---------------+----------+--------------+-----------------------------+
    | manager_id    | integer  |see note [#]_ |                             |
    +---------------+----------+--------------+-----------------------------+
    | **Keys**                                                              |
    |                                                                       |
    | Primary key: city                                                     |
    |                                                                       |
    | Foreign key: manager_id |right-arrow| employee (id)                   |
    +---------------+----------+--------------+-----------------------------+

In some rare cases, it may make sense to handle a one-to-one relationship by simply merging the participating tables into one table.  This should probably be reserved for situations in which both entities have total participation in the relationship.

Higher arity relationships
--------------------------

For relationships with three or more participants, a cross-reference table incorporating primary keys from each of the participating tables is the best choice.

Identifying relationships
-------------------------

Identifying relationships for weak entities are necessarily one-to-many or one-to-one.  However, the conversion of the weak entity already incorporates a column containing primary key values from the parent table.  This suffices to capture the relationship.

Multivalued attributes
::::::::::::::::::::::

Multivalued attributes can be used to model a few different scenarios.  As a result, there are multiple choices for how to store multivalued data in a relational database.

In the simplest case, a multivalued attribute is used when a list of arbitrary values needs to be stored, but there is no particular expectation that the values will be examined in a search of the database.  In this case, an array-valued column may be an appropriate choice for databases that support such columns.

When there is a need to query the values associated with a multivalued attribute, or for databases that do not support array-valued columns, the best choice may be to make a simple table with two columns, one for the primary key of the owning table, and one for the values themselves.  Each entry in the table associates one value with the instance of the entity.

In our example, computer models can be marketed to customers for different applications, such as gaming, video editing, or business use.  This is represented in our data model with the multivalued **application** attribute:

.. image:: multivalued.svg
    :alt: The model entity and its attributes

We might, then, implement the model entity and its attributes using the following two tables:

.. table:: Table **model** (preliminary)
    :class: lined-table

    +---------------+----------+--------------+-----------------------------+
    | Column name   | Type     | Constraints  | Notes                       |
    +===============+==========+==============+=============================+
    | name          | text     | not null     |                             |
    +---------------+----------+--------------+-----------------------------+
    | number        | text     | not null     |                             |
    +---------------+----------+--------------+-----------------------------+
    | type          | text     |              |                             |
    +---------------+----------+--------------+-----------------------------+
    | **Keys**                                                              |
    |                                                                       |
    | Primary key: name, number                                             |
    +---------------+----------+--------------+-----------------------------+

.. table:: Table **model_application** (preliminary)
    :class: lined-table; in this case

    +---------------+----------+--------------+----------------------------------+
    | Column name   | Type     | Constraints  | Notes                            |
    +===============+==========+==============+==================================+
    | model_name    | text     | not null     |                                  |
    +---------------+----------+--------------+----------------------------------+
    | model_number  | text     | not null     |                                  |
    +---------------+----------+--------------+----------------------------------+
    | application   | text     | not null     |                                  |
    +---------------+----------+--------------+----------------------------------+
    | **Keys**                                                                   |
    |                                                                            |
    | Primary key: model_name, model_number, application                         |
    |                                                                            |
    | Foreign key: (model_name, model_number) |right-arrow| model (name, number) |
    +---------------+----------+--------------+----------------------------------+

Many applications also require the values associated with a multivalued attribute to be restricted to a certain list of values.  In this case, an additional table is used.  The additional table exists just to contain the allowed values, allowing us to constrain the data to just those values.  For more complex values, an artificial identifier may be added as a primary key, and the primary key used in the multivalued attribute table instead of the values themselves, in which case the multivalued attribute table becomes a cross-reference table. For small lists of simple values (as in our example), this adds unnecessary complication.

For our example, we will constrain the **application** column using a foreign key constraint referencing this simple table:

.. table:: Table **application**
    :class: lined-table

    +---------------+----------+--------------+-----------------------------+
    | Column name   | Type     | Constraints  | Notes                       |
    +===============+==========+==============+=============================+
    | application   | text     | not null     | gaming, business, etc.      |
    +---------------+----------+--------------+-----------------------------+
    | **Keys**                                                              |
    |                                                                       |
    | Primary key: application                                              |
    +---------------+----------+--------------+-----------------------------+


Full model conversion
:::::::::::::::::::::

In this section, we collect together all of the tables produced from our example data model, using the approach outlined above.  For each table we include a short explanation of how the table relates to the data model.

.. table:: Table **employee**
    :class: lined-table

    +---------------+----------+--------------+-----------------------------+
    | Column name   | Type     | Constraints  | Notes                       |
    +===============+==========+==============+=============================+
    | id            | integer  | not null     |                             |
    +---------------+----------+--------------+-----------------------------+
    | name          | text     | not null     |                             |
    +---------------+----------+--------------+-----------------------------+
    | position      | text     |              |                             |
    +---------------+----------+--------------+-----------------------------+
    | pay_rate      | currency |              |                             |
    +---------------+----------+--------------+-----------------------------+
    | pay_type      | character| 's' or 'h'   | s = salaried, h = hourly    |
    +---------------+----------+--------------+-----------------------------+
    | factory       | text     |              |                             |
    +---------------+----------+--------------+-----------------------------+
    | supervisor_id | integer  |              |                             |
    +---------------+----------+--------------+-----------------------------+
    | **Keys**                                                              |
    |                                                                       |
    | Primary key: id                                                       |
    |                                                                       |
    | Foreign key: factory_city |right-arrow| factory (city)                |
    |                                                                       |
    | Foreign key: supervisor_id |right-arrow| employee (id)                |
    +---------------+----------+--------------+-----------------------------+

The **employee** table contains columns for the attributes of the **employee** entity and foreign keys implementing the relationships **works at** and **supervises**.

.. table:: Table **factory**
    :class: lined-table

    +---------------+----------+--------------+-----------------------------+
    | Column name   | Type     | Constraints  | Notes                       |
    +===============+==========+==============+=============================+
    | city          | text     | not null     |                             |
    +---------------+----------+--------------+-----------------------------+
    | manager_id    | integer  |              |                             |
    +---------------+----------+--------------+-----------------------------+
    | **Keys**                                                              |
    |                                                                       |
    | Primary key: city                                                     |
    |                                                                       |
    | Foreign key: manager_id |right-arrow| employee (id)                   |
    +---------------+----------+--------------+-----------------------------+

The **factory** table contains columns for the attributes of the **factory** entity and a foreign key implementing the relationship **manages**.  The **throughput** attribute is not reflected in the table, as it is a derived attribute.  The throughput of a factory can be computed by summing the throughputs of the assembly lines in the factory.

.. table:: Table **assembly_line**
    :class: lined-table

    +---------------+----------+--------------+-----------------------------+
    | Column name   | Type     | Constraints  | Notes                       |
    +===============+==========+==============+=============================+
    | factory_city  | text     | not null     |                             |
    +---------------+----------+--------------+-----------------------------+
    | number        | integer  | not null     |                             |
    +---------------+----------+--------------+-----------------------------+
    | throughput    | real     |              |                             |
    +---------------+----------+--------------+-----------------------------+
    | **Keys**                                                              |
    |                                                                       |
    | Primary key: factory_city, number                                     |
    |                                                                       |
    | Foreign key: factory_city |right-arrow| factory (city)                |
    +---------------+----------+--------------+-----------------------------+

The **assembly_line** table implements the **assembly line** weak entity.  It incorporates a foreign key referencing the **factory** parent entity.  Its primary key is composed of the parent entity key (**factory_city**) and the partial key (**number**).

.. table:: Table **model**
    :class: lined-table

    +---------------+----------+--------------+-----------------------------+
    | Column name   | Type     | Constraints  | Notes                       |
    +===============+==========+==============+=============================+
    | name          | text     | not null     |                             |
    +---------------+----------+--------------+-----------------------------+
    | number        | text     | not null     |                             |
    +---------------+----------+--------------+-----------------------------+
    | type          | text     |              |                             |
    +---------------+----------+--------------+-----------------------------+
    | factory_city  | text     |              |                             |
    +---------------+----------+--------------+-----------------------------+
    | **Keys**                                                              |
    |                                                                       |
    | Primary key: name, number                                             |
    |                                                                       |
    | Foreign key: factory_city |right-arrow| factory (city)                |
    +---------------+----------+--------------+-----------------------------+

The **model** table contains columns for the attributes of the **model** entity.  Only the component attributes of the composite attribute **designation** are included; as **designation** was also the key attribute for **model**, the **model** table has a composite primary key.  The table also includes a foreign key implementing the **builds** relationship.  As mentioned in the text above, the **builds** relationship could alternatively be implemented using a cross-reference table connecting **factory** and **builds**, but we have opted for the simpler solution here.  We assume that the designation of computer models includes the name of the computer line (e.g. "Orion") and some particular version of the computer line, which we call the "number" of the model.  These versions may contain letters as well as numbers (e.g., "xz450"), which is why a column named "number" is implemented as text.

.. table:: Table **model_application**
    :class: lined-table; in this case

    +---------------+----------+--------------+----------------------------------+
    | Column name   | Type     | Constraints  | Notes                            |
    +===============+==========+==============+==================================+
    | model_name    | text     | not null     |                                  |
    +---------------+----------+--------------+----------------------------------+
    | model_number  | text     | not null     |                                  |
    +---------------+----------+--------------+----------------------------------+
    | application   | text     | not null     |                                  |
    +---------------+----------+--------------+----------------------------------+
    | **Keys**                                                                   |
    |                                                                            |
    | Primary key: model_name, model_number, application                         |
    |                                                                            |
    | Foreign key: (model_name, model_number) |right-arrow| model (name, number) |
    |                                                                            |
    | Foreign key: application |right-arrow| application (application)           |
    +---------------+----------+--------------+----------------------------------+

The **model_application** table implements the multivalued attribute **application** of the **model** entity.  Each row of the table contains a single **application** value describing a particular computer model.  Note that, as the **model** entity has a composite primary key, the **model_application** table has a composite foreign key referencing its parent (*not* two separate foreign keys for each component of the parent key).  Additionally, we constrain the values in **application** to come from a set list of possible values, contained in the **application** table (below).

.. table:: Table **application**
    :class: lined-table

    +---------------+----------+--------------+-----------------------------+
    | Column name   | Type     | Constraints  | Notes                       |
    +===============+==========+==============+=============================+
    | application   | text     | not null     | gaming, business, etc.      |
    +---------------+----------+--------------+-----------------------------+
    | **Keys**                                                              |
    |                                                                       |
    | Primary key: application                                              |
    +---------------+----------+--------------+-----------------------------+

The **application** table contains a simple list of unique values which are available to insert into the **model_application** table.

.. table:: Table **part**
    :class: lined-table

    +---------------+----------+--------------+-----------------------------+
    | Column name   | Type     | Constraints  | Notes                       |
    +===============+==========+==============+=============================+
    | part_number   | text     | not null     |                             |
    +---------------+----------+--------------+-----------------------------+
    | description   | text     |              |                             |
    +---------------+----------+--------------+-----------------------------+
    | **Keys**                                                              |
    |                                                                       |
    | Primary key: part_number                                              |
    +---------------+----------+--------------+-----------------------------+

The **part** table contains columns for the attributes of the **part** entity.  The column **part_number** here, similar to the model "number" above, can contain characters as well as numbers, so again we use a text type column.

.. table:: Table **model_part**
    :class: lined-table

    +---------------+----------+--------------+----------------------------------+
    | Column name   | Type     | Constraints  | Notes                            |
    +===============+==========+==============+==================================+
    | model_name    | text     | not null     |                                  |
    +---------------+----------+--------------+----------------------------------+
    | model_number  | text     | not null     |                                  |
    +---------------+----------+--------------+----------------------------------+
    | part_number   | text     | not null     |                                  |
    +---------------+----------+--------------+----------------------------------+
    | **Keys**                                                                   |
    |                                                                            |
    | Primary key: model_name, model_number, part_number                         |
    |                                                                            |
    | Foreign key: (model_name, model_number) |right-arrow| model (name, number) |
    |                                                                            |
    | Foreign key: part_number |right-arrow| part (part_number)                  |
    +---------------+----------+--------------+----------------------------------+

The **model_part** table is a cross-reference table implementing the **can use** relationship.

.. table:: Table **vendor**
    :class: lined-table

    +---------------+----------+--------------+-----------------------------+
    | Column name   | Type     | Constraints  | Notes                       |
    +===============+==========+==============+=============================+
    | name          | text     | not null     |                             |
    +---------------+----------+--------------+-----------------------------+
    | email         | text     |              |                             |
    +---------------+----------+--------------+-----------------------------+
    | phone         | text     |              |                             |
    +---------------+----------+--------------+-----------------------------+
    | **Keys**                                                              |
    |                                                                       |
    | Primary key: name                                                     |
    +---------------+----------+--------------+-----------------------------+

The **vendor** table contains columns for the attributes of the **vendor** entity.  Only the component attributes of the **contact info** attribute are reflected.

.. table:: Table **vendor_part**
    :class: lined-table

    +---------------+----------+--------------+-----------------------------+
    | Column name   | Type     | Constraints  | Notes                       |
    +===============+==========+==============+=============================+
    | vendor_name   | text     | not null     |                             |
    +---------------+----------+--------------+-----------------------------+
    | part_number   | text     | not null     |                             |
    +---------------+----------+--------------+-----------------------------+
    | price         | currency |              |                             |
    +---------------+----------+--------------+-----------------------------+
    | **Keys**                                                              |
    |                                                                       |
    | Primary key: vendor_name, part_number                                 |
    |                                                                       |
    | Foreign key: vendor_name |right-arrow| vendor (name)                  |
    |                                                                       |
    | Foreign key: part_number |right-arrow| part (part_number)             |
    +---------------+----------+--------------+-----------------------------+

The **vendor_part** table is a cross-reference table implementing the **supplies** relationship.  In addition to the foreign keys for the tables it relates to, it contains a column for the **price** attribute of the relationship.


Self-check exercises
::::::::::::::::::::

This section has some questions you can use to check your understanding of how to convert ERDs to a relational database.

.. mchoice:: erd_to_relational_self_test_1

    Entities in our ERD become tables in our relational database.  What do relationships become?

    -   Tables

        - Any relationship can be converted into a cross-reference table.  Is that the only possibility?

    -   Foreign keys

        - One-to-one and one-to-many relationships can be converted into foreign keys in our database.  Are those the only cardinality ratios?

    -   Merging of tables

        - One-to-one relationships can result in merging tables, although this is rare.

    -   All of the above

        + Each of the methods above can be applied, depending on the cardinality ratio of the relationship and other factors.

.. mchoice:: erd_to_relational_self_test_2

    Consider the ERD below.  We create tables **a** and **b**, each of which have a primary key column named "id".  (Assume there are additional columns from attributes not shown.)  What is the simplest way to convert the relationship between **A** and **B**?

    .. image:: self_test_many_to_one.svg
        :alt: Entities A and B each with key attribute ID.  The relationship between A and B is many-to-one (many on the A side).

    -   Create a column named "a_id" in table **b**, and make it a foreign key referencing table **a**.

        - Since a row in **b** could be related to multiple rows in **a**, we would need to store multiple ID values in column **a_id**.
          Some databases would permit this, but it would complicate queries and updates on the database.

    -   Create a column named "b_id" in table **a**, and make it a foreign key referencing table **b**.

        + This is the simplest solution, assuming we do not expect the relationship to change to many-to-many in the future.

    -   Create a cross-reference table, **a_b**, containing columns **a_id** and **b_id** as foreign keys referencing **a** and **b** respectively.

        - This is an allowable conversion.  Is it the simplest?

    -   Merge tables **a** and **b** into a new table.

        - This is not a good choice; while such a structure can be made to work, it is not considered good database design and is prone to errors.
          We would say that this table is not properly *normalized*.  We explore normalization in :numref:`Part {number} <relational-theory-part>`.

.. mchoice:: erd_to_relational_self_test_3

    Consider the ERD below.  We create table **r** with primary key column **id**.  What should table **w** look like?

    .. image:: self_test_weak.svg
        :alt: Entity R with key ID, and weak entity W with partial key partial.  The identifying relationship between R and W is one-to-many.

    -   The table should have a column **partial** as primary key.  Additionally, create a cross-reference table **r_w**.

        - Partial keys cannot become primary keys.  They do not represent unique identifiers for the instances of the weak entity.

    -   The table should have columns **partial** and **r_id**.  The primary key is **partial**.
        Add a foreign key constraint on **r_id** referencing **r**.

        - Partial keys cannot become primary keys.  They do not represent unique identifiers for the instances of the weak entity.

    -   The table should have columns **partial** and **r_id**.  The primary key is a composite of **r_id** and **partial**.
        Add a foreign key constraint on **r_id** referencing **r**.

        + Correct.

    -   The table should have columns **partial** and **r_id**.  The primary key is **r_id**.  Add a foreign key constraint on **r_id** referencing **r**.

        - The parent key is not a sufficient key for the weak entity; there will be multiple rows in **w** with the same values for **r_id**.
          Therefore it cannot be a primary key.

.. mchoice:: erd_to_relational_self_test_4

    Consider the ERD below.  We create tables **c** and **d**, each of which have a primary key column named "id".  How should we handle the relationship between **C** and **D**?

    .. image:: self_test_relationship_attribute.svg
        :alt: Entities C and D each with key attribute ID.  The relationship between C and D is many-to-many and has an attribute named "x".

    -   Borrow the primary key from one table as a foreign key into the other table (either direction is fine).  Add a column named "x" into the table with the foreign key column.

        - This is not a good choice; while such a structure can be made to work, it is not considered good database design and is prone to errors.
          We would say that this table is not properly *normalized*.  We explore normalization in :numref:`Part {number} <relational-theory-part>`.

    -   Create a cross reference table **c_d** with columns **c_id**, **d_id**, and **x**.  Make a composite primary key using **c_id** and **d_id**.
        Add foreign key constraints on **c_id** and **d_id** referencing **c** and **d**, respectively.

        + Correct.

    -   Create a cross reference table **c_d** with columns **c_id** and **d_id**.  Make a composite primary key using **c_id** and **d_id**.
        Add foreign key constraints on **c_id** and **d_id** referencing **c** and **d**, respectively.  Create another table, **c_d_x**,
        with columns **c_id**, **d_id**, and **x**.  Table **c_d_x** has primary key **x**, and a foreign key constraint on **c_id** and **d_id** referencing table **c_d**.

        - This could almost work (you would need a different primary key for **c_d_x**), but it is unnecessarily complicated.

    -   Create a cross reference table **c_d** with columns **c_id** and **d_id**.  Make a composite primary key using **c_id** and **d_id**.
        Add foreign key constraints on **c_id** and **d_id** referencing **c** and **d**, respectively.  Add column **x** to either **c** or **d**.

        - The values for **x** will differ for different combinations of **c** and **d**.
          There is no good way to capture the dependence of **x** on **d**, for example, if we put the column in **c**.

.. mchoice:: erd_to_relational_self_test_5

    Which of the following statements is *false*?

    -   Composite attributes result in columns for each component as well as the composite.

        + We do not create a column for the composite, just the components.

    -   Multivalued attributes usually require an additional table in the database.

        - This is true.  In some cases it may be possible to use array-valued columns to handle a multivalued attribute,
          but otherwise we need an additional table or tables.

    -   No column is created for derived attributes.

        - This is true.  Derived attributes are not intended to be stored, as they can be computed from other values in the database.

    -   If an entity has a composite key attribute, the resulting table will have a composite primary key.

        - This is true.



|chapter-end|

----

**Notes**

.. [#] Due to the total participation of **factory** in the **manages** relationship, it might seem we should constrain the **manager_id** column to never contain ``NULL``.  Some care should be taken in adding such constraints.  While a factory "must" have a manager, there may be times when a factory has no manager, e.g., when a manager leaves the company and a new manager has not yet been identified.  If the **manager_id** column is constrained to never hold ``NULL``, it will be difficult to correctly reflect the true situation in the database.  In general, use caution and examine all of your edge cases before choosing to constrain a column.

|license-notice|



## Chapter: other-notations.rst

.. _other-notations-chapter:

===============================
ERD alternatives and variations
===============================

In this chapter we explore alternatives to Chen notation entity-relationship data modeling as well as other variations.  We start with *crow's foot* notation, a popular notation for entity-relationship modeling.  We will show how the basic crow's foot notation can be used to model relational databases at lower levels of abstraction.  We will finish with an overview of some of the more common variations you are likely to encounter in both Chen and crow's foot notation.  The examples used throughout correspond to the computer manufacturer data model developed in :numref:`Chapter {number} <erd-chapter>`.

.. index:: crow's foot notation

Crow's foot notation
::::::::::::::::::::

"Crow's foot" is the nickname given to a family of modeling notations that originated in a :ref:`paper by Gordon Everest <data-modeling-references>` in 1976.  The notation has been widely adopted, expanded, and modified since.  The name comes from the symbol used to represent the "many" cardinality in relationships, which resembles a crow's foot (Everest originally called the symbol an "inverted arrow", and later a "fork").

Entity-relationship modeling
----------------------------

In crow's foot notation, entities are represented with simple rectangles.  Entities can be labeled simply with a name for a higher level of abstraction, or they can contain a name and a list of attributes.  Key attributes can be indicated in various ways; we will style keys with bold type and underlining.  In our example data model, we have an entity modeling data regarding employees of our fictional computer manufacturer:

.. image:: crows_foot_entity.svg
    :alt: A rectangle with the header "employee" and a list of the attributes of the employee entity; the ID attribute is boldface and underlined

Relationships are represented with lines connecting entities.  Cardinality ratios are specified with different line ending symbols.  The possible cardinalities are:

.. |cf_zero_or_one| image:: crows_foot_zero_or_one.svg
    :alt: A horizontal line ending in a symbol composed of an open circle and a vertical line

.. |cf_one_exactly| image:: crows_foot_one_exactly.svg
    :alt: A horizontal line ending in a symbol composed of two vertical lines

.. |cf_zero_or_more| image:: crows_foot_zero_or_more.svg
    :alt: A horizontal line ending in a symbol composed of an open circle and three branching lines

.. |cf_one_or_more| image:: crows_foot_one_or_more.svg
    :alt: A horizontal line ending in a symbol composed of a vertical line and three branching lines

=================== ============
|cf_zero_or_one|    Zero or one
|cf_one_exactly|    One exactly
|cf_zero_or_more|   Zero or more
|cf_one_or_more|    One or more
=================== ============

These cardinality symbols have two parts.  The symbol closest to the entity indicates the maximum cardinality - either *one* (represented by a vertical line) or *many* (represented by the branching "crow's foot").  The symbol further from the entity indicates minimum cardinality - either *zero* (represented by the open circle) or *one*.  A minimum cardinality of one is sometimes stated in terms of the entity being *mandatory*, while a minimum cardinality of zero indicates an *optional* entity.

Consider the relationship pictured below:

.. image:: crows_foot_cardinality_example.svg
    :alt: A rectangle labeled "A" connected to a rectangle labeled "B"; the connector on the A side is the "one exactly" connector, while the connector on the "B" side is the "zero or more" connector

This diagram tells us that an instance of the **A** entity can be associated with zero or more instances of **B**.  An instance of **B** must be associated with exactly one instance of **A**.

Relationships may be further annotated with text to name or describe the relationship.

In our example data model, the **employee** entity participates in several relationships with itself and the **factory** entity:

.. image:: crows_foot_relationships.svg
    :alt: Entities employee and factory and their relationships; the employee entity has attributes ID (key), name, position, pay rate, and pay type; the factory entity has the key attribute city; the relationships are the many-to-one (optional on both sides) relationship between employee and factory labeled "works at", the one-to-one (exactly one on the employee side) relationship between employee and factory labeled "manages", and the many-to-one (optional on both sides) relationship between employee and itself labeled "supervises".

The basic crow's foot notation can be extended to encompass the same advanced elements as Chen's notation, such as composite, derived, and multivalued attributes, weak entities and partial keys, relationship attributes, and higher arity relationships.  Different drawing and modeling tools may or may not provide direct support for these, and notations vary widely.

Some database designers prefer crow's foot notation over Chen's notation for entity-relationship modeling, in part due to its relatively compact form.  We can compare the above diagram side-by-side with its equivalent in Chen notation:

.. image:: comparison.svg
    :alt: Side-by-side diagrams in crow's foot and Chen's notation showing the employee and factory entities and their attributes and relationships

Ultimately which notation you use will depend on your preferences and the preferences of the people you are working with on a given project.

.. index:: logical model, physical model

Lower level models
------------------

We have so far been discussing data modeling at an abstract level, which we might call the *conceptual* level.  At the conceptual level, the emphasis is on the fundamental data entities and their relationships, rather than the relational database constructs necessary to implement them.  For example, in conceptual modeling we typically do not include depictions of cross-reference tables, which are necessary in the implementation of many-to-many relationships, but which do not themselves represent entities of interest.  We might say that the conceptual model is focused on the *data* rather than the *database*.

At the next level of abstraction lives the *logical* model, which includes all of the relational database structure that results from applying the techniques described in :numref:`Chapter {number} <erd-to-relational-chapter>`.  Crow's foot notation is well suited to modeling at this level.

Below we show the conceptual and logical versions of two parts of our example data model.  Rectangles in the logical model now represent actual tables and list all columns in the table.  We show columns participating in primary keys in boldface and underlined; foreign key columns are italicized.  Logical models often include data types, but we have omitted those details for now.

.. figure:: crows_foot_conceptual_1.svg

    A conceptual model showing entities **employee** and **factory** and their relationships.

.. figure:: crows_foot_logical_1.svg

    The logical model constructed from the above conceptual model.  Note the addition of foreign key columns in both tables.

.. figure:: crows_foot_conceptual_2.svg

    A conceptual model showing entities **part** and **vendor** and the many-to-many relationship between them.  The relationship has an attribute, which we have shown as a rectangle connected to the relationship line.

.. figure:: crows_foot_logical_2.svg

    The logical model constructed from the above conceptual model.  The many-to-many relationship has been realized as a cross-reference table.

If we choose, we can add even more detail to create a *physical* model.  The physical model would definitely include data types as well as any constraints on columns or tables, and might include details such as indexes or even where a table lives on disk or on the network.

Each level of abstraction has value, but whether or not you create models at a particular level will depend on your needs.  As discussed in :numref:`Chapter {number} <erd-chapter>`, models at the highest levels of abstraction are particularly valuable in the early stages of developing a database, and in communicating with all of the various stakeholders in a project.  The conceptual model can be used to produce a database directly, or you may prefer to create a logical model as an intermediate stage.  On the other hand, for some projects you may skip the conceptual level and start with a logical model.  It can be very useful to maintain a logical model as documentation for a database; with large and complex databases, even regular users of the database can forget the names of tables and columns!  Physical models are mostly used by database administrators (DBAs) on very complex projects and are usually created in software tools that can also generate the SQL code to create the database.


Common variations
::::::::::::::::::

.. index:: UML, unified modeling language

Most visual languages for data modeling derive in greater or lesser degree from Chen's notation or crow's foot notation, although alternatives exist.  One popular alternative is the *unified modeling language* (UML).  While UML is not specifically intended for database design, it has been adapted for the purpose.  UML is especially applicable in more advanced settings involving inheritance hierarchies for entities.  Chen's notation has also been extended for these settings.  We do not cover inheritance in this book.

All data modeling languages share certain commonalities, such as entities, attributes, keys, relationships, and cardinality ratios.  Most have some notion of participation or minimum cardinality.  The basic concepts are the same, but the notations vary.  We give an overview of the most common variations you are likely to encounter below.

.. index:: cardinality ratio; alternate notation

Cardinality ratios and participation
------------------------------------

Participation and minimum cardinality can be equated when working with binary relationships.  If an entity has total participation in a binary relationship, then the minimum cardinality of the other entity is one (or at least, not zero).  Conversely, partial participation of an entity implies a minimum cardinality of zero for the other entity.  Typically you will use either participation or minimum cardinality, but not both.

.. |single-line| image:: single_line.svg
    :alt: A single line

.. |double-line| image:: double_line.svg
    :alt: A double line

.. |dotted-line| image:: dotted_line.svg
    :alt: A dashed line

.. table:: Participation

    +-----------------------+----------------------------+----------------------------+
    |                       | This book                  |  Alternative notation      |
    +=======================+============================+============================+
    | Partial participation | |single-line|              | |dotted-line|              |
    +-----------------------+----------------------------+----------------------------+
    | Total participation   | |double-line|              | |single-line|              |
    +-----------------------+----------------------------+----------------------------+

.. |zero_or_one_p| image:: zero_or_one_parenthetical.svg
    :alt: A line annotated with "(0,1)" at one end

.. |one_exactly_p| image:: one_exactly_parenthetical.svg
    :alt: A line annotated with "(1,1)" at one end

.. |zero_or_more_p| image:: zero_or_more_parenthetical.svg
    :alt: A line annotated with "(0,N)" at one end

.. |one_or_more_p| image:: one_or_more_parenthetical.svg
    :alt: A line annotated with "(1,N)" at one end

.. |two_or_three_p| image:: two_or_three_parenthetical.svg
    :alt: A line annotated with "(2,3)" at one end

.. |zero_or_one_r| image:: zero_or_one_range.svg
    :alt: A line annotated with "0..1" at one end

.. |one_exactly_r| image:: one_exactly_range.svg
    :alt: A line annotated with "1..1" at one end

.. |zero_or_more_r| image:: zero_or_more_range.svg
    :alt: A line annotated with "0..N" at one end

.. |one_or_more_r| image:: one_or_more_range.svg
    :alt: A line annotated with "1..N" at one end

.. |two_or_three_r| image:: two_or_three_range.svg
    :alt: A line annotated with "2..3" at one end

.. table:: Minimum and maximum cardinality

    +-----------------------+----------------------------------------+---------------------------------------------------------------------------------+
    |                       | Crow's foot notation                   |  Alternative notations                                                          |
    +=======================+========================================+============================================+====================================+
    | Zero or one           | |cf_zero_or_one|                       | |zero_or_one_p|                            | |zero_or_one_r|                    |
    +-----------------------+----------------------------------------+--------------------------------------------+------------------------------------+
    | Exactly one           | |cf_one_exactly|                       | |one_exactly_p|                            | |one_exactly_r|                    |
    +-----------------------+----------------------------------------+--------------------------------------------+------------------------------------+
    | Zero or more          | |cf_zero_or_more|                      | |zero_or_more_p|                           | |zero_or_more_r|                   |
    +-----------------------+----------------------------------------+--------------------------------------------+------------------------------------+
    | One or more           | |cf_one_or_more|                       | |one_or_more_p|                            | |one_or_more_r|                    |
    +-----------------------+----------------------------------------+--------------------------------------------+------------------------------------+
    | Specified min/max     |                                        | |two_or_three_p|                           | |two_or_three_r|                   |
    +-----------------------+----------------------------------------+--------------------------------------------+------------------------------------+


Attributes
----------

In our presentation of crow's foot logical models above, we used text styling (boldface and underlining) to indicate primary keys.  We used italics to indicate foreign keys.  Many drawing and modeling tools similarly use text styling to indicate keys, although not necessarily the styling we used.  Tools may also or instead use background or foreground colors to indicate keys and other properties of columns.

Many tools will also (or instead) indicate primary and foreign key columns with text indicators, usually "PK" and "FK".  Some will highlight primary keys by separating them from the other columns:

.. image:: entity_alternative.svg
    :alt: The entity employee with the primary key attribute labeled with "PK" and with the foreign key attributes labeled with "FK"



|chapter-end|


|license-notice|



## Chapter: index.rst

.. _data-modeling-part:

=============
DATA MODELING
=============

Part 2 of this book concerns graphical modeling in general, and entity-relationship diagrams in particular.  The diagram below shows the strong dependencies between chapters; chapters will assume knowledge introduced in earlier chapters as implied by the graph.  The dotted outlines indicate chapters from other sections of the book.

.. figure:: chapter_dependencies.svg

    Chapter dependency graph for Part 2

**Table of contents for Part 2**

.. toctree::
    :maxdepth: 3

    01-introduction/introduction
    02-ERD/ERD
    03-ERD-to-relational/ERD-to-relational
    04-other-notations/other-notations

|license-notice|



## Chapter: relational-model.rst

.. _relational-model-chapter:

====================================
The relational model of the database
====================================

.. index:: database; relational model of, relational model of databases

In this chapter we introduce the mathematical model that relational databases are based on.  The *relational model* of the database provides a mathematical foundation for describing and reasoning about databases.  While most relational database systems in practice vary in small ways from the mathematical model (see :numref:`Chapter {number} <sql-vs-theory-chapter>`), understanding the model facilitates a deeper understanding of these systems.

Given its mathematical foundations, the relational model is most conveniently expressed using at least some mathematical notation and terminology.  In the interests of keeping this book accessible to as wide an audience as possible, however, we will give the basics of the model using a minimum of notation and explain terms as we use them.


Model basics
::::::::::::

We start with a working definition of *set*, a mathematical object that we will use in defining other terms.  We then define *relations*, the fundamental objects of the relational model, and their associated terms.

Sets
----

A set is a mathematical object that represents a collection of distinct values.  Sets can be defined by some property that values have in common, or simply by listing all of the values in the set.  For some arbitrary value and some set, we can ask whether the value is a *member* of the set, that is, whether it is one of the values in the set.  For example, 2 is a member of the set of all numbers (an infinite set) and also a member of the set {1, 2, 3, 4} (a finite set containing four values).  On the other hand, 2 is not a member of the set of odd integers or the set of words describing colors (i.e., {blue, yellow, ...}).

A *subset* of a set is a set containing zero or more elements from the set and only from the set.  For the set {1, 2, 3, 4}, subsets include {2, 4}, {1, 2, 3, 4}, and {} (the *empty set*).  Note that any set is a subset of itself; a subset which is not equal to the whole set is termed a *proper subset* of the set.

A *superset* of a set is a set containing all elements from the set, and may contain elements not from the set.  For the set {1, 2, 3, 4}, supersets include {1, 2, 3, 4}, {1, 2, 3, 4, 5}, and {0, 1, 2, 3, 4, 5, 7}.  Note that any set is a superset of itself; a superset which contains elements not in the set is termed a *proper superset* of the set.

.. index:: relation

Relations
---------

In the relational model, data exist in relations.  A relation is often depicted as a tabular data structure:

.. image:: books.svg
    :alt: A tabular illustration of a relation named simple_books, showing a header with attribute names and several rows of data, or tuples.

This illustration is just one possible way of depicting the relation **simple_books**, and tables (or two-dimensional arrays) are just one data structure that can be used for storing relations.  From the perspective of the relational model, relations are mathematical objects, not data structures.

Formally, a relation is a set of *tuples* that share the same *domain*.

.. index:: tuple, domain

Tuples
------

A tuple in the relational model is defined in two different ways; which is used depends on which is more convenient in a particular context.  We will start with the normal mathematical definition of a tuple as an ordered list of values.  A single value in the tuple is also called an *element* of the tuple.  We denote tuples as a comma-separated list within parentheses.  Tuples correspond to rows in the table above.  For example, one tuple from the **simple_books** relation could be written as:

    (*The House of the Spirits*, Isabel Allende, 1982, magical realism)

Each element of a tuple belongs to some set, which we call the *domain* of the element.  In our example tuple, the first element belongs to the domain of book titles.

The tuple itself also belongs to a domain, which is defined in terms of the domains of each value in the tuple.  Tuples of the **simple_books** relation belong to the domain of tuples with four elements for which the first element belongs to the domain of book titles, the second element is from the domain of authors, the third element belongs to the domain of calendar years, and the fourth element is in the domain of literary genres.

.. index:: tuple; attribute

Attributes
----------

In an alternate definition of tuple, we can speak of the *attributes* of the tuple.  We can think of attributes as the named properties of the value represented by the tuple.  For example, if a tuple in the **simple_books** relation represents one book, then one attribute of the tuple is the book's **title**.  In our example tuple, the **title** attribute is *The House of the Spirits*.  The other attributes of books in our relation are **author**,  **year**, and **genre**.  Attribute names are shown in the header row of the table in the illustration above.

In this definition of tuple, tuples are not necessarily ordered lists; each value in the tuple is associated not with a position but with an attribute.  Each attribute is associated with a domain. For example, the **title** attribute for any tuple in **simple_books** must be a member of the domain of book titles.  Having names associated with values in a tuple is much more convenient than having to refer to the *n*-th element when we want to query our database.

The two definitions of tuple are not exclusive.  In the first definition of tuple, each position in the ordered collection also corresponds to a specific attribute - in our example, the first element is the **title** attribute.  While we can think of tuples as having named attributes in no particular order, in practice we typically assign an ordering to the attributes in a relation - so both definitions of tuple are used simultaneously.

.. index:: schema, relation schema

Schemas
-------

A relation's attributes and domains are defined by its *schema*.  A relation (a set of tuples) is considered to be an *instance* of the relation schema if it conforms to the definition given by the schema; that is, if all of the tuples in the relation have the named attributes defined by the schema, and the attribute values are members of the correct domains.  In some definitions, relation schemas also include constraints which relations must conform to, such as *key* constraints, discussed below.

In a typical database, each relation schema is paired with exactly one relation, which is the current relation for the schema.  When a modification is made to the data in the current relation, it produces a new current relation.  Except in some specialized types of databases, there is no history of past relations associated with a relation schema.  Thus, it is frequent practice to use the same name for the relation and its schema.

A *database* may be defined as a collection of relation schemas and their associated current relations.  The collection of relation schemas is called the database schema.

Uniqueness and permutations
:::::::::::::::::::::::::::

Relations, as sets of tuples, share certain important properties of sets.  First, items in a set must be distinct.  In the relational model, tuples must likewise be distinct, that is, no two tuples can have the same values for every attribute.  For our **simple_books** relation, it is entirely reasonable to suppose that we will add books that have the same author as some other tuple, or books published in the same year as another book.  However, we are forbidden to add a tuple that duplicates an existing tuple.

Another property (or perhaps lack of property) of sets is that there is no defined order of elements in a set.  An element of a set has no rank or position within the set.  Relations likewise have no intrinsic ordering of tuples.

When we provided a tabular illustration of the **simple_books** relation above, we noted that it was just one possible depiction of the relation.  We can, for example, permute the rows of the table, without changing the relation.  If we apply the second definition of tuple above, in which values are likewise not ordered but rather associated with specific attributes, it is valid to permute columns as well.  We would say, then, that the illustration of **simple_books** below is equivalent to our previous illustration:

.. image:: books_permuted.svg
    :alt: A tabular illustration of simple_books, with rows and columns permuted.


Constraints
:::::::::::

*Constraints* are statements about relations which are required to be true at all times.  Some constraints are implicit in the definitions above; for example, the attribute values in a tuple are constrained to be members of the associated domain.  The relational model also incorporates two types of explicit constraint: keys and foreign keys.

.. index:: key - relational model, key - relational model; primary, primary key - relational model, key - relational model; candidate, candidate key, key - relational model; unique, unique key

Keys and primary keys
---------------------

In many cases, relations may contain subsets of attributes which uniquely identify tuples.  For example, for our **simple_books** relation, we will assert that the pair of attributes **author** and **title** uniquely identify any book in our relation, or any book we might choose to add to our relation in the future.  On the other hand, neither **author** nor **title** are sufficient on their own to uniquely identify a book - it is possible for two different authors to create books with the same name, and of course, many books may have the same author.  We state that the set {**author**, **title**} is a *key* for the **simple_books** relation.

Keys play an important part in relational theory, as we will see.  One implication that we will explore further in a later chapter is that no two tuples in our **simple_books** relation (now or ever) can share the exact same **author** and **title** values.  In fact, the assertion that no two tuples can share the same **author** and **title** in return implies that **author** and **title** together uniquely identify any book.  The assertions are equivalent.

It is important to emphasize that the key property is a fact we are stating about the world, not a transitory property of the data in a relation.  For example, our current **simple_books** illustration shows no duplicate values for **year**.  For **year** to be a key, though, requires that **year** never contain duplicates *for any collection of books* we might store in the **simple_books** relation.  Since many books are published every year, we should expect to accumulate duplicate **year** values if we add books to the relation.

Relations may have more than one key.  A common example is that of a table of employees for a company.  In many countries, workers must have a government issued identification (ID) number.  These numbers can be used to uniquely identify an employee.  However, these numbers are often considered sensitive employee data, which should only be shared with certain trusted individuals in the company.  In these cases, companies will generate an internal employee ID number, which is completely independent of the government issued ID.  The company's database will contain both of these unique identifiers.

The keys of a relation are also known as *candidate keys*.  One candidate key is chosen as the *primary key* for the relation.  The remaining keys are sometimes called *unique keys*.

In the relational model, all keys are constrained to be unique.  If a set of tuples contains duplicate values for some key according to some relation schema (e.g., the same **author** and **title** per the **simple_books** schema), we do not consider that a valid relation of the schema.

.. index:: key - relational model; foreign, foreign key - relational model

Foreign keys
------------

Relational databases do not explicitly store connections between related records.  Instead, we must store values in one relation which we can use to "look up" related values in another relation.  In a properly designed relational database, we will nearly always store values from the primary key of the related relation.  The attribute or group of attributes storing the key from the other relation is called a *foreign key*.

Consider the relation **simple_authors** represented below:

.. image:: authors.svg
    :alt: A tabular illustration of the relation simple_authors, which has attributes for name, birth date, and death date.

Our primary key for this relation is the **name** attribute.  Names are generally not a very good choice for keys, as people often share a name with other people, but this is just a simple illustration and not intended to be an example of good database design.

Because every **author** value in **simple_books** matches some **name** value in **simple_authors**, we can connect each book to information about its author.  To assert that it should always be true that any tuple in **simple_books** matches a tuple in **simple_authors**, we declare the **author** attribute of **simple_books** to be a foreign key *referencing* the **name** attribute of **simple_authors**.  This foreign key constraint applies not only to the current relations, but to any future states of **simple_books** and **simple_authors**.  Foreign keys are also known as *referential integrity* constraints.

Note that the foreign key is a constraint on both relations; certain changes in either relation could result in a constraint violation.  The constraint is not symmetric, however; we can have authors listed in **simple_authors** for whom no books are listed in **simple_books**.

.. index:: database; consistency, consistency, inconsistent

Consistency
-----------

A database in which constraints are violated is considered *inconsistent*.  A relational database system is expected to enforce consistency and prevent any data modification operations which would violate constraints.  Consistency helps ensure that we get good answers from our queries, or at least helps us avoid certain common problems.  For example, guaranteeing unique ID values in an employee relation prevents potential issues from confusing two employees, such as issuing two paychecks to the same person (and none to another person).  Foreign key constraints can prevent meaningless results when data in one relation refers to non-existent data in another relation.

Modification operations
:::::::::::::::::::::::

The relational model assumes that a relation may be modified with one of three operations: tuples may be added (inserted) into the relation, values within tuples may be modified (updated) without adding or removing the tuple, or tuples may be removed (deleted) from the relation.  The state of the database must be consistent with all constraints after modification, or the operation must be rejected by the database system.  In certain cases (such as the existence of a circular foreign key relationship), it may be necessary to group multiple modifications together with a *transaction*; constraints may be temporarily violated within the context of the transaction, but must be resolved when all operations have been completed, or none of the operations may take effect.

..
  (We discuss transactions as commonly implemented in :numref:`Chapter {number} <transactions-chapter>`.)

Insertion operations can violate primary and unique key constraints on a relation if the tuple being inserted contains values that duplicate another tuple already in the relation.  Insertion operations can also violate foreign key constraints on a relation if a value is provided for a foreign key attribute that does not exist in the referenced table.  For example, each of the tuples below would violate constraints if added to the **simple_books** relation (assuming the primary and foreign keys discussed in the text above):

    (*The House of the Spirits*, Isabel Allende, 1999, history)

    (*A Wizard of Earthsea*, Ursula K. Le Guin, 1968, fantasy)

In the first case, this author and title already exists in the **simple_books** relation.  In the second case, the author is not present in the **simple_authors** relation.

Deletions, on the other hand, can never violate primary or unique key constraints.  A deletion in one relation can violate a foreign key constraint, however, if a foreign key value in another relation references the deleted key being deleted.  For example, we may not delete from **simple_authors** the tuple:

    (Ralph Ellison, 1914-03-01, 1994-04-16)

This author has a book in the **simple_books** table.

Updates can create any of the constraint violations described above.  For example, an update which changes the value of a primary key must not change the value such that it would duplicate another tuple's primary key.  Similarly, if a foreign key value in another relation depends on the primary key value being updated, then the update cannot proceed.  Finally, an update may not change a foreign key value to something which is not in the referenced table.

.. index:: NULL - relational model

NULL
::::

In the **simple_authors** relation shown earlier, two of the entries show no value for the attribute **death**, which is because those two authors are still living.  If we consider the domain of the **death** attribute to be the domain of calendar dates, then there is truly no value we can choose that accurately represents the situation.  Instead, we are using a special placeholder to represent the *absence of information*.  In the relational model, that placeholder is called *NULL*.

The nature of NULL, and in fact, its very presence in the relational model, is controversial.  Some database scholars treat NULL as a special value that is included with every domain.  So we can say that we have put a NULL value in our table for the death attribute for each living author.  However, NULL exhibits special properties that make it problematic as a value, such as the fact that it cannot be compared with other values, including other NULLs - more on this in a bit.  For this reason, other scholars prefer to treat NULL as a special *state* of the attribute; we can say that the **death** attribute for an author is in a null state when the author is living.  Finally, some scholars reject NULL entirely as fundamentally incompatible with relational theory.

The problem NULL was created to solve is the problem of missing information.  Information may be unknown for many reasons: it may be that nobody knows the true value, or it may have been simply overlooked when entering data into the database, or any number of other causes.  Data may be irrelevant or inapplicable, as in the example of the **death** date for living authors.  Researchers have identified many different meanings that can be ascribed to NULL, which has led some scholars to propose additional placeholders instead of just one (although some of those proposals were intended to highlight the problems with NULL, rather than improve the model).  The problem is, the definition of a tuple requires there to be *something* associated with every attribute defined in the relation schema; even if nothing from the domain is appropriate, the tuple cannot simply be incomplete.

While there are alternatives to the use of NULL, the alternatives are problematic in their own ways.  Most database systems based on the relational model include support for NULL.  For these reasons, NULL is an important part of our discussion of the relational model.

.. index:: three-value logic - relational model

Three-valued logic
------------------

Many operations on relations make use of Boolean logic and the usual operations on logical expressions.  There are only two values in Boolean logic: *true* and *false*.  The basic Boolean operators are easy to understand and apply.  The NOT operation simply inverts the Boolean value: "NOT true" equals false, and "NOT false" equals true [#]_.  Given two Boolean values, *a* and *b*, the expression "a AND b" yields true if and only if *a* is true and *b* is true.  On the other hand, the expression "a OR b" is true if *a* is true or *b* is true, and is false only if both *a* and *b* are false.

However, when NULL is used in most expressions, it is unknown whether the answer is true or false.  For example, the expression "2 = x", where *x* is assigned NULL (or is in the null state, if you prefer) cannot be determined to be true or false.  The problem is that NULL is not a distinct value of its own, but represents the absence of information altogether.  Thus, we *do not know* if *x* equals 2 or something else.  Even the expression "x = y", where both *x* and *y* are NULL cannot be determined to be true or false!

The solution is to enhance Boolean logic with a third value, *unknown*, giving a *three-valued logic*.  With so many combinations, it is easiest to summarize the results of AND, OR, and NOT operations with the following tables:

======== ======== =========== ==========
*a*      *b*      *a* AND *b* *a* OR *b*
======== ======== =========== ==========
true     true     true        true
true     false    false       true
true     unknown  unknown     true
false    true     false       true
false    false    false       false
false    unknown  false       unknown
unknown  true     unknown     true
unknown  false    false       unknown
unknown  unknown  unknown     unknown
======== ======== =========== ==========

======== =======
*a*      NOT *a*
======== =======
true     false
false    true
unknown  unknown
======== =======

It is not necessary to memorize these tables, if some common sense is applied.  Consider the expression "a OR b", and let *b* be unknown.  To determine the result of "a OR b", we simply need to consider whether or not we have enough information without knowing the value of *b*.  In fact, if *a* is true, it does not matter if *b* is true or false - the result "a OR b" is true.  Thus "true OR unknown" equals true.  On the other hand, if *a* is false, then it really does matter whether *b* is true or false; since we don't know, the result "a OR b" is unknown.  A similar thought process can be applied to the other operations.

Constraints and NULL
--------------------

With NULL in our model, we must make some small adjustments to our rules regarding constraints.  First, we must further constrain all primary key attributes to never be NULL.  Remember that a primary key should be an identifier for tuples in a relation, and every tuple must have a unique primary key value.  However, if NULL is present in any primary key attribute for some tuple, it is impossible to search for and find the tuple - any attempt to compare the primary key with a lookup value gives an unknown result.  We likewise cannot properly enforce uniqueness, because we cannot compare a tuple with NULL in the primary key with other tuples to determine if they are distinct from one another.

Second, we modify the rule for a foreign key.  The new rule is that a foreign key may be NULL, otherwise it must match a value in the referenced table.  Allowing NULL in a foreign key may seem surprising, but considering our example relations, how might we handle a book for whom the author is unknown (anonymous)?  If NULL is not allowed for the author, then we cannot add the book to **simple_books** without some matching record in the **simple_authors** table.  However, what is the meaning of a record in the **simple_authors** table for an unknown author?  (Note also we cannot have a NULL name for the author in **simple_authors** due to the primary key.)  While there are multiple ways to approach this problem, allowing NULL for the author is one possible solution.


Self-check exercises
::::::::::::::::::::

This section has some questions you can use to check your understanding of the relational model of the database.

.. dragndrop:: relational_model_self_test_definitions
    :match_1: set|||A collection of distinct values
    :match_2: relation|||A set of tuples from the same domain
    :match_3: attribute|||A named property of a tuple
    :match_4: domain|||A set of values which attribute values belong to
    :match_5: relation schema|||A definition of the attributes and domains of a relation

    Drag the term to its matching definition.

.. mchoice:: relational_model_self_test_tuples

    What is the definition of *tuple* as used in the relational model?

    -   An ordered collection of values; each position in the tuple is associated with a domain.

        - This is one definition.

    -   A set of values associated with a named attribute; each attribute is associated with a domain.

        - This is one definition.

    -   Either or both of the above definitions may be used, depending on the context.

        + Correct.

.. mchoice:: relational_model_self_test_relation_properties

    Which of these best describes a relation?

    -   A collection of tuples in order by primary key value.  Each tuple must be unique and have the same number and types of attributes.

        - Relations have no intrinsic ordering.

    -   A collection of tuples in no particular order.  Each tuple must be unique and have the same number and types of attributes.

        + Correct.

    -   A collection of tuples in no particular order, possibly with duplicates.  Each tuple must have the same number and types of attributes.

        - Tuples in a relation must be distinct, that is, there cannot be duplicate tuples.

    -   A collection of tuples in no particular order.  Each tuple must be unique.  Each tuple has its own attributes, which may differ from tuple to tuple.

        - Tuples in a relation must come from the same domain of tuples; that is, each tuple shares the same definition in terms of attributes and associated domains.

The next four questions concern the two relations pictured below, which map ISO (International Organization for Standardization) country codes to country names and ISO currency codes, and currency codes to the name of the currency.  The primary key for **countries** is **country_code**, and the primary key for **currencies** is **currency_code**.  The **principal_currency_code** column in **countries** is a foreign key referencing **currency_code** in **currencies**.  Obviously this represents a subset of available data, for space reasons.

.. image:: countries.svg
    :alt: A table showing tuples for the countries relation.  The countries listed are Australia (AU), Somalia (SO), Thailand (TH), Mexico (MX), Kiribati (KI), and Denmark (DK).

.. image:: currencies.svg
    :alt: A table showing tuples for the currencies relation.  The currencies listed are the Mexican Peso (MXN), Australian Dollar (AUD, used by Australia and Kiribati), the Danish Krone (DKK), the Thai Baht (THB), and the Somali Shilling (SOS).


.. mchoice:: relational_model_self_test_constraints_1

    What constraint or constraints would be violated if we insert the tuple (DK, Danmark, DKK) into the **countries** relation?

    -   Primary key on the **countries** relation.

        + Correct.

    -   Primary key on the **countries** relation and the foreign key constraint on **principal_currency_code**.

        - DKK is a currency code in the **currencies** relation.

    -   Foreign key constraint on **principal_currency_code**.

        - DKK is a currency code in the **currencies** relation.

    -   No constraints would be violated.

        - Incorrect.

.. mchoice:: relational_model_self_test_constraints_2

    What constraint or constraints would be violated if we delete the tuple (AU, Australia, AUD) from the **countries** relation?

    -   Primary key on the **countries** relation.

        - No, the **country_code** column will still contain unique, non-null entries.

    -   Primary key on the **countries** relation and the foreign key constraint on **principal_currency_code**.

        - No, the **country_code** column will still contain unique, non-null entries, and all **principal_currency_code** values still match values in the **currencies** relation.

    -   Foreign key constraint on **principal_currency_code**.

        - No, all **principal_currency_code** values still match values in the **currencies** relation.

    -   No constraints would be violated.

        + Correct.

.. mchoice:: relational_model_self_test_constraints_3

    What constraint or constraints would be violated if we delete the tuple (THB, Baht) from the **currencies** relation?

    -   Primary key on the **currencies** relation.

        - No, the **currency_code** column will still contain unique, non-null entries.

    -   Primary key on the **currencies** relation and the foreign key constraint on **principal_currency_code**.

        - No, the **currency_code** column will still contain unique, non-null entries.

    -   Foreign key constraint on **principal_currency_code**.

        + Correct.  The entry for Thailand in **countries** will have a **principal_currency_code** that is not matched by anything in the **currencies** relation.

    -   No constraints would be violated.

        - Incorrect.

.. mchoice:: relational_model_self_test_constraints_4

    What constraint or constraints would be violated if we insert the tuple (ARS, Argentine Peso) into the **currencies** relation?

    -   Primary key on the **currencies** relation.

        - No, ARS is distinct from the currency codes previously in the table.

    -   Primary key on the **currencies** relation and the foreign key constraint on **principal_currency_code**.

        - No, ARS is distinct from the currency codes previously in the table, and the foreign key constrains **principal_currency_code** values to be in the **currency_code** column of **currencies**, but not vice-versa.

    -   Foreign key constraint on **principal_currency_code**.

        - No, the foreign key constrains **principal_currency_code** values to be in the **currency_code** column of **currencies**, but not vice-versa.

    -   No constraints would be violated.

        + Correct.


.. mchoice:: relational_model_self_test_constraints_5

    What constraint or constraints would be violated if we insert the tuple (AQ, Antarctica, NULL) into the **countries** relation?  (Yes, Antarctica is technically not a country, but they do have an ISO country code.)

    -   Primary key on the **countries** relation.

        - No, AQ is distinct from the country codes previously in the table.

    -   Primary key on the **countries** relation and the foreign key constraint on **principal_currency_code**.

        - No, AQ is distinct from the country codes previously in the table.  The **principal_currency_code** value is NULL, which is allowed under the definition of a foreign key.

    -   Foreign key constraint on **principal_currency_code**.

        - No, the **principal_currency_code** value is NULL, which is allowed under the definition of a foreign key.

    -   No constraints would be violated.

        + Correct.

.. mchoice:: relational_model_self_test_constraints_6

    What constraint or constraints would be violated if we modify the tuple (AUD, Australian Dollar) in **currencies** to be (DKK, Australian Dollar)?

    -   Primary key on the **currencies** relation.

        - True, but might another constraint be violated?

    -   Primary key on the **currencies** relation and the foreign key constraint on **principal_currency_code**.

        + Correct.  DKK duplicates an existing currency code in **currencies**, and the change would also remove AUD from the list of currencies, which is referenced by two rows in **countries**.

    -   Foreign key constraint on **principal_currency_code**.

        - True, but might another constraint be violated?

    -   No constraints would be violated.

        - Incorrect.

.. dragndrop:: relational_model_self_test_three_value_logic_2
    :match_1: true AND unknown|||unknown
    :match_2: true OR unknown|||true
    :match_3: false AND true|||false

    Drag the expression to the outcome of its evaluation.

.. dragndrop:: relational_model_self_test_three_value_logic_1
    :match_1: NOT false|||true
    :match_2: unknown AND false|||false
    :match_3: false OR unknown|||unknown

    Drag the expression to the outcome of its evaluation.


|chapter-end|

----

**Notes**

.. [#] There are many notations for Boolean logic operators.  For simplicity, we will simply use NOT, AND, and OR instead of more compact notation.

|license-notice|



## Chapter: relational-algebra.rst

.. _relational-algebra-chapter:

==================
Relational algebra
==================

.. index:: relational algebra; relational calculus

In the last chapter, we introduced the relational model of the database, and defined the fundamental mathematical object in the model, the *relation*.  In this chapter, we discuss *relational algebra*, which is the set of algebraic operations that can be performed on relations.  Relational algebra can be viewed as one mechanism for expressing queries on data stored in relations, and an understanding of relational algebra is important in understanding how relational databases represent and optimize queries.  We will cover only basic relational algebra, excluding later extensions such as those for group and aggregate operations and those for outer joins.

A related topic, which we do not cover in this book, is *relational calculus*.  Relational calculus provides another mathematical expression of queries on relations, and is equivalent in expressiveness to relational algebra.

Unary operations
::::::::::::::::

.. index:: selection, projection, renaming, relational algebra operations; selection, relational algebra operations; projection, relational algebra operations; renaming

The unary operations in relational algebra act on one relation and result in another relation.  The unary operations are *selection*, *projection*, and *renaming*, and their associated operators are typically written as the Greek letters which match the starting letters of the operation:

- :math:`\sigma` (sigma): selection
- :math:`\pi` (pi): projection
- :math:`\rho` (rho): renaming

We will explore each of these unary operators in application to the relation **books** shown below:

.. table:: **books**
    :class: lined-table

    ======= ========= ============================ ====
    book_id author_id title                        year
    ======= ========= ============================ ====
    1       3         *The House of the Spirits*   1982
    2       1         *Invisible Man*              1952
    3       6         *The Hobbit*                 1937
    4       2         *Unaccustomed Earth*         2008
    5       6         *The Fellowship of the Ring* 1954
    6       4         *House Made of Dawn*         1968
    7       5         *A Wizard of Earthsea*       1968
    ======= ========= ============================ ====

The **books** relation has primary key **book_id**, while **author_id** is a foreign key to another table we will use later in this chapter.

Selection
---------

Selection applies a Boolean condition to the tuples in a relation.  The result of a selection operation is a relation containing exactly those tuples for which the selection condition is true.  For example, if we are interested in books published after 1960, we can write the selection operation to retrieve just those books as:

.. math::

    \sigma_{\text{year} > 1960}(\text{books})

The operator is written with the Boolean condition as a subscript, and then the operand (the input relation) is given in parentheses.  Note that the Boolean condition refers to an attribute of the **books** relation, comparing it to a constant value.  The result of this operation is a relation with the same schema as **books**, but with no name:

.. table::
    :class: lined-table

    ======= ========= ============================ ====
    book_id author_id title                        year
    ======= ========= ============================ ====
    1       3         *The House of the Spirits*   1982
    4       2         *Unaccustomed Earth*         2008
    6       4         *House Made of Dawn*         1968
    7       5         *A Wizard of Earthsea*       1968
    ======= ========= ============================ ====

Simple Boolean expressions in the relational algebra usually involve comparisons of an attribute with a constant, using any comparison operator.  More complex Boolean expressions can be constructed from simple expressions using **AND**, **OR**, and **NOT**.  For instance, if we are interested in books published after 1960 as well as books by the author with **author_id** equal to 6, we could write:

.. math::

    \sigma_{\text{year} > 1960 \text{ OR } \text{author_id} = 6}(\text{books})

Selection can result in a relation that has all of the tuples from the original (a relation equivalent to the original), some of the tuples from the original, or no tuples at all (an empty set).  In the case of an empty relation, we still consider the relation to have the same schema as the original relation.

Since the result of a selection is a relation, we can apply another selection to the result.  For example, we could find the books published after 1950, and then select from that result the books with **author_id** equal to 6:

.. math::

    \sigma_{\text{author_id} = 6}(\sigma_{\text{year} > 1950}(\text{books}))

This would give us a result with one tuple:

.. table::
    :class: lined-table

    ======= ========= ============================ ====
    book_id author_id title                        year
    ======= ========= ============================ ====
    5       6         *The Fellowship of the Ring* 1954
    ======= ========= ============================ ====

This composition of selection operations is equivalent to a single selection operation using a *conjunction* (AND) of the selection conditions:

.. math::

    \sigma_{\text{author_id} = 6 \text{ AND } \text{year} > 1950}(\text{books})

Projection
----------

The projection operation creates a new relation which has a subset of the attributes of the input relation.  We could use projection, for example, to get a set of tuples expressing just the title and publication year of our books.  We write the projection operator with the list of attribute names in the subscript, followed by the operand in parentheses:

.. math::

    \pi_{\text{title, year}}(\text{books})

This result contains a tuple for each tuple in **books**, but the tuples in the result only have the attributes specified by the projection operation, thus the result relation has a different schema from the original:

.. table::
    :class: lined-table

    ============================ ====
    title                        year
    ============================ ====
    *The House of the Spirits*   1982
    *Invisible Man*              1952
    *The Hobbit*                 1937
    *Unaccustomed Earth*         2008
    *The Fellowship of the Ring* 1954
    *House Made of Dawn*         1968
    *A Wizard of Earthsea*       1968
    ============================ ====

At first glance, it might seem the result of a projection will always have the same number of tuples as the input relation, but this is not the case.  Consider what happens if we project **books** onto the single attribute **year**.  There are two tuples in **books** with the same **year** value of 1968.  Since relations cannot contain duplicates, the result of our projection operation can contain only one tuple with **year** equal to 1968.  Thus, the result has *fewer* tuples than the input relation:

.. table:: :math:`\pi_{\text{year}}(\text{books})`
    :class: lined-table

    +------+
    | year |
    +======+
    | 1982 |
    +------+
    | 1952 |
    +------+
    | 1937 |
    +------+
    | 2008 |
    +------+
    | 1954 |
    +------+
    | 1968 |
    +------+

Since the result of projection is a relation, we can apply selection to the result:

.. math::

    \sigma_{\text{year}=1968}(\pi_{\text{title, year}}(\text{books}))

Note the order of operations here: first, we supply **books** as an input to the projection operation; second, the result of the projection is given as the input to the selection operation.

Similarly, since the result of a selection is a relation, we can apply projection after selection.  The above expression is equivalent to:

.. math::

    \pi_{\text{title, year}}(\sigma_{\text{year}=1968}(\text{books}))

The result in both cases is:

.. table::
    :class: lined-table

    ======================== ====
    title                    year
    ======================== ====
    *House Made of Dawn*     1968
    *A Wizard of Earthsea*   1968
    ======================== ====

It is important to note, however, that you cannot always change the order of projection and selection for an equivalent result.  Consider the following expressions:

.. math::

    \pi_{\text{title}}(\sigma_{\text{year}=1968}(\text{books}))

.. math::

    \sigma_{\text{year}=1968}(\pi_{\text{title}}(\text{books}))

In the first expression, we select the books which were published in 1968, and then project the resulting tuples onto the **title** attribute.  This result is:

.. table::
    :class: lined-table

    +-------------------------+
    | title                   |
    +=========================+
    | *House Made of Dawn*    |
    +-------------------------+
    | *A Wizard of Earthsea*  |
    +-------------------------+

However, the second expression is not a correct expression.  The projection occurs first, yielding a relation with just one attribute named **title**.  The following selection is then incorrect, because it makes reference to an attribute, **year**, which does not exist in the input relation.

Projection can also be applied to the result of another projection; however, the result is equivalent to just performing the second projection.  Compare:

.. math::

    \pi_{\text{title}}(\pi_{\text{title, year}}(\text{books}))

.. math::

    \pi_{\text{title}}(\text{books})

Note that we cannot change the order of the two projection operations in the first expression above, as the expression would then be incorrect.

Renaming
--------

The final unary operation allows for relations and their attributes to be renamed.  As we will see, this operation is primarily useful in eliminating name conflicts in certain binary operations - that is, in expressions involving two relations in which the name of some attribute is the same in both relations.  The general form of the renaming operator lets us provide new names for the relation and all of its attributes:

.. math::

    \rho_{\text{mybooks(b_id, a_id, title, year)}}(\text{books})

This results in a relation with the name **mybooks** with attributes **b_id**, **a_id**, **title**, and **year**.  The tuples of the new relation have the same values as the tuples of the old relation, but the values are associated with the new attribute names.

As in this example, it is not necessary to alter the name of every attribute (we left unchanged the attribute names **title** and **year**), but some name must be provided for every attribute.  A non-standard alternative notation allows us to rename only the attributes we want to change:

.. math::

    \rho_{\text{mybooks(book_id} \rightarrow \text{b_id, author_id} \rightarrow \text{a_id)}}(\text{books})

We can optionally leave out either the relation name or the list of attributes.  For example, the following expression is correct and results in a relation named **books** with attributes **book_id**, **author_id**, **title**, and **publication_year**:

.. math::

    \rho_{\text{(year} \rightarrow \text{publication_year)}}(\text{books})




Cross products and joins
::::::::::::::::::::::::

We now turn our attention to operations which extend tuples in one relation with tuples from another relation.  For this section, we will be using **books** and a second relation, **authors**:

.. table:: **authors**
    :class: lined-table

    ========== ================== =========== ============
    author_id  name               birth       death
    ========== ================== =========== ============
    1          Ralph Ellison      1914-03-01  1994-04-16
    2          Jhumpa Lahiri      1967-07-11
    3          Isabel Allende     1942-08-02
    4          N\. Scott Momaday  1934-02-27
    5          Ursula K. Le Guin  1929-10-21  2018-01-22
    6          J.R.R. Tolkien     1892-01-03  1973-09-02
    7          Kazuo Ishiguro     1954-11-08
    ========== ================== =========== ============

The **authors** relation has a primary key of **author_id**.  The **books** relation is related to **authors** via a foreign key on **author_id**.

.. index:: cross product - relational algebra, relational algebra operations; cross product

Cross product
-------------

The cross product (or *Cartesian product*) of two relations **A** and **B** is a new relation containing all tuples that can be created by concatenating some tuple from **B** onto some tuple from **A** [#]_.  Here we are using the definition of tuple as an ordered list of values.  The attributes of the new relation are normally the attributes of **A** and **B** concatenated.  However, if there is a name collision, e.g., if both **A** and **B** have some attribute **x**, we will disambiguate the attributes in the new relation by prepending the relation names, that is, the cross product will have attributes **A.x** and **B.x**; we can avoid having to do this if we first apply renaming to one relation or the other.

The cross product operator is denoted :math:`\times`, and is written between its two operands. To start, consider two rather abstract relations **S** and **T**:

.. table:: **S**
    :class: lined-table

    == ===
    u  v
    == ===
    1  one
    2  two
    == ===

.. table:: **T**
    :class: lined-table

    ======= ======== ======
    x       y        z
    ======= ======== ======
    green   3.1415   apple
    blue    2.71828  pear
    yellow  1.618    mango
    ======= ======== ======

We write the cross product of **S** and **T** as:

.. math::

    \text{S} \times \text{T}

which gives us the relation containing every pairing of a tuple from **S** with every tuple from **T**:

.. table::
    :class: lined-table

    == === ======= ======== =======
    u  v   x       y        z
    == === ======= ======== =======
    1  one green   3.1415   apple
    1  one blue    2.71828  pear
    1  one yellow  1.618    mango
    2  two green   3.1415   apple
    2  two blue    2.71828  pear
    2  two yellow  1.618    mango
    == === ======= ======== =======

From the definition, it is trivial to determine that the size of the cross product is the product of the sizes of the operands.

.. index:: join - relational algebra, relational algebra operations; join

Join
----

The cross product is a fundamental operation in relational algebra, but not a generally useful one when we consider actual data.  Consider the cross product of **books** and **authors**:

.. math::

    \text{books} \times \text{authors}

The full set of tuples in this relation is large (the number of books multiplied by the number of authors), so we only show a subset below:

.. table::
    :class: lined-table

    ======= =============== ============================ ===== ================== ================== =========== ============
    book_id books.author_id title                        year  authors.author_id  name               birth       death
    ======= =============== ============================ ===== ================== ================== =========== ============
    1       3               *The House of the Spirits*   1982  1                  Ralph Ellison      1914-03-01  1994-04-16
    1       3               *The House of the Spirits*   1982  2                  Jhumpa Lahiri      1967-07-11
    1       3               *The House of the Spirits*   1982  3                  Isabel Allende     1942-08-02
    2       1               *Invisible Man*              1952  1                  Ralph Ellison      1914-03-01  1994-04-16
    2       1               *Invisible Man*              1952  2                  Jhumpa Lahiri      1967-07-11
    2       1               *Invisible Man*              1952  3                  Isabel Allende     1942-08-02
    ======= =============== ============================ ===== ================== ================== =========== ============

The author of *The House of the Spirits* is Isabel Allende.  What meaning, then, can we make of a tuple that pairs *The House of the Spirits* with the author Ralph Ellison (the author of *Invisible Man*)?

We are typically interested in pairing only certain tuples of a relation with certain tuples of another.  In the above example, we are interested in tuples where the **author_id** attribute from **books** agrees with the **author_id** attribute from **authors**.  This relationship is indicated not only by the names we have used for attributes, but also by the foreign key constraint on **books** and **authors**.  To retain only the tuples with matching **author_id** values, we can apply a selection operation to the result of our cross product:

.. math::

    \sigma_{\text{books.author_id}=\text{authors.author_id}}(\text{books} \times \text{authors})

This yields a useful result:

.. table::
    :class: lined-table

    ======= =============== ============================ ===== ================== ================== =========== ============
    book_id books.author_id title                        year  authors.author_id  name               birth       death
    ======= =============== ============================ ===== ================== ================== =========== ============
    1       3               *The House of the Spirits*   1982  3                  Isabel Allende     1942-08-02
    2       1               *Invisible Man*              1952  1                  Ralph Ellison      1914-03-01  1994-04-16
    3       6               *The Hobbit*                 1937  6                  J.R.R. Tolkien     1892-01-03  1973-09-02
    4       2               *Unaccustomed Earth*         2008  2                  Jhumpa Lahiri      1967-07-11
    5       6               *The Fellowship of the Ring* 1954  6                  J.R.R. Tolkien     1892-01-03  1973-09-02
    6       4               *House Made of Dawn*         1968  4                  N\. Scott Momaday  1934-02-27
    7       5               *A Wizard of Earthsea*       1968  5                  Ursula K. Le Guin  1929-10-21  2018-01-22
    ======= =============== ============================ ===== ================== ================== =========== ============

Since this pattern of applying a selection after a cross product is so common, we have an operator that combines the two into an operation known as a *join* [#]_.  Using the join operator, the above expression becomes:

.. math::

    \text{books} \Join_{\text{books.author_id}=\text{authors.author_id}} \text{authors}

or, you can instead format the expression as:

.. math::

    \text{books} \underset{\text{books.author_id}=\text{authors.author_id}}\Join \text{authors}

Note that one tuple from **authors** does not contribute to the join.  This tuple's **author_id** matches none of the tuples in **books**, and thus no combined tuple using it can appear in the join result.  We call this tuple a *dangling tuple*.  Dangling tuples may be an indication of a problem in the data; in this example, it may suggest that we are missing information about books by one author.

.. index:: equijoin, theta join

Theta-join and equijoin
-----------------------

While an equality condition is typically used in joins, more generally any condition of the following form can be used:

.. math::

    \text{A.x } \Theta \text{ B.y}

where **A.x** is an attribute from one relation, **B.y** is an attribute from the other relation, and :math:`\Theta` is a comparison operator (such as =, <, etc.).  A condition of this form is known as a *theta condition*, and a join using such a condition or a conjunction (AND) of such conditions is known as a *theta-join*.

A theta-join using only equality comparisons (as in our example above) is further known as an *equijoin*.

This terminology is not especially important in understanding the algebra, but is something you may encounter if you intend a deeper study of  relational algebra.

.. index:: relational algebra operations; natural join, natural join

Natural join
------------

When we join **books** with **authors** we run into the issue that both relations contain an attribute named **author_id**.  Since a relation cannot have more than one attribute with the same name, joining (or taking a cross product of) these two relations requires us to rename the attributes in some fashion. This can be done either by an explicit renaming operation prior to joining or by prepending the original relation name (as we did in our example).  Because our join condition was equality on the **author_id** attributes, both the **books.author_id** and **authors.author_id** in the resulting relation always agree.  This unnecessary redundancy can be removed using projection and renaming.

In this special situation in which we wish to join specifically by equating the attributes with the same names in both relations - subsequently removing the "duplicate" attributes - we can instead do a *natural join*.  We can indicate a natural join using the join operator with no conditions [#]_:

.. math::

    \text{books} \Join \text{authors}

which yields the simplified relation:

.. table::
    :class: lined-table

    ======= ========= ============================ ===== ================== =========== ============
    book_id author_id title                        year  name               birth       death
    ======= ========= ============================ ===== ================== =========== ============
    1       3         *The House of the Spirits*   1982  Isabel Allende     1942-08-02
    2       1         *Invisible Man*              1952  Ralph Ellison      1914-03-01  1994-04-16
    3       6         *The Hobbit*                 1937  J.R.R. Tolkien     1892-01-03  1973-09-02
    4       2         *Unaccustomed Earth*         2008  Jhumpa Lahiri      1967-07-11
    5       6         *The Fellowship of the Ring* 1954  J.R.R. Tolkien     1892-01-03  1973-09-02
    6       4         *House Made of Dawn*         1968  N\. Scott Momaday  1934-02-27
    7       5         *A Wizard of Earthsea*       1968  Ursula K. Le Guin  1929-10-21  2018-01-22
    ======= ========= ============================ ===== ================== =========== ============

.. index:: set operation - relational algebra, set operation - relational algebra; union, set operation - relational algebra; intersection, set operation - relational algebra; difference, relational algebra operations; union, relational algebra operations; intersection, relational algebra operations; set difference

Set operations
::::::::::::::

Unsurprisingly, given that relations are sets, relational algebra includes the usual set operations - *union*, *intersection*, and *set difference* - with some restrictions.  These binary operations are denoted by:

- :math:`\cup`: union
- :math:`\cap`: intersection
- :math:`-`: set difference

Given two relations **A** and **B**, the union :math:`\text{A} \cup \text{B}` is the set of all tuples that exist in **A**, or exist in **B**, or both.  The intersection :math:`\text{A} \cap \text{B}` is the set of all tuples that exist in both **A** and **B**.  Finally, the set difference :math:`\text{A} - \text{B}` is the set of all tuples that exist in **A** but do not exist in **B**.

For example, let **A** and **B** be the relations below:

.. table:: **A**
    :class: lined-table

    ======= ===
    x       y
    ======= ===
    apple   42
    orange  19
    cherry  77
    ======= ===

.. table:: **B**
    :class: lined-table

    ======== ===
    x        y
    ======== ===
    banana   8
    apple    42
    coconut  17
    ======== ===

Then we have:

.. table:: :math:`\text{A} \cup \text{B}`
    :class: lined-table

    ======== ===
    x        y
    ======== ===
    apple    42
    orange   19
    cherry   77
    banana   8
    coconut  17
    ======== ===

.. table:: :math:`\text{A} \cap \text{B}`
    :class: lined-table

    ======== ===
    x        y
    ======== ===
    apple    42
    ======== ===

.. table:: :math:`\text{A} - \text{B}`
    :class: lined-table

    ======== ===
    x        y
    ======== ===
    orange   19
    cherry   77
    ======== ===

.. table:: :math:`\text{B} - \text{A}`
    :class: lined-table

    ======== ===
    x        y
    ======== ===
    banana   8
    coconut  17
    ======== ===

Note that union and intersection are commutative, but set difference is not.

The important restriction on set operations in relational algebra is that the relations must be compatible in terms of their schemas.  The meaning of "compatible" varies, but for our purposes, assume we view the tuples in a relation as ordered lists, where each position in the list is associated with a particular attribute and type domain.  Then, if we have two relations, we require that, for a given position in the tuples in either relation, the attribute and type domain are the same.  For **A** and **B** shown above, we might assert that the first position corresponds to attribute **x** and contains character strings, while the second position (**y**) contains integers.

A looser requirement allows attribute names (but not type domains) to differ between relations.  This requirement aligns less closely with the second definition of tuple given in the previous chapter, but it eliminates the occasional need for renaming operations prior to applying set operations. If the attribute names do not match in the two relations, we adopt the attribute names from the left-hand operand for the result relation.

While intersection is a useful operation, it is not strictly needed for the algebra, as the same result can be obtained using set difference:

.. math::

    \text{A} \cap \text{B} \equiv \text{A} - (\text{A} - \text{B})

.. index:: division, relational algebra operations; division

Division
::::::::

The operations described above are sufficient for most query needs.  However, one other binary operation, *division*, is typically included in the basic relational algebra.  To divide a relation **P** by another relation **R**, we write:

.. math::

    \text{P} \div \text{R}

Division is the most difficult operation to describe; in a very loose sense it acts as a kind of inverse to a cross product.  That is, if **P**, **Q**, and **R** are relations and

.. math::

    \text{P} = \text{Q} \times \text{R}

then it is true that

.. math::

    \text{P} \div \text{R} = \text{Q}

However, the reverse is not necessarily true.  Rather, let **P** be some relation, with attributes **x** and **y** [#]_.  We require that **R** has attribute **y**.  Then :math:`\text{P} \div \text{R}` will contain the values of **x** which are paired (in **P**) with *every* value of **y** listed in **R**.

We will start with an abstract example.  Let **P** be the relation pictured below:

.. table::  **P**
    :class: lined-table

    === =========
    x   y
    === =========
    1   blue
    1   green
    1   yellow
    2   blue
    2   yellow
    3   blue
    3   green
    3   yellow
    3   red
    === =========

Let **R** be

.. table:: **R**
    :class: lined-table

    +---------+
    | y       |
    +=========+
    | blue    |
    +---------+
    | green   |
    +---------+
    | yellow  |
    +---------+

Then :math:`\text{Q} = \text{P} \div \text{R}` is

.. table:: **Q**
    :class: lined-table

    +----+
    | x  |
    +====+
    | 1  |
    +----+
    | 3  |
    +----+

because only the values 1 and 3 are paired with blue, green, and yellow in **P**.  The value 2 is not paired with green, so it does not appear in the quotient.  The value 3 is also paired with red, but red is not in **R** and thus does not affect the result.

For a more tangible example, consider the following relation, named **authors_awards**:

.. table:: **authors_awards**
    :class: lined-table

    ================== ===========================
    author             award
    ================== ===========================
    Ralph Ellison      National Book Award
    Jhumpa Lahiri	     Pulitzer Prize for Fiction
    N\. Scott Momaday	 Pulitzer Prize for Fiction
    Ursula K. Le Guin	 Hugo Award
    Ursula K. Le Guin	 Nebula Award
    C\. J\. Cherryh	   Hugo Award
    Kazuo Ishiguro	   Booker Prize
    Kazuo Ishiguro	   Nobel Prize in Literature
    Michael Chabon	   Hugo Award
    Michael Chabon	   Nebula Award
    Michael Chabon	   Pulitzer Prize for Fiction
    ================== ===========================

and the relation **science_fiction_awards**:

.. table:: **science_fiction_awards**
    :class: lined-table

    +--------------+
    | award        |
    +==============+
    | Hugo Award   |
    +--------------+
    | Nebula Award |
    +--------------+

We might ask the question, "Which authors have received all of the science fiction book awards?"  The answer is given by

.. table:: :math:`\text{authors_awards} \div \text{science_fiction_awards}`
    :class: lined-table

    +-------------------+
    | author            |
    +===================+
    | Ursula K. Le Guin |
    +-------------------+
    | Michael Chabon    |
    +-------------------+

Like the join and set intersection operations, division can be accomplished using other relational algebra operations; however, the construction is fairly complex.  If we have relation **P** with attributes **x** and **y**, and relation **R** with attribute **y**, then

.. math::

    \text{P} \div \text{R} \equiv \pi_{\text{x}}(\text{P}) - \pi_{\text{x}}((\pi_{\text{x}}(\text{P}) \times \text{R}) - \text{P})

By carefully applying the right-hand side expression above to one of our examples, you can verify that the desired result is obtained, but the basic intuition is that we must first find the values of **x** in **P** which are *not* paired (in **P**) with one or more **y** values listed in **R**, and then subtract that list of **x** values from the list of all **x** values in **P**:

1. Create a relation containing every **x** value in **P** paired with every **y** value in **R**:

.. math::

    \pi_{\text{x}}(\text{P}) \times \text{R}

2. Subtract (using set difference) **P** from the cross product result above.  These are the possible pairings of **x** (in **P**) and **y** (in **R**) that do *not* exist in **P**:

.. math::

    (\pi_{\text{x}}(\text{P}) \times \text{R}) - \text{P}

3. Project the last result onto attribute **x**. These are the **x** values that are not paired with some value from **R**:

.. math::

    \pi_{\text{x}}((\pi_{\text{x}}(\text{P}) \times \text{R}) - \text{P})

4. Subtract the last result from the set of all **x** values in **P** for the final solution:

.. math::

    \pi_{\text{x}}(\text{P}) - \pi_{\text{x}}((\pi_{\text{x}}(\text{P}) \times \text{R}) - \text{P})


Queries
:::::::

As we have seen, the operations of the relational algebra act on relations and result in relations, and thus we can apply relational operations sequentially to obtain a final desired result.  With the operations we have discussed, we can express a very wide array of *queries* (questions to be answered by the data).  We have seen examples of simple queries throughout this chapter, mostly involving one or two basic operations.

Even simple questions, however, can require the application of multiple operations.  Consider the question, "What books by J.R.R. Tolkien were published after 1950?".  This is similar to a question we asked earlier, using the author ID value rather than the author's name.  With only the author's name, we have to do a bit more work.

There are many ways to get to our desired result.  One possible approach might begin with the conditions presented: the author is J.R.R. Tolkien, and the publication year is greater than 1950.  Author names are in the **authors** relation, while publication years are in the **books** relation.  So we might guess we need two selection operations, one on each relation:

.. math::

    \sigma_{\text{name} = \text{J.R.R. Tolkien}}(\text{authors})

and

.. math::

    \sigma_{\text{year} > 1950}(\text{books})

This gives us two relations which are related by the **author_id** attribute present in both.  So a natural join might be our next step:

.. math::

    \sigma_{\text{name} = \text{J.R.R. Tolkien}}(\text{authors}) \Join \sigma_{\text{year} > 1950}(\text{books})

Finally, we are only interested in the book titles (or possibly titles and publication years), so we finish with a projection operation:

.. math::

    \pi_{\text{title}}(\sigma_{\text{name} = \text{J.R.R. Tolkien}}(\text{authors}) \Join \sigma_{\text{year} > 1950}(\text{books}))

This is only one of many possible expressions that yield identical results.  Here are some equivalent expressions:

..
    In chapter XXX, we will look at some of the algebraic identities that can be applied to transform an expression into a different but equivalent expression, and explore how these identities can be used by database software to speed up the execution of queries.  For now, we provide the following equivalent expressions without discussion:

.. math::

    \pi_{\text{title}}(\sigma_{\text{name} = \text{J.R.R. Tolkien AND year} > 1950}(\text{authors} \Join \text{books}))

.. math::

    \pi_{\text{title}}(\sigma_{\text{name} = \text{J.R.R. Tolkien}}(\sigma_{\text{year} > 1950}(\text{books}) \Join \text{authors}))

.. math::

    \pi_{\text{title}}(\sigma_{\text{name} = \text{J.R.R. Tolkien}}(\text{authors} \Join \text{books}) \cap \sigma_{\text{year} > 1950}(\text{authors} \Join \text{books}))


Operation sequences
-------------------

As queries become more complex, expressions like the ones shown above can become quite long and difficult to understand.  An alternative approach is to use intermediate variables to decompose and label the parts of our expression.  The result is a more sequential view of the operations.

We will demonstrate this approach with one of the queries from the last section:

.. math::

    \pi_{\text{title}}(\sigma_{\text{name} = \text{J.R.R. Tolkien}}(\text{authors}) \Join \sigma_{\text{year} > 1950}(\text{books}))

Using variables, we can write this as a sequence of operations:

.. math::

    \begin{eqnarray*}
    \text{A} &=& \sigma_{\text{name} = \text{J.R.R. Tolkien}}(\text{authors}) \\
    \text{B} &=& \sigma_{\text{year} > 1950}(\text{books}) \\
    \text{C} &=& \text{A} \Join \text{B} \\
    \text{R} &=& \pi_{\text{title}}(C) \\
    \end{eqnarray*}

with **R** holding our final result.

.. index:: query trees

Expression trees
----------------

Another representation of relational algebra expressions is in the form of a tree.  Expression trees are a useful visual representation of a query.

..

    We will make use of them again in Chapter XXX, which is concerned with how database software considers different action plans for executing a query.

We will again demonstrate using the query:

.. math::

    \pi_{\text{title}}(\sigma_{\text{name} = \text{J.R.R. Tolkien}}(\text{authors}) \Join \sigma_{\text{year} > 1950}(\text{books}))

The tree representation of this query looks like:

.. image:: tree1.svg

Operations start at the bottom of the tree, with the relations **authors** and **books**, and proceed upwards.  We can apply either selection operation first, then the other; both must be applied before we can perform the join, and we finish with the projection.

Here is another example, corresponding to the expression:

.. math::

    \pi_{\text{title}}(\sigma_{\text{name} = \text{J.R.R. Tolkien}}(\sigma_{\text{year} > 1950}(\text{books}) \Join \text{authors}))

The tree is:

.. image:: tree2.svg


|chapter-end|

----

**Notes**

.. [#] This is consistent with the definition of the Cartesian product of sets of tuples in general mathematics.

.. [#] In fact, the original paper introducing the relational model discusses joins and not cross products.  However, the cross product is now recognized as a more fundamental operation in relational algebra.

.. [#] Some authors use * instead to indicate a natural join.

.. [#] More generally, **x** and **y** can stand in for a list of attributes; that is, **x** might be some list of attributes **x1**, **x2**, ... and similarly for **y**.  We only require that **x** and **y** together represent all attributes of **P**, and that **x** and **y** do not overlap.

|license-notice|



## Chapter: normalization.rst

.. _normalization-chapter:

=============
Normalization
=============

.. index:: normalization

In this chapter we discuss some aspects of how a database is structured - what relation schemas should we use to store our data?  While the material in this chapter is deeply rooted in relational database theory, the basic concepts can be understood without the theoretical foundation, and are important for all database practitioners.  If you are reading this chapter without having read earlier chapters on the relational model of the database, note we use the terms relation, attribute, and tuple in discussing the objects in our database; these terms closely correspond to the terms table, column, and row in relational database systems.

Introduction
::::::::::::

.. index:: redundancy

Normalization is the process of modifying a database structure to meet certain requirements. These requirements are defined by a series of *normal forms*, which we will define shortly.

A primary goal of normalization is to make it easier to maintain a correct collection of data.  Correct data is complete and self-consistent.  The database should not contain data contradicting what we understand to be true.

There are a few clues that can indicate a database is susceptible to common kinds of data corruption.  A very big clue is when a database exhibits redundancy, that is, when the same facts are recorded multiple times.  Another clue is when the database contains NULL in many places.  When these issues are present in a relation, it is usually also the case that the relation is doing too many things.  Relations work best when they contain data regarding a single thing or concept.  It can sometimes be difficult to detect that a relation is doing too much, though, which is why redundancy and excessive NULLs are such useful clues.

.. index:: modification anomaly

Modification anomalies
----------------------

There are three common types of errors that we can consider to better understand the need for normalization.  Each of these *modification anomalies* arise from one of the data modification operations available to us: insert, update, and delete.  We can illustrate each of these with the relation pictured below, which lists information about some classes and teachers at a fictional school.  The relation gives the class name, starting time, room number, instructor name, instructor office number, and instructor department.  Right away, we should be concerned that there is information in the relation about both *classes* and *instructors*.

.. table:: **classes**
    :class: lined-table

    ==================== ===== ========= =========== ====== ==========
    class_name           time  classroom instructor  office department
    ==================== ===== ========= =========== ====== ==========
    Algebra I            8:00  C01       Mr. Reyes   B24    Math
    Geometry             10:00 C01       Mr. Reyes   B24    Math
    World History        9:00  C15       Ms. Tan     A11    Humanities
    English Literature   10:00 C09       Ms. Larsen  A05    Humanities
    Physics              11:00 C06       Ms. Musa    B22    Science
    Chemistry            13:00 C17       Ms. Musa    B22    Science
    Music                9:00  C25       Mr. Pal     A03    Humanities
    ==================== ===== ========= =========== ====== ==========

This relation also exhibits redundancy.  We are given the facts that Mr. Reyes is in the Math department and his office is in room 124 multiple times, for example.  Note that Mr. Reyes appearing multiple times is not itself redundancy, as each appearance is a new fact: Mr. Reyes teaches Algebra I, and Mr. Reyes teaches Geometry.  We do not have any NULLs in this example, but we will see shortly how they might appear when we add or remove data.

.. index:: insert anomaly

Insert anomaly
##############

Consider what happens when a new instructor joins the faculty at the school.  Mr. Hassan is a new faculty member in the department of Math, but he has not yet been assigned any classes to teach.  How should we add Mr. Hassan to the database?  There are a few options, but none of them are good - whatever we do, we must provide values for **class_name**, **classroom**, and **time** in our new tuple.  We might think that NULL is the best choice for each of these attributes, as otherwise we must create fake class information.  Either way, we are making trouble for ourselves later on - our database now contains a tuple that must be handled in a special fashion, different from the other tuples in the relation.

.. index:: delete anomaly

Delete anomaly
##############

Now, consider what happens when Ms. Tan takes a job at another school.  If we are incautious, we will delete the tuple for Ms. Tan - removing World History from our list of classes altogether.  Similarly, we cannot remove English Literature from the list of classes without removing all information about Ms. Larsen.  The only way to avoid these issues with our current database design is to replace the existing values with NULLs.  As with the insert anomaly example, this leaves us with tuples that require special handling.

.. index:: update anomaly

Update anomaly
##############

Update anomalies are a direct consequence of the redundancy in our database.  Consider what happens when Mr. Reyes changes offices.  If we are incautious, we will update the tuple listing Mr. Reyes as the teacher of Algebra I, but forget to update the tuple for Geometry, leaving our data internally consistent.  Mr. Reyes will be listed as having two different offices, without any indication which is correct.  To avoid trouble, we must remember to always update *all* classes for which Mr. Reyes is the instructor.

Example solution
----------------

Normalizing the **classes** relation will prevent each of the situations above.  In effect, normalization requires us to structure relations such that the data is expressed in a very simple and consistent form.  We typically achieve normalization by *decomposing* a relation into multiple smaller relations.

Informally, in a normalized relation, some thing or concept is uniquely identified by a primary key composed of one or more attributes and every other attribute represents a *single-valued* fact about the thing or concept only. For our example, the **classes** relation describes classes; it has **class_name** as a primary key, and **classroom**, **time**, and **instructor** as single-valued attributes.  (An example of an attribute that is not single-valued would be a list of students in the class.  We call such an attribute *multi-valued*.)  However, **office** and **department** are not really facts about a class; instead, they are facts about instructors.  These extended facts need to be removed to another relation through *decomposition* of the **classes** relation:

.. table:: **classes**
    :class: lined-table

    ==================== ===== ========= ===========
    class_name           time  classroom instructor
    ==================== ===== ========= ===========
    Algebra I            8:00  C01       Mr. Reyes
    Geometry             10:00 C01       Mr. Reyes
    World History        9:00  C15       Ms. Tan
    English Literature   10:00 C09       Ms. Larsen
    Physics              11:00 C06       Ms. Musa
    Chemistry            13:00 C17       Ms. Musa
    Music                9:00  C25       Mr. Pal
    ==================== ===== ========= ===========

.. table:: **instructors**
    :class: lined-table

    =========== ====== ==========
    name        office department
    =========== ====== ==========
    Mr. Reyes   B24    Math
    Ms. Tan     A11    Humanities
    Ms. Larsen  A05    Humanities
    Ms. Musa    B22    Science
    Mr. Pal     A03    Humanities
    =========== ====== ==========

Note how we have eliminated redundancy through this decomposition.  If we need to update office information for an instructor, there is exactly one tuple to update.  We also no longer need to worry about modification anomalies.  Adding or removing an instructor is completely independent of adding or removing classes; this also removes any need for excessive NULLs in the **classes** relation [#]_.

.. index:: normal form

Normal forms
::::::::::::

The concept of normalization originates with the relational model itself.  Additional refinements have been added over time, leading to a series of normal forms, which mostly build on earlier normal forms.  We will not study every normal form that has been proposed, but focus on the forms which are most useful and most likely to be of value in most applications.  The first form we consider is appropriately named the *first normal form*, abbreviated 1NF.  We proceed with the second, third, and fourth normal forms (2NF, 3NF, 4NF) as well as Boyce-Codd normal form (BCNF), which fits in between 3NF and 4NF.

When a database meets the requirement for a normal form, we say that the database is *in* the form.  As commonly defined, most normal forms include a requirement that earlier normal forms are also met.  Therefore, any database that is in 4NF is necessarily also in 1NF, 2NF, 3NF, and BCNF; a database in BCNF is also in 3NF and below; and so forth.  However, it is also true that higher forms address less frequently occurring situations, so, for example, a database that has been restructured to be in 3NF is very likely to also be in BCNF or even 4NF.  3NF is generally considered the minimum requirement a database must meet to be considered "normalized".

To explain most of the normal forms, we first need to provide some additional foundation, covered in the next few sections.  However, we can explain 1NF immediately.  1NF requires that the domain of an attribute of a relation contains *atomic* values only.  Atomic here simply means that we cannot usefully break the value down into smaller parts.  Non-atomic elements include compound values, arrays of values, and relations.  For example, a character string containing an author's name may be atomic [#]_, but a string identifying a book by author and title is probably compound; a list of authors would be an array; and a table of values giving a book's publication history (including publisher, year, ISBN, etc. for each publication) would be a relation.  To meet the 1NF requirements, compound values should be broken into separate attributes, while arrays and relations should be broken out into their own relations (with a foreign key referencing the original relation).

1NF is often described as simply part of the definition of a relational database, and early relational database systems indeed provided no capabilities that would permit violations of 1NF.  Some modern database systems now provide support for compound values, in the form of user-defined types, and array values.  While 1NF technically remains a requirement for all higher normal forms, for certain applications these violations of 1NF may be highly useful.  Some authors have argued for permitting relation-valued attributes as well.

.. index:: key - normalization; superkey

Keys and superkeys
::::::::::::::::::

This section reiterates some material from :numref:`Chapter {number} <relational-model-chapter>` in which we defined the term *key*, but in a bit more detail.  We start by defining a more general term, *superkey*.

A superkey of a relation is some subset of attributes of the relation which uniquely identifies any tuple in the relation.  Consider the **library** relation below (we will be using this example extensively):

.. table:: **library**
    :class: lined-table

    ================= ========================== ==== ================ ============ ============ ===================
    author            title                      year genre            author_birth author_death section
    ================= ========================== ==== ================ ============ ============ ===================
    Ralph Ellison     Invisible Man              1952 fiction          1914-03-01   1994-04-16   literature
    Jhumpa Lahiri     Unaccustomed Earth         2008 fiction          1967-07-11                literature
    J.R.R. Tolkien    The Hobbit                 1937 fantasy          1892-01-03   1973-09-02   speculative fiction
    Isabel Allende    The House of the Spirits   1982 magical realism  1942-08-02                literature
    J.R.R. Tolkien    The Fellowship of the Ring 1954 fantasy          1892-01-03   1973-09-02   speculative fiction
    Ursula K. Le Guin The Dispossessed           1974 science fiction  1929-10-21   2018-01-22   speculative fiction
    ================= ========================== ==== ================ ============ ============ ===================

(The blank entries for **author_death** in this table represent NULLs.  The authors are still living at the time of this writing.)

We assert that the set of attributes {**author**, **title**, and **year**} is a superkey for the **library** relation.

The definition of superkey applies not just to the current data in the relation, but to *any data we might possibly store in the relation*.  That is, a superkey is not a transitory property of the data, but a constraint we impose on the data.  For example, although each publication year listed in the **year** column above is unique to its book, that cannot be guaranteed for future books we might add to the relation.  Therefore the set {**year**} is not a superkey for **library**.

A second, and equivalent definition of superkey is as a subset of attributes of the relation that are guaranteed to contain a unique setting of values for any tuple in the relation.  For our example, this means there can never be two books in the **library** relation which share the same author, title, and year.  From this second definition and the definition of a relation, we note that *every* relation has at least one superkey: the set of all attributes of the relation.  The set {**author**, **title**, **year**, **genre**, **author_birth**, **author_death**, **section**} is a superkey for the **library** relation simply because every tuple in the relation must be unique.

We can further state that any subset of attributes of the relation which is a superset of some superkey of the relation is also a superkey of the relation.  For our example, {**author**, **title**, **year**, **author_birth**} must be a superkey because it is a superset of a known superkey.

A *key* of a relation is a superkey of the relation from which we cannot subtract any attributes and get a superkey.  For the **library** relation, we assert that {**author**, **title**} is a superkey of the relation; furthermore, both **author** and **title** are needed.  That is, neither {**author**} nor {**title**} is a superkey of **library**.  Therefore, {**author**, **title**} is a key of **library**; the set {**author**, **title**, **year**} is a superkey but not a key because we can remove **year** and still have a superkey [#]_.

Identifying the keys of a relation is a key step in analyzing whether or not a relation is already normalized with respect to 2NF or higher.

.. index:: functional dependency

Functional dependencies
:::::::::::::::::::::::

Now we turn to the topic of functional dependencies, which are closely related to superkeys.

A *functional dependency* (FD) is a statement about two sets of attributes of a relation.  Consider two sets of attributes, which we will label *X* and *Y*.  We say that *X* *functionally determines* *Y*, or *Y* is *functionally dependent on* *X*, if, whenever two tuples in the relation agree on the values in *X*, they must also agree on the values in *Y*.  The notation for this is:

.. math::
    X \rightarrow Y

As with keys, FDs are constraints that we impose on the data.  Another way of thinking about a functional dependency is, if you had a relation such that the relation contains only the attributes that are in *X* or *Y*, then *X* would be a superkey for that relation.  That is, *X* uniquely determines everything in the union of *X* and *Y*.  (We can now provide another defintiion of superkey as a subset of attributes of a relation that functionally determines the set of all attributes of the relation.)

Another way of thinking about FDs is, if *X* functionally determines *Y*, then if we know the values in *X*, we know or can determine the values in *Y*, because *Y* just contains single-valued facts about *X*.  In our **library** relation, the set {**author**, **title**} functionally determines the set {**year**}, because if we know the author and title of the book, then we should be able to find out what the publication year is; and whatever sources we consult to find the year should all give us the same answer.  The dependency is "functional" in this sense; there exists some *function* between the domain of (author, title) pairs and the domain of publication years that yields the correct answer for every valid input.  The function in this case is simply a mapping between domains, not something we can analytically derive.

Here are some more FDs for the **library** relation:

.. math::

    \begin{eqnarray*}
    \text{\{author, title\}} & \rightarrow & \text{\{genre\}} \\
    \text{\{author\}} & \rightarrow & \text{\{author_birth, author_death\}} \\
    \text{\{genre\}} & \rightarrow & \text{\{section\}} \\
    \text{\{author, title\}} & \rightarrow & \text{\{title, year\}} \\
    \text{\{title, genre\}} & \rightarrow & \text{\{title\}} \\
    \end{eqnarray*}

The first FD tells us that each book is categorized into exactly one genre in our database.  The second tells us that an author's dates of birth and death should be the same every time the author appears in the database.  The third tells us that the location in the library in which a book is shelved depends on the genre of the book.  The last two FDs are different from the previous ones; in these, there is an overlap between the set on the left-hand side and the set on the right-hand side.  We will give special names to these in a moment.  For now, the fourth FD tells us that, if we know the author and title of a book, then we know the title and the publication year.  The final FD simply tells us that any two tuples having the same title and genre, have the same title!

Types of functional dependency
------------------------------

FDs are categorized into three types: *trivial*, *non-trivial*, and *completely non-trivial*.

A trivial FD is one in which the right-hand side of the FD is a subset of the left-hand side.  The last FD in our example above is a trivial FD.  A trivial FD conveys no useful information - it tells us "we know what we know" - but they still have some use to us in our normalization procedures.  Every trivial FD we can write down for a relation is true, as long as the left-hand side of the FD is a subset of the attributes of the relation.

A non-trivial FD is one in which some part of the right-hand side of the FD is not in the left-hand side.  The intersection of the left-hand side and the right-hand side is not empty, but the right-hand side is not a subset of the left-hand side.  The fourth FD above is a non-trival FD.  These FDs convey some new information.  Identifying non-trivial FDs in our relations is a crucial step in normalization.

As you might guess by now, a completely non-trivial FD is one for which there is no overlap between the left-hand side and the right-hand side - the intersection of the two sets is the empty set.  The first three FDs above are completely non-trivial.

.. index:: functional dependency; inference rules

Inference rules
---------------

Many FDs can be inferred or derived from other FDs.  We are particularly interested in non-trivial FDs which have a maximal set on the right-hand side, that is, a set which cannot be added to without making the FD false.  There is a straightforward algorithm to infer such FDs from a set of FDs, which we discuss in the next section.  We need the five inference rules below for the algorithm.  The first three inference rules are known as *Armstrong's axioms*, and can be used to prove the remaining rules.

We present these without proof, but the intuition behind these should be clear.  Let *X*, *Y*, and *Z* be subsets of the attributes of the same relation.  Let the union of *Y* and *Z* be denoted *YZ*.  Then we have:

*Reflexive rule*
    If Y is a subset of X, then

    .. math::

        X \rightarrow Y

    This is simply a statement that all trivial FDs are true.

*Augmentation rule*
    If

    .. math::

        X \rightarrow Y

    then

    .. math::

        XZ \rightarrow YZ

    also holds.

    This rule says we can add the same attributes to both the left-hand and right-hand sides of an FD.  Trivially, if we add *Z* to what we know (left-hand side), then we should be able to determine *Z* in addition to what we could determine previously (right-hand side).

    In our **library** example, we are given

    .. math::

        \text{\{author\}} \rightarrow \text{\{author_birth, author_death\}}

    therefore, it is also true that

    .. math::

        \text{\{author, genre\}} \rightarrow \text{\{author_birth, author_death, genre\}}

    A special case of this is that we can add the left-hand side to both sides; this leaves the left-hand side unchanged, since the union of any set with itself is just the set:

    .. math::

        X \rightarrow Y

    implies

    .. math::

        X \rightarrow XY


*Transitive rule*
    If we have both of

    .. math::

        X \rightarrow Y \\
        Y \rightarrow Z

    then

    .. math::

        X \rightarrow Z

    also holds.  That is, if knowing *X* tells us *Y*, and from *Y* we can know *Z*, then knowing *X* also tells us *Z*.

    In our **library** relation we have

    .. math::

        \text{\{author, title\}} \rightarrow \text{\{genre\}}
        \text{\{genre\}} \rightarrow \text{\{section\}} \\

    thus

    .. math::

        \text{\{author, title\}} \rightarrow \text{\{section\}}

*Splitting rule (or decomposition, or projective, rule)*
    If

    .. math::

        X \rightarrow YZ

    holds, then so do

    .. math::

        X \rightarrow Y \\
        X \rightarrow Z

    Plainly stated, if knowing the values for *X* tells us the values for *Y* **and** *Z*, then knowing the values for *X* tells us the values for *Y*, and likewise for *Z*.  In our **library** example, we have

    .. math::

        \text{\{author\}} \rightarrow \text{\{author_birth, author_death\}}

    therefore, it is also true that

    .. math::

        \text{\{author\}} \rightarrow \text{\{author_birth\}} \\
        \text{\{author\}} \rightarrow \text{\{author_death\}}

    Note that we can "split" the right-hand side only.  For example, given :math:`\text{\{author, title\}} \rightarrow \text{\{year\}}`, it is **not** true that :math:`\text{\{author\}} \rightarrow \text{\{year\}}`.

*Combining rule (or union, or additive, rule)*
    This is the splitting rule in reverse.  If we have both of

    .. math::

        X \rightarrow Y \\
        X \rightarrow Z

    then

    .. math::

        X \rightarrow YZ

    also holds. In our **library** example, we have

    .. math::

        \text{\{author, title\}} \rightarrow \text{\{year\}} \\
        \text{\{author, title\}} \rightarrow \text{\{genre\}}

    thus

    .. math::

        \text{\{author, title\}} \rightarrow \text{\{year, genre\}}

While any FDs that can be inferred from a given collection of FDs on a relation can be inferred using the above rules, there is unfortunately no way of deciding that some collection of FDs is, in fact, *complete* - that is, that the collection of FDs lets us infer every possible true FD on the relation.  FDs come from the minds of the database designer and others involved in analysis and design, a process which requires some "trial and error", i.e., iterative improvement.

.. index:: closure

Closure
-------

As mentioned, we are going to be particularly interested in non-trivial FDs which have a maximal set on the right-hand side.  The *closure* of a subset *X* of relation *R* given some collection of FDs is the union of all sets {*a*} such that *a* is an attribute of *R* and we can infer :math:`X \rightarrow {a}`.  Informally, the closure of *X* is the set of attributes which are functionally determined by *X*.  The closure of *X* is denoted *X*:sup:`+`.

We are interested in closure for a couple of reasons.  First, note from this definition that the closure of a superkey of a relation is the set of all attributes of the relation.  We can use this fact to test whether or not some set of attributes is a superkey; further, we could in theory find all superkeys of a relation by examining the closure of every subset of attributes (in practice this can become too much work fairly quickly as the number of attributes increases).  Second, closure will be useful in the decomposition step of our normalization algorithms.

The closure of a set of attributes can be determined using the following algorithm.

*Closure algorithm*
    Given a collection *F* of FDs and a set of attributes *X*:

    1. Let *C* = *X*.  Trivially, :math:`X \rightarrow C`.
    2. While there exists some functional dependency :math:`Y \rightarrow Z` in *F* such that *Y* is a subset of *C* and *Z* contains some attributes not in *C*, add the attributes in *Z* to *C* to create *C\'*.  Then,

       .. math::

          \begin{eqnarray*}
          & & C \rightarrow Y    ~~\text{(reflexive rule)} \\
          & & C \rightarrow Z    ~~\text{(transitive rule)} \\
          & & X \rightarrow Z    ~~\text{(transitive rule)} \\
          & & X \rightarrow C'   ~~\text{(combining rule)} \\
          \end{eqnarray*}

       Let *C* = *C\'*.

    3. When no more FDs meet the criteria above, *C* = *X*:sup:`+`.

We previously asserted that the set {author, title} is a superkey for our example **library** relation, so the closure {author, title}\ :sup:`+` should be the set of all attributes of **library**.  We now show that this follows from our inference rules, and from the FDs given previously:

.. math::

    \begin{eqnarray*}
    \text{\{author, title\}} & \rightarrow & \text{\{year\}} \\
    \text{\{author, title\}} & \rightarrow & \text{\{genre\}} \\
    \text{\{author\}} & \rightarrow & \text{\{author_birth, author_death\}} \\
    \text{\{genre\}} & \rightarrow & \text{\{section\}} \\
    \text{\{author, title\}} & \rightarrow & \text{\{title, year\}} \\
    \text{\{title, genre\}} & \rightarrow & \text{\{title\}} \\
    \end{eqnarray*}

1. Let *C* = {author, title}.
2. We have :math:`\text{\{author, title\}} \rightarrow \text{\{year\}}`, and {author, title} is a subset of *C*, so add **year** to *C*: *C* = {author, title, year}.
3. Similarly, :math:`\text{\{author, title\}} \rightarrow \text{\{genre\}}`, so let *C* = {author, title, year, genre}.
4. We have :math:`\text{\{author\}} \rightarrow \text{\{author_birth, author_death\}}`, and {author} is a subset of *C*.  Let *C* = {author, title, year, genre, author_birth, author_death}.
5. We have :math:`\text{\{genre\}} \rightarrow \text{\{section\}}`, and {genre} is a subset if *C*.  Let *C* = {author, title, year, genre, author_birth, author_death, section}.
6. The algorithm completes at this point because the right-hand sides of all of the unused FDs are already subsets of *C*; and in any case, *C* already has all attributes of **library**.

Thus, {author, title}\ :sup:`+` = {author, title, year, genre, author_birth, author_death, section}.

.. index:: second normal form, 2NF, third normal form, 3NF, Boyce-Codd normal form, BCNF

Second, third, and Boyce-Codd normal forms
::::::::::::::::::::::::::::::::::::::::::

We are now ready to discuss the normal forms up to Boyce-Codd normal form (BCNF).  In this section we will provide definitions of the normal forms, with examples.

Second normal form
------------------

A relation is in second normal form (2NF) if it is in 1NF and there are no *non-key attributes* which are functionally dependent on a proper subset of the key.  A non-key attribute is an attribute which is not part of any key.

From this definition, we can see that **library** is not in 2NF.  The key of **library** is {author, title}.  However, we have the FD

.. math::

    \text{\{author\}} \rightarrow \text{\{author_birth, author_death\}}

in which the left-hand side only contains **author**.  We say that the above FD *violates* second normal form.

Note that any relations (in 1NF) for which the key has a single attribute is automatically in 2NF.

Third normal form
-----------------

A relation is in third normal form (3NF) if it is in 2NF and there are no non-key attributes which are functionally dependent on other non-key attributes.

Considering the **library** relation again, the dependency

.. math::

    \text{\{genre\}} \rightarrow \text{\{section\}}

violates 3NF because neither **genre** nor **section** are part of any key.

Boyce-Codd normal form
----------------------

Boyce-Codd [#]_ normal form is a slightly stronger version of third normal form; any relation in BCNF is also in 3NF.  However, most relations in 3NF are also in BCNF.  BCNF has a simple and general definition which encompasses the definitions of 2NF and 3NF:

*Definition of BCNF*
    A relation is in BCNF if it is in 1NF and if, for every non-trivial functional dependency of the form :math:`X \rightarrow Y` on the relation, *X* is a superkey of the relation.

It may not be obvious from this definition that relations in BCNF are also in 2NF and 3NF.  We will demonstrate that this is true for 2NF; a similar argument holds for 3NF.  Recall that 2NF requires we have no non-key attributes functionally dependent on a proper subset of the key.  By the definition of key, a proper subset of the key cannot be a key or superkey; therefore, an FD forbidden by 2NF must have a left-hand side that is not a superkey.  On the other hand, non-key attributes cannot be part of the key at all.  The right-hand side of an FD forbidden by 2NF can have no intersection with the left-hand side, so the FD is completely non-trivial.  Thus any FDs that would violate 2NF also meet the criteria for violating BCNF.

The difference between 3NF and BCNF is simply that 3NF permits FDs for which the right-hand side is a subset of a key.  This situation is fairly uncommon, which is why most relations in 3NF are also in BCNF.  We will explore this difference further in a later section.

.. index:: decomposition, normalization; decomposition

Decomposition
:::::::::::::

We say that a database is normalized with respect to some normal form if all relations in the database are in the normal form.  To normalize a database, we must *decompose* relations which have some violating FD.  Decomposition of a relation involves creating two new relations, each of which has a subset of the attributes of the original relation.  The original relation can then be discarded.

In this section we discuss the BCNF decomposition algorithm and provide an example walkthrough of normalization.  We close the section by exploring why some problematic relations may be better left in 3NF.

Decomposition algorithm
-----------------------

There is a simple approach to decomposition that both eliminates a violation of a normal form, and that allows for exact recovery of the original relation in all cases.  The algorithm below is expressed in terms of BCNF, but works equally well for 2NF and 3NF:

*Decomposition algorithm*
    Given some relation *R*, and a functional dependency :math:`X \rightarrow Y` on *R* that violates BCNF:

    1. (Optional, but strongly recommended) Add to *Y* any attributes that are functionally determined by *X* and that are not already in *Y*; i.e., let *Y* = *X*:sup:`+`.  (It is easy to show that :math:`X \rightarrow X^{+}` violates BCNF given the original violation, so we are merely substituting one violating FD for another.)
    2. Let *Z* be the set of attributes of *R* that are not in *X* or *Y*.  (This set must be non-empty because, by definition, *X* is not a superkey.)
    3. Create relations *R1* and *R2* such that *R1* has the attributes in the union of *X* and *Y*, and *R2* has the attributes in the union of *X* and *Z*.  In relational algebra terms, we use projection to create the new relations:

       .. math::

          R1 = \pi_{XY}(R) \\
          R2 = \pi_{XZ}(R)

    4. Discard *R*.

Worked example
--------------

We now apply this algorithm to a database initially composed of just the **library** relation.  To start, we previously noted that the FD

.. math::

    \text{\{author\}} \rightarrow \text{\{author_birth, author_death\}}

violates 2NF and thus BCNF.  To apply the decomposition algorithm to this violation:

1. Let *Y* be the closure of {author}, which is {author, author_birth, author_death}.
2. Let *Z* then be {title, year, genre, section}.
3. The union of *X* and *Y* is just *Y* because we did the optional closure in step 1.  The union of *X* and *Z* is {author, title, year, genre, section}.  Projecting on to these attribute sets yields the following relations, which we rename to **authors** and **library2**:

.. table:: **authors**
    :class: lined-table

    ================= ============ ============
    author            author_birth author_death
    ================= ============ ============
    Ralph Ellison     1914-03-01   1994-04-16
    Jhumpa Lahiri     1967-07-11
    J.R.R. Tolkien    1892-01-03   1973-09-02
    Isabel Allende    1942-08-02
    Ursula K. Le Guin 1929-10-21   2018-01-22
    ================= ============ ============

.. table:: **library2**
    :class: lined-table

    ================= ========================== ==== ================ ====================
    author            title                      year genre            section
    ================= ========================== ==== ================ ====================
    Ralph Ellison     Invisible Man              1952 fiction          literature
    Jhumpa Lahiri     Unaccustomed Earth         2008 fiction          literature
    J.R.R. Tolkien    The Hobbit                 1937 fantasy          speculative fiction
    Isabel Allende    The House of the Spirits   1982 magical realism  literature
    J.R.R. Tolkien    The Fellowship of the Ring 1954 fantasy          speculative fiction
    Ursula K. Le Guin The Dispossessed           1974 science fiction  speculative fiction
    ================= ========================== ==== ================ ====================

4. Discard **library**.

Note that we can recover the original relation by applying a natural join operation to **authors** and **library2**.

We must now look at our new relations, and determine if they are now normalized.  A first step is determining keys and FDs for the new relations.  There is a formal process to compute the superkeys and FDs of the new relation from the FDs on the old relation [#]_.  However, in practice it is usually possible for a database designer to identify the FDs and keys of the new relations given their knowledge of the data, without all of the computations implied above.

For our example, in **authors** we can quickly determine that the only useful non-trivial FD is

.. math::

    \text{\{author\}} \rightarrow \text{\{author_birth, author_death\}}

From this we can also see that the closure of {author} includes all attributes in authors, and thus {author} is a key.  There are no violating FDs remaining in this relation, so it is normalized with respect to BCNF.

Now consider the relation **library2**.  Note that the FD above does not apply, because **author_birth** and **author_death** are not attributes in **library2**.  From our knowledge of the FDs in the **library** relation, we can determine that these FDs hold in **library2**:

.. math::

    \begin{eqnarray*}
    \text{\{author, title\}} & \rightarrow & \text{\{year, genre, section\}} \\
    \text{\{genre\}} & \rightarrow & \text{\{section\}} \\
    \end{eqnarray*}

and that the key is {author, title}.

The second FD above violates BCNF (and 3NF).  Decomposing on this FD, we have *X* = {genre}, *Y* = {section}, and *Z* = {title, author, year, genre}.  Decomposition results in the following relations, which we rename to **books** and **genres**:

.. table:: **books**
    :class: lined-table

    ================= ========================== ==== ================
    author            title                      year genre
    ================= ========================== ==== ================
    Ralph Ellison     Invisible Man              1952 fiction
    Jhumpa Lahiri     Unaccustomed Earth         2008 fiction
    J.R.R. Tolkien    The Hobbit                 1937 fantasy
    Isabel Allende    The House of the Spirits   1982 magical realism
    J.R.R. Tolkien    The Fellowship of the Ring 1954 fantasy
    Ursula K. Le Guin The Dispossessed           1974 science fiction
    ================= ========================== ==== ================

.. table:: **genres**
    :class: lined-table

    =============== ===================
    genre           section
    =============== ===================
    fiction         literature
    fantasy         speculative fiction
    magical realism literature
    science fiction speculative fiction
    =============== ===================

We discard **library2**, leaving us with just three relations: **authors**, **books**, and **genres**. All three relations are now in BCNF, so no further normalization (with respect to BCNF or lower) is possible.  We can recover the **library2** relation by a natural join of **books** and **genres**; or we can recover the original **library** relation by a natural join of all three relations.

Note that the normalized database has a clear separation of concerns in the different relations; one relation is just about authors, another about books, and a third with specialized information about the layout of a library.  Redundancy has been reduced, and modification anomalies are much less likely.

Decomposition properties
------------------------

There are two desirable properties for a normalization decomposition, which we discuss in this section.

Exact recovery
##############

This first property we have mentioned, which is that the original relation must be recoverable by joining the decomposition products.  This means that the joined relation must have all of the tuples of the original, and no extra tuples.  This property is non-negotiable; a join of the relations must give true answers.  In fact, the BCNF decomposition algorithm as presented fulfills this condition; an arbitrary decomposition would not necessarily do so.

We omit a full proof of the correctness of the decomposition algorithm.  An intuitive understanding begins with a consideration of the meaning of functional dependency.  The existence of some functional dependency :math:`X \rightarrow Y` tells us that the *Y* attributes must remain in lockstep with the *X* attributes.  Any distinct value of *X* can be associated with exactly one setting of *Y* values; so *X* uniquely identifies *Y*.  Therefore, if we have a relation that lets us look up the values for *Y* for each distinct value of *X*, we can use *just the* X *attributes* in the original relation as representative of both *X* and *Y*.  The decomposition algorithm creates exactly this situation; projection onto the attributes involved in the functional dependency creates the "lookup" relation (**authors** in our first decomposition example); the *X* attributes (**author**) remain as a foreign key and the *Y* attributes (**author_birth**, **author_death**) can be removed.  A join of the relations on the shared foreign key restores the *Y* values to the correct tuples.

Dependency preservation
#######################

A second desirable property for a decomposition is *not* always met with BCNF decomposition.  This second property requires that all constraints implied by the original functional dependencies are preserved in the database after decomposition.  It turns out that we can guarantee this property by normalizing to 3NF, but not BCNF.  This is best illustrated with an example.

Consider the relation below, regarding the Hugo and Nebula awards for literary and other works in the science fiction genre.  These two awards are given each year in multiple categories, such as "Best Novel", "Best Short Story" and so forth.  Typically only one work in a given format in a given year wins a given award (we will assume that rule is always enforced for example purposes).  Therefore, if we are given the award, year, and format, we can unambiguously determine the award winning work.  The relation below gives some representative data:

.. table:: **scifi_awards**
    :class: lined-table

    ====== ==== =========== ================= ====================
    award  year format      author            title
    ====== ==== =========== ================= ====================
    Hugo   1975 novel       Ursula K. Le Guin The Dispossessed
    Hugo   1975 short story Larry Niven       The Hole Man
    Hugo   1974 novel       Arthur C. Clarke  Rendezvous With Rama
    Nebula 1975 novel       Joe Haldeman      The Forever War
    Nebula 1974 novel       Ursula K. Le Guin The Dispossessed
    ====== ==== =========== ================= ====================

There are two important functional dependencies.  The first, reflecting the rule that only one work in each format can win a particular award in a given year, is

.. math::

    \text{\{award, year, format\}} \rightarrow \text{\{author, title\}}

The first constraint does not violate 3NF or BCNF, because the left-hand side is a key for the relation.

The second FD acknowledges that each work is in a particular format; a work may be a novel or a short story, but not both:

.. math::

    \text{\{author, title\}} \rightarrow \text{\{format\}}

This relation falls into the narrow category of relations that are in 3NF but not in BCNF.  As in this example, this occurs when the relation contains sets of attributes *A*, *B*, and *C*, with :math:`AB \rightarrow C` and :math:`C \rightarrow B`.  The second FD violates BCNF, because {author, title} is not a key for this relation (as demonstrated in the example data above).  However, the FD does not violate 3NF, because the right-hand side ({format}) is part of a key for the relation.

If we decompose as usual on the BCNF violation, the immediate decomposition products must join together to return the original relation, which has correct data, so that is not a problem.  However, after decomposition, we have relations with attributes {author, title, format} and {award, year, author, title}.  The first FD above, which enforced the constraint of an award going to only one work in each format each year, no longer applies to either relation.  The new relations cannot prevent us storing data such as the following:

.. table:: **scifi_awards_1**
    :class: lined-table

    ================= ==================== ======
    author            title                format
    ================= ==================== ======
    Ursula K. Le Guin The Dispossessed     novel
    Roger Zelazny     Doorways in the Sand novel
    ================= ==================== ======

.. table:: **scifi_awards_2**
    :class: lined-table

    ===== ==== ================= ====================
    award year author            title
    ===== ==== ================= ====================
    Hugo  1975 Ursula K. Le Guin The Dispossessed
    Hugo  1975 Roger Zelazny     Doorways in the Sand
    ===== ==== ================= ====================

Since the Hugo award is given to multiple works in a given year (just for different categories of work), the data in the second relation *could be* valid - but only if the two works listed happen to be in different categories.  However, as the first relation shows, they are in the same category (the second relation, as it happens, contains false data).  Only if we join these two relations can we see that we have violated our constraint.

In this particular case, it would be preferable to leave the original relation in 3NF and preserve the constraint with a primary key composed of {award, year, format}.  The redundancy involved is small, given that works can appear at most twice in the relation (since we only have the two awards).  If you encounter such a situation, however, you must determine the best way forward for your particular case.  If you leave the relation in 3NF, then you must manage the modification anomalies implied implied by the BCNF violation (in the application software, or some other mechanism).  If you move the relation to BCNF, then you must enforce the lost constraint in some other fashion.

.. index:: multivalued dependency, fourth normal form, 4NF

Multivalued dependencies and fourth normal form
:::::::::::::::::::::::::::::::::::::::::::::::

Relations that violate BCNF frequently occur in normal data collection activities.  For example, a web server keeping activity logs might record user information along with information about the pages the user visits on the website.  Redundancy is apparent in the user information appearing identically in multiple log entries.

In contrast, fourth normal form (4NF) violations are unlikely to occur in data gathering.  Instead, 4NF addresses problems that occur when an attempt is made to store data that includes multiple independent one-to-many relationships in a single relation.  Redundancy in this setting is more subtle and harder to identify.

For an example, we will consider some of the many awards given for literary merit.  Some awards are given to authors (Nobel Prize in Literature, Neustadt International Prize for Literature) without reference to a specific work.  Others (Pulitzer Prize, Nebula Award) are given in recognition of specific works.  An author can win multiple awards of either type.  If we are incautious in our design, we might come up with a relation like the following:

.. table:: **authors_and_awards**
    :class: lined-table

    =============== =========================== ===================================
    author          author_award                book_award
    =============== =========================== ===================================
    Louise Glück    Nobel Prize                 Pulitzer Prize
    Louise Glück    Nobel Prize                 National Book Award
    John Steinbeck  Nobel Prize                 Pulitzer Prize
    Alice Munro     Nobel Prize                 Giller Prize
    Alice Munro     International Booker Prize  Giller Prize
    Alice Munro     Nobel Prize                 National Book Critics Circle Award
    Alice Munro     International Booker Prize  National Book Critics Circle Award
    =============== =========================== ===================================

This is just an illustration; we would probably want to include other attributes to our relation such as the year each award was won, or the book for which a book award was won, but these extra attributes distract from the central concern we are trying to address.

At a casual glance it appears that there are many redundancies in this relation.  For example, we have two tuples showing that Louise Glück won a Nobel Prize, and the same for Alice Munro.  We show Alice Munro winning the Giller Prize in two different tuples [#]_.  For this relation, however, there are no non-trivial functional dependencies whatsoever.  The only key for the relation is the set {author, author_award, book_award}, so each tuple is unique.  Therefore the relation is in BCNF.

The pattern here is indicative of something called a *multivalued dependency* (MVD).  The formal definition of an MVD is rather opaque, and we will not state it here.  Informally, we have subsets of attributes *A*, *B*, and *C*, such that, for a given *A*, every distinct value of *B* must be paired with every distinct value of *C* associated with the value of *A*.  When this is true we state that *A* *multidetermines* *B*, and write

.. math::

    A \twoheadrightarrow B

The situation is also symmetric; when *A* multidetermines *B* it also multidetermines *C*.  Thus we may write

.. math::

    A \twoheadrightarrow B|C

In our example, considering Alice Munro and her Nobel Prize, what book awards did she win?  The answer must include both the Giller Prize and the National Book Critics Circle Award.  The same answer applies when we consider her International Booker Prize.  We might instead consider Alice Munro and her Giller prize and ask what author awards she won; this time the answer would include her Nobel Prize and her International Booker Prize.  Thus, for this relation the MVD

.. math::

  \text{\{author\}} \twoheadrightarrow \text{\author_award\}} | \text{\{book_award\}}

holds.

The definition of fourth normal form looks much like the definition of BCNF, substitution MVD for FD:

*Definition of 4NF*
    A relation is in 4NF if, for every non-trivial multivalued dependency of the form :math:`X \twoheadrightarrow Y` on the relation, *X* is a superkey of the relation.

Clearly in our example relation, the set {author} is not a superkey, so the relation is not in 4NF.  The solution to a 4NF violation happens to be identical to the solution for a BCNF violation.  Given an MVD :math:`X \twoheadrightarrow Y` that violates 4NF, we decompose into two relations, one with the attributes in *XY*, and the other with the attributes in *XZ*, where *Z* is everything not in *X* or *Y* (*Z* is also multidetermined by *X* as discussed above).  The decomposition eliminates the pairing of independent concepts.  For our example, the decomposition yields:

.. table:: **author_awards**
    :class: lined-table

    =============== ===========================
    author          author_award
    =============== ===========================
    Louise Glück    Nobel Prize
    John Steinbeck  Nobel Prize
    Alice Munro     Nobel Prize
    Alice Munro     International Booker Prize
    =============== ===========================

.. table:: **author_book_awards**
    :class: lined-table

    =============== ===================================
    author          book_award
    =============== ===================================
    Louise Glück    Pulitzer Prize
    Louise Glück    National Book Award
    John Steinbeck  Pulitzer Prize
    Alice Munro     Giller Prize
    Alice Munro     National Book Critics Circle Award
    =============== ===================================

The formal definition of MVD is sufficiently general that every FD qualifies as an MVD.  Therefore, a relation in 4NF is also in BCNF.

Trade-offs
::::::::::

As we have seen, the process of normalization leads to increased numbers of (generally smaller) relations.  Despite this proliferation of relations, normalization actually simplifies application software due to eliminating modification anomalies and related issues.  Smaller relations may also provide modest space savings, and performing queries on the relations in isolation will be faster.  However, when a query requires data collected into many different relations, performance can suffer.  Particularly when large volumes of data are involved, join operations become expensive for relational database systems.

As a result, there are occasions when it is desirable to create a *de-normalized* database, in which data is held in one or more large relations representing the result of joining together numerous relations.  Such a decision should not be made lightly and without consideration for the impact of modification anomalies.  One popular approach creates not one, but two databases containing the same data.  In this approach, one database is fully normalized and is used to process data updates.  The other, de-normalized database is used solely for read-only queries, and may be updated (or re-created) only periodically (perhaps daily or hourly).  Users of the de-normalized database receive slightly out-of-date answers, but faster.

Normalization in database design
::::::::::::::::::::::::::::::::

Databases can be created using a number of approaches.  The approach taken depends greatly on the circumstances which have led to the need for a database.

In some cases, data have been previously collected and stored in some fashion, but not organized into something we would consider a database.  Many scientific, industrial, and business processes produce large amounts of data in the form of sensor readings, application logs, reports, and form responses.  This data may exist in electronic form or on paper.  There may be little structure to the data; it may exist in a *flat* form in which there is only one type of record which stores every piece of information relevant to some event.  Creating a database to more efficiently work with such data may be best accomplished using a top-down approach, in which relations are systematically decomposed.  Data modeling (:numref:`Part {number} <data-modeling-part>`) may be used as part of this process, to document, communicate, and reason about the evolving database.

In contrast, when creating a new software application, a bottom-up approach may be preferred.  The application developers and other interested parties work to identify the data attributes that need to be collected and stored.  Multiple relations emerge naturally, corresponding to different parts of the application.  Data modeling should almost always occur early in this process.

Data modeling is very effective at producing relations that accurately represent independent concepts and the relationships between them.  However, some relations may still require normalization.  Normalization provides a different perspective on database design.  As with data modeling, our understanding of the real world and our data informs our choices.  However, while data modeling focuses on mapping concepts in the real world to relations, normalization works to produce a database structure that is more resistant to data errors.  Data modeling ensures our database accurately captures the data we need, while normalization ensures our database can be used effectively.  The two activities are thus complementary.  Whether or not normalization is applied formally, an understanding of normalization and its trade-offs is important for any database designer.


|chapter-end|

----

**Notes**

.. [#] We may need to use NULLs when information is truly unknown or absent; for example, we would set the **instructor** attribute NULL for classes which have no instructor assigned at the current time.  Similarly, we might set the **office** attribute NULL for new instructors who do not yet have an office.  Neither of these cases requires special handling in our software, so we consider these NULLs acceptable.  While it is possible to design a database that avoids even these NULLs, it would complicate the database (with more relations) for little gain.

.. [#] It is common practice in some countries where English is the primary language to break a name into first (or given), middle, and last name (or surname).  However, this naming scheme is by no means universal, even for English speakers.  Unless there is a compelling need to break a name into components for your application, we recommend a single name attribute.  For more on this topic, see https://www.w3.org/International/questions/qa-personal-names.

.. [#] We reiterate that a superkey is a constraint *we impose* on the data.  When designing a database, we of course hope to create a structure that accommodates true facts from the world, but a) we sometimes fail due to incomplete information about the world, and b) we sometimes compromise on a simpler design that accommodates *most* facts from the world.  For our **simple_books** relation, we are unaware of any books by the same author with the same title in the same year, so we are comfortable asserting that {**author**, **title**, **year**} is a valid superkey (but we could be wrong).  On the other hand, this design intentionally fails to capture any number of the complexities of books in the real world.  For one example, authors occasionally re-publish a book with small changes, under the same title, years after the original publication.  Is this the same "book" (in which case **year** really stands for "year of first publication"), or a different book (in which case {**author**, **title**} is *not* a superkey)?  For another example, we are completely ignoring the fact that some books have multiple authors, and some have no known authors.  Databases about books can be very complex!

.. [#] Named after Raymond F. Boyce and Edgar F. Codd, who published a :ref:`paper <relational-theory-references>` in 1974 defining this normal form.  However, a 1971 paper by Ian Heath gave a prior description.

.. [#] Given *R* and *R1* and a collection of FDs on R1, for every subset *X* of the attributes of *R1*, compute the closure, *X*:sup:`+` in *R*. For every attribute *a* of *R1* that is in the closure of *X*, by the splitting rule, :math:`X \rightarrow \{a\}` is an FD for *R1*. If *X*:sup:`+` contains every attribute of *R1*, then *X* is a superkey of *R1*.

.. [#] As it happens, Alice Munro won two Giller Prizes, in different years; if we included an attribute for year, we would have to double the number of entries for Alice Munro!

|license-notice|



## Chapter: sql-vs-theory.rst

.. _sql-vs-theory-chapter:

================================================
Differences between SQL and the relational model
================================================

The relational model of the database inspires and informs relational database systems.  However, the model differs from the actual implementation of most such systems.  The structured query language (SQL, covered in :numref:`Part {number} <sql-part>`) largely dictates the behavior of relational database systems, and therefore we frame this chapter as a comparison between SQL and the relational model.  This chapter is intended as a practical guide to these differences for students who have learned the relational model and must now learn SQL, or users of SQL learning the relational model.

Relations as sets
:::::::::::::::::

A key difference between SQL and the relational model regards the treatment of duplicate tuples in a relation.  Since relations are sets, in the model there can be no notion of "duplicate" tuples.  A tuple either is or is not in the relation, without multiplicity.  By contrast, SQL permits duplicates.  A SQL relation (or *table*) may contain multiple identical tuples (or *rows*) if it is not constrained with a primary key - we say that SQL relations are *multisets* rather than sets.  SQL queries may also return duplicate rows, for example, if a query asks for some subset of attributes (a projection) from a relation or a join of relations.

Duplicate tuples can be the source of serious errors if care is not taken.  As an example, consider a hypothetical database with the following relations: the first relation lists employees of a company with attributes including employee salary, the second lists projects in the company, while the third relation connects the first two relations in a many-to-many relationship.  Assuming that the primary key for the employee table is **employee_id** and the primary key for the project table is **project_id**, then the third relation contains only the attributes named **project_id** and **employee_id**, which are foreign keys on the attributes of the same name in the first two tables.  The existence of a tuple in this relation indicates that a particular employee works on a particular project.

Now, consider a query asking for the total employee salary costs to the company for a list of projects.  One approach to this problem using relational algebra or SQL involves a simple join of the three tables followed by projection onto the employee id and salary attributes.  The final answer is obtained by summing the salaries of the employees.  Using relational algebra, this produces the correct result, because each employee engaged in any of the projects of interest is listed only once.  Using SQL, however, the sum is incorrect if any employees work on more than one of the projects of interest, because those employees will be listed more than once in the join result.

There are, of course, multiple solutions to the hypothetical problem described above.  If the SQL query is restructured to use subqueries (using **IN**) instead of a join, or if the cross-reference relation is redesigned to include, say, a percentage of effort for an employee attributable to a particular project, then a more accurate result can occur.  However, this requires some effort on the designers and programmers of the SQL database to prevent a result that cannot happen using relational algebra.  The counter argument is that care must also be taken when applying relational algebra; suppose the join result is projected solely onto the employee salary attribute, which is, after all, the only value we need to sum.  In this case, we will obtain an incorrect result if two employees have the same salary!

The choice to permit duplicate tuples in query results is perhaps based on practical performance considerations.  To ensure uniqueness in a query result (e.g., when using the SQL **DISTINCT** operator), database systems typically sort or index the result, which adds cost to the operation.  If a query has a very large result (not uncommon in the modern era of "big data") the cost may become prohibitive.  While there are situations which permit the database engine to utilize indexes already available on the original tables involved in a query in order to produce a unique result efficiently, this is not possible for all queries in the general case. (One can posit that, had early database designers chosen to enforce uniqueness, technology and practical use would have evolved to largely erase these concerns; however, performance was a serious concern for the early relational databases in competition with more mature non-relational systems.)

Tuples and attributes
:::::::::::::::::::::

SQL also differs from the relational model regarding some aspects of tuples (or rows).  In the relational model, tuples are composed of values which are each associated with a specific named attribute and which are members of the domain of values for the attribute.  Tuples in the model may sometimes be treated as ordered lists of values, but only with the implicit understanding that each value is associated with an attribute as defined in some relation schema.  Finally, attribute names within a tuple must be unique.

In SQL, rows are treated somewhat more flexibly.  Rows stored in a relation (or table) generally conform to the above requirements on tuples.  However, rows returned from a query may not have well defined attributes associated with each value.  Where the query returns column values from some table, the values can be considered to be associated with a well defined attribute, following the definition of the original table.  SQL also permits queries to return values that are the results of operations or functions invoked on values; in most SQL database systems, those values will at least have an associated type, such as "integer" or "character string".  However, unless the query specifically provides a name for each such value, the database system may choose to provide a generic name or no name at all.  These anonymous values can be identified solely by their position in the row.  In some SQL systems, it is also possible to have multiple values associated with the same name.

These differences may not present serious difficulties in usual practice.  However, there is a sense in which such values lack the context necessary to give them meaning, and it is therefore possible to contrive scenarios in which problems arise.  For example, consider a company which awards bonuses as well as pay raises to its employees at the end of each year based on some complex mathematical formulas.  A SQL query may be used to calculate both values.  It would take only a momentary distraction for a developer programming the company's accounting software to reverse the intended application of each number if each number is identified solely by its columnar position within the returned rows.

Logical confusions
::::::::::::::::::

While not specifically a conflict between the relational model and SQL, SQL's implementation of three-valued logic using NULL can lead to some puzzling situations.  One of the more cited issues relates to *tautological* expressions - expressions which are logically always true.  For example, assuming some integer variable *x*, in the absence of NULL, the statement that "*x* is less than 17 or *x* is greater than or equal to 17" must be true.

However, if NULL is permitted and *x* is NULL, then comparing *x* to 17 using three-valued logic gives us the result *unknown*.  In SQL, the **OR** of two unknown values yields another unknown, rather than the expected true.  This outcome is partially a result of practical limitations; asking the SQL interpreter to reason about arbitrary logical expressions in order to reveal tautologies would impact the speed with which queries can be answered.  If our logical expectation is that the expression must be true in the relational model, then this represents a difference between SQL and the relational model.

It can be argued, though, that this is really a problem in how we assign meaning to NULL.  NULL may mean that *x* is some integer, but we do not know which integer it is.  However, NULL is also used for other meanings, such as that *x* is *not applicable*.  Consider a relation storing data on the inhabitants of some country where the relation includes an attribute for the person's passport number.  If a person never travels outside the country, they may not have a passport, and the passport number attribute has no meaning for the person.  In this case it is difficult to argue that an expression such as "the first digit of the person's passport number is less than 5 OR the first digit is greater than or equal to 5" should evaluate to true.

As an even simpler example of a problem with tautology, consider the SQL query below, which returns no rows in which NULL is assigned to the column *x*:

::

    SELECT * FROM some_table WHERE x = x;

The inclusion of NULL in the relational model is controversial at least in part due to confusions of this type.


|chapter-end|

|license-notice|



## Chapter: index.rst

.. _relational-theory-part:

==========================
RELATIONAL DATABASE THEORY
==========================

Part 3 of this book explains the mathematical and theoretical foundations of relational database technology.  The diagram below shows the strong dependencies between chapters.  The first three chapters need to be read in order; however, chapter 3.3 on database normalization should be accessible for students who have a strong foundation in relational databases through the lens of SQL (:numref:`Part {number} <sql-part>` of the text) even without the preceding chapters on the relational model.  Readers of chapter 3.4 will benefit from some exposure to SQL as well, although that is not a prerequisite.

.. figure:: chapter_dependencies.svg

    Chapter dependency graph for Part 3

.. toctree::
    :maxdepth: 3

    01-relational-model/relational-model
    02-relational-algebra/relational-algebra
    03-normalization/normalization
    04-sql-vs-theory/sql-vs-theory


|license-notice|



## Chapter: index.rst

==========================
PROGRAMMING WITH DATABASES
==========================

- basics, with examples in Python
- basics, with examples in Java
- Javascript? Others?
- SQL injection, with examples in Python
- SQL injection, with examples in Java
- ORMs
- web programming and CRUD APIs?
- would be great to cover e.g. graphql

.. toctree::
    :maxdepth: 3

..    01-introduction/introduction

|license-notice|



## Chapter: history.rst

.. _history-chapter:

===================================
A brief history of database systems
===================================

Prior to the invention of the hard drive in the 1950's, collections of data intended for computer processing were stored on media such as paper tape, paper punch cards, and magnetic tape.  These media allowed *sequential access* to data; data input started from the beginning of the collection and proceeded linearly through.  In general, processing proceeded by first reading a large amount of data into a computer's main memory, where it could be accessed and manipulated efficiently.  Processed data could then be stored on similar media for future use.

In contrast, a modern storage device such as a hard drive or solid-state drive allows for *random access*; the computer can quickly move to an arbitrary location in a data store without having to read through all of the data in earlier locations.  If data is carefully organized on a random access medium, it becomes possible to efficiently access or modify individual pieces of data on demand.

Early software applications used this approach to create organized data stores that were application-specific; the data store could only be understood or managed by the specific software application.  If it became necessary to modify the structure of the data (for instance, by storing new attributes for every piece of data), the software would have to be rewritten, and the existing data store would have to be converted to the new structure.


A brief history
:::::::::::::::

The first commercial database systems appeared in the 1960's, not long after the commercial introduction of hard disk drive storage.  These early database systems allowed software developers to organize data in structures similar to trees or graphs.  Individual pieces of data were stored in fixed-size *records*, which were often direct mappings of a software application's data structures in memory.  Connections between records were also stored in the database, often using references which could be directly translated to addresses on the storage device, allowing for fast navigation between related pieces of information.  These *navigational* databases were very successful, and their successors are still sold today.

Navigational databases had certain drawbacks in interfacing with software application code.  In particular, navigational databases coupled program code to the structures stored in the database.  Changes to the database could require extensive changes to program code.  Changes in the needs of the software could require the addition of more structures to the database, leading to an accumulation of structures to be maintained over time.

Edgar F. Codd, a computer scientist working for computer company IBM, is credited [#]_ with proposing a new database model based on mathematical set theory, the relational model.  The new approach eliminates many (although not all) of the dependencies coupling application code to the structure of the database.  Some of the structures built into navigational databases (those storing connections between records) are no longer needed, while others (such as indexes) are effectively hidden from application code.  Data queries can be expressed in a simple and consistent fashion using mathematical operations.  The relational model thus raises the level of abstraction in interfacing application code with the database system.

Codd shared his relational model internally at IBM, and then publicly in :ref:`a paper <relational-theory-references>` in 1970.  Codd and other authors further developed the relational model in subsequent papers and books.  The first relational database systems based on Codd's work appeared in the mid-to-late 1970's.  Relational database systems came into heavy use in subsequent decades.  While it is difficult to measure the prevalence of relational databases relative to other types in use today, the relational model remains hugely influential and important.

Relational model beginnings
:::::::::::::::::::::::::::

The first commercial database systems appeared in the 1960's, not long after the commercial introduction of hard disk drive storage.  These early database systems allowed software developers to organize data in structures similar to trees or graphs.  Individual pieces of data were stored in fixed-size *records*, which were often direct mappings of a software application's data structures in memory.  Connections between records were also stored in the database, often using references which could be directly translated to addresses on the storage device, allowing for fast navigation between related pieces of information.  These *navigational* databases were very successful, and their successors are still sold today.

Edgar F. Codd, a computer scientist working for computer company IBM, is credited [#]_ with proposing a new database model based on mathematical set theory.  This new approach differs from navigational database systems in that links between records are not explicitly stored in the database.  Rather than following predetermined access paths provided by the database designer, relational database users and application code are free to write arbitrary queries that translate to simple mathematical operations on sets of records.  Responsibility for determining proper and efficient execution largely shifts from application code to the database system itself.  The result is a higher level of abstraction in the interface to the database compared to earlier database systems.

Codd shared his relational model internally at IBM, and then publicly in :ref:`a paper <relational-theory-references>` in 1970.  Codd and other authors further developed the relational model in subsequent papers and books.  The first database systems based on Codd's work appeared in the mid-to-late 1970's.  While it is difficult to measure the prevalence of relational databases relative to other types in use today, the relational model remains hugely influential and important.

For more on the history of database systems, see :numref:`Chapter {number} <history-chapter>`.

|chapter-end|

----

**Notes**

.. [#] :ref:`An earlier paper by David L. Childs <relational-theory-references>` in 1968 on the application of set theory to data systems is a precursor cited by Codd.  However, it was Codd's 1970 paper that became widely circulated and influential in later work on the relational model, and in the creation of early relational database systems such as System R from IBM and the INGRES database developed at the University of California, Berkeley.

.. [#] :ref:`An earlier paper by David L. Childs <relational-theory-references>` in 1968 on the application of set theory to data systems is a precursor cited by Codd.  However, it was Codd's 1970 paper that became widely circulated and influential in later work on the relational model, and in the creation of early relational database systems such as System R from IBM and the INGRES database developed at the University of California, Berkeley.

|license-notice|



## Chapter: index.rst

===============
SELECTED TOPICS
===============

- transactions
- workloads and applications, OLTP and OLAP
- workflow
- B-trees
- query processing and query performance tuning
- NoSQL
- NewSQL
- big data?

.. toctree::
    :maxdepth: 3

..    01-introduction/introduction


|license-notice|



## Chapter: datasets.rst

.. _appendix-a:

==============================================
Appendix A: Example datasets used in this book
==============================================

This appendix contains descriptions of the tables in the textbook database as well as SQL scripts and data files that can be used to recreate the book's database in other database systems.

.. contents:: Quick links
   :local:
   :depth: 2
   :backlinks: none

Dataset descriptions
::::::::::::::::::::

In this section we provide descriptions of each dataset or group of related tables.  The tables are described in detail in tabular format. Entity-relationship diagrams (ERDs) and logical models using crow's foot notation (as described in :numref:`Part {number} <data-modeling-part>`) are also provided for some datasets.  Finally, each dataset section contains an interactive query tool set up to retrieve the data from all of the tables in the dataset (note that the interactive query tool limits results to 100 rows, and some tables have more than that number of rows).

The simple books dataset
------------------------

The simple books dataset consists of the tables **simple_books** and **simple_authors**.  The **simple_books** table contains data about 12 books, each by a different author, while the **simple_authors** table contains data on each of the 12 authors appearing in **simple_books**.

This dataset is used in the early chapters of :numref:`Part {number} <sql-part>` of the text to introduce SQL, and is not intended as an example of good database design.  The rows in **simple_books** are implicitly identified by unique book titles, and the rows in **simple_authors** are implicitly identified by author names, but neither table has a primary key.  Similarly, the rows in **simple_books** are in one-to-one correspondence with the rows in **simple_authors**, however, there is no explicit relationship between the tables via a foreign key constraint.

.. container:: data-dictionary

    The **simple_books** table records works of fiction, non-fiction, poetry, etc. by a single author.

    ================ ================= ===================================
    column           type              description
    ================ ================= ===================================
    author           character string  the book's author
    title            character string  the book's title
    publication_year integer           year the book was first published
    genre            character string  a genre describing the book
    ================ ================= ===================================

.. container:: data-dictionary

    The **simple_authors** table records persons who have authored books.

    ========== ================= ===================================
    column     type              description
    ========== ================= ===================================
    name       character string  full name of the author
    birth      date              birth date of the author, if known
    death      date              death date of the author, if known
    ========== ================= ===================================

Use the query tool below to view the data.

.. activecode:: appendix_a_simple_books_dataset
    :language: sql
    :dburl: /_static/textbook.sqlite3

    SELECT * FROM simple_books;
    SELECT * FROM simple_authors;

To see the **CREATE TABLE** code for a table, you can use the query tool above to query the **sqlite_master** table, e.g.:

::

        SELECT sql FROM sqlite_master WHERE name = 'simple_books';


The expanded books dataset
--------------------------

The expanded books dataset includes information on 200 books (in the **books** table) and their authors (76 authors in total in the **authors** table).  An **awards** table lists some major awards given to authors for their body of work or for specific books.  Two cross-reference tables associate authors with their awards (**authors_awards**) and specific books with their awards (**books_awards**).  Finally, the **editions** table contains publication data related to just four books by author J.R.R. Tolkien.  (Only four books were included to reduce the size of the database file, which must be downloaded and held in the web browser's memory.)  The publication data is particularly "dirty" in the sense that it contains numerous inaccuracies, omissions, and redundancies; see the section title `Data collection notes`_, below.

This dataset is introduced in :numref:`Chapter {number} <joins-chapter>` and is used throughout much of the rest of :numref:`Part {number} <sql-part>` of the text.  While the dataset represents a highly simplified model of books (e.g., books are assumed to always have a single author), the schema attempts to emulate best practices in database design while illustrating fundamental SQL database concepts.  The design makes use of primary key constraints (using synthetic unique identifiers), foreign key constraints, and cross-reference tables implementing many-to-many relationships.

We provide below detailed descriptions of each table in the dataset, an entity-relationship diagram (ERD) modeling the data, and a logical model in crow's foot notation showing the tables and their relationships.

.. container:: data-dictionary

    The **authors** table records persons who have authored books.  Every author corresponds to at least one book in the database.

    ========== ================= ===================================
    column     type              description
    ========== ================= ===================================
    author_id  integer           unique identifier for the author
    name       character string  full name of the author
    birth      date              birth date of the author, if known
    death      date              death date of the author, if known
    ========== ================= ===================================

.. container:: data-dictionary

    The **books** table records works of fiction, non-fiction, poetry, etc. by a single author.  Each book corresponds to a single author from the **authors** table, and may correspond to many editions of the book listed in the **editions** table.

    ================ ================= =================================================
    column           type              description
    ================ ================= =================================================
    book_id          integer           unique identifier for the book
    author_id        integer           author_id of book's author from **authors** table
    title            character string  the book's title
    publication_year integer           year the book was first published
    ================ ================= =================================================

.. container:: data-dictionary

    The **editions** table records specific publications of a book.  Each edition corresponds to a single book from the **books** table.  For space reasons, the **editions** table only includes data on four books by J.R.R. Tolkien.

    ================== ================= ====================================================================
    column             type              description
    ================== ================= ====================================================================
    edition_id         integer           unique identifier for the edition
    book_id            integer           book_id of the book (from **books** table) published as this edition
    publication_year   integer           year this edition was published
    publisher          character string  name of the publisher
    publisher_location character string  city or other location(s) where the publisher is located
    title              character string  title this edition was published under
    pages              integer           number of pages in this edition
    isbn10             character string  10-digit international standard book number
    isbn13             character string  13-digit international standard book number
    ================== ================= ====================================================================

.. container:: data-dictionary

    The **awards** table records various author and/or book awards.

    ========= ================= =========================================
    column    type              description
    ========= ================= =========================================
    award_id  integer           unique identifier for the award
    name      character string  name of the award
    sponsor   character string  name of the organization giving the award
    criteria  character string  what the award is given for
    ========= ================= =========================================

.. container:: data-dictionary

    The **authors_awards** table is a *cross-reference* table (explained in :numref:`Chapter {number} <joins-chapter>`) relating **authors** and **awards**; each entry in the table records the giving of an award to an author (not for any particular book) in a particular year.

    =========== =========== ===========================================
    column      type        description
    =========== =========== ===========================================
    author_id   integer     author_id of the author receiving the award
    award_id    integer     award_id of the award received
    year        integer     year the award was given
    =========== =========== ===========================================

.. container:: data-dictionary

    The **books_awards** table is a cross-reference table relating **books** and **awards**; each entry in the table records the giving of an award to an author for a specific book in a particular year.

    =========== =========== =================================================
    column      type        description
    =========== =========== =================================================
    book_id     integer     book_id of the book for which the award was given
    award_id    integer     award_id of the award given
    year        integer     year the award was given
    =========== =========== =================================================

Here is the data model for the expanded books dataset, as an ERD:

.. image:: books_ERD.svg
    :alt: A data model of the books dataset given as an entity-relationship diagram.

A logical model of the expanded books dataset is shown below.  In this crow's foot diagram, primary keys are shown underlined and in boldface, while foreign keys are italicized.

.. image:: books_logical.svg
    :alt: A crow's foot diagram showing the logical model of the books dataset.

Use the query tool below to view the expanded books data.  Note that the query tool limits results to 100 rows, but the **books** and **editions** tables have more than 100 rows each.

.. activecode:: appendix_a_expanded_books_dataset
    :language: sql
    :dburl: /_static/textbook.sqlite3

    SELECT * FROM authors;
    SELECT * FROM books;
    SELECT * FROM editions;
    SELECT * FROM awards;
    SELECT * FROM authors_awards;
    SELECT * FROM books_awards;

The bookstore dataset
---------------------

The bookstore dataset consists of the tables **bookstore_inventory** and **bookstore_sales**.  These tables simulate a very simple database that a seller of used books might use.  The **bookstore_inventory** table represents books that the bookseller is selling.  The table actually includes some books that have already been sold - when a book is sold, an entry is added to the companion table, **bookstore_sales**.  The bookseller thus has to look at both tables to determine which books are actually available to be sold.  The bookseller may choose to periodically remove old records from the tables.

While students should feel free to modify any data within the textbook database (secure in the knowledge that any changes will be reverted when they reload the page in their browser), the bookstore dataset was specifically designed with data modification in mind.  To avoid complications in introducing data modification queries, there are no foreign key constraints on the tables.  However, the tables as provided have a one-to-one relationship: each record in **bookstore_sales** matches exactly record in **bookstore_inventory**, while each record in **bookstore_inventory** matches at most one record in **bookstore_sales**.

This dataset is used briefly to illustrate one-to-one relationships in :numref:`Chapter {number} <joins-chapter>`.  In :numref:`Chapter {number} <data-modification-chapter>`, the tables are used to demonstrate data modification queries.  The tables are used in examples of grouping and aggregation in :numref:`Chapter {number} <grouping-chapter>`.

.. container:: data-dictionary

    The **bookstore_inventory** table contains information on new and used books for sale.

    ============= ================= ==================================================
    column        type              description
    ============= ================= ==================================================
    stock_number  integer           unique key identifying a particular copy of a book
    author        character string  the author of the book
    title         character string  the title of the book
    condition     character string  the condition of the book (new, good, fair, etc.)
    price         fixed-point       the price of the book, in some unit of currency
    ============= ================= ==================================================

.. container:: data-dictionary

    The **bookstore_sales** table gives information about the sales of books from **bookstore_inventory**.

    =============== ================= =================================================================
    column          type              description
    =============== ================= =================================================================
    receipt_number  integer           unique key identifying this sale
    stock_number    integer           key of the book copy (from **bookstore_inventory**) that was sold
    date_sold       date              the date on which the books was sold
    payment         character string  the method of payment used in the sale (case, credit card, etc.)
    =============== ================= =================================================================

Use the query tool below to view the data.

.. activecode:: appendix_a_bookstore_dataset
    :language: sql
    :dburl: /_static/textbook.sqlite3

    SELECT * FROM bookstore_inventory;
    SELECT * FROM bookstore_sales;

Other tables in the database
----------------------------

In addition to the above, the database contains some very small tables which are used to illustrate various points in the text: **fruit_stand**, **s**, **s2**, **s3**, **t**, **t2**, and **t3**.  As these tables are give in full in the text, we do not further explain them here.  However, you can use the interactive query tool below to view the data.

.. activecode:: appendix_a_miscellaneous_tables
    :language: sql
    :dburl: /_static/textbook.sqlite3

    SELECT * FROM fruit_stand;
    SELECT * FROM s;
    SELECT * FROM s2;
    SELECT * FROM s3;
    SELECT * FROM t;
    SELECT * FROM t2;
    SELECT * FROM t3;

Data collection notes
:::::::::::::::::::::

The selection of books in the simple and expanded books datasets was driven by several interests.  First, the textbook's author is a fan of science fiction and fantasy - these genres are thus perhaps overrepresented in the dataset.  Second, an attempt was made to include a diverse set of authors, in hopes of providing some common points of reference for students everywhere.  (There is nevertheless a strong bias towards English-language literature, reflecting the context of the textbook's author.) Lastly, the selection favored books by authors who have received literary awards.  To keep things manageable, the number of books was capped at 200.

Authors were handpicked, based on the textbook author's knowledge and on internet searches of major literary awards. `Wikipedia`_ was extremely helpful in collecting data such as authors' birth and death dates.  (Note that the dataset was finalized in 2022; it is very possible that some authors in the dataset have died since the data was entered.  This inaccuracy is regrettable but unavoidable under the circumstances.)

Some authors are represented by a single work (typically an award winning or at least widely acclaimed book), while in other cases many books by the author were included.  There was no consistent decision process used to decide how many books to include by each author.  Many choices were made in support of specific examples in the text.  Most of the data regarding individual books was hand collected from Wikipedia and other freely available sources on the internet.  Some publication year values were extracted from the freely available `Open Library`_ dataset.

Data on author and book awards was hand collected from Wikipedia and the websites representing the awards.  Data on the many editions of works comes entirely from the Open Library.

To the best of the author's knowledge, all of the data in the simple and expanded books datasets is in the public domain.

The bookstore dataset uses books from the expanded books dataset, but is otherwise entirely fabricated, as are the fruit stand and other abstract example tables.


.. _`Wikipedia`: https://www.wikipedia.org/
.. _`Open Library`: https://openlibrary.org/

Getting the data
::::::::::::::::

:numref:`Part {number} <sql-part>` of this book includes interactive elements allowing the reader to work directly with a relational database.  This functionality lets students immediately try example code on a real database system.  As the database available on each page is actually a copy (in memory) of a fixed database, changes to the database do not persist over time - refreshing the browser window will return the database to the same initial state each time.  This is useful in that students can safely experiment with destructive SQL commands, knowing that no changes are permanent.  On the other hand, it means that students cannot use the system for longer term projects.

The database system used in this textbook is `SQLite`_.  While SQLite is a powerful and popular relational database system, it lacks some features of the client-server database systems commonly used in industry.  It also differs in significant ways from the SQL standard (notably with its use of dynamic typing).

.. _`SQLite`: https://www.sqlite.org/

For these reasons, users of this textbook may wish to set up their own database system.  Many different database systems are available, each with their own system requirements and installation procedures.  There are likewise many ways to access and query each database system.  Instructions for setting up and accessing different systems are therefore out of the scope of this textbook.  However, in the interest of providing a transition from the textbook's database to the users' systems of choice, we provide scripts and data files below, which can be used to recreate the book's database on the database system of your choice.

SQLite
------

The `SQLite`_ database engine is unique (in the set of systems supported by this textbook) in that it works with databases stored entirely in a single file.  SQLite databases can be shared by simply copying the files containing them.  We provide below the database file used by this textbook.  Additionally, we provide a SQL script (a text file in UTF-8 Unicode format) with the SQL commands necessary to re-create the database from scratch.  Use the former if you simply want a copy of the textbook's database for your own use; use the latter if you want to create the textbook's database tables within an existing SQLite database.  The SQL script contains only **CREATE TABLE** and **INSERT** statements, and therefore should not replace existing tables within the database.

- :download:`textbook.sqlite3`, the textbook's SQLite database file
- :download:`sqlite.sql`, the SQL script

This SQL script was verified to work correctly using version 3.39.2 of the ``sqlite3.exe`` program on Windows 10 and with version 3.31.1 of the ``sqlite3`` program running on linux (Linux Mint 20.3 with kernel version 5.15.0-41).

PostgreSQL
----------

The SQL script below can be used to create the equivalent of the textbook's tables in a `PostgreSQL`_ database.  The SQL script contains only **CREATE TABLE** and **INSERT** statements, and therefore should not replace existing tables within the database.

.. _`PostgreSQL`: https://www.postgresql.org/

- :download:`postgresql.sql`

This SQL script was verified to work correctly using version 12.5 of the ``psql.exe`` program on Windows 10 and with version 12.11 of the ``psql`` program running on linux (Linux Mint 20.3 with kernel version 5.15.0-41), loading into a PostgreSQL version 12.8 instance running on linux (Linux Mint 20 with kernel version 5.4.0-86).  Note: on Windows 10, you may need to first issue the command ``\encoding utf8`` (at the ``psql`` command line) before loading or querying the data.  This setting may not be sufficient to ensure all characters can be viewed correctly when returned by a query, but the data can be loaded correctly.

Notable differences from the textbook:

- As described in the text, SQLite does not use a standard SQL approach to automatically generate sequential ID values.  The **AUTOINCREMENT** option used in the SQLite database (in **bookstore_sales** and **bookstore_inventory**) is not available in PostgreSQL, but the standard SQL **GENERATED BY DEFAULT AS IDENTITY** option is.  Accordingly, the PostgreSQL script uses the standard approach.  The two options behave slightly differently.

MySQL
-----

The SQL script below can be used to create the equivalent of the textbook's tables in a `MySQL`_ database.  The SQL script contains only **CREATE TABLE** and **INSERT** statements, and therefore should not replace existing tables within the database.

.. _`MySQL`: https://www.mysql.com/

- :download:`mysql.sql`

This SQL script was verified to work correctly using version 8.0.29 of the MySQL Shell (``mysqlsh.exe``) program on Windows 10 and with version 8.0.29 of the ``mysql`` program running on linux (Linux Mint 20.3 with kernel version 5.15.0-41), loading into a MySQL version 8.0.26 instance running on linux (Linux Mint 20 with kernel version 5.4.0-86).

Notable differences from the textbook:

- The **bookstore_sales** table in the textbook database has a **DEFAULT** clause to set the **date_sold** column to the current date when no value is provided for the column.  MySQL does not permit default setting for columns of type **DATE**, but does allow it for the **TIMESTAMP** type.  Accordingly, the **date_sold** column in the MySQL script is of type **TIMESTAMP** (and thus includes time as well as date).
- The MySQL **AUTO_INCREMENT** option is very similar to the **AUTOINCREMENT** option in SQLite (used in **bookstore_sales** and **bookstore_inventory**), but may have slightly different behavior.
- The **bookstore_inventory** table contains a column named **condition**.  This is a reserved keyword in MySQL, which means that queries such as "SELECT DISTINCT condition FROM bookstore_inventory" will fail unless you put backticks around the word "condition".  (The backtick character looks like an apostrophe, but slanting in the opposite direction.)

Oracle
------

The SQL script below can be used to create the equivalent of the textbook's tables in an Oracle database.  The SQL script contains only **CREATE TABLE** and **INSERT** statements and statements setting temporary session variables, and therefore should not replace existing tables within the database.

- :download:`oracle.sql`

This SQL script was verified to work correctly using Oracle's SQLcl utility (release 22.2) running on linux (Linux Mint 20.3 with kernel version 5.15.0-41) with OpenJDK version 11.0.15, loading into an Oracle Database XE 18c instance running on linux (openSUSE Leap 15.2 with kernel version 5.3.18).  On Windows 10 with SQLcl (release 22.2), the script ran without reporting errors, but some character values were loaded incorrectly.  Note: if you run this script with SQLcl or SQL\*Plus, you *must* uncomment the command ``SET DEFINE OFF`` at the top of the script.  Otherwise, the program will interpret any \& characters to imply a variable substitution sequence, which will halt the script and prevent the data from loading correctly.

Notable differences from the textbook:

- As described in the text, SQLite does not use a standard SQL approach to automatically generate sequential ID values.  The **AUTOINCREMENT** option used in the SQLite database (in **bookstore_sales** and **bookstore_inventory**) is not available in Oracle, but the standard SQL **GENERATED BY DEFAULT AS IDENTITY** option is.  Accordingly, the Oracle script uses the standard approach.  The two options behave slightly differently.

SQL Server
----------

The SQL script below can be used to create the equivalent of the textbook's tables in a Microsoft SQL Server database.  The SQL script primarily contains **CREATE TABLE** and **INSERT** statements, and should not replace existing tables within the database.  The **USE** statement at the top of the script assumes that data will be loaded into an existing database named "textbook".  This statement is needed for use with the ``sqlcmd`` utility and possibly other software, and should be edited to indicate the correct database as needed.  The statement may not be needed in other client software programs.

- :download:`sqlserver.sql`

This SQL script was verified to work correctly using the ``sqlcmd`` program (version 17.10.0001.1) running on linux (Linux Mint 20.3 with kernel version 5.15.0-41), loading into a SQL Server 2019 instance running on linux (Linux Mint 20 with kernel version 5.4.0-86).  On Windows 10 with version 15.0.2000.5 of ``sqlcmd.exe``, the script ran without reporting errors, but some character values were loaded incorrectly.  Note that a collation supporting UTF8 must be used (this can be set on the database using an **ALTER DATABASE** statement); the test system used the "Latin1_General_100_CI_AS_SC_UTF8" collation.

Notable differences from the textbook:

- SQL Server generates sequential integer values for columns with the **IDENTITY** property, which differs in behavior compared to both the standard SQL **GENERATED BY...** and SQLite's **AUTO_INCREMENT**.

Raw data files
--------------

If you wish to use a database other than one of those listed above, you can likely adapt one of the above scripts for use with your database, using the find/replace function of a text editor and some trial and error.  Alternatively, you may create the desired tables manually, and load the data from the data files in the zip archive linked below - most database systems provide mechanisms to load data from formatted files.  The data files are in comma-separated value (CSV) format, and are encoded in UTF-8.  Each file includes a header row with labels matching the column names from the textbook database.  If your database system does not support this file format, you may be able to open the files with a spreadsheet program and then export a format that is supported by your system.

- :download:`practical_db_data_files.zip`


----

|license-notice|



## Chapter: reference.rst

.. _appendix-b:

=========================
Appendix B: SQL Reference
=========================

This appendix contains documentation on various aspects of the SQL standard (2016).  This is not an exhaustive guide to the standard.  Where possible, variations from the standard by various database implementations (SQLite, PostgreSQL, MySQL, Oracle, Microsoft SQL Server) are shown.  Note that documentation of this sort is a moving target, so the information below may be out-of-date when you read it.  Consult your database vendor's documentation for current information.

In the documentation below, options may be indicated using square brackets.  For example, usage of the **SUBSTRING** function is documented as

::

    SUBSTRING(*s* FROM *start* [FOR *length*])

meaning both of the following expressions are valid:

::

    SUBSTRING('hello, world' FROM 1 FOR 5)
    SUBSTRING('hello, world' FROM 8)

(The first expression evaluates to ``'hello'``, and the second to ``'world'``.)

.. _appendix-b-data-types:

Data types
::::::::::

.. _appendix-b-number-types:

Number types
------------

The SQL standard provides for both exact (integers and fixed-precision decimal) and inexact (floating point) numbers.  Details of these types (e.g., the number of bits used in the number representation) are left up to individual implementations, so consult your database's documentation to fully understand its capabilities.

Integers
########

SQL defines three integer types: **INTEGER**, **SMALLINT**, and **BIGINT**.  Implementations of these types vary, but it is not uncommon for **INTEGER** (often abbreviated as **INT**) to store 32-bit integers, **SMALLINT** 16-bit integers, and **BIGINT** 64-bit integers.  Not all databases recognize all of these types, but **INTEGER** is recognized by all of the databases considered for this book.  Additional integer types may be available for your database system.

Exact decimal numbers
#####################

Decimal number types allow for exact storage of numbers that have digits to the right of the decimal point, e.g., 1234.56789.  These numbers are exact (compare to the floating point types below), and permit exact mathematical operations where possible (addition, subtraction, and multiplication).  The two defined types for SQL are **NUMERIC** and **DECIMAL**, which are synonyms of each other.  These types may be defined with parameters representing *precision* and *scale*, where precision is the number of significant digits that can be stored, and scale is the number of digits following the decimal point.  If the precision is given, but not the scale, the scale defaults to zero.

For example, in most implementations:

- **NUMERIC(3, 2)** defines a type that can store the values between -999.99 and 999.99, with a maximum of 2 digits past the decimal point.
- **NUMERIC(4)** defines a type that can store integers between -9999 and 9999.
- **NUMERIC** defines a type that can exactly store decimal values with implementation-defined precision and scale.

Different implementations behave differently when an attempt is made to store values with more digits than are allowed by the specified precision and scale.  This may result in an error, or (in the case of too many digits to the right of the decimal point), it may result in rounding or truncation of the value.

Floating point numbers
######################

Floating point number types allow for (possibly inexact) storage of real numbers, similar (or sometimes identical to) the `IEEE 754`_ specification.  The SQL standard defines the types **FLOAT**, **REAL**, and **DOUBLE PRECISION** (often abbreviated **DOUBLE**), but implementation of these types vary.

.. _`IEEE 754`: https://en.wikipedia.org/wiki/IEEE_754

Database support for number types
#################################

A summary of database support for number types is shown below (for the five databases this textbook attempts to cover):

================  ===================== ============================== ======== ================================== ================
Type              SQLite                PostgreSQL                     MySQL    Oracle                             SQL Server
================  ===================== ============================== ======== ================================== ================
INTEGER           yes                   yes                            yes      use NUMBER                         yes
SMALLINT          equivalent to INTEGER yes                            yes      use NUMBER                         yes
BIGINT            equivalent to INTEGER yes                            yes      use NUMBER                         yes
NUMERIC/DECIMAL   yes                   yes                            yes      use NUMBER                         yes
FLOAT             equivalent to REAL    equivalent to DOUBLE PRECISION yes      yes; but BINARY_DOUBLE recommended yes
REAL              yes                   yes                            yes      yes; but BINARY_DOUBLE recommended yes
DOUBLE PRECISION  equivalent to REAL    yes                            yes      yes; but BINARY_DOUBLE recommended use FLOAT
================  ===================== ============================== ======== ================================== ================


.. _appendix-b-string-types:

Character string types
----------------------

There are three main data types for storing character data in SQL.  Officially, these are named **CHARACTER**, **CHARACTER VARYING**, and **CHARACTER LARGE OBJECT**.  In addition, the modifier **NATIONAL** may be used to indicate strings containing data from locale-dependent character sets.  These names are fairly long and clunky, so databases typically use abbreviations or even completely different names for the same concepts.

The type **CHARACTER**, usually abbreviated as **CHAR**, is used for fixed-length strings.  The type **CHAR** is followed by parentheses enclosing the length of the string.  All values in a column of type **CHAR(4)**, for example, must contain exactly 4 characters.  In practice, many databases relax the "exactly" part of the definition and allow for shorter strings to be stored, although they may "pad" the value with trailing space characters.  Attempting to store strings longer than *n* usually results in an error.

**CHARACTER VARYING** is usually abbreviated as **VARCHAR**, and is used for strings of varying length up to some maximum, which must be specified just as with the **CHAR** type.  It is usually an error to attempt to store strings longer than the maximum.

**CHARACTER LARGE OBJECT** goes by many names, and is used to store strings of arbitrary length, up to some implementation-defined maximum (for example, Oracle's **CLOB** type allows strings of up to 128TB in some cases).  In many implementations, this type is limited in the operations or functions that may be used, and may not allow indexing.

A summary of database support for character strings is shown below:

=======================  ===================== ========== ======== =============== ================
Type                     SQLite                PostgreSQL MySQL    Oracle          SQL Server
=======================  ===================== ========== ======== =============== ================
CHARACTER(n)             equivalent to TEXT    yes        yes      yes             yes
CHARACTER VARYING(n)     equivalent to TEXT    yes        yes      use VARCHAR2(n) yes
CHARACTER LARGE OBJECT   equivalent to TEXT    use TEXT   use TEXT use CLOB        use VARCHAR(MAX)
=======================  ===================== ========== ======== =============== ================


.. _appendix-b-datetime-types:

Date and time types
-------------------

The SQL standard defines three or five principal types, depending on how you count.  The types are **DATE**, **TIME** (with or without time zone), and **TIMESTAMP** (with or without time zone).  If you specify simply **TIME** or **TIMESTAMP**, you get the version without time zones; append **WITH TIME ZONE** to additionally store time zone information.

- **DATE** values store dates in such a way that any particular day in history can be accurately recorded.  Typically the Gregorian calendar is supported, but some implementations will convert to and from Julian dates or other calendars.
- **TIME** represents a time of day, without reference to the date.  **TIME WITH TIME ZONE** includes information specifying the time zone relative to which the time should be evaluated.
- **TIMESTAMP** represents a precise moment in time, incorporating both the date and the time of day (with or without time zone).

A summary of database support for date and time types is shown below:

========================  ========================== ========== ======== ================================ ================
Type                      SQLite                     PostgreSQL MySQL    Oracle                           SQL Server
========================  ========================== ========== ======== ================================ ================
DATE                      use TEXT, REAL, or INTEGER yes        yes      yes                              yes
TIME                      use TEXT, REAL, or INTEGER yes        yes      no, use TIMESTAMP                yes
TIME WITH TIME ZONE       use TEXT, REAL, or INTEGER yes        no       no, use TIMESTAMP WITH TIME ZONE no
TIMESTAMP                 use TEXT, REAL, or INTEGER yes        yes      yes                              use DATETIME2
TIMESTAMP WITH TIME ZONE  use TEXT, REAL, or INTEGER yes        no       yes                              no
========================  ========================== ========== ======== ================================ ================

In addition to the date and time types, SQL defines a set of types known as *interval* types, where an interval represents a span of days or time between two date or time values.  Intervals are not covered in this book.


Operators and functions
:::::::::::::::::::::::

.. _appendix-b-comparison-operators:

Comparison operators
--------------------

Generally speaking, two non-NULL values of the same type can be compared, resulting in a Boolean value.  In certain cases, comparisons can made between different types, e.g., when both are numbers.  Numeric values are compared according to their algebraic values.  Date, time, and timestamp values are compared chronologically.  The Boolean value ``True`` is greater than ``False``.

Character string comparison is somewhat complex, as the comparison done depends on the *collation* rules in effect for the values; collation may depend on many factors including: the DBMS implementation, DBMS configuration parameters (such as the *locale*), operating system parameters, and any explicit collation settings for a given database table.  Collations may be used to implement proper sorting, for example, in a particular language context.  In general, if string *s* would appear in sorted (ascending) order prior to string *t*, then *s* \< *t*.

A comparison of any value with ``NULL`` results in ``NULL`` [#]_ when using any of the operators in the table below.

=========== ========================= =========================== =============================================
operator    meaning                   usage                       notes
=========== ========================= =========================== =============================================
\=          equal to                  *x* \= *y*
\<\>        not equal to              *x* \<\> *y*                can also use != in most DBMSes (nonstandard)
\<          less than                 *x* \< *y*
\>          greater than              *x* \> *y*
\<=         less than or equal to     *x* \<= *y*
\>=         greater than or equal to  *x* \>= *y*
BETWEEN     range comparison          *x* BETWEEN *y* AND *z*     equivalent to *x* \>= *y* AND *x* \<= *z*
NOT BETWEEN exterior range comparison *x* NOT BETWEEN *y* AND *z* equivalent to NOT(*x* BETWEEN *y* AND *z*)
=========== ========================= =========================== =============================================

Comparison of ``NULL`` values requires special treatment; the expression ``NULL = NULL`` results in ``NULL``, not ``True``, and thus is not useful in testing for ``NULL``.  The **IS NULL** operator is provided for this purpose.  **IS NULL** (and the inverse, **IS NOT NULL**) expressions always result in ``True`` or ``False``.

Another standard SQL operator that has utility in the presence of ``NULL`` values are the binary operators **IS DISTINCT FROM** and **IS NOT DISTINCT FROM**.  These operators compare two values, treating ``NULL`` as if it were a special, distinct value, and always return ``True`` or ``False``.  Thus, the expression ``x IS NOT DISTINCT FROM y`` returns ``True`` if ``x = y`` evaluates to ``True`` or if *x* and *y* are both ``NULL``.  Of the databases considered for this book, only PostgreSQL implements **IS DISTINCT FROM** and **IS NOT DISTINCT FROM**.

The table below summarizes these operators.

==================== ============================ =========================================================== ================
operator             usage                        result                                                      notes
==================== ============================ =========================================================== ================
IS NULL              *x* IS NULL                  True if and only if *x* evaluates to NULL
IS NOT NULL          *x* IS NOT NULL              equivalent to NOT (*x* IS NULL)
IS DISTINCT FROM     *x* IS DISTINCT FROM *y*     equivalent to NOT (*x* IS NOT DISTINCT FROM *y*)            PostgreSQL only
IS NOT DISTINCT FROM *x* IS NOT DISTINCT FROM *y* True if *x* = *y* is true, or if *x* and *y* are both NULL  PostgreSQL only
==================== ============================ =========================================================== ================

Also see the `Boolean operators`_ section below for comparison operators that only apply to Boolean values.

.. _appendix-b-math-operators:

Mathematical operators and functions
------------------------------------

Unless otherwise noted, the operands or parameters below can be any numeric type.

================== ===================== ================================ ===========================================
operator/ function meaning               usage                            notes
================== ===================== ================================ ===========================================
\+                 addition              *x* + *y*
\-                 subtraction           *x* - *y*
\*                 multiplication        *x* * *y*
\/                 division              *x* / *y*
ABS                absolute value        ABS(*x*)
MOD                modulus (remainder)   MOD(*x*, *divisor*)              integers only in standard SQL
LOG                logarithm             LOG(*base*, *x*)                 in SQL Server, use LOG(*x*, *base*)
LN                 natural logarithm     LN(*x*)                          in SQL Server, use LOG(*x*)
LOG10              base-10 logarithm     LOG10(*x*)                       in Oracle, use LOG(10, *x*)
EXP                exponential function  EXP(*x*)
POWER              raise to power        POWER(*base*, *exponent*)
SQRT               square root           SQRT(*x*)
FLOOR              floor function        FLOOR(*x*)
CEILING            ceiling function      CEILING(*x*) or CEIL(*x*)
SIN                sine function         SIN(*x*)                         argument in radians
COS                cosine function       COS(*x*)
TAN                tangent function      TAN(*x*)
ASIN               inverse sine          ASIN(*x*)
ACOS               inverse cosine        ACOS(*x*)
ATAN               inverse tangent       ATAN(*x*)
SINH               hyperbolic sine       SINH(*x*)
COSH               hyperbolic cosine     COSH(*x*)
TANH               hyperbolic tangent    TANH(*x*)
================== ===================== ================================ ===========================================

Most database implementations provide additional non-standard functions and operators; for example, most include some mechanism for generating random numbers.

Mathematical expressions where one or more operands or inputs are ``NULL`` evaluate to ``NULL``.


.. _appendix-b-string-operators:

Character string operators and functions
----------------------------------------

Below is a partial listing of operators and functions acting on character strings, omitting some less frequently implemented functions and some less frequently used optional parameters.

The SQL standard defines several operators and functions making use of three different pattern-matching languages: the one used by the operator **LIKE** (discussed in `Chapter 3`_), and two different regular expression (regex) languages; however the databases considered for this book mostly do not conform to the standard with respect to these operators and functions.  Many implementations provide functions with similar effect, but under different names and using different regex languages.  These functions are therefore omitted, but you are encouraged to read the documentation for your database to see what options are available to you.

.. _`Chapter 3`: ../03-expressions/expressions.html

================== ================================== ================================================== ===========================================
operator/function  meaning                            usage                                              notes
================== ================================== ================================================== ===========================================
\||                concatenation                      *s* || *t*                                         in MySQL, use CONCAT(*s*, *t*); in SQL Server, use *s* + *t*
LIKE               pattern comparison                 *s* LIKE *pattern*                                 see :numref:`Chapter {number} <expressions-chapter>`
NOT LIKE           inverse of LIKE                    *s* NOT LIKE *pattern*                             equivalent to NOT (*s* LIKE *pattern*)
CHAR_LENGTH        length of string                   CHARACTER_LENGTH(*s*) or CHAR_LENGTH(*s*)          in SQLite and Oracle, use LENGTH(*s*); in SQL Server, use LEN(*s*)
POSITION           index of substring                 POSITION(*t* IN *s*)                               in SQLite and Oracle, use INSTR(*s*, *t*)
SUBSTRING          substring extraction               SUBSTRING(*s* FROM *start* [FOR *length*])         in SQLite and Oracle, use SUBSTR(*s*, *start*, *length*); in SQL Server, use SUBSTRING(*s*, *start*, *length*)
UPPER              convert to uppercase               UPPER(*s*)
LOWER              convert to lowercase               LOWER(*s*)
TRIM               remove leading/trailing characters TRIM([[LEADING|TRAILING|BOTH] [*t*] FROM] *s*)     If *t* is omitted, whitespace is trimmed; BOTH is the default if LEADING etc. are omitted; in SQLite, Oracle, and SQL Server use LTRIM, RTRIM and TRIM (varying usage)
OVERLAY            substring replacement              OVERLAY(*s* PLACING *t* FROM *start* FOR *length*) not in SQLite, Oracle, or SQL Server, but see REPLACE
================== ================================== ================================================== ===========================================

Most database implementations provide additional non-standard functions and operators.

String operator or function expressions where the operands or inputs are ``NULL`` result in ``NULL``.


.. _appendix-b-boolean-operators:

Boolean operators
-----------------

The principal Boolean operators in SQL are **AND**, **OR**, and **NOT**.  Given operands that are strictly truth valued, i.e., not ``NULL``, these operators result in the logic operations they are named for.  That is, ``a AND b`` evaluates to ``True`` if and only if ``a`` and ``b`` are both ``True``, ``c OR d`` evaluates to ``True`` if either ``c`` or ``d`` are ``True``, and ``NOT e`` inverts the value ``e``.

However, since expressions resulting in Boolean values may also result in NULL (e.g., ``4 > NULL``), ``NULL`` is also a valid operand for the Boolean operators, and we can think of SQL as therefore having a 3-valued (rather than truly Boolean) logic [#]_.  The truth tables for **AND**, **OR**, and **NOT** are given below.  Treating ``NULL`` as meaning "unknown" in Boolean expressions, we can generally infer the result of a Boolean expression involving ``NULL``.  For example, ``True AND NULL`` must evaluate to ``NULL`` (meaning unknown), because the truth of the second operand is unknown.  On the other hand, ``True OR NULL`` must evaluate to ``True``, as it doesn't matter whether the second operand represents a true or a false value.

===== ===== =========== ==========
*a*   *b*   *a* AND *b* *a* OR *b*
===== ===== =========== ==========
True  True  True        True
True  False False       True
True  NULL  NULL        True
False True  False       True
False False False       False
False NULL  False       NULL
NULL  True  NULL        True
NULL  False False       NULL
NULL  NULL  NULL        NULL
===== ===== =========== ==========

===== =======
*a*   NOT *a*
===== =======
True  False
False True
NULL  NULL
===== =======

The SQL standard defines some less frequently used unary operators on Boolean values:  **IS [NOT] TRUE**, **IS [NOT] FALSE**, and **IS [NOT] UNKNOWN**, with **IS UNKNOWN** equivalent to **IS NULL** except that it only applies to the result of a Boolean expression.  So for example, SQL allows us to write ``NULL < 7 IS FALSE``, which would evaluate to ``False``.

SQL Server and Oracle do not implement **IS [NOT] TRUE**, **IS [NOT] FALSE**, and **IS [NOT] UNKNOWN**.  SQLite does not implement **IS [NOT] UNKNOWN**.

Some database implementations provide additional non-standard operators, such as **XOR**, **&** as an alternative to **AND**, etc.


.. _appendix-b-datetime-operators:

Date and time operators and functions
-------------------------------------

The SQL standard defines several basic operations relating **DATE**, **TIME** (with and without timezone), **TIMESTAMP** (with and without timezone), and **INTERVAL** data types.  (For a description of these data types, consult the section on `Data types`_ above.)

Comparison of like types is accomplished using the `Comparison operators`_ previously documented.  For example, **DATE** values can be compared with other **DATE** values, but not with **TIME**, **TIMESTAMP**, or **INTERVAL** values. (Behavior varies widely among the different database implementations - some do allow comparisons between types not allowed in the SQL standard.  However, it is generally inadvisable to compare different types, unless you know exactly how the comparison is being made.)

In addition, the mathematical operators *+*, *-*, *\**, and */* may be used as follows:

======== ========================= ======================== =====================
operator left operand              right operand            result type
======== ========================= ======================== =====================
\-       DATE, TIME, or TIMESTAMP  DATE, TIME, or TIMESTAMP INTERVAL
\+ or \- DATE, TIME, or TIMESTAMP  INTERVAL                 DATE, TIME, or TIMESTAMP
\+       INTERVAL                  DATE, TIME, or TIMESTAMP DATE, TIME, or TIMESTAMP
\+ or \- INTERVAL                  INTERVAL                 INTERVAL
\* or \/ INTERVAL                  number (INTEGER, etc.)   INTERVAL
\*       number (INTEGER, etc.)    INTERVAL                 INTERVAL
======== ========================= ======================== =====================

So, for example, a subtraction of one **TIMESTAMP** from another yields an **INTERVAL** representing the difference in days, hours, minutes, and seconds.

Other operators and functions involving dates and times:

===================== ============================================ ======================================
operator or function  meaning                                      usage
===================== ============================================ ======================================
CURRENT_DATE          evaluates to the current date                CURRENT_DATE
CURRENT_TIME          evaluates to the current time                CURRENT_TIME
CURRENT_TIMESTAMP     evaluates to the current date and time       CURRENT_TIMESTAMP
EXTRACT               get a date or time field from a date or time EXTRACT(*field* FROM *date/time/interval*), where *field* is e.g., 'YEAR', 'HOUR', etc.
OVERLAPS              test if one span of time overlaps another    *period1* OVERLAPS *period2*, where each *period* can be (*start date/time*, *end date/time*) or (*start date/time*, *interval*)
===================== ============================================ ======================================

Examples:

``EXTRACT('HOUR' FROM TIME '10:03:21')`` results in the integer ``10``.

``(DATE '2002-07-19', DATE '2003-01-31') OVERLAPS (DATE '2002-12-31', DATE '2005-05-05')`` results in a ``True``.

In actual practice, the databases considered for this book vary widely in their implementation of the SQL standard in regards to date and time types and operations on those types.  The variations are so great, we have not attempted to list departures from the standard in the above tables.  In most implementations, similar types can be compared, date and time types can be subtracted to yield intervals, and intervals can be added or subtracted to date and time types to yield a modified date or time.  Most databases implement **CURRENT_DATE**, **CURRENT_TIME**, and **CURRENT_TIMESTAMP**, or something similar.  Most implementations provide some function or functions replicating some of the functionality of **EXTRACT**.


Miscellaneous operators and functions
-------------------------------------

This section collects some miscellaneous SQL functions that do not fit neatly into the above categories.

================== ====================================== ==================================================== ===========================================
function           meaning                                usage                                                notes
================== ====================================== ==================================================== ===========================================
NULLIF             ``NULL`` if *a* = *b*, else *a*        NULLIF(*a*, *b*)
COALESCE           yield first non-``NULL`` argument      COALESCE(*a*, *b*, ...)
CASE               general purpose conditional expression see :numref:`Chapter {number} <expressions-chapter>`
CAST               explicit type conversion               CAST (*a* AS *type*)
================== ====================================== ==================================================== ===========================================


.. _appendix-b-aggregate-functions:

Aggregate functions
:::::::::::::::::::

Below is a reference to some of the more commonly implemented aggregate functions defined by the SQL standard.  See :numref:`Chapter {number} <grouping-chapter>` for a basic guide to their use.  The SQL standard also defines a number of statistical functions on two variables; these are implemented in PostgreSQL and Oracle only.  Most database implementations provide additional non-standard aggregate functions.

================== ====================================== ==================================================== ===========================================
function           meaning                                usage                                                notes
================== ====================================== ==================================================== ===========================================
COUNT              count of rows or non-``NULL`` values   COUNT(\*) or COUNT([DISTINCT] *a*)
AVG                average or mean                        AVG([DISTINCT] *a*)                                  *a* must be numeric
MAX                maximum                                MAX([DISTINCT] *a*)
MIN                minimum                                MIN([DISTINCT] *a*)
SUM                sum                                    SUM([DISTINCT] *a*)                                  *a* must be numeric
VAR_POP            population variance                    VAR_POP([DISTINCT] *a*)                              *a* must be numeric; not in SQLite; in SQL Server, use VARP(*a*)
VAR_SAMP           sample variance                        VAR_SAMP([DISTINCT] *a*)                             *a* must be numeric; not in SQLite; in SQL Server, use VAR(*a*)
STDDEV_POP         population standard deviation          STDDEV_POP([DISTINCT] *a*)                           *a* must be numeric; not in SQLite; in SQL Server, use STDEVP(*a*)
STDDEV_SAMP        sample standard deviation              STDDEV_SAMP([DISTINCT] *a*)                          *a* must be numeric; not in SQLite; in SQL Server, use STDEV(*a*)
LISTAGG            concatenate values into a string       LISTAGG(*a* [, *delim*])                             In SQLite and MySQL, use GROUP_CONCAT(*a*, *delim*); in PostgreSQL and SQL Server, use STRING_AGG(*a*, *delim*)
================== ====================================== ==================================================== ===========================================

----

**Notes**

.. [#] Technically, a comparison with NULL results in the value "unknown".  However, in all databases that we are aware of, NULL is indistinguishable from "unknown" except when using the operator **IS [NOT] UNKNOWN**.

.. [#] See above note.  The truth table technically should use "unknown" everywhere "NULL" appears.

|license-notice|



## Chapter: acknowledgments.rst

===============
Acknowledgments
===============

I would like to thank the `Colorado School of Mines`_ and particularly the `Department of Computer Science`_ for their support in writing this textbook.  Thank you to the `Mines OER`_ steering committee and the OER incentive grant program for their financial support.  Thank you to Emily Bongiovanni for advice and encouragement in the early stages of this effort.

A special thank you goes to Jaidynn Fohr for proofreading and helping prepare this book .  This book would not be the same without your many corrections and suggestions.

Thank you to Brad Miller and the other authors and maintainers of `Runestone Academy`_ for creating and advancing this amazing platform for textbook publishing.

Thank you to my family for your encouragement and support, and your patience with long writing sessions.  Patty, Ian, and Tim, I love you so much.

.. _`Colorado School of Mines`: https://www.mines.edu/

.. _`Department of Computer Science`: https://cs.mines.edu/

.. _`Mines OER`: https://libguides.mines.edu/oer

.. _`Runestone Academy`: https://runestone.academy/

|chapter-end|

|license-notice|



## Chapter: preface.rst

=======
Preface
=======

    *In God we trust, all others bring data.*

    -- attributed to W. Edwards Deming

This book, *A Practical Introduction to Databases*, was created to fill the need for a low-cost, up-to-date textbook suitable for an introductory course on databases:

- The book is free to students and instructors (although we encourage you to support the Runestone Academy platform to help ensure its future sustainability and growth).
- The book is open. [#]_  Its contents are licensed under the `Creative Commons Attribution-ShareAlike 4.0 International License`_, meaning that anyone is free to share, adapt, and redistribute them for any purpose whatsoever, as long as appropriate credit is given and the license terms persist.  The  source for this book is available on github; you may fork, extend, and re-release this book in any form you wish (pull requests welcome!).  This book is intended as a living document, to be updated and expanded regularly as technology changes, by any interested author.
- The book is oriented to students encountering databases for the first time, with a focus on key skills needed by future software engineers.

.. _`Creative Commons Attribution-ShareAlike 4.0 International License`: https://creativecommons.org/licenses/by-sa/4.0/

In this first release, the book covers three core topics: SQL, data modeling, and relational database theory. [#]_  In determining which material to include or exclude, choices were made to prefer material with high impact and practical application over exhaustive coverage.  Instructors may therefore wish to use this book as a foundation, supplemented with additional material as required for their course.  Instructors of more advanced courses in databases may also find value in providing this book as a supplement for students encountering the subject for the first time.  To the extent possible, the content is presented in a way that allows different orderings of topics, although some dependencies are unavoidable.

In keeping with the applied focus of the book, SQL is offered as the starting point in :numref:`Part {number} <sql-part>` of the text.  At a time when academia and industry alike are developing new advances in database technology seemingly on a daily basis, the relational database model as mediated by SQL remains the gravitational center for practitioners.  SQL is the common point of reference used to evaluate job applicants on their database skills.  The online book uses an embedded SQLite database engine to provide interactive examples and facilitate exploration (scripts are provided in :ref:`Appendix A <appendix-a>` to create the textbook's database on several other major database systems, if preferred).

:numref:`Part {number} <data-modeling-part>` discusses data modeling.  Here, the emphasis is on database design using entity-relationship diagrams (ERDs) and related tools.  The coverage includes a detailed example demonstrating ERD construction along with step-by-step instructions for converting ERDs to a relational database schema.

Finally, :numref:`Part {number} <relational-theory-part>` of the text provides coverage of relational database theory, including relational algebra and normalization (through fourth normal form).


|chapter-end|

----

**Notes**

.. [#] This book is an Open Education Resource (OER), and is aligned with the goals laid out in the `UNESCO Recommendation on Open Educational Resources`_, among others.

.. [#] Future releases are planned, covering software programming with databases, NoSQL, and other topics of practical interest.

.. _`UNESCO Recommendation on Open Educational Resources`: https://www.unesco.org/en/legal-affairs/recommendation-open-educational-resources-oer

|license-notice|



## Chapter: index.rst

.. meta::
   :description: A Practical Introduction to Databases, an open educational resource textbook.
   :keywords: sql, database, relational database, computer science

.. raw:: html

   <style type="text/css">
      body {
        background-image: url("_static/library_small.jpg");
        background-size: cover;
      }

      #main-content {
        background-color: rgba(248, 248, 235, 0.75);
        border-radius: 4px;
      }

      #main-content h1 {
        border-top: solid 1px #21314D !important;
        border-bottom: solid 1px #21314D !important;
      }
   </style>

=====================================
A Practical Introduction to Databases
=====================================

.. raw:: html

    <h3>Christopher Painter&#8209;Wakefield, Colorado School of Mines</h3>


Table of contents
:::::::::::::::::

.. toctree::
   :maxdepth: 1

   front-matter/preface

.. toctree::
   :numbered:
   :maxdepth: 2

   PART1_SQL/index
   PART2_DATA_MODELING/index
   PART3_RELATIONAL_DATABASE_THEORY/index

.. toctree::
   :maxdepth: 1

   references/references

.. toctree::
   :maxdepth: 2

   Appendix A: Example datasets used in this book <appendix-a-datasets/datasets>
   Appendix B: SQL reference <appendix-b-reference/reference>

* :ref:`genindex`
* :ref:`search`

.. toctree::
   :maxdepth: 1

   front-matter/acknowledgments

Cover photo
-----------

Photo of the library of Trinity College by `Henry Be <https://unsplash.com/@henry_be?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText>`_ on `Unsplash <https://unsplash.com/s/photos/library?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText>`_.

License
-------

.. raw:: html

   <div typeof="cc:Work" xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/">
    <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/" target="_blank">
      <img alt="Creative Commons License" style="display: block;" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png"/>
    </a>
   <br/>
   <span href="http://purl.org/dc/dcmitype/InteractiveResource" property="dct:title" rel="dct:type">
    <i>A Practical Introduction to Databases</i>
   </span>
   by
   <span property="cc:attributionName">Christopher Painter&#8209;Wakefield</span>
   is licensed under a
   <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>.
  </div>

Version
-------

This is release 0.1.2 of *A Practical Introduction to Databases*, committed 2023-08-26.



## Chapter: references.rst

.. _references:

==========
References
==========

SQL
::::

International Organization for Standardization and International Electrotechnical
Commission. (2016). *Information technology — Database languages — SQL — Part 2: Foundation (SQL/Foundation)* (ISO/IEC 9075-2, Fifth Edition).

SQLite Documentation. Retrieved from https://www.sqlite.org/docs.html.

PostgreSQL 12 Documentation. Retrieved from https://www.postgresql.org/docs/12/index.html.

MySQL 8.0 Reference Manual. Retrieved from https://dev.mysql.com/doc/refman/8.0/en/.

Oracle Database SQL Language Reference 18c. (April, 2020).  Retrieved from https://docs.oracle.com/en/database/oracle/oracle-database/18/sqlrf/.

Transact-SQL Reference. (April 29, 2020).  Retrieved from https://docs.microsoft.com/en-us/sql/t-sql/language-reference?view=sql-server-ver15.

.. _data-modeling-references:

Data modeling
:::::::::::::

Chen, Peter Pin-Shan. "The entity-relationship model—toward a unified view of data." *ACM transactions on database systems (TODS)* 1.1 (1976): 9-36.

Elmasri, Ramez, and Sham Navathe. *Fundamentals of Database Systems.* 7th edition, Pearson, 2016.

Everest, Gordon C. "Basic data structure models explained with a common example." *Proc. Fifth Texas Conference on Computing Systems*. 1976.

.. _relational-theory-references:

Relational database theory
::::::::::::::::::::::::::

Childs, David L. "Feasibility of a set-theoretic data structure: a general structure based on a reconstituted definition of relation." *Proc. IFIP Cong.* (1968).

Codd, Edgar Frank. "A relational model of data for large shared data banks." *Communications of the ACM* 26.1 (1983): 64-69.


|license-notice|


