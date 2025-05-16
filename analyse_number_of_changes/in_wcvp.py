from wcvpy.wcvp_download import wcvp_accepted_columns, wcvp_columns

from WCVP_methods.updating_taxonomies import get_all_databases
from analyse_number_of_changes.helper_functions import get_species_differences, get_accepted_species_that_become_unaccepted, \
    get_unaccepted_species_that_become_accepted, get_names_that_resolve_in_old_but_not_in_new


def main():
    v10_taxa, v11_taxa, v12_taxa, v13_taxa = get_all_databases()
    get_species_differences(v10_taxa, v13_taxa, 'v10', 'v13')
    get_accepted_species_that_become_unaccepted(v10_taxa, v13_taxa, 'v10', 'v13')

    get_unaccepted_species_that_become_accepted(v10_taxa, v13_taxa, 'v10', 'v13')

    get_names_that_resolve_in_old_but_not_in_new(v10_taxa,v13_taxa, 'v10', 'v13')

if __name__ == '__main__':
    main()
