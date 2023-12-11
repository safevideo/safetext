from lingua import Language, LanguageDetectorBuilder

LANGUAGE_TO_CODE = {
    Language.ENGLISH: "en",
    Language.TURKISH: "tr",
    Language.GERMAN: "de",
    Language.FRENCH: "fr",
    Language.SPANISH: "es",
}
LANGUAGES = [Language.ENGLISH, Language.TURKISH, Language.GERMAN, Language.FRENCH, Language.SPANISH]
DETECTOR = LanguageDetectorBuilder.from_languages(*LANGUAGES).build()


def detect_language_from_text(text: str) -> str:
    """
    Detects the language of the given text.

    Args:
        text (str): The text to detect the language of.

    Returns:
        str: The language code of the detected language.
            (e.g. "en", "tr")
    """
    result = DETECTOR.detect_language_of(text)
    return LANGUAGE_TO_CODE[result]


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
    import pysrt

    subs = pysrt.open(srt_file, encoding="utf-8")
    text = " ".join([sub.text_without_tags.replace("\n", " ") for sub in subs[:use_first_n_subs]])

    return detect_language_from_text(text)
