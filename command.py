from typing import Callable, Union
from typing_extensions import Self


class CommandError(Exception):
    """Exception if a command has an error"""
    pass


class Command:
    """A command, consisting of a phrase and an effect"""

    def __init__(self, phrase: Union[str, list[str]], effect: Callable[[], Union[str, None]]) -> Self:
        """Phrase can be a string or list of strings and will be normalized.
        Effect is a function that may raise `CommandError`."""
        if phrase.isinstance(str):
            self.phrase = [phrase.strip().lower()]
        else:
            self.phrase = [p.strip().lower() for p in phrase]
        self.effect = effect

    def matches(self, phrase: str):
        if any(p in phrase.strip().lower() for p in self.phrase):
            return True
        else:
            return False

    def run(self):
        return self.effect()
