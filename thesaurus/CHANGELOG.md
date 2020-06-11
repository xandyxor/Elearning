# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.2.3] - 2018-12-16
### Added
- Custom exceptions for when we can't connect to thesaurus (`ThesaurusRequestError`), it doesn't have our word (`WordNotFoundError`), or it thinks we've made a misspelling (`MisspellingError`).

### Changed
- Previously, we didn't throw exceptions. We do now.
- The url we fetch is https instead of http. Their DNS person screwed us.
