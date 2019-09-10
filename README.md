democlub-ppc-scraper
====================

Scrapes UK politcal party lists of PPCs and compares them with [Democracy Club](https://democracyclub.org.uk/)'s [list](https://docs.google.com/spreadsheets/d/1cHlm1irk7FFqPKO6jTgBh9Ya5k_erWGIH7AP65nkWCc/edit).

Lists places where a party claims a candidate is standing, where Democracy Club doesn't claim the same thing.

Does not do the backwards check; i.e. if Democracy Club claims someone is standing, and the party doesn't list a candidate, nothing is emitted.

How to run
----------

```
pip install -r requirements.txt
python3.7 main.py
```

Green Party
-----------

Uses https://my.greenparty.org.uk/candidates as a source of truth.

Labour Party
------------

Uses http://vote.labour.org.uk/all-candidates as a source of truth. Unfortunately, there's no clear way to determine whether a currently-sitting MP is standing as a candidate again, so it probably only works for candidates not currently sitting as MPs.

Note that the Labour Party have a series of typos in people's names which brings up some false positives. It also claims that one candidate (Rhea Wolfson in Livingston) is running who Democracy Club believe has since stepped down.

Liberal Democrat Party
----------------------

Uses https://www.markpack.org.uk/153722/liberal-democrat-parliamentary-candidates/ as a source of truth.

How to contribute
-----------------

Send a pull request! :)
