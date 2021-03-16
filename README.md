<img src="https://d2jx2rerrg6sh3.cloudfront.net/image-handler/ts/20200420091641/ri/674/picture/2020/4/%40shutterstock_1647268288.jpg">

<!-- Add buttons here -->
![Follow me at Twitter](https://img.shields.io/twitter/follow/NMashinchi?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/navido89/Time-Series-Analysis-ARIMA-Model-Covid19-Predictions)

# COVID-19 Dashboar - Web App
**Project Status: Completed**
<br>
<a href="https://share.streamlit.io/navido89/covid19-dashboard-dataviz/app.py" target="_blank">Check out my app.</a>

## Table of contents
- [Project Objective](#project-objective)
- [Methods Used](#methods-used)
- [Technologies](#technologies)
- [Installation](#installation)

## Project Objective & Description
[(Back to top)](#table-of-contents)
<br>
Welcome to my COVID-19 data visualization web app. The purpose of this project is to have a look at the current state of COVID-19 using visualizations from different geographical perspectives. The plots have been created by using data visualization tools such as Plotly and Folium. The project is broken down into three parts.

+ **1. Global COVID-19 Situation**: We will display a folium map that shows the total cases, total deaths, total cases per 100,000, and total deaths per 100,000. In addition to that, we will display various time series plots to understand better how the disease spreads over time across the globe.

+ **2. COVID-19 Situation by World Health Organization Region (WHO)**: In the following section, we look at the disease from the World Health Organization's regional perspective. We will compare the different regions based on their total cases, total deaths, total cases per 100 million and total deaths per 100 million deaths.

+ **3. COVID-19 Situation in the United States**: Last but not least, we pay our attention to the United States and explore the current situation in the US based on the cases, deaths (with and without per capita), vaccine status, and the status of the different variants spreading across the states.

The data is pulled from various resources, as you can see below in the Data Source section, and it will be updated daily by the various organizations listed below.

If you have any questions regarding this project or require any further information, feel free to <a href="https://www.navidma.com/contact" target="_blank">contact me.</a>

<br>
<p align="center">
<img src="images/shootings_by_year.png" style>
</p>

## Methods Used
[(Back to top)](#table-of-contents)
+ Data Cleaning
+ Feature Engineering
+ Data Visualization

## Technologies:
[(Back to top)](#table-of-contents)
+ Streamlit
+ Python
+ Pandas 
+ NumPy 
+ GeoPandas
+ Folium
+ Plotly 
+ Branca 
+ Jinja2
+ Date

## Data Source:
[(Back to top)](#table-of-contents)


**COVID-19 - Data:**            
+ [Global Cases](https://raw.githubusercontent.com/CSSEGISandData/COVID19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv) by Johns Hopkins CCSE.
+ [Global Deaths](https://raw.githubusercontent.com/CSSEGISandData/COVID19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv) by Johns Hopkins CCSE.
+ [US Cases](https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv) by Johns Hopkins CCSE.
+ [US Deaths](https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv) by Johns Hopkins CCSE.
+ [Global Data](https://covid19.who.int/WHO-COVID-19-global-data.csv) by World Health Organization.
+ [US Vaccine Data](https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/us_state_vaccinations.csv) by Our World in Data.
+ [US COVID-19 Cases Variants Data](https://www.cdc.gov/coronavirus/2019-ncov/downloads/transmission/03112021_Web-UpdateCSV-TABLE.csv) by Centers for Disease Control and Prevention (CDC).

**Population - Data:**
+ [2020 Population by country](https://www.kaggle.com/tanuprabhu/population-by-country-2020?select=population_by_country_2020.csv) from Kaggle.
+ [Population by WHO region](https://apps.who.int/gho/athena/data/xmart.csv?target=GHO/WHS9_86,WHS9_88,WHS9_89,WHS9_92,WHS9_96,WHS9_97,WHS9_90&profile=crosstable&filter=COUNTRY:-;REGION:*&x-sideaxis=REGION&x-topaxis=GHO;YEAR) by World Health Organization.
        
**GeoJSON - Data:**
+ [World geoJSON file](https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json)
+ [US geoJSON file](https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/us-states.json)

## Installation:
[(Back to top)](#table-of-contents)
+ Clone this repo <a href="https://docs.github.com/en/free-pro-team@latest/github/creating-cloning-and-archiving-repositories/cloning-a-repository" target="_blank">(for help see this tutorial).</a>
+ Raw data, data processing/transformation script is being kept in this repo. <a href="https://github.com/navido89/Police_Force_US/blob/main/Police%20Force%20Project.ipynb" target="_blank">Click here for notebook.</a>
+ **Note**: If GitHub doesn't load the notebook please refer to <a href="https://nbviewer.jupyter.org/github/navido89/Police_Force_US/blob/main/Police%20Force%20Project.ipynb" target="_blank">Jupyter Notebook Viewer.</a>
