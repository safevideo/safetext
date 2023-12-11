from safetext.utils import detect_language_from_srt, detect_language_from_text

from .languages.de import GermanProfanityChecker
from .languages.en import EnglishProfanityChecker
from .languages.es import SpanishProfanityChecker
from .languages.pt import PortugueseProfanityChecker
from .languages.tr import TurkishProfanityChecker

__version__ = "0.0.4"


class SafeText:

    def __init__(self, language="en"):
        self.language = language
        self.checker = None
        if language is not None:
            self.set_language(language)

    def set_language(self, language):
        self.language = language
        if language == "en":
            self.checker = EnglishProfanityChecker()
        elif language == "tr":
            self.checker = TurkishProfanityChecker()
        elif language == "es":
            self.checker = SpanishProfanityChecker()
        elif language == "de":
            self.checker = GermanProfanityChecker()
        elif language == "pt":
            self.checker = PortugueseProfanityChecker()
        else:
            raise ValueError("Language not supported")

    def set_language_from_text(self, text):
        """
        Detects the language of the given text.

        Args:
            text (str): The text to detect the language of.

        Returns:
            str: The language code of the detected language.
                (e.g. "en", "tr")
        """
        language = detect_language_from_text(text)
        self.set_language(language)

    def set_language_from_srt(self, srt_file, use_first_n_subs=10):
        """
        Detects the language of the given SRT file.

        Args:
            srt_file (str): The path to the SRT file to detect the language of.
            use_first_n_subs (int): The number of subtitles to use for detection.

        Returns:
            str: The language code of the detected language.
                (e.g. "en", "tr")
        """
        language = detect_language_from_srt(srt_file, use_first_n_subs)
        self.set_language(language)

    def check_profanity(self, text):
        """
        Checks the given text for profanity.

        Args:
            text (str): The text to check for profanity.

        Returns:
            list: A list of profanity infos. Each profanity info is a dict with the following keys:
                - word: The profanity word.
                - index: The index of the profanity word in the text.
                - start: The start index of the profanity word in the text.
                - end: The end index of the profanity word in the text.
        """
        if self.checker is None:
            raise ValueError("Language not set")
        return self.checker.check(text)

    def censor_profanity(self, text):
        """
        Censors the given text for profanity.

        Args:
            text (str): The text to censor for profanity.

        Returns:
            str: The censored text. The profanity words are replaced with asterisks.
        """
        if self.checker is None:
            raise ValueError("Language not set")
        return self.checker.censor(text)
