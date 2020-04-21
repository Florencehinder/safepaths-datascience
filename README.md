# safepaths-datascience
Repository with various data science projects in the branches (More coming soon)

## Data files
Links to several repositories of publicly available data are stored in the `data_sources.json` with the following structure:

```
data_sources.json:
    |--Global:
        |--source:link
    |--Nations:
        |--Regions:
            |--Provinces:
                |--source:link
```

## Ingesting algorithms
Ingesting pipelines need to check:
- file format: `csv`, `json`, etc.
- based on the file format, select the `longitude`, `latitude` and `timestamp` values (where present) _(in progress)_
- logging errors _(in progress)_
- build a harmonized file containing _only_ those three columns
- harmonize values (need to avoid doubling of data qhen present from different sources)
