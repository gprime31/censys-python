"""
Interact with the Censys' Maxmind API.

Classes:
    CensysAdminMaxmind

Functions:
    main()
"""

import csv
import argparse
from pathlib import Path
from typing import List, Set

import netaddr

from censys.base import CensysAPIBase


class CensysAdminMaxmind(CensysAPIBase):
    def upload(self, collection: str, version: int, records: List[Set[dict]]):
        url = "/admin/maxmind/%s/%i" % (collection, version)
        return self._post(url, data={"records": records})

    def delete(self, collection: str, version: int):
        url = "/admin/maxmind/%s/%i" % (collection, version)
        return self._delete(url)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("collection")
    parser.add_argument("version", type=int)
    parser.add_argument("locations_path", metavar="locations.csv", type=Path)
    parser.add_argument("blocks_path", metavar="blocks.csv", type=Path)
    args = parser.parse_args()

    collection = args.collection
    version = args.version

    censys = CensysAdminMaxmind()

    to_upload = []
    # population dictionary with all the details for a geoid
    locations = {}
    headers = [
        "geoname_id",
        "locale_code",
        "continent_code",
        "continent_name",
        "country_iso_code",
        "country_name",
        "subdivision_1_iso_code",
        "subdivision_1_name",
        "subdivision_2_iso_code",
        "subdivision_2_name",
        "city_name",
        "metro_code",
        "time_zone",
    ]
    with open(args.locations_path, "r") as locations_file:
        for row in csv.reader(locations_file):
            if not row:
                continue
            if row[0].startswith("geoname_id"):
                continue
            locations[row[0]] = dict(zip(headers, row))

    # now that all geoid data is in memory, go through ips, generate full
    # records and then upload them in batches to Censys.
    headers = [
        "network",
        "geoname_id",
        "registered_country_geoname_id",
        "represented_country_geoname_id",
        "is_anonymous_proxy",
        "is_satellite_provider",
        "postal_code",
        "latitude",
        "longitude",
    ]
    with open(args.blocks_path, "r") as blocks_file:
        for row in csv.reader(blocks_file):
            if not row:
                continue
            if row[0].startswith("network"):
                continue
            geoid = row[1]
            if geoid == "":
                geoid = row[2]
            cidr = netaddr.IPNetwork(row[0])
            rec = {"ip_begin": int(cidr[0]), "ip_end": int(cidr[-1])}
            rec.update(dict(zip(headers, row)))
            rec.update(locations[geoid])
            print(rec)
            to_upload.append(rec)
            if len(to_upload) > 10000:
                censys.upload(collection, version, to_upload)
                to_upload = []

        censys.upload(collection, version, to_upload)


if __name__ == "__main__":
    main()
