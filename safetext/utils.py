import os
from typing import List

import pysrt
from lingua import Language, LanguageDetectorBuilder


def available_languages() -> List[Language]:
    """
    Scans the 'languages' directory to identify available languages based on directory names.

    Returns:
        List[Language]: A list of available languages as Language enum values.
    """
    current_file_directory = os.path.dirname(__file__)

    languages_path = os.path.join(current_file_directory, "languages")

    all_items_in_languages_dir = os.listdir(languages_path)

    available_lang_codes = []

    for item in all_items_in_languages_dir:
        item_full_path = os.path.join(languages_path, item)

        if os.path.isdir(item_full_path):
            available_lang_codes.append(item)

    available_langs = []
    for lang in Language:
        if lang.iso_code_639_1.name.lower() in available_lang_codes:  # Correctly access the ISO 639-1 code
            available_langs.append(lang)

    return available_langs


def initialize_detector() -> LanguageDetectorBuilder:
    """
    Dynamically initializes the language detector based on the available languages.

    Returns:
        LanguageDetectorBuilder: An initialized language detector.
    """
    return LanguageDetectorBuilder.from_languages(*available_languages()).build()


def detect_language_from_text(text: str) -> str:
    """
    Detects the language of the given text using the dynamically initialized language detector.

    Args:
        text (str): The text to detect the language of.

    Returns:
        str: The ISO 639-1 language code of the detected language.
    """
    DETECTOR = initialize_detector()
    detected_language = DETECTOR.detect_language_of(text)
    return detected_language.iso_code_639_1.name.lower()  # IsoCode639_1


def detect_language_from_srt(srt_file: str, use_first_n_subs: 10) -> str:
    """
    Detects the language of the given SRT file.

    Args:
        srt_file (str): The path to the SRT file to detect the language of.
        use_first_n_subs (int): The number of subtitles to use for detection.

    Returns:
        str: The language code of the detected language.
            (e.g. "en", "tr")
    """
    subs = pysrt.open(srt_file, encoding="utf-8")
    text = " ".join([sub.text_without_tags.replace("\n", " ") for sub in subs[:use_first_n_subs]])

    return detect_language_from_text(text)
