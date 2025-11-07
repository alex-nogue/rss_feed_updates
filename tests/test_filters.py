from rss_notifier.filters import matches_filters


def make_entry(title, summary=""):
    return {"title": title, "summary": summary}


def test_keyword_match():
    kws = ["one piece"]
    regexes = []
    entry = make_entry("New One Piece chapter")
    assert matches_filters(entry, kws, regexes)


def test_regex_match():
    import re

    kws = []
    regexes = [re.compile(r"isekai", re.I)]
    entry = make_entry("A new isekai anime announced")
    assert matches_filters(entry, kws, regexes)


def test_no_match():
    kws = ["naruto"]
    regexes = []
    entry = make_entry("Some unrelated news")
    assert not matches_filters(entry, kws, regexes)
