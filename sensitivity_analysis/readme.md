# Understand the Default Parameters!
As we have analyzed in the ablation study (and also in our comparison between Auto-RIOLU and Guided-RIOLU), **an accurate estimation of $r_{cov}$** is essential for the inference quality of RIOLU. Auto-RIOLU relies on **$r_{cov\\_init}$** and **$N_{subset}$** for the estimation. To validate the effectiveness of our default parameter choice, we carried out a sensitivity analysis to ensure the parameters are generalizable to different datasets. 

# Variation Ranges
- **$r_{cov\\_init}$**: 0.85, 0.9, 0.95, 0.99 (Run ```Auto_RIOLU_alt_nsubset.py``` to replicate the experiment.)
- **$N_{subset}$**: From 1 to 10 (Run ```Auto_RIOLU_alt_inircov.py``` to replicate the experiment.)

# Our Findings

![sensitivity_analysis](../images/sensitivity_analysis.png?raw=true)
- **$r_{cov\\_init}$**: The optimal choice of $r_{cov\\_init}$ varies across datasets, given that their error rates are drastically different. Although we can optimize the average performance on the datasets by 4% by decreasing the $r_{cov\\_init}$ value, we stuck to the setting of 0.95 based on the intuition by Song and He, that the non-conforming values tend to be minor in production. 

- **$N_{subset}$**: We observed a peak of average f1 score when setting Nsubset to 5: a smaller number may cause the samples to be less representative, whereas a larger number would decrease the efficiency and may cause too many overlaps among the samples. 

Overall, we observe that the performance of Auto-RIOLU is relatively stable across different parameter settings.
