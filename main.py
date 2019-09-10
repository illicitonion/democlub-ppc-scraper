import csv
from collections import defaultdict

import green
import labour

import requests

from common import constituency_to_dc_id

labour_candidates = labour.get_candidates()
green_candidates = green.get_candidates()

constituency_to_party_to_candidate = defaultdict(dict)

for candidate in labour_candidates:
    constituency_to_party_to_candidate[constituency_to_dc_id(candidate.constituency)]["PP53"] = candidate

for candidate in green_candidates:
    constituency_to_party_to_candidate[constituency_to_dc_id(candidate.constituency)]["PP63"] = candidate


response = requests.get(
    "https://docs.google.com/spreadsheets/d/1cHlm1irk7FFqPKO6jTgBh9Ya5k_erWGIH7AP65nkWCc/export?format=csv&id=1cHlm1irk7FFqPKO6jTgBh9Ya5k_erWGIH7AP65nkWCc&gid=0"
)

reader = csv.reader(response.iter_lines(decode_unicode=True))
for line in reader:
    if not line:
        continue
    constituency_id, party_id, party_name, candidate_name, candidate_profile_url, source, twitter, facebook, website, email, email_source, comments, shrug = (
        line
    )
    if constituency_id in constituency_to_party_to_candidate:
        if party_id in constituency_to_party_to_candidate[constituency_id]:
            candidate = constituency_to_party_to_candidate[constituency_id][party_id]
            if not candidate.has_name(candidate_name):
                print(
                    f"Difference! Constituency={constituency_id}, party={party_id}, party_candidate={candidate.name}, democlub={candidate_name}"
                )
