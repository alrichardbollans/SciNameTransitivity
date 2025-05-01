## Do this for a single chain as the formats at change and there isn't a package for simply handling different versions.


import os
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

_wfo_downloads_path = os.path.join(Path.home(), '.wfo_downloads')

_all_ranks = list(sorted(
    ['variety', 'species', 'form', 'subspecies', 'unranked', 'prole', 'subvariety', 'lusus', 'subform', 'section', 'subseries', 'series',
     'subsection', 'subgenus', 'genus', 'family', 'tribe', 'subtribe', 'supertribe', 'subfamily', 'order', 'superorder', 'subclass', 'class',
     'phylum', 'kingdom', 'suborder', 'subkingdom']))

ranks_to_use = list(sorted(
    ['variety', 'species', 'form', 'subspecies', 'unranked', 'prole', 'subvariety', 'lusus', 'subform', 'section', 'subseries', 'series',
     'subsection', 'subgenus', 'genus']))


def parse_wfo_data(all_wfo_data):
    all_wfo_data_untouched = all_wfo_data.copy(deep=True)
    ### Check statuses in data
    statuses = all_wfo_data['taxonomicStatus'].dropna().unique().tolist()
    assert (list(sorted(statuses)) == ['Accepted', 'Synonym', 'Unchecked']) or (
            statuses == ['Synonym', 'Doubtful', 'Accepted', 'heterotypicSynonym', 'homotypicSynonym'])

    # restrict to genus and lower

    all_wfo_data = all_wfo_data[~all_wfo_data['genus'].isna()]

    all_wfo_data['taxonRank'] = all_wfo_data['taxonRank'].str.lower()  # in old version they use upper case :(
    ahhhh = list(sorted(all_wfo_data['taxonRank'].unique().tolist()))
    for a in ahhhh:
        assert a in ranks_to_use

    ### set scientificnames to include authors
    all_wfo_data['taxon_name_w_authors'] = all_wfo_data['scientificName'] + ' ' + all_wfo_data['scientificNameAuthorship'].fillna('').astype(str)

    ## Add a species name

    print(all_wfo_data['taxonRank'].unique().tolist())
    all_wfo_data['species_name'] = np.where(all_wfo_data['taxonRank'] == 'genus', np.nan,
                                            all_wfo_data['genus'] + ' ' + all_wfo_data['specificEpithet'].fillna('').astype(str))

    ### Set accepted_name_ids either from taxonID (for accepted names) or acceptedNameUsageID
    all_wfo_data['accepted_name_id'] = np.where(all_wfo_data['taxonomicStatus'] == 'Accepted', all_wfo_data['taxonID'],
                                                all_wfo_data['acceptedNameUsageID'])
    ### Remove instances without accepted ids
    resolved_wfo_data = all_wfo_data.dropna(subset=['accepted_name_id'])

    ### Check statuses again
    statuses = resolved_wfo_data['taxonomicStatus'].unique().tolist()
    assert (list(sorted(statuses)) == ['Accepted', 'Synonym']) or (
            statuses == ['Synonym', 'Accepted', 'heterotypicSynonym', 'homotypicSynonym'])

    ### Use the accepted IDs to get accepted names from the original dataframe
    accepted_data = all_wfo_data[all_wfo_data['taxonomicStatus'] == 'Accepted'][['taxonID', 'taxon_name_w_authors', 'species_name', 'genus']]
    accepted_data = accepted_data.dropna(subset=['taxonID'])
    accepted_data = accepted_data.rename(
        columns={'taxonID': 'acc_id', 'taxon_name_w_authors': 'accepted_name_w_author', 'species_name': 'accepted_species',
                 'genus': 'accepted_genus'})
    resolved_wfo_data = pd.merge(resolved_wfo_data, accepted_data, how='left', left_on=['accepted_name_id'], right_on=['acc_id'])

    ### Sanity checks
    accepted_check = resolved_wfo_data[resolved_wfo_data['taxonomicStatus'] == 'Accepted']
    pd.testing.assert_series_equal(accepted_check['taxon_name_w_authors'], accepted_data['accepted_name_w_author'], check_names=False,
                                   check_index=False)

    # Cases where accepted_ids in resolved_wfo_data aren't found in accepted_data
    nan_issues = resolved_wfo_data[resolved_wfo_data['accepted_name_w_author'].isna()]
    if len(nan_issues) > 0:
        # In old version, some taxa resolve to an ID which just isn't in the data but these won't be included anyway
        # should_be_accepted = all_wfo_data_untouched[all_wfo_data_untouched['taxonID'].isin(nan_issues['accepted_name_id'].values)]
        # should_be_accepted2 = accepted_data[accepted_data['acc_id'].isin(nan_issues['accepted_name_id'].values)]

        dataset_issues = all_wfo_data_untouched[all_wfo_data_untouched['acceptedNameUsageID'].isna()]
        dataset_issues2 = all_wfo_data_untouched[~all_wfo_data_untouched['acceptedNameUsageID'].isin(all_wfo_data_untouched['taxonID'].values)]

        non_issues = nan_issues[nan_issues['taxonID'].isin(dataset_issues['taxonID'].values)]

        should_be_accepted3 = all_wfo_data[all_wfo_data['taxonID'].isin(nan_issues['accepted_name_id'].values)]
        assert should_be_accepted3['taxonomicStatus'].tolist() == ['Doubtful']
        assert len(nan_issues) < 25

    ## Only return cases with accepted names
    resolved_wfo_data = resolved_wfo_data.dropna(subset=['accepted_name_w_author'])

    ### and only return used columns
    return resolved_wfo_data[['taxonID', 'taxon_name_w_authors', 'accepted_name_w_author', 'accepted_name_id', 'accepted_species', 'accepted_genus']]


def get_latest_version():
    input_zip_file = os.path.join(_wfo_downloads_path, 'WFO_Backbone_v.2023.12.zip')
    zf = zipfile.ZipFile(input_zip_file)
    csv_file = zf.open('classification.csv')

    all_wfo_data = pd.read_csv(csv_file, sep='\t', encoding='latin1')

    resolved = parse_wfo_data(all_wfo_data)

    csv_file.close()
    return resolved


def get_oldest_version():
    input_zip_file = os.path.join(_wfo_downloads_path, 'WFOTaxonomicBackbone_201807.zip')
    zf = zipfile.ZipFile(input_zip_file)
    csv_file = zf.open('classification.txt')

    all_wfo_data = pd.read_csv(csv_file, sep='\t')

    resolved = parse_wfo_data(all_wfo_data)

    csv_file.close()
    return resolved


if __name__ == '__main__':
    # get_latest_version()
    get_oldest_version()
