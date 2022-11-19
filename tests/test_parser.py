from icortex.parser import extract_prompt, lex_prompt


def test_extract_prompt():
    assert extract_prompt("no flags in this")[0] == "no flags in this"
    assert (
        extract_prompt("this one hasn't a single quote")[0]
        == "this one hasn't a single quote"
    )
    assert (
        extract_prompt("this one hasn't a single quote and a --flag")[0]
        == "this one hasn't a single quote and a"
    )
    assert (
        extract_prompt('"this one hasn\'t a single quote and a --flag"')[0]
        == "this one hasn't a single quote and a --flag"
    )
    assert extract_prompt(
        '"this one hasn\'t a single quote and a --flag" --flag-outside'
    ) == ("this one hasn't a single quote and a --flag", "--flag-outside")

    assert extract_prompt("before before -a after after")[0] == "before before"
    assert extract_prompt("before before --long after after")[0] == "before before"
    assert (
        extract_prompt("'before before -a after' after")[0] == "before before -a after"
    )
    assert (
        extract_prompt('"before before -a after"  after -e after')[0]
        == "before before -a after"
    )


def test_lex_prompt():
    assert lex_prompt("no flags in this") == ["no flags in this"]
    assert lex_prompt("this one hasn't a single quote") == [
        "this one hasn't a single quote"
    ]
    assert lex_prompt(
        "this one hasn't a single quote and a --flag 123 --another-flag"
    ) == ["this one hasn't a single quote and a", "--flag", "123", "--another-flag"]
    assert lex_prompt(
        '"this one hasn\'t a single quote and a --flag" --flag-outside'
    ) == ["this one hasn't a single quote and a --flag", "--flag-outside"]

    assert lex_prompt("before before -a after after") == [
        "before before",
        "-a",
        "after",
        "after",
    ]
    assert lex_prompt("before before --long after after") == [
        "before before",
        "--long",
        "after",
        "after",
    ]
    assert lex_prompt("'before before -a after' after") == [
        "before before -a after",
        "after",
    ]
    assert lex_prompt('"before before -a after"  after -e after') == [
        "before before -a after",
        "after",
        "-e",
        "after",
    ]
