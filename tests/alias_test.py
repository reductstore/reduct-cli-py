"""Unit tests for alias command"""


def test__empty_list(runner, conf):
    """Should show empty aliases"""
    result = runner(f"-c {conf} alias ls")
    assert result.exit_code == 0
    assert result.output == ""


def test__add_alias_ok(runner, conf, url):
    """Should add an alias"""
    token = "token"
    result = runner(f"-c {conf} alias add storage", input=f"{url}\n{token}\n")
    assert result.exit_code == 0

    result = runner(f"-c {conf} alias ls")
    assert result.exit_code == 0
    assert result.output == "storage\n"


def test__add_alias_twice(runner, conf, url):
    """Should not add an alias if the name alread exists"""
    result = runner(f"-c {conf} alias add storage", input=f"{url}\ntoken\n")
    assert result.exit_code == 0

    result = runner(f"-c {conf} alias add storage")
    assert result.exit_code == 1
    assert result.output == "Alias 'storage' already exists\nAborted!\n"


def test__rm_ok(runner, conf, url):
    """Should remove alias"""
    result = runner(f"-c {conf} alias add storage", input=f"{url}\ntoken\n")
    assert result.exit_code == 0

    result = runner(f"-c {conf} alias rm storage")
    assert result.exit_code == 0

    result = runner(f"-c {conf} alias ls")
    assert result.exit_code == 0
    assert result.output == ""


def test__rm_not_exist(runner, conf):
    """Shouldn't remove alias if it doesn't exist"""
    result = runner(f"-c {conf} alias rm storage")
    assert result.exit_code == 1
    assert result.output == "Alias 'storage' doesn't exist\nAborted!\n"


def test__show(runner, conf, url):
    """Should show alias"""
    result = runner(f"-c {conf} alias add storage", input=f"{url}\ntoken\n")
    assert result.exit_code == 0

    result = runner(f"-c {conf} alias show storage")
    assert result.exit_code == 0
    assert result.output.replace(" ", "") == f"URL:{url}\n"


def test__show_with_token(runner, conf, url):
    """Should show alias with token"""
    result = runner(f"-c {conf} alias add storage", input=f"{url}\ntoken\n")
    assert result.exit_code == 0

    result = runner(f"-c {conf} alias show --token storage")
    assert result.exit_code == 0
    assert result.output.replace(" ", "") == f"URL:{url}\nToken:token\n"


def test__show_not_exist(runner, conf):
    """Should not show alias if alias doesn't exist"""
    result = runner(f"-c {conf} alias show storage")
    assert result.exit_code == 1
    assert result.output == "Alias 'storage' doesn't exist\nAborted!\n"
