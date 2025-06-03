from WFO_methods.get_WFO import get_latest_version, get_oldest_version, get_other_versions
from analyse_number_of_changes.helper_functions import do_all_analyses_for_a_pair


def main():
    latest_version, new_wfo_tag = get_latest_version()
    oldest_version, old_wfo_tag = get_oldest_version()

    do_all_analyses_for_a_pair(oldest_version, latest_version, old_wfo_tag, new_wfo_tag)

    other_versions = get_other_versions()

    for other_version in other_versions:
        print(f'Running {other_version}')
        do_all_analyses_for_a_pair(oldest_version, other_versions[other_version], old_wfo_tag, other_version)

        do_all_analyses_for_a_pair(other_versions[other_version], latest_version, other_version, new_wfo_tag)

        for other_version2 in other_versions:
            # Get all combinations of other versions (if possible)
            try:
                do_all_analyses_for_a_pair(other_versions[other_version2], other_versions[other_version], other_version2, other_version)
            except:
                print(f'Could not compare {other_version2} to {other_version}')


if __name__ == '__main__':
    main()
