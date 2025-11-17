# XBI Flow – Cross-Species Trial Extraction Pipeline

This repository contains a data-processing pipeline for extracting and standardising trial-level information from touchscreen-based behavioural experiments across multiple primate species.  

The script processes raw CSV exports from different XBI/LXBI/MXBI systems and produces a unified **AllTrialsDF.csv** file containing harmonised trial metadata for marmosets, long-tailed macaques, and rhesus macaques.

---

## Overview

The main Python script:

- loads raw `.csv` data files from the `data/` directory  
- detects the experiment type from filenames (`CM_AUT`, `CM_2AC`, `LT`, `RM_MCI`, `RM_AUT`, `RM_MDSS`)  
- applies species-specific preprocessing steps  
- reformats and cleans inconsistent columns  
- extracts one row per trial (start + outcome)  
- attaches metadata such as animal, group, device, date, timestamps, task type, experiment type, and trial duration  
- concatenates all species into a single dataframe  
- exports a fully standardised file: **AllTrialsDF.csv**

The resulting dataframe contains comparable trial-level structure across experimental paradigms and species.

---

## Supported Data Types

The pipeline processes touchscreen data for:

### **Common Marmosets (CM)**
- Automatic training staircase (AUT)
- 2-alternative choice (2AC)

### **Long-tailed Macaques (LT)**
- AUT / 2AC-style tasks (harmonised automatically)

### **Rhesus Macaques (RM)**
- MCI (Monkey Continuous Integration task)
- AUT
- MDSS

Each dataset receives dedicated parsing, renaming, filtering, and trial-matching logic reflecting its specific format.

---

## Output Format

The final **AllTrialsDF.csv** includes the following harmonised columns:

- species  
- animal  
- trial  
- trial_timestamp  
- date  
- time  
- outcome  
- outcome_timestamp  
- step  
- experiment  
- task  
- device  
- group  
- duration  
- total_trials  
- fluid  
- food  
- isolation  
- stimulus_size  
- stimulus_speed  

All numeric fields are type-formatted, and categorical fields are string-normalised.

## License

All rights reserved.  
Please do not reuse or redistribute the code, data, or video assets without explicit permission.

© Antonino Calapai, 2021
