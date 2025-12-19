# date-fuzz

[![Release](https://img.shields.io/github/v/release/hal609/date-fuzz)](https://img.shields.io/github/v/release/hal609/date-fuzz)
[![Build status](https://img.shields.io/github/actions/workflow/status/hal609/date-fuzz/main.yml?branch=main)](https://github.com/hal609/date-fuzz/actions/workflows/main.yml?query=branch%3Amain)
[![Commit activity](https://img.shields.io/github/commit-activity/m/hal609/date-fuzz)](https://img.shields.io/github/commit-activity/m/hal609/date-fuzz)
[![License](https://img.shields.io/github/license/hal609/date-fuzz)](https://img.shields.io/github/license/hal609/date-fuzz)


# date-fuzz for Python 🗓️
## What Is date-fuzz?
Lightweight Python package to fuzzy extract dates from a corpus of text.

## Installation

```
pip install date_fuzz
```

## Usage

```python
from date_fuzz import find_dates

text = "A thing happened on Jan 1st 2012 and the next morning at 09:15 and also jan 15th at 12am in 2018."
dates = find_dates(text)
print(dates)

# Output
[
    ('2012-01-01', 4),
    ('2012-01-02 09:15', 9),
    ('2018-01-15 12:00', 15)
]
```
