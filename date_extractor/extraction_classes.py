from enum import Enum


class IndicatorType(Enum):
    DATE = 0
    YEAR = 1
    MONTH = 2
    DAY = 3
    DAY_WORD = 4  # e.g. First, Second, Third
    WEEKDAY = 5  # e.g. Monday, Tuesday, Wednesday
    TIME = 6


# Class to store data about each token
class DateIndicator:
    def __init__(self, tok: str, position: int, time_type: IndicatorType):
        self.token: str = tok
        self.pos: int = position
        self.time_type: IndicatorType = time_type

    def check_type(self) -> None:
        print(self.time_type, type(self.time_type))

    def __str__(self) -> str:
        return f"({self.token}, loc: {self.pos}, time_type: '{self.time_type}')"

    def __repr__(self) -> str:
        return self.__str__()

    def __lt__(self, other: "DateIndicator") -> bool:
        return self.time_type.value < other.time_type.value

    def __gt__(self, other: "DateIndicator") -> bool:
        return self.time_type.value > other.time_type.value

    def __le__(self, other: "DateIndicator") -> bool:
        return self.time_type.value <= other.time_type.value

    def __ge__(self, other: "DateIndicator") -> bool:
        return self.time_type.value >= other.time_type.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DateIndicator):
            return NotImplemented
        return self.time_type.value == other.time_type.value

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, DateIndicator):
            return NotImplemented
        return self.time_type.value != other.time_type.value


month_dict = {
    "january": "01",
    "jan": "01",
    "february": "02",
    "feb": "02",
    "march": "03",
    "mar": "03",
    "april": "04",
    "apr": "04",
    "may": "05",
    "jun": "06",
    "june": "06",
    "jul": "07",
    "july": "07",
    "august": "08",
    "aug": "08",
    "september": "09",
    "sep": "09",
    "october": "10",
    "oct": "10",
    "november": "11",
    "nov": "11",
    "december": "12",
    "dec": "12",
}

date_dict = {
    "first": "01",
    "second": "02",
    "third": "03",
    "fourth": "04",
    "fifth": "05",
    "sixth": "06",
    "seventh": "07",
    "eighth": "08",
    "ninth": "09",
    "tenth": "10",
    "eleventh": "11",
    "twelfth": "12",
    "thirteenth": "13",
    "1st": "01",
    "2nd": "02",
    "3rd": "03",
    "4th": "04",
    "5th": "05",
    "6th": "06",
    "7th": "07",
    "8th": "08",
    "9th": "09",
    "10th": "10",
    "11th": "11",
    "12th": "12",
    "13th": "13",
    "14th": "14",
    "15th": "15",
    "16th": "16",
    "17th": "17",
    "18th": "18",
    "19th": "19",
    "20th": "20",
    "21st": "21",
    "22nd": "22",
    "23rd": "23",
    "24th": "24",
    "25th": "25",
    "26th": "26",
    "27th": "27",
    "28th": "28",
    "29th": "29",
    "30th": "30",
    "31st": "31",
}

number_map = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}

days_of_the_week = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]

twenty_four_hour_time_dict = {
    "0100": "01:00",
    "0200": "02:00",
    "0300": "03:00",
    "0400": "04:00",
    "0500": "05:00",
    "0600": "06:00",
    "0700": "07:00",
    "0800": "08:00",
    "0900": "09:00",
    "1000": "10:00",
    "1100": "11:00",
    "1200": "12:00",
    "1300": "13:00",
    "1400": "14:00",
    "1500": "15:00",
    "1600": "16:00",
    "1700": "17:00",
    "1800": "18:00",
    "1900": "19:00",
    "2000": "20:00",
    "2100": "21:00",
    "2200": "22:00",
    "2300": "23:00",
    "2400": "24:00",
}


def is_day_of_the_week(text: str) -> bool:
    return text.lower() in days_of_the_week
