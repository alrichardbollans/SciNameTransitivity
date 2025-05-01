# TaxoDrift

In botanical research, and biological research more broadly, taxonomic names change frequently due to new discoveries, updated classifications, and
revised nomenclature rules. **TaxoDrift** is a project aimed at analyzing and understanding the phenomenon of taxonomic drift and nomenclature changes
in botanical research.
This repository explores how taxonomic databases evolve over time and focuses on the following aspects:

- Identifying and understanding taxonomic drift across different database versions.
- Analyzing the impact of nomenclature changes on data standardization.

## Overview

I find with a lot of data curation tools/platforms (e.g. WikiData [1]) when someone adds a record for a plant, the reported name is resolved to some
up to date taxonomy, rather than just giving the reported name. For a few reasons this seems like bad practice,
but in particular I've been wondering if this can create inconsistencies over time as taxonomies are updated.

For example, say _Species A_, is found to contain quinine in some publication. Suppose in v10 of the World Checklist of Vascular Plants (WCVP) [2] this
is a synonym and the name resolves to
_Species B_ and so the recorded entry in WikiData is for _Species B_ when the data is entered. When the WCVP is updated to, say, v13, and the WikiData
entry is updated accordingly (either internally or when someone downloads the data and updates the taxonomy themselves) is the resolution of _Species B_
in v13 the same as the (presumably more accurate) direct resolution of _Species A_?

## Some Findings

It turns out this is not necessarily the case (examples are currently organised in [outputs](disagreements/outputs)). For example, _Panicum nitidum_ Lam. resolves to _Dichanthelium dichotomum_ (L.) Gould in v10, which in turn
resolves to _Dichanthelium dichotomum_ (L.) Gould in v13. However, if you were to use v13 directly to resolve the name given in the publication you get
_Dichanthelium nitidum_ (Lam.) Mohlenbr.

I found that this happens for around 0.7% of plant names, though the majority aren't particularly severe (the resolutions only differ at the
infraspecies level). The resolutions differ at the species level for around 0.3% of names, and at the genus level for around 0.03% of names e.g.
_Listrostachys pescatoriana_ (Lindl.) S.Moore -> _Oeoniella polystachys_ (Thouars) Schltr. -> _Oeoniella polystachys_ (Thouars) Schltr., in contrast to the
direct resolution of _Listrostachys pescatoriana_ (Lindl.) S.Moore -> _Listrostachys pertusa_ (Lindl.) Rchb.f.

I also found that chaining the resolutions via periodic updates e.g. v10->v11->v12->v13, doesn't seem to mitigate the issue.

While these percentages seem small, the drift across v10-v13 is less than 2 years of updates (v10 released 2022-12-08, v13 released 2024-05-21).

It's an issue that propagates over time --- a discrepancy for 0.24% of plant names for v10-v11 and 0.52% for v10-v12 compared to 0.72% for v10-v13.

This analysis uses the [wcvpy python package](https://github.com/alrichardbollans/wcvpy) and WCVP versions downloaded from http://sftp.kew.org/pub/data-repositories/WCVP/.

## References

[1] Vrandečić, Denny, and Markus Krötzsch. "Wikidata: a free collaborative knowledgebase." Communications of the ACM 57.10 (2014): 78-85.

[2] Govaerts, R., Nic Lughadha, E. et al. The World Checklist of Vascular Plants, a continuously updated resource for exploring global plant
diversity. Sci Data 8, 215 (2021). https://doi.org/10.1038/s41597-021-00997-6