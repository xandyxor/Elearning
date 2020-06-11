"""
Global thesaurus exception and warning classes. Based on the exceptions of
  goldsmith/Wikipedia
"""

import sys


class ThesaurusException(Exception):
    """Base thesaurus exception class."""

    def __init__(self, error):
        self.error = error

    def __unicode__(self):
        return "An unknown error occured: \"{0}\". Please report it on GitHub!".format(self.error)

    if sys.version_info > (3, 0):
        def __str__(self):
            return self.__unicode__()

    else:
        def __str__(self):
            return self.__unicode__().encode('utf8')


class WordNotFoundError(ThesaurusException):
    """Exception raised when thesaurus.com doesn't have this word."""

    def __init__(self, word):
        self.word = word

    def __unicode__(self):
        return u"No thesaurus results for word '{0}'.".format(self.word)


class MisspellingError(ThesaurusException):
    """Exception raised when thesaurus.com believes your word is misspelled."""

    def __init__(self, word, possiblyCorrectWord):
        self.word = word
        self.possiblyCorrectWord = possiblyCorrectWord

    def __unicode__(self):
        if self.possiblyCorrectWord:
            return u"No thesaurus results for word '{0}'. Did you mean '{1}'?".format(self.word, self.possiblyCorrectWord)
        else:
            return u"No thesaurus results for word '{0}'. Did you possibly misspell it?".format(self.word)


class ThesaurusRequestError(ThesaurusException):
    """Exception raised when a connection to thesaurus.com couldn't be made."""

    def __init__(self, error):
        super(ThesaurusRequestError, self).__init__(error)

    def __unicode__(self):
        return u"Error connecting to thesaurus.com :\n{0}\n".format(self.error)
