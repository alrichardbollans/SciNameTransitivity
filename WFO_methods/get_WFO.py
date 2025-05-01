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
    ## Get a copy that wont be edited, just for sanity checks
    all_wfo_data_untouched = all_wfo_data.copy(deep=True)

    # restrict to genus and lower
    # some genus names werent correctly set
    all_wfo_data['genus'] = np.where(all_wfo_data['taxonRank'] == 'genus', all_wfo_data['scientificName'], all_wfo_data['genus'])
    all_wfo_data = all_wfo_data[~all_wfo_data['genus'].isna()]

    all_wfo_data['taxonRank'] = all_wfo_data['taxonRank'].str.lower()  # in old version they use upper case :(

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

    ### Use the accepted IDs to get accepted names from the original dataframe
    accepted_data = all_wfo_data[all_wfo_data['taxonomicStatus'] == 'Accepted'][['taxonID', 'taxon_name_w_authors', 'species_name', 'genus']]
    accepted_data = accepted_data.dropna(subset=['taxonID'])
    accepted_data = accepted_data.rename(
        columns={'taxonID': 'acc_id', 'taxon_name_w_authors': 'accepted_name_w_author', 'species_name': 'accepted_species',
                 'genus': 'accepted_genus'})

    resolved_wfo_data = pd.merge(resolved_wfo_data, accepted_data, how='left', left_on=['accepted_name_id'], right_on=['acc_id'])

    ###################
    ### Sanity checks
    accepted_check = resolved_wfo_data[resolved_wfo_data['taxonomicStatus'] == 'Accepted']
    pd.testing.assert_series_equal(accepted_check['taxon_name_w_authors'], accepted_data['accepted_name_w_author'], check_names=False,
                                   check_index=False)

    ### Check statuses in data
    statuses = all_wfo_data_untouched['taxonomicStatus'].dropna().unique().tolist()
    assert (list(sorted(statuses)) == ['Accepted', 'Synonym', 'Unchecked']) or (
            statuses == ['Synonym', 'Doubtful', 'Accepted', 'heterotypicSynonym', 'homotypicSynonym'])

    ### Check statuses again
    statuses = resolved_wfo_data['taxonomicStatus'].unique().tolist()
    assert (list(sorted(statuses)) == ['Accepted', 'Synonym']) or (
            statuses == ['Synonym', 'Accepted', 'heterotypicSynonym', 'homotypicSynonym'])

    ahhhh = list(sorted(all_wfo_data['taxonRank'].unique().tolist()))
    for a in ahhhh:
        assert a in ranks_to_use

    # Cases where accepted_ids in resolved_wfo_data aren't found in accepted_data
    nan_issues = resolved_wfo_data[resolved_wfo_data['accepted_name_w_author'].isna()]
    if len(nan_issues) > 0:
        # In old version, some taxa resolve to an ID which isn't counted as accepted. These will just be removed
        to_check = resolved_wfo_data[~resolved_wfo_data['accepted_name_id'].isin(accepted_data['acc_id'].values)]
        things_that_have_been_removed = all_wfo_data_untouched[all_wfo_data_untouched['taxonID'].isin(to_check['accepted_name_id'].values)]
        to_check2 = resolved_wfo_data[~resolved_wfo_data['accepted_name_id'].isin(all_wfo_data_untouched['taxonID'].values)]

        what_are_these = all_wfo_data_untouched[all_wfo_data_untouched['taxonID'].isin(nan_issues['accepted_name_id'].values)]
        what_are_these = what_are_these[
            ~what_are_these['taxonRank'].isin(['family', 'tribe', 'subfamily', 'order', 'class', 'subtribe'])]  # a family/tribe etc.. was erroneously included
        print(what_are_these['taxonomicStatus'].unique().tolist())
        assert 'Accepted' not in what_are_these['taxonomicStatus'].values

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
