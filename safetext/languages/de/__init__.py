from safetext.languages.base import BaseProfanityChecker


class GermanProfanityChecker(BaseProfanityChecker):
    """German profanity checker."""

    def __init__(self):
        super().__init__(language="de")
