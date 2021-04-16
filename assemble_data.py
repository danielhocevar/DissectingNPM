"""
This module consists of all the functions required to query the npms.io API
and download a dataset of packages and package metadata.

The core function in this file is get_detailed_data, which genereates a
CSV data used in the rest of this project.


Copyright and Usage Information
===============================
This file is Copyright (c) 2021 Daniel Hocevar and Roman Zupancic.

This files contents may not be modified or redistributed without written
permission from Daniel Hocevar and Roman Zupancic.
"""
import json
import time
from typing import Optional
import requests
import pandas as pd
import python_ta


HEADERS = [
    'name',
    'version',
    'description',
    'keywords',
    'dependencies',
    'devDependencies',
    'communityInterest',
    'downloadsCount',
    'downloadsAcceleration',
    'dependentsCount',
    'quality',
    'popularity',
    'maintenance',
    'maintainers'
]


def get_detailed_data(base_packages_file: str = 'popular.txt',
                      max_lines: int = 1000,
                      output_file: str = 'big_v2.csv') -> None:
    """
    Use the packages listed in base_packages_file as root nodes to search for dependancies,
    and save data pertaining those dependancies to the output file.

    Read up to max_lines of the base_packages_file.

    Preconditions:
        - base_packages_file is a newline-separated list of valid npm packages
        - output_file must NOT have the prefix './'
    """
    print('Generating Dataset...')
    packages_so_far = []
    seen = set()

    with open(base_packages_file, 'r') as file:
        data = file.readlines()
        i = 1  # A variable to keep help us keep track of progress
        for line in data[:max_lines]:
            no_newline = line.replace('\n', '')
            print(f'Line ({i}) for package: {no_newline}')
            packages_so_far.extend(all_package_dependencies(line, seen))
            print(f'Length of list is now: {len(packages_so_far)}')
            i += 1
            # Rate limit, so that npms.io doesn't block us
            time.sleep(1)

    # Encode usernames as integers to protect identity
    num_maintainers = 0
    all_maintainers = {}
    for a in range(len(packages_so_far)):
        for b in range(len(packages_so_far[a][13])):
            if packages_so_far[a][13][b] in all_maintainers:
                # Encode the username as an integer using the encoding defined in
                # the all_maintainers dictionary
                packages_so_far[a][13][b] = all_maintainers[packages_so_far[a][13][b]]
            else:
                # Encode the username as an integer, and define a new encoding in
                # the all_maintainers dictionary
                all_maintainers[packages_so_far[a][13][b]] = str(num_maintainers)
                packages_so_far[a][13][b] = all_maintainers[packages_so_far[a][13][b]]
                num_maintainers += 1

    # Convert the list of all packages we have collected to a dataframe, and then write
    # this dataframe to file
    df = pd.DataFrame(packages_so_far, columns=HEADERS)

    print('Writing Final DataFrame')
    df.to_csv(f'./{output_file}')


def all_package_dependencies(package: str, seen: set) -> list[list]:
    """
    Get info for the current package, as well as info for all of the
    package's upstream dependencies.

    Seen is a set of packages that will not be re-investigated.
    """
    all_packages = []  # accumulator list

    # Use the API to get data for the package
    data = get_package(package)

    if data is None:
        return []
    else:
        # Parse the json data returned by the API and include
        # only the data we need in a list
        data_list = _convert_package_json_to_list(data)

        # Update the accumulator variable
        all_packages.append(data_list)

        seen.add(package)

        # Recursively get data for each of the package's upstream dependencies
        if data_list[4] is not None:
            for dependency in data_list[4]:
                if dependency not in seen:
                    vals = all_package_dependencies(dependency, seen)
                    # Update the accumulator variable
                    all_packages.extend(vals)

        return all_packages


def get_package(package_name: str) -> Optional[dict]:
    """Return package data corresponding to package_name from the npms.io API.

    Returns None if something went wrong with the API call (package doesn't exist,
    API is down, etc.).
    """

    # If there are slashes in the package name, we need to make them readable by the API
    if "/" in package_name:
        package_name = package_name.replace('/', '%2F')

    r = requests.get("https://api.npms.io/v2/package/" + package_name)

    # Ensure it doesn't error
    if r.status_code == 200:
        package = json.loads(r.text)
        return package
    else:
        # raise KeyError('Package Name is invalid, or the webpage is unavailable')
        print('Error getting package!')
        print(f'Package name: {package_name}')
        print(f'Request url: {r.url}')
        print(f'Request text: {r.text}')
        print('Continuing...')
        return None


def _convert_package_json_to_list(data: dict) -> list:
    """
    Return an ordered list of entries corresponding to specific keys in the
    given json-formatted data.

    The returned list matches the format of the HEADERS constant.
    """

    # Filter only the data that we need
    body = [
        data.get('collected').get('metadata').get('name'),  # str
        data.get('collected').get('metadata').get('version'),  # str
        data.get('collected').get('metadata').get('description'),  # str
        data.get('collected').get('metadata').get('keywords'),  # lst[str]
        data.get('collected').get('metadata').get('dependencies'),  # dict[str, str]
        data.get('collected').get('metadata').get('devDependencies'),  # dict[str, str]
        data.get('evaluation').get('popularity').get('communityInterest'),  # float
        data.get('evaluation').get('popularity').get('downloadsCount'),  # float
        data.get('evaluation').get('popularity').get('downloadsAcceleration'),  # float
        data.get('evaluation').get('popularity').get('dependentsCount'),  # float
        data.get('score').get('detail').get('quality'),  # float
        data.get('score').get('detail').get('popularity'),  # float
        data.get('score').get('detail').get('maintenance'),  # float
        data.get('collected').get('metadata').get('maintainers')  # lst[dict[str, str]]
    ]

    # Only collect user names for maintainers
    maintainers = body[13]
    if maintainers is not None:
        maintainers_usernames = [user['username'] for user in maintainers]
    else:
        maintainers_usernames = []
    body[13] = maintainers_usernames

    return body


if __name__ == '__main__':
    python_ta.check_all(
        config={
            'extra-imports': ['python_ta', 'requests', 'json', 'pandas', 'time', 'typing'],
            'allowed-io': ['get_detailed_data', 'all_package_dependencies', 'get_package'],
            'max-line-length': 100,
            'disable': ['E1136'],
            'max-nested-blocks': 4
        }
    )
