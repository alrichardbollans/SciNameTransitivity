import os

import pandas as pd
from wcvpy.wcvp_download import get_all_taxa, add_authors_to_col

from chaining_methods import compare_two_versions, chain_two_databases, get_direct_name_updates, compare_and_output_chained_and_direct_updates, \
    summarise_results

repo_path = os.environ.get('KEWSCRATCHPATH')
this_repo_path = os.path.join(repo_path, 'TaxoDrift')
_output_path = os.path.join(this_repo_path, 'WCVP_methods', 'outputs')
_input_path = os.path.join(this_repo_path, 'WCVP_methods', 'inputs')

if not os.path.isdir(_output_path):
    os.mkdir(_output_path)


def compare_all_pairs():
    v10_taxa, v11_taxa, v12_taxa, v13_taxa = get_all_databases()

    compare_two_versions(v10_taxa, v13_taxa,
                         'v10', 'v13', _output_path)
    compare_two_versions(v10_taxa, v12_taxa,
                         'v10', 'v12', _output_path)
    compare_two_versions(v11_taxa, v13_taxa,
                         'v11', 'v13', _output_path)

    compare_two_versions(v10_taxa, v11_taxa,
                         'v10', 'v11', _output_path)
    compare_two_versions(v11_taxa, v12_taxa,
                         'v11', 'v12', _output_path)
    compare_two_versions(v12_taxa, v13_taxa, 'v12', 'v13', _output_path)


def full_chain_results():
    # Note when chaining like this, in intermediary steps ambiguous/non resolving names may be dropped.
    # This may somewhat reflect real world situations but is optimistic about the chaining process
    out_dir = os.path.join('outputs', 'full_chain')
    v10_taxa, v11_taxa, v12_taxa, v13_taxa = get_all_databases()
    # Start with 10 -> 11
    v10_11_chained = chain_two_databases(v10_taxa, v11_taxa, 'v10', 'v11', out_dir)
    v10_11_chained = v10_11_chained.rename(columns={'v11_chained_accepted_name_w_author': 'accepted_name_w_author'})
    v10_11_chained = v10_11_chained[['taxon_name_w_authors', 'accepted_name_w_author']]

    # Then chain -> 12
    v10_11_12_chained = chain_two_databases(v10_11_chained, v12_taxa, 'v10_11', 'v12', out_dir)
    v10_11_12_chained = v10_11_12_chained.rename(columns={'v12_chained_accepted_name_w_author': 'accepted_name_w_author'})
    v10_11_12_chained = v10_11_12_chained[['taxon_name_w_authors', 'accepted_name_w_author']]

    # Then -> 13
    v10_11_12_13_chained = chain_two_databases(v10_11_12_chained, v13_taxa, 'v10_11_12', 'v13', out_dir)

    direct_updated_records = get_direct_name_updates(v10_taxa, v13_taxa, 'v13', out_dir)
    results_df = compare_and_output_chained_and_direct_updates(v10_11_12_13_chained, direct_updated_records, 'v10_11_12', 'v13', out_dir)
    pass


def get_all_databases():
    # v10_taxa = get_all_taxa(version='10', output_csv=os.path.join(_input_path, 'v10_taxa.csv'))
    # v11_taxa = get_all_taxa(version='11', output_csv=os.path.join(_input_path, 'v11_taxa.csv'))
    # v12_taxa = get_all_taxa(version='12', output_csv=os.path.join(_input_path, 'v12_taxa.csv'))
    # v13_taxa = get_all_taxa(version=None, output_csv=os.path.join(_input_path, 'v13_taxa.csv'))

    v10_taxa = pd.read_csv(os.path.join(_input_path, 'v10_taxa.csv'), index_col=0)
    v11_taxa = pd.read_csv(os.path.join(_input_path, 'v11_taxa.csv'), index_col=0)
    v12_taxa = pd.read_csv(os.path.join(_input_path, 'v12_taxa.csv'), index_col=0)
    v13_taxa = pd.read_csv(os.path.join(_input_path, 'v13_taxa.csv'), index_col=0)

    v10_taxa['taxon_name_w_authors'] = add_authors_to_col(v10_taxa, 'taxon_name')
    v11_taxa['taxon_name_w_authors'] = add_authors_to_col(v11_taxa, 'taxon_name')
    v12_taxa['taxon_name_w_authors'] = add_authors_to_col(v12_taxa, 'taxon_name')
    v13_taxa['taxon_name_w_authors'] = add_authors_to_col(v13_taxa, 'taxon_name')

    return v10_taxa, v11_taxa, v12_taxa, v13_taxa





if __name__ == '__main__':
    # compare_all_pairs()
    # full_chain_results()
    summarise_results(os.path.join(_output_path, 'v10_v13'), 'v10_v13')
    summarise_results(os.path.join(_output_path, 'v11_v13'), 'v11_v13', old_tag='v11')
    summarise_results(os.path.join(_output_path, 'v12_v13'), 'v12_v13', old_tag='v12')
    summarise_results(os.path.join(_output_path, 'v10_v12'), 'v10_v12')
    summarise_results(os.path.join(_output_path, 'v10_v11'), 'v10_v11')
    summarise_results(os.path.join(_output_path, 'full_chain'), 'v10_11_12_v13')
