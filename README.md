# eamena-functions
> Functions for EAMENA data management

## type of functions

| type | description |
|----------|----------|
| reference_data   | [reference_data.py](reference_data.py)   |
| business_data   | [business_data.py](business_data.py)   |

### reference_data 

#### UUIDs

Run the Python function [nodes_uuids()](https://github.com/eamena-project/eamena-functions/blob/main/reference_data.py) on a **RM** (JSON) or a file of **concepts** (XML) to collect the UUIDs of the nodes

* **RM** (example)

```Python
df_nodes = nodes_uuids(choice = "rm", rm = "https://raw.githubusercontent.com/eamena-project/eamena/master/eamena/pkg/graphs/resource_models/Heritage%20Place.json")
file_path = "C:/Rprojects/eamenaR/inst/extdata/ids_temp.csv"
df_nodes.to_csv(file_path, sep=',', index=False)
```
Gives this [ids_temp.csv](https://github.com/eamena-project/eamenaR/blob/main/inst/extdata/ids_temp.csv) file. Such a mapping table can be used in the [eamenaR package](https://github.com/eamena-project/eamenaR?tab=readme-ov-file#uuids-of-the-nodes)

* **concepts** (example)
 
```Python
nodes_uuids(choice = "concept")
```
Gives the [concepts_readonly.tsv](https://github.com/eamena-project/eamena-arches-dev/blob/main/dbs/database.eamena/data/reference_data/concepts/concepts_readonly.tsv) listing

> **Note:** Fieldnames (ex: "Effect type") have UUIDs. To check these correspondances, check the `nodeid` in the RM. For example, the "Effect type" field has the UUID `34cfea90-c2c0-11ea-9026-02e7594ce0a0` (see its [fieldname](https://github.com/achp-project/prj-eamena-marea/blob/8e397ad1343cd7fb04e4ca8a50247a1e3a687cb2/resource_models/Heritage%20Place.json#L2036) and [uuid](https://github.com/achp-project/prj-eamena-marea/blob/8e397ad1343cd7fb04e4ca8a50247a1e3a687cb2/resource_models/Heritage%20Place.json#L6530)).



**TODO**: 
- add all reference data based function in only one script: `reference_data.py` for reference data, and `business_data` for business data

```py
##################################################################################################################
## renamed, adapted and moved to https://github.com/eamena-project/eamena-functions/tree/main/reference_data.py ##
## renamed, adapted and moved to https://github.com/eamena-project/eamena-functions/tree/main/business_data.py  ##
####################################################################################################################
```

- archive all previous scripts (`grids.py`,https://github.com/eamena-project/eamena-arches-dev/blob/main/dbs/database.eamena/data/reference_data/uuids/nodes_uuids.py, etc.) 
