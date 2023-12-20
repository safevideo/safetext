import logging
import os
import re
from typing import Dict, List, Optional

import requests

from safetext.utils import detect_language_from_srt, detect_language_from_text

__version__ = "0.0.6"


class SafeText:
    """
    A class to provide text analysis for profanity detection using either the built-in ProfanityChecker or the
    ModerateContentAPI.

    Attributes:
        language (str): The current language of the text.
        checker (ProfanityChecker): An instance of ProfanityChecker for detecting profanity.
        use_api (bool): Flag to use ModerateContentAPI instead of ProfanityChecker.
        api_checker (ModerateContentAPI): An instance of ModerateContentAPI, if use_api is True.
        compare_results (bool): Flag to enable comparison logging between the two methods.
    """

    def __init__(
            self,
            language: str = "en",
            use_api: bool = False,
            api_key: Optional[str] = None,
            validate_profanity: bool = False):
        """
        Initializes the SafeText with a specified language, checker preference, and validation option.

        Args:
            language (str): The language code for the profanity list.
            use_api (bool): Flag to use ModerateContentAPI for profanity detection.
            api_key (str, optional): The API key for ModerateContentAPI.
            validate_profanity (bool): Flag to enable validation of profanity detection results
                                       against ModerateContentAPI when using ProfanityChecker.
        """
        self.language = language
        self.checker = None
        if language is not None:
            self.set_language(language)
        self.use_api = use_api
        self.api_checker = ModerateContentAPI(api_key) if use_api else None
        self.validate_profanity = validate_profanity and not use_api

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
        Checks the given text for profanity using the selected method.

        Args:
            text (str): The text to check for profanity.

        Returns:
            list: A list of profanity infos if using ProfanityChecker, or
                  a list of bad words if using ModerateContentAPI.
        """
        if self.use_api:
            return self.api_checker.get_bad_words(text)

        if self.checker is None:
            self._auto_set_language(text)

        checker_results = self.checker.check(text)
        if self.validate_profanity:
            self._validate_profanity(text, checker_results)
        return checker_results

    def censor_profanity(self, text: str) -> str:
        """
        Censors the given text for profanity.

        Args:
            text (str): The text to censor for profanity.

        Returns:
            str: The censored text using the selected method.
        """
        if self.use_api:
            return self.api_checker.censor(text)  # Using ModerateContentAPI
        else:
            return self.checker.censor(text)  # Using built-in ProfanityChecker

    def _auto_set_language(self, text: str):
        detected_language = detect_language_from_text(text)
        self.set_language(detected_language)

    def _validate_profanity(self, text: str, checker_results: list):
        """
        Validates the profanity detection results by comparing with ModerateContentAPI results.

        Args:
            text (str): The text that was checked.
            checker_results (list): Results from the ProfanityChecker.
        """
        api_bad_words = self.api_checker.get_bad_words(text)
        checker_bad_words = [result["word"] for result in checker_results]
        missing_words = set(api_bad_words) - set(checker_bad_words)
        false_positives = set(checker_bad_words) - set(api_bad_words)

        if missing_words:
            logging.info(f"Possible missing bad words: {missing_words}")
        if false_positives:
            logging.info(f"Possible false detected words: {false_positives}")


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

    def get_bad_words(self, text: str) -> List[str]:
        """
        Retrieves a list of bad words found in the given text.

        Args:
            text (str): The text to scan for profanities.

        Returns:
            List[str]: A list of bad words detected in the text.
        """
        profanity_infos = self.check(text)
        bad_words = []

        for profanity in profanity_infos:
            bad_word = profanity["word"]
            if bad_word not in bad_words:
                bad_words.append(bad_word)
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

    def cencor(self, text: str, exclude: Optional[str] = None, replace: Optional[str] = None) -> str:
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
