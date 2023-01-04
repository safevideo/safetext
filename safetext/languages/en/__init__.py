from safetext.languages.base import BaseProfanityChecker


class EnglishProfanityChecker(BaseProfanityChecker):
    """Turkish profanity checker."""

    def __init__(self):
        super().__init__(language="en")
