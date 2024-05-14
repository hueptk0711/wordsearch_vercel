import string
from abc import ABC, abstractmethod


class Validator(ABC):
    @abstractmethod
    def validate(self, value: str, *args, **kwargs) -> bool:
        """Validate the value.s"""


class NoSingleLetterWords(Validator):
    """A validator to ensure the value is larger than one character."""

    def validate(self, value: str, *args, **kwargs) -> bool:
        return len(value) > 1


class NoPunctuation(Validator):
    """A validator to ensure the value doesn't contain punctuation."""

    def validate(self, value: str, *args, **kwargs) -> bool:
        return not any(c in string.punctuation for c in value)


class NoPalindromes(Validator):
    """A validator to ensure the value isn't a palindrome."""

    def validate(self, value: str, *args, **kwargs) -> bool:
        return value != value[::-1]


class NoSubwords(Validator):
    """A validator to ensure the value isn't a subword of another word."""

    def validate(self, value: str, *args, **kwargs) -> bool:  # type: ignore
        placed_words = kwargs["placed_words"] or []
        for test_word in placed_words:
            if (
                value.lower() in test_word.lower()
                or value[::-1].lower() in test_word.lower()
                or test_word.lower() in value.lower()
                or test_word.lower()[::-1] in value.lower()
            ):
                return False
        return True
