import csv
import math
import os
from collections import defaultdict

import green
import labour
import libdem

import requests

from common import constituency_to_dc_id


if os.getenv("BING_MAPS_API_KEY", None) is None:
    print("WARNING: env var BING_MAPS_API_KEY is not set - will not look up existing candidate pages")


def source_for(party):
    if party == "PP53":
        return labour.source
    if party == "PP63":
        return green.source
    if party == "PP90":
        return libdem.source


party_to_name_and_id_to_constituencies = defaultdict(lambda: defaultdict(set))
response = requests.get("https://candidates.democracyclub.org.uk/media/candidates-all.csv")
response.encoding = "utf-8"
for line in csv.reader(response.iter_lines(decode_unicode=True)):
    if not line:
        continue
    id, name, honorific_prefix, honorific_suffix, gender, birth_date, election, party_id, party_name, post_id, post_label, mapit_url, elected, email, twitter_username, facebook_page_url, party_ppc_page_url, facebook_personal_url, homepage_url, wikipedia_url, linkedin_url, image_url, proxy_image_url_template, image_copyright, image_uploading_user, image_uploading_user_notes, twitter_user_id, election_date, election_current, party_lists_in_use, party_list_position, old_person_ids, gss_code, parlparse_id, theyworkforyou_url, party_ec_id, favourite_biscuits, cancelled_poll, wikidata_id, blog_url, instagram_url, youtube_profile = (
        line
    )
    if election.startswith("local."):
        continue
    party = f"PP{party_id[6:]}"
    party_to_name_and_id_to_constituencies[party][(name, id)].add(post_label)


constituency_to_party_to_candidate = defaultdict(dict)

for candidate in labour.get_candidates():
    constituency_to_party_to_candidate[constituency_to_dc_id(candidate.constituency)]["PP53"] = candidate

for candidate in green.get_candidates():
    constituency_to_party_to_candidate[constituency_to_dc_id(candidate.constituency)]["PP63"] = candidate

for candidate in libdem.get_candidates():
    constituency_to_party_to_candidate[constituency_to_dc_id(candidate.constituency)]["PP90"] = candidate

location_to_coords = {}


def coords_for(location):
    bing_maps_api_key = os.environ.get("BING_MAPS_API_KEY", None)
    if not bing_maps_api_key:
        return None
    if location not in location_to_coords:
        resp = requests.get(
            "http://dev.virtualearth.net/REST/v1/Locations",
            params={"query": location, "maxResults": 1, "key": bing_maps_api_key},
        )
        resourceSets = resp.json()["resourceSets"]
        if not resourceSets:
            location_to_coords[location] = None
            return None
        resources = resourceSets[0]["resources"]
        if not resources:
            location_to_coords[location] = None
            return None
        location_to_coords[location] = resources[0]["point"]["coordinates"]
    return location_to_coords[location]


def distance_between(lat1, lon1, lat2, lon2):
    def to_radians(degrees):
        return degrees * math.pi / 180

    R = 6371e3  # meters
    φ1 = to_radians(lat1)
    φ2 = to_radians(lat2)
    Δφ = to_radians(lat2 - lat1)
    Δλ = to_radians(lon2 - lon1)

    a = math.sin(Δφ / 2) * math.sin(Δφ / 2) + math.cos(φ1) * math.cos(φ2) * math.sin(Δλ / 2) * math.sin(Δλ / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def find_known_page(party, candidate):
    latlon = coords_for(candidate.constituency)
    if not latlon:
        return None
    for (name, id), constituencies in party_to_name_and_id_to_constituencies.get(party, {}).items():
        if candidate.has_name(name):
            if candidate.constituency in constituencies:
                return f"https://candidates.democracyclub.org.uk/person/{id}"
            for constituency in constituencies:
                maybe_latlon = coords_for(constituency)
                if maybe_latlon:
                    if distance_between(*latlon, *maybe_latlon) < 80_000:
                        return f"https://candidates.democracyclub.org.uk/person/{id}"
    return None


response = requests.get(
    "https://docs.google.com/spreadsheets/d/1cHlm1irk7FFqPKO6jTgBh9Ya5k_erWGIH7AP65nkWCc/export?format=csv&id=1cHlm1irk7FFqPKO6jTgBh9Ya5k_erWGIH7AP65nkWCc&gid=0"
)
response.encoding = "utf-8"

democlub_knows_more = []
new_values = []
differences = []

democlub_constituencies = set()

democlub_candidate_counts = defaultdict(lambda: 0)
reader = csv.reader(response.iter_lines(decode_unicode=True))
for line in reader:
    if not line:
        continue
    constituency_id, party_id, party_name, candidate_name, candidate_profile_url, source, twitter, facebook, website, email, email_source, comments, shrug = (
        line
    )
    democlub_constituencies.add(constituency_id)
    if candidate_name:
        democlub_candidate_counts[party_name] += 1
    if constituency_id in constituency_to_party_to_candidate:
        if party_id in constituency_to_party_to_candidate[constituency_id]:
            candidate = constituency_to_party_to_candidate[constituency_id][party_id]
            if not candidate.has_name(candidate_name):
                if not candidate_name:
                    new_values.append(
                        f"{constituency_id}\t{party_id}\t{party_name}\t{candidate.name}\t{find_known_page(party_id, candidate) or ''}\t{candidate.href or source_for(party_id)}"
                    )
                else:
                    differences.append(
                        f"{constituency_id}\t{party_id}\t{party_name}\tDemoClub={candidate_name}|Found={candidate.name}\tDemoClub={candidate_profile_url}|Found={find_known_page(party_id, candidate)}\t{comments}"
                    )
        elif party_id in {"PP53", "PP63", "PP90"} and candidate_name:
            print(f"DemoClub knows more?: {constituency_id} {party_id} {party_name} {candidate_name} {source}")

for constituency, value in constituency_to_party_to_candidate.items():
    if constituency not in democlub_constituencies:
        print("!!! Constituency mismatch: {}: {}".format(constituency, value))

if new_values:
    print("")
    print("New values:")
    print("===========")
    print("")
for new in new_values:
    print(f"{new}")

if differences:
    print("")
    print("Differences:")
    print("============")
    print("")

for diff in differences:
    print(f"{diff}")


print("")
print("Summary:")
print("========")
for party, count in sorted(democlub_candidate_counts.items(), key=lambda kv: kv[1], reverse=True):
    if count > 9:
        print(f"{party}: {count}")
