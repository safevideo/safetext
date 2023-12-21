import logging
import os
import re
from typing import Dict, List, Optional

import requests

from safetext.utils import detect_language_from_srt, detect_language_from_text

__version__ = "0.0.7"


class SafeText:
    """A class to provide text analysis for profanity detection using the built-in ProfanityChecker and
    optionally validating the results against the ModerateContentAPI.
    """

    def __init__(self, language: str = "en", validate_profanity: bool = False):
        """
        Initializes the SafeText with a specified language and validation option.

        Args:
            language (str): The language code for the profanity list. (ISO 639-1)
            validate_profanity (bool): Flag to enable validation of profanity detection results
                                       against ModerateContentAPI when using ProfanityChecker.
        """
        self.language = language
        self.checker = None
        if language is not None:
            self.set_language(language)
        self.moderate_content_api_key = os.getenv('MODERATE_CONTENT_API_KEY')
        self.validate_profanity = validate_profanity

        if validate_profanity and not self.moderate_content_api_key:
            raise ValueError(
                "MODERATE_CONTENT_API_KEY key must set as an environment variable for validation.")

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

    def check_profanity(self, text: str):
        """
        Checks the given text for profanity using the selected method. If validation is enabled, it logs the
        probable missing bad words and false positives between the results of ProfanityChecker and
        ModerateContentAPI.

        Args:
            text (str): The text to check for profanity.

        Returns:
            list: A list of profanity infos. Each profanity info is a dict with the following keys:
                - word: The profanity word.
                - index: The index of the profanity word in the text.
                - start: The start index of the profanity word in the text.
                - end: The end index of the profanity word in the text.
        """
        checker_results = self.checker.check(text)
        if self.validate_profanity:
            checker_bad_words = [profanity["word"] for profanity in checker_results]
            self._validate_profanity(text, checker_bad_words)

        return checker_results

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

    def get_bad_words(self, text: str = None, profanity_results: Optional[List[Dict]] = None) -> List[str]:
        """
        Retrieves a list of bad words found in the given text or from provided profanity results.

        Args:
            text (str, optional): The text to scan for profanities.
            profanity_results (Optional[List[Dict]], optional): Pre-calculated profanity results.

        Returns:
            List[str]: A list of bad words detected in the text.
        """
        return self.checker.get_bad_words(text, profanity_results)

    def _auto_set_language(self, text):
        """
        Detects the language of the given text and sets the language of the profanity checker.

        Args:
            text (str): The text to detect the language of.
        """
        language = detect_language_from_text(text)
        self.set_language(language)

    def _validate_profanity(self, text: str, checker_bad_words: list):
        """
        Validates the profanity detection results of ProfanityChecker against the ModerateContentAPI.

        Args:
            text (str): The text that was checked.
            checker_bad_words (list): The list of bad words detected by ProfanityChecker.
        """
        api_bad_words = ModerateContentAPI(self.moderate_content_api_key).get_bad_words(text)

        missing_words = set(api_bad_words) - set(checker_bad_words)
        false_positives = set(checker_bad_words) - set(api_bad_words)

        if missing_words:
            logging.info(f"Possible missing bad words: {missing_words}")
        if false_positives:
            logging.info(f"Possible false detected words: {false_positives}")
        if not missing_words and not false_positives:
            logging.info("All good for validation!")


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

    def get_bad_words(self, text: str = None, profanity_results: Optional[List[Dict]] = None) -> List[str]:
        """
        Retrieves a list of bad words found in the given text or from provided profanity results.

        Args:
            text (str, optional): The text to scan for profanities.
            profanity_results (Optional[List[Dict]], optional): Pre-calculated profanity results from
            ProfanityChecker.check() method.

        Returns:
            List[str]: A list of bad words detected in the text.
        """
        if text is None and profanity_results is None:
            raise ValueError("Either text or profanity_results must be provided.")

        if profanity_results is None:
            profanity_results = self.check(text)

        bad_words = []
        for profanity in profanity_results:
            if profanity["word"] not in bad_words:
                bad_words.append(profanity["word"])

        return bad_words

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

    def check(self, text: str) -> List[Dict]:
        """
        Checks the given text for profanity.

        Args:
            text (str): The text to check for profanity.

        Returns:
            List[Dict]: A list of dictionaries, each containing information about a found profanity.
        """
        return self._find_profanities(text)


class ModerateContentAPI:
    """
    A class to interact with the Moderate Content API for profanity detection.

    This class facilitates the detection of bad words in text using the
    Moderate Content API. It allows for fetching a list of bad words detected
    in a given text.

    Attributes:
        api_key (str): The API key for accessing the Moderate Content API.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initializes the ModerateContentAPI with an optional API key.

        Args:
            api_key (str, optional): The API key for the Moderate Content API.
                                     If not provided, it will look for an API key
                                     in the MODERATE_CONTENT_API_KEY environment variable.
        """
        self.api_key = api_key or os.getenv('MODERATE_CONTENT_API_KEY')
        if not self.api_key:
            raise ValueError("API key must be provided or set as an environment variable.")

    def _request_api(self, text: str, exclude: Optional[str] = None, replace: Optional[str] = None) -> Dict:
        """
        Makes a request to the Moderate Content API and returns the response.

        Args:
            text (str): The text to analyze for bad words.
            exclude (str, optional): A comma-delimited list of words to exclude from checking.
            replace (str, optional): A string of characters to replace bad words with.

        Returns:
            Dict: A dictionary containing the API response.
        """
        api_url = "https://api.moderatecontent.com/text/"
        params = {'key': self.api_key, 'msg': text, 'exclude': exclude, 'replace': replace}
        try:
            response = requests.get(api_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            # Log the exception details here
            raise ConnectionError("Failed to connect to the Moderate Content API.") from e

    def get_bad_words(self,
                      text: str,
                      exclude: Optional[str] = None,
                      replace: Optional[str] = None) -> List[str]:
        """
        Analyzes the given text and returns a list of bad words found.

        Args:
            text (str): The text to analyze for bad words.
            exclude (str, optional): A comma-delimited list of words to exclude from checking.
            replace (str, optional): A string of characters to replace bad words with.

        Returns:
            List[str]: A list of bad words detected in the text.
        """
        response = self._request_api(text, exclude, replace)
        return response.get('bad_words', [])

    def censor(self, text: str, exclude: Optional[str] = None, replace: Optional[str] = None) -> str:
        """
        Analyzes the given text and returns a censored version of it.

        Args:
            text (str): The text to analyze for bad words.
            exclude (str, optional): A comma-delimited list of words to exclude from checking.
            replace (str, optional): A string of characters to replace bad words with.

        Returns:
            str: The censored text with bad words replaced by asterisks.
        """
        response = self._request_api(text, exclude, replace)
        return response.get('clean', '')

    def check(self, text: str):
        """
        Checks the given text for profanity.

        Args:
            text (str): The text to check for profanity.

        Returns:
            List[str]: A list of bad words detected in the text.
        """
        return self.get_bad_words(text)
