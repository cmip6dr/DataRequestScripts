# CMIP6 Priority Variables

The spreadsheet [AR6WG1_priorityVariables_table.xlsx](https://github.com/cmip6dr/DataRequestScripts/blob/master/AR6WG1_variables/AR6WG1_priorityVariables_table.xlsx)
is an edited version of a file created by Jasmin John, GFDL, listing variables mentioned in the IPCC WG1 AR6 First Order Draft.
Variable and experiment names have been adjusted to match valid CMIP6 names.

The JSON file [AR6WG1_priorityVariables.json](https://github.com/cmip6dr/DataRequestScripts/blob/master/AR6WG1_variables/AR6WG1_priorityVariables.json)
lists the variables requested for each experiment. E.g. 
```
dict = load.json( open( 'AR6WG1_priorityVariables.json' ) )
print ( dict["requested"]["1pctCO2"]["Amon"] )
```
Should print '["rlut", "rlutcs", "rsdt", "rsut", "rsutcs", "tas"]', which is the list of `Amon` variables needed from the `Amon` table. 

`dict["uids"]` contains the data request identifiers for each CMOR variable.

The JSON file [AR6WG1_priorityVariables_volumes.json](https://github.com/cmip6dr/DataRequestScripts/blob/master/AR6WG1_variables/AR6WG1_priorityVariables_volumes.json) is similar,
but contains a volume estimate for each variable based on a 1-degree atmosphere and 0.5-degree ocean.

The spreadsheet [AR6WG1_priorityVariables_table.xlsx](https://github.com/cmip6dr/DataRequestScripts/blob/master/AR6WG1_variables/AR6WG1_priorityVariables_table.xlsx) gives
a tabular view of these volume estimates.

# Issues

The list of variables requested from `1pctCO2` for `Amon` is rather short ... and should perhaps be augmented with other heavuly used 2-d fields, such as `pr` (precipitation) and `cl` (cloud cover).

A separate WGCM discussion raised the issue of [GCOS Global Climate Indicators](https://gcos.wmo.int/en/global-climate-indicators) which would also point to the need for a wider range of basic variables.
