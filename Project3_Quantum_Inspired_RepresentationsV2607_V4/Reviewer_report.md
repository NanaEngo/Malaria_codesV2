Reviewer 1

A molecular descriptor is useful if it supports building a useful QSAR model - and each property to predict has its own "useful" descriptors. Therefore, your way of approaching this problem is wrong: "African" antimalarial compounds (what on Earth is an "African" molecule anyway? Are the protons in the carbon nuclei 100% African? Are you sure, because it seems to me that they were artificially generated - by the way, what made you think that is a good idea? Don't you think that the hundred billion feasible compounds are enough!? Being proud of one's origin does not mean that this needs to interfere with scientific objective assessment of reality!) is not it. Calculated activity scores even less so - those are notoriously easy to predict. And, anyway, each time you get ROC AUC values of 0.96 you may as well throw your model away - because it's better than real life: NOTHING in bioactivity measurement can be achieved with that high experimental accuracy! Not, anyway, in Malaria, where the ChEMBL results span a diverse battery of tests against different targets in Plasmodium at different development stages: pooling these absolutely uncorrelated data together makes no sense at all (other than learning the associated chemo types by heart).
So -speaking of ChEMBL: there are thousands of endpoints reported therein, and more than 700 of those have enough associated molecules - both actives and inactives, with reported pKi or pIC50 values that CAN be compared to each other (because they stem from a same assay!). Some of these sets feature thousands of compounds - in any case, you can duly benchmark your new descriptors against ECFP on all this rich data: sometimes they will win, sometimes they will lose - but if there is at least ONE target for which you can get a decent model with your descriptors but you cannot with classical ones, then your descriptors are good. Good everywhere, not only in Africa.

Reviewer 2

This study applies pretty recent methods for virtual screening.

major issues:
(1) page 9 section 4.2:
Correlation (assumingly Pearson's) coefficients around 0.47 rather
indicate low correlation and therefore are of litte predictive use.
The (general) question is furthermore if docking scores for this
target are reliable enough compared to available experimental data.
Therefore I recommend to formulate this section more carefully.

minor issues:
page 5 section 2.7: Two reference are missing marked by "??"
page 7 section 3.4: Two annonations are missing marked by "??"
page 8 section 3.6: One annonation is missing marked by "??"
page 8 section 3.7: The source and type of "multi-target docking data"
is not clear. Please add conclusive information (which is seemingly
found in the supporting information page S10?)
page 8 section 3.7: One reference to the suppl. material is missing "??"
Presumably, the format and style of reference citation have to be
adjusted to the requested form used in JCAMD.
supplementary information page 2 section 2: One annonation is missing marked by "??"
supplementary information page 2 section 3: two annonation are missing marked by "??"
supplementary information page 9 table S9: one annonation is missing marked by "??"
