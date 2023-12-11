from safetext.languages.base import BaseProfanityChecker


class SpanishProfanityChecker(BaseProfanityChecker):
    """Spanish profanity checker."""

    def __init__(self):
        super().__init__(language="es")
