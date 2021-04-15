"""
This module consists of all the functions required to query the npms.io API
and download a dataset of packages and package metadata.

The core function in this file is get_detailed_data, which genereates a
CSV data used in the rest of this project.


Copyright and Usage Information
===============================
This file is Copyright (c) 2021 Daniel Hocevar and Roman Zupancic. 

This files contents may not be modified or redistributed without written
permission from Daniel Hocevar and Roman Zupancic
"""

import requests
import json
import pandas as pd
import time
from typing import Optional


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
        i = 1 # A variable to keep help us keep track of progress
        for line in data[:max_lines]:
            no_newline = line.replace('\n', '')
            print(f'Line ({i}) for package: {no_newline}')
            packages_so_far.extend(all_package_dependencies(line, seen))
            print(f'Length of list is now: {len(packages_so_far)}')
            i += 1

            # if i % 10 == 0:
            #     df = pd.DataFrame(packages_so_far, columns=HEADERS)
            #     print('Writing DataFrame')
            #     df.to_csv(f'./intermediate/big{i}.csv')
            time.sleep(1)

    # Encode usernames as integers to protect identity
    num_maintainers = 0
    all_maintainers = {}
    for a in range(len(packages_so_far)):
        for b in range(len(packages_so_far[a][13])):
            if packages_so_far[a][13][b] in all_maintainers:
                packages_so_far[a][13][b] = all_maintainers[packages_so_far[a][13][b]]
            else:
                all_maintainers[packages_so_far[a][13][b]] = str(num_maintainers)
                packages_so_far[a][13][b] = all_maintainers[packages_so_far[a][13][b]]
                num_maintainers += 1


    df = pd.DataFrame(packages_so_far, columns=HEADERS)

    print('Writing Final DataFrame')
    df.to_csv(f'./{output_file}')


def all_package_dependencies(package: str, seen: set) -> list[list]:
    """
    Get info for the current package, as well as info 
    for all of the package's upstream dependencies.
    
    Seen is a set of packages that will not be re-investigated.
    """
    all_packages = [] # accumulator list
    # Get data for the current package

    data = get_package(package)

    if data is None:
        return []
    else:
        data_list = _convert_package_json_to_list(data)

        all_packages.append(data_list)

        seen.add(package)
        # Recursively get data for each of the package's upstream dependencies
        if data_list[4] is not None:
            for dependency in data_list[4]:
                if dependency not in seen:
                    c = all_package_dependencies(dependency, seen)
                    all_packages.extend(c)

        return all_packages


def get_package(package_name: str) -> Optional[dict]:
    """Return package data corresponding to package_name from the npms.io API.

    Returns None if something went wrong with the API call (package doesn't exist, 
    API is down, etc.).
    """

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
        print(f'Continuing...')
        return None


def _trim_package_data(data: dict) -> None:
    """Mutate the given data dictionary to remove irrelevant keys.
    
    This function is kept for legacy purposes, and is not actually used anywhere
    else in this project.
    """
    # When we requested the data
    data.pop('analyzedAt')

    data['collected']['metadata'].pop('date')
    data['collected']['metadata'].pop('author')
    data['collected']['metadata'].pop('publisher')
    #data['collected']['metadata'].pop('maintainers')
    data['collected']['metadata'].pop('repository')
    data['collected']['metadata'].pop('links')
    data['collected']['metadata'].pop('releases')
    data['collected']['metadata'].pop('hasTestScript')
    data['collected']['metadata'].pop('hasSelectiveFiles')

    # NPM internal stuff
    data['collected'].pop('npm')

    # Package Github Stuff
    data['collected'].pop('github')

    # Remove all source entries
    data['collected'].pop('source')

    # Only collect maintainer usernames
    maintainers = data['collected']['maintainers']
    try:
        if maintainers is not None:
         maintainers_usernames = [user['username'] for user in maintainers]
        else:
            maintainers_usernames = []
    except:
        maintainers_usernames = []
    data['collected']['maintainers'] = maintainers_usernames


def _convert_package_json_to_list(data: dict) -> list:
    """Return an ordered list of entries corresponding to specific keys in the 
    given json-formatted data.
    
    The returned list matches the format of the HEADERS constant.
    """

    body = [
        data.get('collected').get('metadata').get('name'), # str
        data.get('collected').get('metadata').get('version'), # str
        data.get('collected').get('metadata').get('description'), # str
        data.get('collected').get('metadata').get('keywords'), # lst[str]
        data.get('collected').get('metadata').get('dependencies'), # dict[str, str]
        data.get('collected').get('metadata').get('devDependencies'), # dict[str, str]
        data.get('evaluation').get('popularity').get('communityInterest'), # float
        data.get('evaluation').get('popularity').get('downloadsCount'), # float
        data.get('evaluation').get('popularity').get('downloadsAcceleration'), # float
        data.get('evaluation').get('popularity').get('dependentsCount'), # float
        data.get('score').get('detail').get('quality'), # float
        data.get('score').get('detail').get('popularity'), # float
        data.get('score').get('detail').get('maintenance'), # float
        data.get('collected').get('metadata').get('maintainers')
    ]

    # Only collect user names for maintainers
    maintainers = body[13]
    if maintainers is not None:    
        maintainers_usernames = [user['username'] for user in maintainers]
    else: 
        maintainers_usernames = []
    body[13] = maintainers_usernames

    return body


# def write_sample_package_names() -> set[str]:
#     """
#     Write a list of packages to a text file. The list is generated by
#     searching for packages alphabetically, and then selecting
#     the first few.

#     This function is kept for legacy purposes, and is not actually used anywhere
#     else in this project.
#     """
#     packages = set()
#     chars = 'abcdefghijklmnopqrstuvwxyz'
#     for char in chars:
#         for i in range(10):
#             start = 250 * i
#             r = requests.get("https://api.npms.io/v2/search?from=" + str(start) + "&" + "size=250&q=" + char + "+boost-exact:false")
#             results = json.loads(r.text)
#             results = results['results']
#             for package in results:
#                 packages.add(package['package']['name'])
#     print('Starting to write')
#     with open('package_list.txt', 'w') as file:
#         for package in packages:
#             file.write(package + '\n')

#     return packages


# def write_popular_package_names() -> set[str]:
#     """
#     Write a list of popular packages to a text file.

#     This function is kept for legacy purposes, and is not actually used anywhere
#     else in this project.
#     """
#     packages = set()
#     chars = 'abcdefghijklmnopqrstuvwxyz'
#     for char in chars:
#         for i in range(10):
#             start = 250 * i
#             r = requests.get("https://api.npms.io/v2/search?from=" + str(start) + "&" + "size=250&q=" + char + "+boost-exact:false")
#             results = json.loads(r.text)
#             results = results['results']
#             for package in results:
#                 #score = package['score']['detail']['quality'] + package['score']['detail']['maintenance'] + package['score']['detail']['popularity']
#                 score = package['searchScore']
#                 packages.add((score, package['package']['name']))

#     package_list = list(packages)
#     # packages_sorted = sorted(package_list)

#     package_list = package_list[len(package_list) - 501:]

#     print('Starting to write')
#     with open('popular.txt', 'w') as file:
#         for package in package_list:
#             file.write(package[1] + '\n')

#     return packages


if __name__ == '__main__':
    # for i in range(300000):
    #     print(i)
    print('Go')
#     get_packages(['firebase', 'react'])