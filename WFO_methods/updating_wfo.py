import os

from WFO_methods.get_WFO import get_latest_version, get_oldest_version, get_other_versions
from disagreements.updating_taxonomies import compare_two_versions, summarise_results, chain_two_databases, get_direct_name_updates, \
    compare_and_output_chained_and_direct_updates

_output_path = os.path.join('outputs')


def main_case():
    latest_version, new_tag = get_latest_version()
    oldest_version, old_tag = get_oldest_version()

    compare_two_versions(oldest_version, latest_version, old_tag, new_tag)
    path_tag = f'{old_tag}_{new_tag}'
    summarise_results(os.path.join(_output_path, path_tag), path_tag, old_tag=old_tag)


def compare_all_pairs():
    oldest_version, old_tag = get_oldest_version()
    other_versions = get_other_versions()
    for other_version in other_versions:
        print(f'Running {other_version}')
        compare_two_versions(oldest_version, other_versions[other_version], old_tag, other_version)
        path_tag = f'{old_tag}_{other_version}'
        summarise_results(os.path.join(_output_path, path_tag), path_tag, old_tag=old_tag)


def full_chain_results():
    # Note when chaining like this, in intermediary steps ambiguous/non resolving names may be dropped.
    # This may somewhat reflect real world situations but is optimistic about the chaining process
    out_dir = os.path.join(_output_path, 'wfo_full_chain')
    oldest_version, old_tag = get_oldest_version()
    new, new_tag = get_latest_version()
    other_versions = get_other_versions()
    ordered_keys = ['201905', '202112', '202207', '202306']
    first_key = ordered_keys[0]
    # Start with 1 -> 2
    vold_next_chained = chain_two_databases(oldest_version, other_versions[first_key], old_tag, first_key, out_dir)
    vold_next_chained = vold_next_chained.rename(columns={f'{first_key}_chained_accepted_name_w_author': 'accepted_name_w_author'})
    v_next_chained = vold_next_chained[['taxon_name_w_authors', 'accepted_name_w_author']]

    previous_tag = first_key
    for key in ordered_keys:
        if key != first_key:
            vold_next_chained = chain_two_databases(v_next_chained, other_versions[key], previous_tag, key, out_dir)
            vold_next_chained = vold_next_chained.rename(columns={f'{key}_chained_accepted_name_w_author': 'accepted_name_w_author'})
            v_next_chained = vold_next_chained[['taxon_name_w_authors', 'accepted_name_w_author']]
            previous_tag = key

    # Then final case
    full_chain = chain_two_databases(v_next_chained, new, 'previous_chain', new_tag, out_dir)

    direct_updated_records = get_direct_name_updates(oldest_version, new, new_tag, out_dir)
    results_df = compare_and_output_chained_and_direct_updates(full_chain, direct_updated_records, 'previous_chain', new_tag, out_dir)
    pass


def main():
    # main_case()
    # compare_all_pairs()
    # full_chain_results()
    summarise_results(os.path.join(_output_path, 'wfo_full_chain'), 'previous_chain_202406', old_tag='201807')


if __name__ == '__main__':
    main()
