from safetext.languages.base import BaseProfanityChecker


class PortugueseProfanityChecker(BaseProfanityChecker):
    """Portuguese profanity checker."""

    def __init__(self):
        super().__init__(language="pt")
