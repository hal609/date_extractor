import re
from .datetime_extraction_classes import *

date_time_patterns_dict = {
    # 1. Full/Abbreviated Day Names (e.g., Mon, Monday)
    re.compile(r'\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b', re.IGNORECASE): IndicatorType.WEEKDAY,

    # 2. Full/Abbreviated Month Names (e.g., Jan, January)
    re.compile(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)\b', re.IGNORECASE): IndicatorType.MONTH,

    # 3. Numeric Dates (e.g., 12/31/2025, 2025-12-31, 12.31.25)
    # Matches common DD/MM/YYYY, MM-DD-YY, or YYYY.MM.DD formats
    re.compile(r'\b\d{1,4}[-/.\\]\d{1,2}[-/.\\]\d{2,4}\b'): IndicatorType.DATE,

    # 4. Standalone Years (e.g., 1999, 2024)
    re.compile(r'\b(?:19|20)\d{2}\b'): IndicatorType.YEAR,

    # 5. Times (e.g., 10:30, 10:30:45) + AM/PM Indicators (e.g., 10:30 am, 10 am, 5PM)
    re.compile(
        r'\b\d{1,2}(?::\d{2})?\s?(?:am|pm)\b' + # Match times in the format XX:XX
        r'|' + # OR
        r'\b\d{1,2}:\d{2}(?::\d{2})?\b', # Match times in the format XXpm, XX am, etc.
        re.IGNORECASE): IndicatorType.TIME,

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

def time_formatter(time_string: str):
    time_string = time_string.replace(" ", "")
    
    if time_string in twenty_four_hour_time_dict.keys():
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

    hours = (int(hours)+hours_add)%24
    
    return f"{hours:02}:{(mins):02}"

        
def has_token_type(group, type: IndicatorType):
    for entry in group:
        if entry.time_type == type:
            return True
    return False

def get_token_type(group, type: IndicatorType):
    for entry in group:
        if entry.time_type == type:
            return entry.token
    return ""

def format_token_groups(groups):
    year = "0000"
    month = "00"
    day = "00"
    weekday = ""
    time = ""

    formatted_groups = []

    for group in groups:

        if has_token_type(group, IndicatorType.DATE):
            formatted_groups.append(get_token_type(group, IndicatorType.DATE))
            continue
        if has_token_type(group, IndicatorType.YEAR):
            new_year = get_token_type(group, IndicatorType.YEAR)
            # If the next date is in a new year then reset all lower level info e.g. month and day and update year
            if new_year != year: 
                month = ""
                day = ""
                time = ""
                year = new_year

        if has_token_type(group, IndicatorType.MONTH):
            new_month = get_token_type(group, IndicatorType.MONTH)
            # If the next date is in a new month then reset all lower level info e.g. day, and update month
            if new_month != month:
                day = ""
                time = ""
                month = new_month

        if has_token_type(group, IndicatorType.DAY):
            new_day = get_token_type(group, IndicatorType.DAY)
            
            # If day has changed then clear out previous time
            if new_day != day:
                time = ""

            offset_match = re.match(
                r'(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+day[s]?\s+(later|after)', 
                new_day, 
                re.IGNORECASE
            )
            if new_day in ["that day", "same day"]:
                continue
            elif new_day in ["next day", "following day", "day after", "day later"]:
                day = f"{int(day)+1:02}"
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

        if has_token_type(group, IndicatorType.TIME):
            time = get_token_type(group, IndicatorType.TIME)
        
        if day.lower() in date_dict.keys():
            day = date_dict[day.lower()]

        weekday = get_token_type(group, weekday)

        if month.lower() in month_dict.keys():
            month = month_dict[month.lower()]
        composite_datetime = f"{weekday} {year}-{month.lower()}-{day} {time_formatter(time)}"

        while composite_datetime[-1] in [" ", "-"]:
            composite_datetime = composite_datetime[:-1]
        while composite_datetime[0] in [" ", "-"]:
            composite_datetime = composite_datetime[1:]

        formatted_groups.append(composite_datetime)


    return formatted_groups