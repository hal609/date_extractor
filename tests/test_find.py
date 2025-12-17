from date_extractor import find_dates


def test_find():
    text = "A thing happened on Jan 1st 2012 and the next morning at 09:15 and also jan 15th at 12am in 2018."
    found_dates = find_dates(text)

    expected_out = [("2012-01-01", 4), ("2012-01-02 09:15", 9), ("2018-01-15 12:00", 15)]

    assert found_dates == expected_out
