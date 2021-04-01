"""
Copyright, Daniel Hocevar and Roman Zupancic

"""

import requests
import json

def get_packages(package_names: list[str]) -> list[dict]:
    """Query npms.io for package data corresponding to package_name.
    """
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    } 
    r = requests.get(f'https://api.npms.io/v2/package/mget',
                     headers=headers, data=str(package_names))

    # Ensure it doesn't error
    if r.status_code == 200:
        print(r.text)
        packages = json.loads(r.text)

        for package in packages:
            _trim_package_data(package[package])

        print(packages)

        return packages
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


def get_sample_package_names() -> set[str]:
    keywords = ['database',
                'interface',
                'state management',
                'interaction',
                'animations',
                'payments',
                'authentication',
                'themes',
                'deep learning',
                '3d',
                'machine learning',
                'data science',
                'storage',
                'performance',
                'optimization',
                'analytics',
                'query',
                'cloud']
    packages = {}
    for keyword in keywords:
        r = requests.get("https://api.npms.io/v2/search/suggestions?q=" + keyword)
        results = r['results']
        for package in results:
            package.add(package['name'])
    return packages



if __name__ == '__main__':
    get_packages(['firebase', 'react'])