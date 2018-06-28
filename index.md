# Bouchard's GIS Portfolio

This page contains GIS and coding samples created in recent years - ranging from scripts to maps produced, as well as screencaptures of prior apps. 

## Contents
* [Apps & Projects](#apps)
* [Maps](#maps)
* [Reports](#reports)
* [Scripts](#scripts)
* [Resume](#resume)

---

## Apps & Projects <a name="apps"></a>
### SEEP Web App - Solar Energy Estimations & Projections
[![alt text](https://bouchardgis.github.io/images/SEEP_SolarEnergyEstimationsAndProjections_Screencap.PNG "SEEP Web App")](https://bouchardgis.github.io/images/SEEP_SolarEnergyEstimationsAndProjections_Screencap.PNG)

The goal of this project was to create a process driven solar energy estimation web app for the City of Airdrie. This was a pilot project to show how a process-driven tool for solar energy estimation could be scaled up to other locales. 

The web app was created from LiDAR and census data for the City of Airdrie, all of the data open source catalog and is available to download by the general public. ESRI’s ArcGIS Solar radiation tools were used to produce estimated solar insolation on the rooftops of buildings in the city for a full calendar year (simulated). Further calculations were done based on NREL's (National Renewable Energy Laboratory) research for the cost of solar energy generation - these results were added as tabular data for each building in the city. The results of this project are a working web app for the City of Airdrie that will give users key solar information for a given address.

<a href="http://sait.maps.arcgis.com/apps/webappviewer/index.html?id=2fb5fd4773eb4cefb37facf0c7ac1ae7" target="_blank">SEEP - Solar Energy Estimations & Projections (Web App)</a>

---

## Maps <a name="maps"></a>
### Natural Regions of Alberta
[![alt text](https://bouchardgis.github.io/images/Alberta_NaturalRegionsMap.PNG   "Natural Regions of Alberta")](https://bouchardgis.github.io/images/Alberta_NaturalRegionsMap.PNG)

### Crane Glacier Surfaces
[![alt text](https://bouchardgis.github.io/images/CraneGlacier_SurfaceGeneration.PNG  "Crane Glacier - Surfaces")](https://bouchardgis.github.io/images/CraneGlacier_SurfaceGeneration.PNG)

The Crane Glacier, in Antarctica, has been undergoing dramatic changes in recent decades due to a changing climate. These changes can be studied in greater detail with the help of surface visualizations. This map includes a compilation of surfaces generated using ArcGIS: a digital elevation model (DEM), slope, aspect, hillshade, viewshed sample, and solar insolation.

For more details, please read the [Crane Glacier Surfaces Generation Report (PDF)](https://bouchardgis.github.io/reports/CraneGlacierStudy_SurfaceGenerationReport.pdf).

### Waiparous Image Classication
[![alt text](https://bouchardgis.github.io/images/Waiparous_ImageClassification_forWesternSkyLandTrust.PNG  "Waiparous Image Classification")](https://bouchardgis.github.io/images/Waiparous_ImageClassification_forWesternSkyLandTrust.PNG) 

The Western Sky Land Trust (WSLT) is striving to conserve open and natural areas within the Calgary region, focusing on watershed lands associated to agricultural, natural, heritage, scenic, and recreational values (WSLT, 2015). They have approached our team to help them to produce a sampling strategy for a species inventory program on a land parcel near Waiparous, AB – including vegetation, wildlife, and aquatic species.

For more details, please read the [Waiparous, AB - Image Classification Report (PDF)](https://bouchardgis.github.io/reports/WaiparousAB_ImageClassification_forWLST.pdf).

---

## Reports <a name="reports"></a>
### Crane Glacier - Surfaces Generation
The report that goes along with the Crane Glacier Surfaces Map describes in detail how the surfaces were generated in ArcGIS. 

[Crane Glacier Surfaces Generation Report (PDF)](https://bouchardgis.github.io/reports/CraneGlacierStudy_SurfaceGenerationReport.pdf)

### Waiparous, Alberta - Image Classification
This report details the process used to gather data of the Waiparous region of Alberta for image classification.

[Waiparous, AB - Image Classification Report (PDF)](https://bouchardgis.github.io/reports/WaiparousAB_ImageClassification_forWLST.pdf)

---

## Scripts <a name="scripts"></a>
### PowerShell Data Handling Samples
#### Data Rollup
```powershell
#
# PowerShell Data Rollup
# 
# Purpose: to roll up all of the wells in a group into one well that shows the total volumes =sum(all wells for each column)
#  -ie. All values for a particular date need to be summed; vastly reducing the number of rows - a rollup
# 
# Created by: BouchardGIS
# Date: June 20, 2018
#
# References: https://serverfault.com/questions/141923/importing-from-csv-and-sorting-by-date
#            https://stackoverflow.com/questions/12368142/powershell-retrieving-a-variable-from-a-text-file?rq=1
#


# Initialize Directories
#$scriptpath = $MyInvocation.MyCommand.Path
$dir = "D:\sample\"
$configFile = "$dir\CustomCfg.cfg"

# Retrieve Config Data from DSCustomCfg (Custom Scripts config file)
$config = Get-Content $configFile | Out-String | ConvertFrom-StringData

# Initialize Required Filenames
# TODO: Determine what filename the autoloader outputs
$inputFileName = $config.inputFileName
$intermediate = "ParamountResourcesLtd_TEMP.csv"
$outputFileName = $config.outputFileName

# FTP Credential Setup
$ftp = $config.ftp
$user = $config.user
$pass = $config.pass
$uploadfilepath = "$dir\$outputFileName"

# =============== User Variables ===============
# NOTE: This is where the UWI, Battery, Well, Company Name and Field Name can be changed for the group rollup
$CompanyName = $config.CompanyName
$FieldName = $config.FieldName
$Battery = $config.Battery
$Well = $config.Well
$UWI = $config.UWI


# Import CSV & Export a Temp File (Intermediate)
# - Sorts rows by Date
$Imported = Import-Csv "$dir\$inputFileName" | Sort-Object -Property {$_.'Date' -as [datetime]} | ConvertTo-Csv -NoTypeInformation | Select -Skip 0 | ForEach-Object {$_ -replace """", ""} | Set-Content -path "$dir\$intermediate"

# Import Intermediate CSV
$Imported = Import-Csv "$dir\$intermediate" -Header A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W

# Initialize Counters & Sums
# Columns: oilVol, H; waterVol, I; condVol, J; gasVol, K; hoursOn, M
$rowCounter = 0
$maxRows = 0
$oilVol = 0.00
$waterVol = 0.00
$condVol = 0.00
$gasVol = 0.00
$hoursOn = 24.00
$tubingPrs = 0.00
$casingPrs = 0.00
$chokeSz = 0.00

# - Initialize Current date
$currentDate = ""
$previousDate = ""

# - Determine Size of Object using rowCounter, Reset rowCounter After Use
foreach($r in $Imported) {
	$rowCounter++
}

$maxRows = $rowCounter - 1

#Write-Host $maxRows

$rowCounter = 0

# Cycle Through Sorted File, Sum Variables
$Output = foreach ($i in $Imported) {
	$currentDate = $i.G
	
	# If first row, store header row (first = 0)
	if($rowCounter -le 1) {
		if($rowCounter -eq 0) {
			$i
		}

		# If second row (1) start summing values
		if($rowCounter -eq 1) {
			$oilVol += [double]$i.H
			$waterVol += [double]$i.I
			$condVol += [double]$i.J
			$gasVol += [double]$i.K

			# If second row Tubing, Casing, or Choke size are not equal to the initial value
			if(([double]$i.O -ne 0) -or ([double]$i.P -ne 0) -or ([double]$i.U -ne 0)) {
				$tubingPrs = [double]$i.O
				$casingPrs = [double]$i.P
				$chokeSz = [double]$i.U
			}
		}
	}
	else {
		# If current date is equal to previous date (row)
		# - Add to sums
		if($currentDate -eq $previousDate) {
			$oilVol += [double]$i.H
			$waterVol += [double]$i.I
			$condVol += [double]$i.J
			$gasVol += [double]$i.K
		}
		
		# If current date is not equal to previous date (row)
		# - Change UWI, Set Totalled Values, Store in $i, Reset Counters
		# - Columns L, N, Q, R, S, T, V, W should be set to values as below (this can be changed for other scripts)
		if(($currentDate -ne $previousDate) -or ($rowCounter -eq $maxRows)) {
			# Set Company, Field, Battery, Well, UWI, and values to blank for new stored row
			$i.B = $CompanyName
			$i.C = $FieldName
			$i.D = $Battery
			$i.E = $Well
			$i.F = $UWI
			$i.L = '0'
			$i.N = 'none'
			$i.Q = '0'
			$i.R = '0'
			$i.S = '0'
			$i.T = '0'
			$i.V = '0'
			$i.W = 'none'

			# Store Tubing, Casing, and Choke values as needed (if they haven't already been updated in line 1 of data)
			if(([double]$i.O -ne 0) -or ([double]$i.P -ne 0) -or ([double]$i.U -ne 0)) {
				$tubingPrs = [double]$i.O
				$casingPrs = [double]$i.P
				$chokeSz = [double]$i.U
			}

			# Store Current Totals into Set Variables
			$oilVolSet = [double]$oilVol
			$waterVolSet = [double]$waterVol
			$condVolSet = [double]$condVol
			$gasVolSet = [double]$gasVol
			$hoursOnSet = $hoursOn
			$tubingPrsSet = [double]$tubingPrs
			$casingPrsSet = [double]$casingPrs
			$chokeSzSet = [double]$chokeSz

			# Reset Totals to the values in the current row (to start the next set)
			$oilVol = [double]$i.H
			$waterVol = [double]$i.I
			$condVol = [double]$i.J
			$gasVol = [double]$i.K

			# Set Totalled Values (Replace this Row's Values)
			$i.H = $oilVolSet
			$i.I = $waterVolSet
			$i.J = $condVolSet
			$i.K = $gasVolSet
			$i.M = $hoursOnSet
			$i.O = $tubingPrsSet
			$i.P = $casingPrsSet
			$i.U = $chokeSzSet

			# Set the date for this set (previous date)
			$i.G = $previousDate

			# Store in Output Object
			$i
		}	
	}

	# At end of loop, set $previousDate to equal the currentDate 
	# (so the next cycle through should show a difference in dates when required)
	$previousDate = $currentDate

	$rowCounter++

	
}


# Export Finished File
$Output | ConvertTo-Csv -NoTypeInformation | Select -Skip 1 | Set-Content -path "$dir\$outputFileName"

# Cleanup
Remove-Item "$dir\$Intermediate"

# Push files to FTP
# - Setup Webclient
$webclient = New-Object System.Net.WebClient

$webclient.Credentials = New-Object System.Net.NetworkCredential($user, $pass)

# - Upload Converted CSV to FTP Server
$uri = New-Object System.Uri($ftp+$outputFileName)
$webclient.UploadFile($uri,$uploadfilepath)
```

Configuration File:
"CustomCfg.cfg"
```
inputFileName = inputFileName.csv
outputFileName = outputFileName.csv
CompanyName = Sample Company Inc
FieldName = Sample Field
Battery = Sample Battery Location
Well = Sample Well Location
UWI = sample UWI
ftp = ftp://sampleftp.com/
user = "username"
pass = "samplePassword"
```


### Python ArcGIS Samples


---

## Resume <a name="resume"></a>
[Click here to see full Resume](https://linkedin.com/in/davidjbouchard)

