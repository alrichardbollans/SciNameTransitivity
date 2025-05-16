from WFO_methods.get_WFO import get_latest_version, get_oldest_version, get_version_comparable_to_v10
from analyse_number_of_changes.helper_functions import get_species_differences, get_accepted_species_that_become_unaccepted, \
    get_names_that_resolve_in_old_but_not_in_new, get_unaccepted_species_that_become_accepted


def main():
    new, new_tag = get_latest_version()
    old, old_tag = get_oldest_version()

    get_species_differences(old, new, old_tag, new_tag)
    get_accepted_species_that_become_unaccepted(old, new, old_tag, new_tag)

    get_unaccepted_species_that_become_accepted(old, new, old_tag, new_tag)

    get_names_that_resolve_in_old_but_not_in_new(old, new, old_tag, new_tag)

    v10_rep, v10_rep_tag = get_version_comparable_to_v10()
    get_species_differences(v10_rep, new, v10_rep_tag, new_tag)
    get_accepted_species_that_become_unaccepted(v10_rep, new, v10_rep_tag, new_tag)

    get_unaccepted_species_that_become_accepted(v10_rep, new, v10_rep_tag, new_tag)

    get_names_that_resolve_in_old_but_not_in_new(v10_rep, new, v10_rep_tag, new_tag)


if __name__ == '__main__':
    main()
