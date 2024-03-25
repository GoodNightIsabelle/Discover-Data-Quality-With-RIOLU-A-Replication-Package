# Discover-Data-Quality-With-RIOLU-A-Replication-Package

### The repository contains the replication package for the paper "Automated, Unsupervised, and Non-parameterized Inference of Data Patterns and Anomaly Detection".

## Introduction
The workflows of our tool (Auto-RIOLU and Guided-RIOLU) are shown in the following graph:

![image](https://github.com/GoodNightIsabelle/Discover-Data-Quality-With-RIOLU-A-Replication-Package/assets/64899589/e7d854d7-b559-435a-9d81-8a1ac8f4d730)

**Column Sampling:** Sample a subset of data from the column to generate the patterns. 

**Coverage Rate (rcov) Estimation:** Estimate the percentage of healthy values (rcov) in each column using either the supervised or unsupervised method.

**Constrained Template Generation:** Constrained Template Generation: Generate raw templates for each record with an exact matching rate rEM (rEM=rcov in our study) as a granularity constraint.

**Pattern Generation:** Generate pattern constraints for each template according to the coverage rate (rcov).

**Pattern Selection:** Select patterns based on some heuristics (e.g., their generalizability). 

## Dependencies

- Python >= 3.8

- Pandas == 1.5.3

- Numpy == 1.24.3

- Scikit-learn == 1.3.2

- Matplotlib == 3.7.5

## Dataset

### Source
We use the DOMAINS dataset documented in FlashProfile for data profiling evaluation. The original data is shared through https://github.com/SaswatPadhi/FlashProfileDemo/tree/master/tests. According to the instructions, we removed the extreme-size data (containing <40 or >100k records) and the duplicates. The files for the DOMAINS dataset can be accessed through the ```test_data_profiling``` folder. 

We use the modified version of the Hospital, Flights, and Movies dataset (https://github.com/visenger/clean-and-dirty-data, https://github.com/BigDaMa/raha/tree/master/datasets) for data anomaly detection task. The modified versions are available in ```test_anomaly_detection``` folder, and the ground truths for these data are in the ```ground_truth_anomaly_detection``` folder (-1 for null values, 1 for anomalies, 0 for non-anomalies). 

## Experiments
The procedure for replicating our experiments is as follows:

### Data Profiling
Run code ```test_profiling.py``` to get the data profiling result provided by RIOLU's pattern generation module. The patterns for each file, overall precisions, and overall recalls will be printed in the output, and a graphic result will be automatically stored in the folder. 

An example of the printed graph: 
![profiling_quality](https://github.com/GoodNightIsabelle/Discover-Data-Quality-With-RIOLU-A-Replication-Package/assets/64899589/06dd9b38-da43-42a2-b261-980411513e2e)

### Anomaly Detection
The two anomaly detection tools read the dataset in the ```test_anomaly_detection``` folder. Change the variable of ```dataset``` in the code to specify the desired dataset (valid data in our folder: hosp_1k, hosp_10k, hosp_100k, movies), the code will automatically read the ground truth to fetch the columns to be tested (not all the columns contain pattern anomalies). 

#### Unsupervised Version (Auto-RIOLU)
![image](https://github.com/GoodNightIsabelle/Discover-Data-Quality-With-RIOLU-A-Replication-Package/assets/64899589/328c417a-e2f6-4fd0-8667-daa9beccd670)

Run code ```Auto-RIOLU.py``` to get the result of the unsupervised version of RIOLU; the predicted CSV file will be stored. 

#### Supervised Version (Guided-RIOLU)
![image](https://github.com/GoodNightIsabelle/Discover-Data-Quality-With-RIOLU-A-Replication-Package/assets/64899589/a0da6dca-33aa-4865-bac5-ad3ac1059210)

Run code ```Guided-RIOLU.py```to get the result of the supervised version of RIOLU; the predicted CSV file will be stored. We use the cleaned version of each dataset as a support to estimate the coverage rate (rcov). 
