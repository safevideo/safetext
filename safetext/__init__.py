from .languages.en import EnglishProfanityChecker
from .languages.tr import TurkishProfanityChecker

__version__ = "0.0.1"


class SafeText:
    def __init__(self, language="en"):
        self.language = language
        self.checker = None
        self.set_language(language)

    def set_language(self, language):
        self.language = language
        if language == "en":
            self.checker = EnglishProfanityChecker()
        elif language == "tr":
            self.checker = TurkishProfanityChecker()
        else:
            raise ValueError("Language not supported")

    def check_profanity(self, text):
        if self.checker is None:
            raise ValueError("Language not set")
        return self.checker.check(text)

    def censor_profanity(self, text):
        if self.checker is None:
            raise ValueError("Language not set")
        return self.checker.censor(text)
