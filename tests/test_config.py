from io import StringIO
import sys
from icortex.cli import main


class FakeTerminalIO(StringIO):
    encoding = "UTF-8"

    def fileno(self):
        return 0


class Test:
    def test_function(self, tmpdir):
        sys.stdin = FakeTerminalIO(
            """echo
n
"123"
"""
        )
        config_path = tmpdir.join("icortex.toml")

        main(["--init", "--config", str(config_path)])
        assert (
            open(config_path, "r").read()
            == """service = \"echo\"

[echo]
prefix = \"123\"
"""
        )

    def setup_method(self):
        self.orig_stdin = sys.stdin

    def teardown_method(self):
        sys.stdin = self.orig_stdin
