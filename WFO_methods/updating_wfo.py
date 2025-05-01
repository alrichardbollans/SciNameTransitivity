import os

import pandas as pd

from WFO_methods.get_WFO import get_latest_version, get_oldest_version
from disagreements.updating_taxonomies import compare_two_versions

_output_path = os.path.join('outputs')


def main():
    latest_version = get_latest_version()
    oldest_version = get_oldest_version()

    compare_two_versions(oldest_version, latest_version, '2018.07', '2023.12')


if __name__ == '__main__':
    main()
