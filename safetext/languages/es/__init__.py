from safetext.languages.base import BaseProfanityChecker


class SpanishProfanityChecker(BaseProfanityChecker):
    """Turkish profanity checker."""

    def __init__(self):
        super().__init__(language="es")
