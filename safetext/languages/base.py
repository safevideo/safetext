class BaseProfanityChecker:
    """Base class for profanity checkers."""

    def __init__(self, language):
        self.language = language

    @property
    def words_filepath(self):
        """Get the filepath for the profanity words file."""
        import pathlib

        return f"{pathlib.Path(__file__).parent.resolve()}/{self.language}/words.txt"

    @property
    def profanity_words(self):
        """Get the profanity words for the language."""
        if not hasattr(self, "_profanity_words"):
            self._profanity_words = self._read_words(self.words_filepath)

        return self._profanity_words

    def _check(self, text):
        """Check the text for profanity."""
        # Split the text into a list of words
        words = text.split()

        # Initialize a list to store the indices of profanity words
        profanity_infos = []

        for i, word in enumerate(words):
            if word.lower() in self.profanity_words:
                start_index = sum(
                    len(w) + 1 for w in words[:i]
                )  # +1 to account for space between words
                end_index = start_index + len(word)
                profanity_info = {
                    "word": word,
                    "index": i + 1,
                    "start": start_index,
                    "end": end_index,
                }
                profanity_infos.append(profanity_info)

        return profanity_infos

    def _read_words(self, filepath):
        """Read the profanity words from the given file."""
        with open(filepath, "r", encoding="utf8") as f:
            profanity_words = f.read().splitlines()

        return profanity_words

    def _preprocess(self, text):
        """Preprocess the text before checking for profanity."""
        return text

    def check(self, text):
        """
        Check the text for profanity.

        Args:
            text (str): The text to check for profanity.

        Returns:
            list: A list of profanity infos. Each profanity info is a dict with the following keys:
                - word: The profanity word.
                - index: The index of the profanity word in the text.
                - start: The start index of the profanity word in the text.
                - end: The end index of the profanity word in the text.
        """
        return self._check(self._preprocess(text))

    def censor(self, text):
        """Censor the text."""
        detected_profanities = self.check(text)
        for profanity in detected_profanities:
            start_index = profanity["start"]
            end_index = profanity["end"]
            text = text.replace(text[start_index:end_index], "***")

        return text
