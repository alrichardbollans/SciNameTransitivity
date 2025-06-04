import os

from WFO_methods.get_WFO import get_latest_version, get_oldest_version, get_other_versions, other_version_strings, all_wfo_version_strings, \
    oldest_wfo_version_string, get_version_comparable_to_v10, wfo_version_comparable_to_v10_string, get_versions_after_v10, \
    wfo_version_strings_after_v10
from chaining_methods import compare_two_versions, summarise_results, chain_two_databases, get_direct_name_updates, \
    compare_and_output_chained_and_direct_updates

repo_path = os.environ.get('KEWSCRATCHPATH')
this_repo_path = os.path.join(repo_path, 'TaxoDrift')
_output_path = os.path.join(this_repo_path, 'WFO_methods', 'outputs')


def main_case():
    compare_two_versions(oldest_version, latest_version, old_wfo_tag, new_wfo_tag, _output_path)
    path_tag = f'{old_wfo_tag}_{new_wfo_tag}'
    summarise_results(os.path.join(_output_path, path_tag), path_tag, old_tag=old_wfo_tag)


def main_case_v10_equivalent():
    compare_two_versions(v10_equiv, latest_version, v10_equiv_tag, new_wfo_tag, _output_path)
    path_tag = f'{v10_equiv_tag}_{new_wfo_tag}'
    summarise_results(os.path.join(_output_path, path_tag), path_tag, old_tag=v10_equiv_tag)


def compare_all_pairs():
    for other_version in other_versions:
        print(f'Running {other_version}')
        compare_two_versions(oldest_version, other_versions[other_version], old_wfo_tag, other_version, _output_path)
        path_tag = f'{old_wfo_tag}_{other_version}'
        summarise_results(os.path.join(_output_path, path_tag), path_tag, old_tag=old_wfo_tag)

        compare_two_versions(other_versions[other_version], latest_version, other_version, new_wfo_tag, _output_path)
        path_tag = f'{other_version}_{new_wfo_tag}'
        summarise_results(os.path.join(_output_path, path_tag), path_tag, old_tag=other_version)

        for other_version2 in other_versions:
            # Get all combinations of other versions (if possible)
            if other_version2 !=other_version and other_version2 < other_version:
                try:
                    compare_two_versions(other_versions[other_version2], other_versions[other_version], other_version2, other_version, _output_path)
                    path_tag = f'{other_version2}_{other_version}'
                    summarise_results(os.path.join(_output_path, path_tag), path_tag, old_tag=other_version2)
                except:
                    print(f'Could not compare {other_version2} to {other_version}')


def compare_pairs_to_v10_equivalent():
    for other_version in versions_after_v10:
        print(f'Running {other_version}')
        compare_two_versions(v10_equiv, other_versions[other_version], v10_equiv_tag, other_version, _output_path)
        path_tag = f'{v10_equiv_tag}_{other_version}'
        summarise_results(os.path.join(_output_path, path_tag), path_tag, old_tag=v10_equiv_tag)


def full_chain_results(old_df, old_tag_, dict_of_other_versions, ordered_keys, out_dir):
    # Note when chaining like this, in intermediary steps ambiguous/non resolving names may be dropped.
    # This may somewhat reflect real world situations but is optimistic about the chaining process
    first_key = ordered_keys[0]
    # Start with 1 -> 2
    vold_next_chained = chain_two_databases(old_df, dict_of_other_versions[first_key], old_tag_, first_key, out_dir)
    vold_next_chained = vold_next_chained.rename(columns={f'{first_key}_chained_accepted_name_w_author': 'accepted_name_w_author'})
    v_next_chained = vold_next_chained[['taxon_name_w_authors', 'accepted_name_w_author']]

    previous_tag = first_key
    for key in ordered_keys:
        if key != first_key:
            vold_next_chained = chain_two_databases(v_next_chained, dict_of_other_versions[key], previous_tag, key, out_dir)
            vold_next_chained = vold_next_chained.rename(columns={f'{key}_chained_accepted_name_w_author': 'accepted_name_w_author'})
            v_next_chained = vold_next_chained[['taxon_name_w_authors', 'accepted_name_w_author']]
            previous_tag = key

    # Then final case
    full_chain = chain_two_databases(v_next_chained, latest_version, 'previous_chain', new_wfo_tag, out_dir)

    direct_updated_records = get_direct_name_updates(old_df, latest_version, new_wfo_tag, out_dir)
    results_df = compare_and_output_chained_and_direct_updates(full_chain, direct_updated_records, 'previous_chain', new_wfo_tag, out_dir)
    pass


def main():
    main_case()
    compare_all_pairs()
    full_chain_results(oldest_version, old_wfo_tag, other_versions, other_version_strings, os.path.join(_output_path, 'wfo_full_chain'))
    summarise_results(os.path.join(_output_path, 'wfo_full_chain'), 'previous_chain_202406', old_tag=old_wfo_tag)

    main_case_v10_equivalent()
    compare_pairs_to_v10_equivalent()
    full_chain_results(v10_equiv, v10_equiv_tag, versions_after_v10, wfo_version_strings_after_v10,
                       os.path.join(_output_path, 'wfo_full_chain_after_v10'))
    for y in all_wfo_version_strings:
        for y2 in all_wfo_version_strings:
            try:
                summarise_results(os.path.join(_output_path, f'{y2}_{y}'), f'{y2}_{y}',
                                  old_tag=y2)
            except:
                print(f'Could not summarise {y}, {y2}')


if __name__ == '__main__':
    other_versions = get_other_versions()
    versions_after_v10 = get_versions_after_v10(other_versions)

    latest_version, new_wfo_tag = get_latest_version()
    oldest_version, old_wfo_tag = get_oldest_version()
    v10_equiv, v10_equiv_tag = get_version_comparable_to_v10()

    main()
