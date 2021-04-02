"""
Copyright, Daniel Hocevar and Roman Zupancic

"""

import requests
import json

def get_packages(package_name: str) -> list[dict]:
    """Query npms.io for package data corresponding to package_name.
    """
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    data = r'{ "keys": ["react", "firebase"] }'
    print(data)
    
    r = requests.post(f'https://replicate.npmjs.com/_all_docs?include_docs=true',
                      headers = headers,
                      data = str(data))

    print(r.text)
    # Ensure it doesn't error
    if r.status_code == 200:
        package = json.loads(r.text)

        _trim_package_data(package[package])

        print(package)

        return package
    else:
        raise KeyError('Package Name is invalid, or the webpage is unavailable')



def _trim_package_data(data: dict) -> None:
    """Mutate the given data dictionary to remove irrelevant keys.
    """
    # When we requested the data
    data.pop('analyzedAt')

    # Package release versions
    data['collected']['metadata'].pop('releases')

    # Package Github Contributors
    data['collected']['github'].pop('contributors')
    # Package Github statuses
    data['collected']['github'].pop('statuses')

    # Remove all source entries
    data['collected'].pop('source')


def get_dependencies():
    with open('package_list.txt', 'r') as file:
        data = file.read()
        i = 0
        for line in data:
            r = requests.get("https://api.npms.io/v2/package/" + line)
            print(i)
            i += 1
        
    # r = requests.get("https://api.npms.io/v2/package/graphql")

    # results = json.loads(r.text)
    # print(results)


def write_sample_package_names() -> set[str]:
    """
    Write a list of packages to a text file
    """
    packages = set()
    chars = 'abcdefghijklmnopqrstuvwxyz'
    for char in chars:
        print(char)
        for i in range(10):
            start = 250 * i
            r = requests.get("https://api.npms.io/v2/search?from=" + str(start) + "&" + "size=250&q=" + char + "+boost-exact:false")
            results = json.loads(r.text)
            results = results['results']
            for package in results:
                packages.add(package['package']['name'])
    print('Starting to write')
    with open('package_list.txt', 'w') as file:
        for package in packages:
            file.write(package + '\n')
    
    return packages


def write_popular_package_names() -> set[str]:
    """
    Write a list of popular packages to a text file
    """
    packages = set()
    chars = 'abcdefghijklmnopqrstuvwxyz'
    chars = 'a'
    for char in chars:
        print(char)
        for i in range(10):
            start = 250 * i
            r = requests.get("https://api.npms.io/v2/search?from=" + str(start) + "&" + "size=250&q=" + char + "+boost-exact:false")
            results = json.loads(r.text)
            results = results['results']
            print(results)
            for package in results:
                packages.add(package['package']['name'])
    print('Starting to write')
    with open('package_list.txt', 'w') as file:
        for package in packages:
            file.write(package + '\n')
    
    return packages


if __name__ == '__main__':
    get_packages(['firebase', 'react'])