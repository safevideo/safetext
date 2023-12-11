import os
import re
from typing import Dict, List

from safetext.utils import detect_language_from_srt, detect_language_from_text

__version__ = "0.0.4"


class SafeText:

    def __init__(self, language="en"):
        self.language = language
        self.checker = None
        if language is not None:
            self.set_language(language)

    def set_language(self, language: str):
        """Sets the language of the profanity checker."""
        words_file_path = self._get_words_filepath(language)
        if not os.path.exists(words_file_path):
            raise ValueError(f"No profanity word list found for language '{language}'.")

        self.language = language
        self.checker = ProfanityChecker(language)

    def _get_words_filepath(self, language: str) -> str:
        return os.path.join(os.path.dirname(__file__), f"languages/{language}/words.txt")

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
            self._auto_set_language(text)
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
            self._auto_set_language(text)
        return self.checker.censor(text)

    def _auto_set_language(self, text: str):
        detected_language = detect_language_from_text(text)
        self.set_language(detected_language)


class ProfanityChecker:
    """
    A class for checking and censoring profanity in text.

    This class supports detection of both single-word and phrase-based profanities.
    It requires a list of profane words and phrases to be provided in a text file.

    Attributes:
        language (str): The language code (e.g., 'en' for English).
    """

    def __init__(self, language: str):
        """
        Initializes the ProfanityChecker with a specified language.

        Args:
            language (str): The language code for the profanity list.
        """
        self.language = language
        self._profanity_words = self._load_profanity_list()

    def _load_profanity_list(self) -> List[str]:
        """
        Loads the profanity words list from the corresponding file.

        Returns:
            List[str]: A list of profanity words and phrases.
        """
        words_filepath = os.path.join(os.path.dirname(__file__), f"languages/{self.language}/words.txt")
        with open(words_filepath, encoding="utf8") as file:
            return file.read().splitlines()

    def _find_profanities(self, text: str) -> List[Dict]:
        """
        Finds profanities in the given text.

        Args:
            text (str): The text to scan for profanities.

        Returns:
            List[Dict]: A list of dictionaries, each containing information about a found profanity.
        """
        profanity_infos = []
        lower_text = text.lower()
        words = re.findall(r'\b\w+\b', lower_text)

        for profanity in self._profanity_words:
            if ' ' in profanity:
                self._find_profanity_phrase(profanity, lower_text, profanity_infos)
            else:
                self._find_profanity_word(profanity, words, text, profanity_infos)

        return profanity_infos

    def _find_profanity_word(self, profanity: str, words: List[str], text: str, profanity_infos: List[Dict]):
        """
        Searches for a single-word profanity in the list of words.

        Args:
            profanity (str): The profanity word to search for.
            words (List[str]): The list of words in the text.
            text (str): The original text.
            profanity_infos (List[Dict]): List to append found profanities.
        """
        for i, word in enumerate(words):
            if word == profanity:
                pattern = re.compile(r'\b' + re.escape(profanity) + r'\b', re.IGNORECASE)
                for match in pattern.finditer(text):
                    profanity_infos.append({
                        "word": word,
                        "index": i + 1,
                        "start": match.start(),
                        "end": match.end()
                    })

    def _find_profanity_phrase(self, profanity: str, lower_text: str, profanity_infos: List[Dict]):
        """
        Searches for a phrase-based profanity in the text.

        Args:
            profanity (str): The profanity phrase to search for.
            lower_text (str): The lowercased text.
            profanity_infos (List[Dict]): List to append found profanities.
        """
        start = lower_text.find(profanity)
        while start != -1:
            end = start + len(profanity)
            word_count_before = len(re.findall(r'\b\w+\b', lower_text[:start]))
            profanity_infos.append({
                "word": profanity,
                "index": word_count_before + 1,
                "start": start,
                "end": end
            })
            start = lower_text.find(profanity, end)

    def check(self, text: str) -> List[Dict]:
        """
        Checks the given text for profanity.

        Args:
            text (str): The text to check for profanity.

        Returns:
            List[Dict]: A list of dictionaries, each containing information about a found profanity.
        """
        return self._find_profanities(text)

    def censor(self, text: str) -> str:
        """
        Censors profanity in the given text.

        Args:
            text (str): The text to censor.

        Returns:
            str: The censored text with profanities replaced by asterisks.
        """
        detected_profanities = self.check(text)
        for profanity in sorted(detected_profanities, key=lambda x: x['start'], reverse=True):
            start_index = profanity["start"]
            end_index = profanity["end"]
            text = text[:start_index] + '*' * (end_index - start_index) + text[end_index:]
        return text
