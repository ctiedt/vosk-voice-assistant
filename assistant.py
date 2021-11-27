from typing import Iterator
import pyttsx3
from command import Command, CommandError


class Assistant:
    """A voice assistant instance"""

    def __init__(self):
        self.commands: list[Command] = []
        self.engine = pyttsx3.init()

    def add_command(self, cmd: Command):
        """Add the given command to list of known commands"""
        self.commands.append(cmd)

    def process(self, phrase: str):
        """Check if a given phrase matches any known command and respond appropriately"""
        for cmd in (c for c in self.commands if c.matches(phrase)):
            try:
                if (response := cmd.run()) is not None:
                    self.engine.say(response)
                else:
                    self.engine.say("Okeh.")
            except CommandError:
                self.engine.say("Ein Fehler ist aufgetreten.")
            finally:
                self.engine.runAndWait()

    def run(self, phrases: Iterator[str]):
        """Runs `self.process` on every item of the iterator `phrases`"""
        for phrase in phrases:
            self.process(phrase)
