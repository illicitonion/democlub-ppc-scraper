import re

from dataclasses import dataclass


@dataclass
class Candidate:
    href: str
    constituency: str
    name: str

    def has_name(self, name):
        def split(s):
            parts = re.split(" |-", s.strip().lower().replace("’", "'"))
            if parts[0] == "dr":
                parts = parts[1:]
            if parts[0] == "robbie":
                parts[0] = "robert"
            if parts[-1] == "mp":
                parts = parts[:-1]
            return parts

        self_name_parts = split(self.name)
        other_name_parts = split(name)
        if not self_name_parts or not other_name_parts:
            return False
        if self_name_parts[-1] != other_name_parts[-1]:
            return False
        return self_name_parts[0] in other_name_parts[0] or other_name_parts[0] in self_name_parts[0]


def constituency_to_dc_id(constituency):
    return f"parl.{constituency.lower().replace(' ', '-').replace(',', '').replace('&', 'and').replace('ô', 'o')}.next"
