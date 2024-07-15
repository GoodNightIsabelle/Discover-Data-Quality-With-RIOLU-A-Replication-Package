# Anomaly Detection Dataset
## Source 
The data (both the real-life raw version and the cleaned version) originally came from previous data quality studies. We selected several columns in the datasets that contain pattern violation issues for RIOLU's anomaly detection evaluation. 
1. ```Hosp-1k, Hosp-10k, Hosp-100k```: Hospital data from US Department of Health & Human Services. ([original](https://github.com/visenger/clean-and-dirty-data))
3. ```Flights```: Flight departure/arrival data from 3 airline websites (AA, UA, and Continental), 8 airport websites (e.g., SFO, DEN), and 27 third-party websites (e.g., Orbitz, Travelocity). ([original](https://github.com/visenger/clean-and-dirty-data))
4. ```Movies```: IMdB film dataset.  ([original](https://github.com/BigDaMa/raha/tree/master/datasets/movies_1))

## ChatGPT Predictions
The data sampled for ChatGPT prompting are under the ```chatgpt_sampled``` folder, with the format of ```dirty_{dataset}.csv```. The inferred regexes are stored in the txt files with names: ```pred_{dataset}.txt```. 
