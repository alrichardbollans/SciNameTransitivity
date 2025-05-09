import os.path
from operator import index

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

def get_wcvp_species_results():
    data = []
    version_dict = {'2023-04':'v11', '2023-09': 'v12', '2024-05':'v13'}
    for y in version_dict:
        result_df = pd.read_csv(os.path.join('..', 'WCVP_methods', 'outputs', f'v10_{version_dict[y]}','result_summary.csv'), index_col=0)
        species_percent = result_df['Percentages'].loc['species_disagreements']
        print(species_percent)
        data.append([y, species_percent])
    return data
def plot_changes():
    # flights = sns.load_dataset("flights")

    wcvp_df = pd.DataFrame(get_wcvp_species_results(),
                           columns=['Year', 'Species Discrepancy (%)'])
    wcvp_df['Taxonomy'] = 'WCVP'

    wfo_df = pd.DataFrame([[2017, 1], [2018, 2], [2019, np.nan], [2020, 4], [2021, 6]], columns=['Year', 'Species Discrepancy (%)'])
    wfo_df['Taxonomy'] = 'WFO'

    df = pd.concat([wcvp_df, wfo_df])
    df["Year"] = df["Year"].astype(str)
    df = df.sort_values(by='Year', ascending=True)
    df = df.reset_index(drop=True)
    plot = sns.lineplot(
        # ax=ax
        data=df, x="Year", y="Species Discrepancy (%)", hue='Taxonomy'
        # , hue=df["Data"].isna().cumsum()
        # , palette=["blue"] * sum(df["Data"].isna())
    )

    # ax.set_xticklabels([])

    plt.show()


if __name__ == '__main__':
    plot_changes()
