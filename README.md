---
title: Parse dates and times from text
description: A Python module to fuzzy extract dates from a corpus of text.
---

# date-extractor

[![Release](https://img.shields.io/github/v/release/hal609/date-extractor)](https://img.shields.io/github/v/release/hal609/date-extractor)
[![Build status](https://img.shields.io/github/actions/workflow/status/hal609/date-extractor/main.yml?branch=main)](https://github.com/hal609/date-extractor/actions/workflows/main.yml?query=branch%3Amain)
[![Commit activity](https://img.shields.io/github/commit-activity/m/hal609/date-extractor)](https://img.shields.io/github/commit-activity/m/hal609/date-extractor)
[![License](https://img.shields.io/github/license/hal609/date-extractor)](https://img.shields.io/github/license/hal609/date-extractor)


# date-extractor for Python 🗓️
## What Is date-extractor?
Lightweight Python package to fuzzy extract dates from a corpus of text.

## Installation

```
pip install date_extractor
```

## Usage

```python
from date_extractor import find_dates

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
