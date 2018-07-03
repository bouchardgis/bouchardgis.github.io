## Script Samples
### Zion National Park - Python-Generated Map
The two scripts are used to create a map document where input features are buffered to show an impact zone around the input features of Zion National Park. Once done, a PDF of the map is automatically exported. 

#### Part A
This script takes input features that may be impacted by impacting features (input), and outputs a feature class including the input features that would be impacted within a buffer of the impacting features. 

Python: [ZionNationalPark_PythonGeneratedMap_PartA.py](https://github.com/bouchardgis/bouchardgis.github.io/blob/master/scripts/ZionNationalPark_PythonGeneratedMap_PartA.py)

#### Part B
This script is for Part B: Adds the provided datasets, and outputs from Part A to an already-created map document (MXD file). The map, once saved programmatically, is then exported to a PDF of the same name.

Python: [ZionNationalPark_PythonGeneratedMap_PartB.py](https://github.com/bouchardgis/bouchardgis.github.io/blob/master/scripts/ZionNationalPark_PythonGeneratedMap_PartB.py)

### SEEP - Solar Energy Estimations and Projections Scripts
#### DSM Generator
This script creates digital surface models (DSM) for the use in solar radiation simulations. 

Python: [SEEP_DSMGenerator.py](https://github.com/bouchardgis/bouchardgis.github.io/blob/master/scripts/SEEP_DSMGenerator.py)

#### Solar Energy Simulations & Energy Cost Estimations
This scrip creates solar radiation maps for the buildings specified in the building footprint and SQL search query parameters. Outputs a feature estimating the ideal solar installation for the building or home, and a solar map raster for its projected insolation in watt-hour per meter squared. 

Python: [SEEP_SolarEnergySimulationsAndEnergyCostEstimations.py](https://github.com/bouchardgis/bouchardgis.github.io/blob/master/scripts/SEEP_SolarEnergySimulationsAndEnergyCostEstimations.py)

