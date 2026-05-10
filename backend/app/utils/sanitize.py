"""Input sanitization — strips HTML tags from user-supplied text fields."""
import re

_HTML_TAG_RE = re.compile(r"<[^>]*>")


def strip_html(value: str | None) -> str | None:
    """Remove HTML tags from a string. Returns None if input is None."""
    if value is None:
        return None
    return _HTML_TAG_RE.sub("", value)
