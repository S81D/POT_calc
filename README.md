# POT_calc
Calculate recorded POT in ANNIE and from the IFBeam Database. ```POT_calculator.py``` sums the POT from both toroid devices stored in ```BeamFetcherV2``` root files for ANNIE. The beam data was fetched based on the recorded CTC timestamps, and thus is the POT "seen" by ANNIE. ```querybnb_ind.py``` fetches device information as recorded by the IFBeam database.

### usage:
```python3 querybnb_ind.py "2024-03-27 11:24:55.511343" "2024-03-31 15:57:41.028200"```

```python3 POT_calculator.py```
