import re


def _int_or_none(text):
    if text == "":
        return None
    else:
        return int(text)


class Range:
    """An inclusive range of indices."""

    RANGE_RE = re.compile(
        r"""
        ^
        (?:
            (?P<index>0|-?[1-9][0-9]*)|
            (?P<start>|0|-?[1-9][0-9]*):(?P<end>|0|-?[1-9][0-9]*)
        )
        $
        """,
        re.VERBOSE
    )

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __str__(self):
        return f"[{self.start}, {self.end}]"

    def extract(self, staged, unstaged):
        start = 0 if self.start is None else self.start
        end = len(unstaged) if self.end is None else self.end + 1

        start_is_greater_than_end = start is not None and end is not None and start > end
        if (start >= len(unstaged) or end > len(unstaged) or
                start < -len(staged) or end < -len(staged) or
                start_is_greater_than_end):
            raise IndexError()

        extracted_staged = []
        if start < 0:
            staged_end = len(staged) if end > -1 else end
            extracted_staged = staged[start:staged_end]

        return extracted_staged + unstaged[max(start, 0):max(end, 0)]

    @classmethod
    def parse(cls, text):
        match = cls.RANGE_RE.match(text)
        if match:
            if match.group("index"):
                return cls(int(match.group("index")), int(match.group("index")))
            else:
                return cls(
                    _int_or_none(match.group("start")), _int_or_none(match.group("end"))
                )

        raise ValueError(f"invalid range specifier: {text!r}")
