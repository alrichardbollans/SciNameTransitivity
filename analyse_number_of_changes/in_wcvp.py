from WCVP_methods.updating_wcvp import get_all_databases
from analyse_number_of_changes.helper_functions import do_all_analyses_for_a_pair


def main():
    v10_taxa, v11_taxa, v12_taxa, v13_taxa, v14_taxa = get_all_databases()
    ## v14
    do_all_analyses_for_a_pair(v10_taxa, v14_taxa, 'v10', 'v14')
    do_all_analyses_for_a_pair(v11_taxa, v14_taxa, 'v11', 'v14')
    do_all_analyses_for_a_pair(v12_taxa, v14_taxa, 'v12', 'v14')
    do_all_analyses_for_a_pair(v13_taxa, v14_taxa, 'v13', 'v14')

    ## v13
    do_all_analyses_for_a_pair(v10_taxa, v13_taxa, 'v10', 'v13')
    do_all_analyses_for_a_pair(v11_taxa, v13_taxa, 'v11', 'v13')
    do_all_analyses_for_a_pair(v12_taxa, v13_taxa, 'v12', 'v13')

    ## v12
    do_all_analyses_for_a_pair(v10_taxa, v12_taxa, 'v10', 'v12')
    do_all_analyses_for_a_pair(v11_taxa, v12_taxa, 'v11', 'v12')

    ## v11
    do_all_analyses_for_a_pair(v10_taxa, v11_taxa, 'v10', 'v11')


if __name__ == '__main__':
    main()
