import re
from copy import deepcopy

from .extraction_classes import (
    DateIndicator,
    IndicatorType,
    date_dict,
    days_of_the_week,
    month_dict,
    number_map,
    twenty_four_hour_time_dict,
)

date_time_patterns_dict = {
    # 1. Full/Abbreviated Day Names (e.g., Mon, Monday)
    re.compile(
        r"\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b", re.IGNORECASE
    ): IndicatorType.WEEKDAY,
    # 2. Full/Abbreviated Month Names (e.g., Jan, January)
    re.compile(
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)\b",
        re.IGNORECASE,
    ): IndicatorType.MONTH,
    # 3. Numeric Dates (e.g., 12/31/2025, 2025-12-31, 12.31.25)
    # Matches common DD/MM/YYYY, MM-DD-YY, or YYYY.MM.DD formats
    re.compile(r"\b\d{1,4}[-/.\\]\d{1,2}[-/.\\]\d{2,4}\b"): IndicatorType.DATE,
    # 4. Standalone Years (e.g., 1999, 2024)
    re.compile(r"\b(?:19|20)\d{2}\b"): IndicatorType.YEAR,
    # 5. Times (e.g., 10:30, 10:30:45) + AM/PM Indicators (e.g., 10:30 am, 10 am, 5PM)
    re.compile(
        r"\b\d{1,2}(?::\d{2})?\s?(?:am|pm)\b"  # Match times in the format XX:XX
        + r"|"  # OR
        + r"\b\d{1,2}:\d{2}(?::\d{2})?\b",  # Match times in the format XXpm, XX am, etc.
        re.IGNORECASE,
    ): IndicatorType.TIME,
    # 7. Ordinal Dates (e.g., 1st, 22nd, 30th)
    re.compile(r"\b\d{1,2}(?:st|nd|rd|th)\b", re.IGNORECASE): IndicatorType.DAY,
    re.compile(
        r"\b(?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth|thirteenth)\b",
        re.IGNORECASE,
    ): IndicatorType.DAY_WORD,
    # 8. Relative/Descriptive Time Words (e.g., today, tomorrow, ago, noon)
    re.compile(r"\b(?:noon|midnight|o\'clock|ago|now)\b", re.IGNORECASE): IndicatorType.TIME,
    re.compile(
        r"\b(?:today|tomorrow|yesterday|later|(?:following|next|subsequent|same|that|this) (?:day|morning|evening|afternoon|night)|day later)\b",
        re.IGNORECASE,
    ): IndicatorType.DAY,
    # Match a given number of days later/after
    re.compile(
        r"\b(?:(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+day[s]?\s+(?:later|after))\b", re.IGNORECASE
    ): IndicatorType.DAY,
    # 9. Time Zones (e.g., UTC, EST, PDT)
    re.compile(r"\b(?:GMT|UTC|EST|PST|CST|EDT|PDT|CDT)\b", re.IGNORECASE): IndicatorType.TIME,
}


def find_date_time_indicators(text: str) -> list[DateIndicator]:
    found_list = []
    for pattern in date_time_patterns_dict:
        matches = pattern.findall(text)
        for match in matches:
            found_list.append(DateIndicator(match, 0, date_time_patterns_dict[pattern]))

    return found_list


def strip_dates(text: str) -> str:
    """Function to remove all date/time indicators from a text sample.

    Args:
        text (str): Text block to strip.

    Returns:
        str: Text block with dates/times removed.

    Examples:
        This can be used to get raw text once dates have been extracted.

        >>> strip_dates("Jan 1st 2012: A thing happened.")
        A thing happened.
    """
    stripped_text = deepcopy(text)
    for pattern in date_time_patterns_dict:
        stripped_text = pattern.sub("", stripped_text)

    stripped_text = stripped_text.replace("  ", " ")
    stripped_text = stripped_text.replace(" ,", "")
    stripped_text = stripped_text.replace(" :", "")
    stripped_text = stripped_text.replace(" .", ".")
    return stripped_text.replace("  ", " ")


def find_dates(text: str) -> list[tuple[str, int]]:
    """Returns a list of tuples comprising the located date and the
    word index at which it was found.

    Args:
        text (str): The corpus of text in which to find dates/times.

    Returns:
        list[tuple[str, int]]: A list of tuples containing a string
            representing the date and time and an integer word index at
            which it was found.

    Examples:
        Get dates from a text sample.

        >>> find_dates("A thing happened on Jan 1st 2012 and the next morning at 09:15 and also jan 15th at 12am in 2018.")
        [
            ('2012-01-01', 4),
            ('2012-01-02 09:15', 9),
            ('2018-01-15 12:00', 15)
        ]
    """
    # Check for multiples of the same token
    token_counts = {}
    found_indicators = find_date_time_indicators(text)
    if len(found_indicators) == 0:
        return []

    found_tokens = [indicator.token for indicator in found_indicators]
    for entry in found_tokens:
        token_counts[entry] = found_tokens.count(entry)

    token_running_counts = {}
    for token in token_counts:
        token_running_counts[token] = 0

    words = text.split()

    tokens = []
    located_positions = set()

    for indicator in found_indicators:
        token, token_type = indicator.token, indicator.time_type

        for i, _w in enumerate(words):
            # Skip previously matched entries to prevent collisions
            if i in located_positions:
                continue

            # If the token has multiple words then check sequences of that number of words
            num_words = token.count(" ") + 1

            # Although it looks like this will overflow the words list, python just handles trying to slice beyond the end
            w_to_check = " ".join(words[i : i + num_words])

            # Strip extra characters to ensure indicators are located correctly in text recognition
            w_to_check = w_to_check.replace(".", "")
            w_to_check = w_to_check.replace(",", "")
            # w_to_check = w_to_check.replace(" ", "")

            if token == w_to_check:
                if token_running_counts[token] == token_counts[token]:
                    break
                token_running_counts[token] += 1
                located_positions.add(i)
                tokens.append(DateIndicator(token, i, token_type))
                if token_running_counts[token] == token_counts[token]:
                    break
    groups = group_tokens(text, tokens)
    formatted_groups = format_token_groups(groups)

    return formatted_groups


def group_tokens(text: str, tokens: list[DateIndicator]) -> list[list[DateIndicator]]:
    words = text.split()

    connecting_patterns = {
        "SINGLE_WORD": r"^(of|the|at|on|in|around|after|about|from|before|almost)$",
        "TWO_WORD": r"^(at|just|nearly|about|abouts|after|before)\s+(around|about|abouts|approximately|nearly|almost|past|before|from)",
        "IN_FROM_ETC": r"^in(\s+the)?(\s+(early|late|mid))?(\s+(morning|afternoon|evening))?(\s+(just|approximately))?(\s+(from|after|around|at))$",
        "EXPRNAME": r"^in(\s+the)?(\s+(early|late|mid))?\s+(hours|morning|afternoon|evening|night)\s+of$",
        # Phrases e.g. "at roughly the late afternoon", or "in the evening"
        "PREP_TIME_OF": r"^(in|on|at|by|around|about)(\s+(roughly|approximately|about|around))?(\s+the)?(\s+(early|late|mid))?\s+(hours|morning|afternoon|evening|night)(\s+of|of the|from)?$",
        # Concept: Pinpointing a time relative to a larger block.
        # Example Phrases: "at the start of the day", "by the end of the week".
        "START_END_OF": r"^(at|by|near)\s+the\s+(start|beginning|end)(\s+of)?(\s+the)?$",
        # "RANGE_TO": r"^(to|until|through|thru)$",
        # "RANGE_AND": r"^(and|&)$",
        "TIME_OF": r"^(morning|afternoon|evening|night)\s+of$",
        "OF_THE_ETC": r"^of\s+(the|this|next|last)$",
        "OF_THE_SIMPLE": r"^of\s+the$",
        "DAY_RELATIVE": r"^(day|week|month|year)\s+(before|after)$",
        "THE_DAY_RELATIVE": r"^the\s+(day|week|month)\s+(before|after)$",
        "ON_THE": r"^on\s+the$",
        "IN_THE": r"^in\s+the$",
    }

    # Sort tokens by position
    sorted_tokens = sorted(tokens, key=lambda x: x.pos)
    groups = []
    current_group = [sorted_tokens[0]]

    for i in range(1, len(sorted_tokens)):
        prev_token = sorted_tokens[i - 1]
        curr_token = sorted_tokens[i]
        distance = curr_token.pos - prev_token.pos

        # If the last token had multiple words then the distance gets thrown off
        # so subtract the numbfind_dateser of spaces to compensate
        last_token_space_count = prev_token.token.count(" ")
        distance -= last_token_space_count

        # Check for full stops in previous words and if so, always break the current group
        previous_token_words = " ".join(words[prev_token.pos : prev_token.pos + last_token_space_count + 1])
        if "." in previous_token_words:
            distance = 99

        if distance == 1:
            # Adjacent so same group
            current_group.append(curr_token)
        elif distance <= 10:  # Max distance to check for connecting words/phrases
            # Check if the in-between word is a connecting word
            end_of_prev_token = prev_token.pos + last_token_space_count + 1
            between_words = words[end_of_prev_token : end_of_prev_token + distance - 1]
            between_words_str = " ".join(between_words).lower()
            is_connecting = False
            for pattern in connecting_patterns.values():
                # re.match() checks if the pattern matches from the *start* of the string.
                # Since we use ^ and $ anchors, it ensures the *entire* string matches.
                if re.match(pattern, between_words_str):
                    is_connecting = True
                    break  # Found a match, no need to check other patterns
            if is_connecting:
                current_group.append(curr_token)
            else:
                groups.append(sorted(current_group))
                current_group = [curr_token]
        else:
            # Too far apart so new group
            groups.append(sorted(current_group))
            current_group = [curr_token]

    # Add last group
    if current_group:
        groups.append(sorted(current_group))

    return groups


def time_formatter(time_string: str) -> str:
    time_string = time_string.replace(" ", "")

    if time_string in twenty_four_hour_time_dict:
        time_string = twenty_four_hour_time_dict[time_string]

    hours_add = 0
    if "pm" in time_string.lower():
        hours_add = 12

    time_string = time_string.replace("am", "")
    time_string = time_string.replace("pm", "")

    split = time_string.split(":")
    for i, part in enumerate(split):
        if not part.isnumeric():
            split[i] = ""

    hours = split[0]
    if len(hours) == 0:
        return ""

    mins = "00"

    if len(split) > 1:
        mins = split[1]

    hours_num = (int(hours) + hours_add) % 24

    return f"{hours_num:02}:{(mins):02}"


def strip_leading_trailing_chars(datetime_string: str) -> str:
    strip_chars = [" ", "-"]
    while datetime_string[-1] in strip_chars:
        datetime_string = datetime_string[:-1]
    while datetime_string[0] in strip_chars:
        datetime_string = datetime_string[1:]

    return datetime_string


def compose_dt(year: str, month: str, day: str, weekday: str, time: str) -> str:
    composite_date = f"{year}-{month.lower()}-{day}"
    composite_date = strip_leading_trailing_chars(composite_date)

    composite_datetime = f"{weekday} {composite_date} {time_formatter(time)}"
    composite_datetime = strip_leading_trailing_chars(composite_datetime)

    return composite_datetime


def update_day(day: str, new_day: str, weekday: str) -> tuple[str, str]:
    offset_match = re.match(
        r"(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+day[s]?\s+(later|after)", new_day, re.IGNORECASE
    )

    # Skip updating the day if the token indicates the day is the same as the previous
    if re.match(r"(?:that|same|this) (?:day|morning|afternoon|night|evening)|today|earlier on", new_day, re.IGNORECASE):
        return day, weekday
    # Increment the day if the token indicates it refers to the day after
    elif re.match(
        r"(?:next|following|subsequent) (?:day|morning|afternoon|night|evening)|day after", new_day, re.IGNORECASE
    ):
        if weekday.lower() in days_of_the_week:
            day_index = days_of_the_week.index(weekday.lower())
            next_day_index = (day_index + 1) % 7
            weekday = days_of_the_week[next_day_index].capitalize()
        return f"{int(day) + 1:02}", weekday
    # If token indicates a greater number of days later
    elif offset_match:
        number_str = offset_match.group(1)

        # Determine the offset value
        offset = int(number_str) if number_str.isdigit() else number_map[number_str]

        if offset is not None:
            return f"{int(day) + offset:02}", ""
    # Otherwise just return new day and clear weekday
    else:
        return new_day, ""


def has_token_type(group: list[DateIndicator], tok_type: IndicatorType) -> bool:
    return any(entry.time_type == tok_type for entry in group)


def get_token_type(group: list[DateIndicator], tok_type: IndicatorType) -> str:
    for entry in group:
        if entry.time_type == tok_type:
            return entry.token
    return ""


def update_next_datetime(
    group: list[DateIndicator], year: str, month: str, day: str, weekday: str, time: str
) -> tuple[str, str, str, str, str]:
    if has_token_type(group, IndicatorType.YEAR):
        new_year = get_token_type(group, IndicatorType.YEAR)
        # If the next date is in a new year then reset all lower level info e.g. month and day and update year
        if new_year != year:
            month = "00"
            day = "00"
            weekday = ""
            time = ""
            year = new_year

    if has_token_type(group, IndicatorType.MONTH):
        new_month = get_token_type(group, IndicatorType.MONTH)
        # If the next date is in a new month then reset all lower level info e.g. day, and update month
        if new_month != month:
            day = "00"
            weekday = ""
            time = ""
            month = new_month

    if has_token_type(group, IndicatorType.DAY):
        new_day = get_token_type(group, IndicatorType.DAY)
        # If day has changed then clear out previous time
        if new_day != day:
            time = ""
        day, weekday = update_day(day, new_day, weekday)

    time = get_token_type(group, IndicatorType.TIME) if has_token_type(group, IndicatorType.TIME) else time

    if day.lower() in date_dict:
        day = date_dict[day.lower()]

    if has_token_type(group, IndicatorType.WEEKDAY):
        weekday = get_token_type(group, IndicatorType.WEEKDAY)

    if month.lower() in month_dict:
        month = month_dict[month.lower()]

    return year, month, day, weekday, time


def format_token_groups(groups: list[list[DateIndicator]]) -> list[tuple[str, int]]:
    year = ""
    month = "00"
    day = "00"
    weekday = ""
    time = ""

    formatted_groups = []
    group_start_locations = []

    for group in groups:
        # If a group contains only a day word e.g. first second third then it is
        # likely not actually indicating a date and that group should be removed
        # to prevent erroneously matching phrases such as: "the second time I went"
        if len(group) == 1 and group[0].time_type == IndicatorType.DAY_WORD:
            continue

        group_start_locations.append(min([token.pos for token in group]))

        if has_token_type(group, IndicatorType.DATE):
            formatted_groups.append(get_token_type(group, IndicatorType.DATE))
            continue

        year, month, day, weekday, time = update_next_datetime(group, year, month, day, weekday, time)

        formatted_groups.append(compose_dt(year, month, day, weekday, time))

    return list(zip(formatted_groups, group_start_locations))
