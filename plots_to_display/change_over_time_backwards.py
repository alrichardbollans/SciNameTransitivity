import os.path

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from scipy import stats

from WCVP_methods.updating_wcvp import wcvp_version_order
from WFO_methods.get_WFO import all_wfo_version_strings, latest_wfo_version_string

repo_path = os.environ.get('KEWSCRATCHPATH')
this_repo_path = os.path.join(repo_path, 'TaxoDrift')
_wcvp_output_path = os.path.join(this_repo_path, 'WCVP_methods', 'outputs')
_wfo_output_path = os.path.join(this_repo_path, 'WFO_methods', 'outputs')
version_dict = {'2022-10': 'v10', '2023-04': 'v11', '2023-09': 'v12', '2024-05': 'v13'}


def format_wfo_string(given_string):
    return given_string[:4] + '-' + given_string[4:]


def get_wcvp_species_results(latest_version):
    data = []
    for y in version_dict:
        if version_dict[y] != latest_version:
            if wcvp_version_order.index(version_dict[y]) < wcvp_version_order.index(latest_version):
                result_df = pd.read_csv(os.path.join(_wcvp_output_path, f'{version_dict[y]}_{latest_version}', 'result_summary.csv'), index_col=0)
                species_percent = result_df['Percentages'].loc['species_disagreements']
                print(species_percent)
                data.append([y, species_percent])
        else:
            data.append([y, 0])
    return data


def get_wfo_species_results(latest_version):
    data = []
    for y in all_wfo_version_strings:
        if y != latest_version:
            if all_wfo_version_strings.index(y) < all_wfo_version_strings.index(latest_version):
                result_df = pd.read_csv(os.path.join(_wfo_output_path, f'{y}_{latest_version}', 'result_summary.csv'), index_col=0)
                species_percent = result_df['Percentages'].loc['species_disagreements']
                # print(species_percent)
                y_formatted = format_wfo_string(y)
                data.append([y_formatted, species_percent])
        else:
            data.append([format_wfo_string(latest_version), 0])
    return data


def plot_changes_just_with_last_version():
    # flights = sns.load_dataset("flights")
    sns.set_theme()
    wcvp_df = pd.DataFrame(get_wcvp_species_results('v13'),
                           columns=['Date', 'Species Discrepancy (%)'])
    wcvp_df['Taxonomy'] = 'WCVP'

    wfo_df = pd.DataFrame(get_wfo_species_results('202412'), columns=['Date', 'Species Discrepancy (%)'])
    wfo_df['Taxonomy'] = 'WFO'

    df = pd.concat([wcvp_df, wfo_df])
    df["Date"] = df["Date"].astype(str)
    df = df.sort_values(by='Date', ascending=True)
    df = df.reset_index(drop=True)
    plot = sns.lineplot(
        # ax=ax
        data=df, x="Date", y="Species Discrepancy (%)", hue='Taxonomy'
        # , hue=df["Data"].isna().cumsum()
        # , palette=["blue"] * sum(df["Data"].isna())
    )
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()
    # ax.set_xticklabels([])

    plt.savefig('outputs/species_discrepancy_over_time_backwards.png', dpi=300)
    plt.close()


def plot_changes_separate_taxonomies():
    # flights = sns.load_dataset("flights")
    sns.set_theme()
    all_wcvp_df = pd.DataFrame()
    for w in wcvp_version_order[1:]:
        wcvp_df = pd.DataFrame(get_wcvp_species_results(w),
                               columns=['Date', 'Species Discrepancy (%)'])
        wcvp_df['Taxonomy'] = f'WCVP ({w})'
        all_wcvp_df = pd.concat([all_wcvp_df, wcvp_df])

    all_wcvp_df["Date"] = all_wcvp_df["Date"].astype(str)
    df = all_wcvp_df.sort_values(by='Date', ascending=True)
    df = df.reset_index(drop=True)
    plot = sns.lineplot(
        # ax=ax
        data=df, x="Date", y="Species Discrepancy (%)", hue='Taxonomy', linestyle='--'
        # , hue=df["Data"].isna().cumsum()
        # , palette=["blue"] * sum(df["Data"].isna())
    )
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()
    # ax.set_xticklabels([])

    plt.savefig('outputs/species_discrepancy_over_time_backwards_WCVP_cases.png', dpi=300)
    plt.close()

    all_wfo_df = pd.DataFrame()
    for w in all_wfo_version_strings[1:]:
        wfo_df = pd.DataFrame(get_wfo_species_results(w),
                               columns=['Date', 'Species Discrepancy (%)'])
        wfo_df['Taxonomy Version'] = f'WFO ({w})'
        all_wfo_df = pd.concat([all_wfo_df, wfo_df])

    all_wfo_df["Date"] = all_wfo_df["Date"].astype(str)
    df = all_wfo_df.sort_values(by='Date', ascending=True)
    df = df.reset_index(drop=True)
    plot = sns.lineplot(
        # ax=ax
        data=df, x="Date", y="Species Discrepancy (%)", hue='Taxonomy Version', linestyle='--'
        # , hue=df["Data"].isna().cumsum()
        # , palette=["blue"] * sum(df["Data"].isna())
    )
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()
    # ax.set_xticklabels([])

    plt.savefig('outputs/species_discrepancy_over_time_backwards_WFO_cases.png', dpi=300)
    plt.close()



def do_permutation_spearman_test(x, y):
    def statistic(x):  # permute only `x`

        return stats.spearmanr(x, y).statistic

    res_exact = stats.permutation_test((x,), statistic,

                                       permutation_type='pairings')
    return res_exact


def spearman_tests():
    out_data = []
    wcvp_data = get_wcvp_species_results('v13')

    # Test monotonic relationships of data over time
    y = [wcvp_data.index(c) for c in wcvp_data[:-1]]  ## remove last case as thats a given

    x = [c[1] for c in wcvp_data[:-1]]
    res_exact = do_permutation_spearman_test(x, y)
    out_data.append([res_exact.statistic, res_exact.pvalue, 'WCVP'])
    print(res_exact)
    print(res_exact.statistic)
    print(res_exact.pvalue)

    wfo_data = get_wfo_species_results('202412')

    y = [wfo_data.index(c) for c in wfo_data[:-1]]  ## remove last case as thats a given

    x = [c[1] for c in wfo_data[:-1]]
    res_exact = do_permutation_spearman_test(x, y)
    print(res_exact)
    print(res_exact.statistic)
    print(res_exact.pvalue)
    out_data.append([res_exact.statistic, res_exact.pvalue, 'WFO'])

    out_df = pd.DataFrame(out_data, columns=['Spearman Correlation', 'P-value', 'Taxonomy'])
    out_df.to_csv('outputs/spearman_tests_backwards.csv')


if __name__ == '__main__':
    plot_changes_separate_taxonomies()
    # plot_changes_just_with_last_version()
    # spearman_tests()
