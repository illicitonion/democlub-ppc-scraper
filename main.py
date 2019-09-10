import csv
from collections import defaultdict

import green
import labour
import libdem

import requests

from common import constituency_to_dc_id

constituency_to_party_to_candidate = defaultdict(dict)

for candidate in labour.get_candidates():
    constituency_to_party_to_candidate[constituency_to_dc_id(candidate.constituency)]["PP53"] = candidate

for candidate in green.get_candidates():
    constituency_to_party_to_candidate[constituency_to_dc_id(candidate.constituency)]["PP63"] = candidate

for candidate in libdem.get_candidates():
    constituency_to_party_to_candidate[constituency_to_dc_id(candidate.constituency)]["PP90"] = candidate


response = requests.get(
    "https://docs.google.com/spreadsheets/d/1cHlm1irk7FFqPKO6jTgBh9Ya5k_erWGIH7AP65nkWCc/export?format=csv&id=1cHlm1irk7FFqPKO6jTgBh9Ya5k_erWGIH7AP65nkWCc&gid=0"
)
response.encoding = "utf-8"

democlub_constituencies = set()
reader = csv.reader(response.iter_lines(decode_unicode=True))
for line in reader:
    if not line:
        continue
    constituency_id, party_id, party_name, candidate_name, candidate_profile_url, source, twitter, facebook, website, email, email_source, comments, shrug = (
        line
    )
    democlub_constituencies.add(constituency_id)
    if constituency_id in constituency_to_party_to_candidate:
        if party_id in constituency_to_party_to_candidate[constituency_id]:
            candidate = constituency_to_party_to_candidate[constituency_id][party_id]
            if not candidate.has_name(candidate_name):
                print(
                    f"Difference! Constituency={constituency_id}, party={party_id}, party_candidate={candidate.name}, democlub={candidate_name}"
                )

for constituency, value in constituency_to_party_to_candidate.items():
    if constituency not in democlub_constituencies:
        print("!!! Constituency mismatch: {}: {}".format(constituency, value))
