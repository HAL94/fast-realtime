from datetime import datetime, timedelta, timezone


def date_to_timestamp(date_string: str):
  """
  Converts a date string in "%Y-%m-%d" format to a Unix timestamp (seconds since epoch, UTC).

  Args:
    date_string: The date string to convert.

  Returns:
    A float representing the Unix timestamp, or None if the input is invalid.
  """
  try:
    date_object = datetime.strptime(date_string, "%Y-%m-%d").date()
    datetime_object = datetime.combine(date_object, datetime.min.time())
    datetime_utc = datetime_object.replace(tzinfo=timezone.utc)
    timestamp = datetime_utc.timestamp()
    return timestamp
  except ValueError:
    return None  # Handle cases where the input string is not in the correct format


def timestamp_to_date(timestamp: int | float):
  """
  Converts a Unix timestamp (seconds since epoch) to a date string in "%Y-%m-%d" format.

  Args:
    timestamp: The Unix timestamp (float or integer).

  Returns:
    A string representing the date in "%Y-%m-%d" format, or None if the input is invalid.
  """
  try:
    # Convert the timestamp to a timezone-aware datetime object (UTC)
    datetime_utc = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    # Convert the UTC datetime to the local timezone (Saudi Arabia)
    datetime_local = datetime_utc.astimezone(timezone(timedelta(hours=3)))
    # Format the datetime object as a date string
    date_string = datetime_local.strftime("%Y-%m-%d")
    return date_string
  except TypeError:
    return None  # Handle cases where the input is not a valid timestamp