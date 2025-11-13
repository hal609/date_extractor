import re
from .datetime_extraction_classes import *

date_time_patterns_dict = {
    # 1. Full/Abbreviated Day Names (e.g., Mon, Monday)
    re.compile(r'\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b', re.IGNORECASE): IndicatorType.DAY,

    # 2. Full/Abbreviated Month Names (e.g., Jan, January)
    re.compile(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)\b', re.IGNORECASE): IndicatorType.MONTH,

    # 3. Numeric Dates (e.g., 12/31/2025, 2025-12-31, 12.31.25)
    # Matches common DD/MM/YYYY, MM-DD-YY, or YYYY.MM.DD formats
    re.compile(r'\b\d{1,4}[-/.\\]\d{1,2}[-/.\\]\d{2,4}\b'): IndicatorType.DATE,

    # 4. Standalone Years (e.g., 1999, 2024)
    re.compile(r'\b(?:19|20)\d{2}\b'): IndicatorType.YEAR,

    # 5. Times (e.g., 10:30, 10:30:45)
    re.compile(r'\b\d{1,2}:\d{2}(?::\d{2})?\b'): IndicatorType.TIME,

    # 6. AM/PM Indicators (e.g., 10:30 am, 10 am, 5PM)
    re.compile(r'\b\d{1,2}(?::\d{2})?\s?(?:am|pm)\b', re.IGNORECASE): IndicatorType.TIME,

    # 7. Ordinal Dates (e.g., 1st, 22nd, 30th)
    re.compile(r'\b\d{1,2}(?:st|nd|rd|th)\b', re.IGNORECASE): IndicatorType.DAY,

    re.compile(r'\b(?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth|thirteenth)\b', re.IGNORECASE): IndicatorType.DAY,

    # 8. Relative/Descriptive Time Words (e.g., today, tomorrow, ago, noon)
    re.compile(r'\b(?:noon|midnight|o\'clock|ago|now)\b', re.IGNORECASE): IndicatorType.TIME,

    re.compile(r'\b(?:today|tomorrow|yesterday|later|next day|same day|that day|following day|day later)\b', re.IGNORECASE): IndicatorType.DAY,

    # Match a given number of days later/after
    re.compile(r'\b(?:(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+day[s]?\s+(?:later|after))\b', re.IGNORECASE): IndicatorType.DAY,

    # 9. Time Zones (e.g., UTC, EST, PDT)
    re.compile(r'\b(?:GMT|UTC|EST|PST|CST|EDT|PDT|CDT)\b', re.IGNORECASE): IndicatorType.TIME
}

def find_date_time_indicators(text):
    found_list = []
    for pattern in date_time_patterns_dict.keys():
        matches = pattern.findall(text)
        for match in matches:
            found_list.append(DateIndicator(match, 0, date_time_patterns_dict[pattern]))

    return found_list


def find_dates(text):
    # Check for multiples of the same token
    token_counts = {}
    found_indicators = find_date_time_indicators(text)
    if len(found_indicators) == 0: return []
    
    found_tokens = [indicator.token for indicator in found_indicators]
    for entry in found_tokens:
        token_counts[entry] = found_tokens.count(entry)

    token_running_counts = {}
    for token in token_counts.keys():
        token_running_counts[token] = 0

    words = text.split()

    tokens = []
    for indicator in found_indicators:
        token, token_type = indicator.token, indicator.time_type

        for i, w in enumerate(words):
            w_to_check = w
            num_words = token.count(" ") + 1
            if num_words == 2:
                if i != len(words) - 1:
                    w_to_check = words[i] + " " + words[i + 1]
            if num_words == 3:
                if i != len(words) - 2:
                    w_to_check = words[i] + " " + words[i + 1] + " " + words[i + 2]
            if token in w_to_check:
                if token_running_counts[token] == token_counts[token]: break
                token_running_counts[token] += 1
                tokens.append(DateIndicator(token, i, token_type))
                if token_running_counts[token] == token_counts[token]: break
    

    groups = group_tokens(text, tokens)
    formatted_groups = format_token_groups(groups)

    return formatted_groups

def group_tokens(text, tokens):
    words = text.split()

    # Define connecting words that can bridge gaps of 2
    connecting_words = {"of", "the", "at", "on", "in"}

    # Sort tokens by position
    sorted_tokens = sorted(tokens, key=lambda x: x.pos)

    groups = []
    current_group = [sorted_tokens[0]]

    for i in range(1, len(sorted_tokens)):
        prev_token = sorted_tokens[i - 1]
        curr_token = sorted_tokens[i]
        distance = curr_token.pos - prev_token.pos
        
        # If the last token had multiple words then the distance gets thrown off
        # so subtract the number of spaces to compensate
        last_token_space_count = prev_token.token.count(" ")
        distance -= last_token_space_count

        # Check for full stops in previous words and if so, always break the current group
        previous_token_words = " ".join(words[prev_token.pos:prev_token.pos+last_token_space_count+1])
        if "." in previous_token_words: distance = 99
        
        if distance == 1:
            # Adjacent → same group
            current_group.append(curr_token)
        elif distance == 2:
            # Check if the in-between word is a connecting word
            between_word = words[prev_token.pos + last_token_space_count + 1]
            if between_word.lower() in connecting_words:
                current_group.append(curr_token)
            else:
                groups.append(sorted(current_group))
                current_group = [curr_token]
        else:
            # Too far apart → new group
            groups.append(sorted(current_group))
            current_group = [curr_token]

    # Add last group
    if current_group:
        groups.append(sorted(current_group))

    return groups

def has_date(group):
    for entry in group:
        if entry.time_type == IndicatorType.DATE:
            return True
    return False

def get_date(group):
    for entry in group:
        if entry.time_type == IndicatorType.DATE:
            return entry.token
    return ""
        
def has_year(group):
    for entry in group:
        if entry.time_type == IndicatorType.YEAR:
            return True
    return False

def get_year(group):
    for entry in group:
        if entry.time_type == IndicatorType.YEAR:
            return entry.token
    return ""
        
def has_month(group):
    for entry in group:
        if entry.time_type == IndicatorType.MONTH:
            return True
    return False

def get_month(group):
    for entry in group:
        if entry.time_type == IndicatorType.MONTH:
            return entry.token
    return ""

def has_day(group):
    for entry in group:
        if entry.time_type == IndicatorType.DAY:
            return True
    return False

def get_day(group):
    for entry in group:
        if entry.time_type == IndicatorType.DAY:
            return entry.token
    return ""
        
def has_time(group):
    for entry in group:
        if entry.time_type == IndicatorType.TIME:
            return True
    return False

def get_time(group):
    for entry in group:
        if entry.time_type == IndicatorType.TIME:
            return entry.token
    return ""
        
def get_all_years(groups):
    years = []
    for group in groups:
        years.append(get_year(group))
    return years

def format_token_groups(groups):
    year = "0000"
    month = "00"
    day = "00"
    time = ""

    formatted_groups = []

    for group in groups:
        if has_date(group):
            formatted_groups.append(get_date(group))
            continue
        if has_year(group):
            year = get_year(group)
        if has_month(group):
            month = get_month(group)
        if has_day(group):
            new_day = get_day(group)
            offset_match = re.match(
                r'(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+day[s]?\s+(later|after)', 
                new_day, 
                re.IGNORECASE
            )
            if new_day in ["that day", "same day"]:
                continue
            elif new_day in ["next day", "following day", "day after", "day later"]:
                
                if day.isnumeric():
                    day = f"{int(day)+1:02}"
                else: # If previous day was a weekday e.g. "Saturday" then
                    if is_day_of_the_week(day):
                        day = days_of_the_week[days_of_the_week.index(day.lower()) + 1].capitalize()

            elif offset_match:
                number_str = offset_match.group(1)
                
                # Determine the offset value
                if number_str.isdigit():
                    offset = int(number_str)
                else:
                    offset = number_map[number_str]
                    
                if offset is not None:
                    day = f"{int(day)+offset:02}"
            else:
                day = new_day

        if has_time(group):
            time = get_time(group)
        
        if day.lower() in date_dict.keys():
            day = date_dict[day.lower()]
        
        composite_datetime = f"{year}-{month_dict[month.lower()]}-{day} {time}"

        # Clear trailing formatting characters
        if composite_datetime[-1] in [" ", "-"]:
            composite_datetime = composite_datetime[:-1]
        # Clear leading formatting characters
        if composite_datetime[0] in [" ", "-"]:
            composite_datetime = composite_datetime[1:]

        # Add formatted datetime string to list
        formatted_groups.append(composite_datetime)


    return formatted_groups