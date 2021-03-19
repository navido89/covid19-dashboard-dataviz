# We import the libraries
import streamlit as st
import plotly.express as px # This is for bubble maps and bar plots
import pandas as pd
import folium
from streamlit_folium import folium_static
import geopandas as gpd
import numpy as np
import branca
from branca.element import MacroElement
from jinja2 import Template
from datetime import date, datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pytz


# WHO Global Data
who_global_data = "https://covid19.who.int/WHO-COVID-19-global-data.csv"

# Create this for the folium map.
class BindColormap(MacroElement):
    """Binds a colormap to a given layer.

    Parameters
    ----------
    colormap : branca.colormap.ColorMap
        The colormap to bind.
    """
    def __init__(self, layer, colormap):
        super(BindColormap, self).__init__()
        self.layer = layer
        self.colormap = colormap
        self._template = Template(u"""
        {% macro script(this, kwargs) %}
            {{this.colormap.get_name()}}.svg[0][0].style.display = 'block';
            {{this._parent.get_name()}}.on('overlayadd', function (eventLayer) {
                if (eventLayer.layer == {{this.layer.get_name()}}) {
                    {{this.colormap.get_name()}}.svg[0][0].style.display = 'block';
                }});
            {{this._parent.get_name()}}.on('overlayremove', function (eventLayer) {
                if (eventLayer.layer == {{this.layer.get_name()}}) {
                    {{this.colormap.get_name()}}.svg[0][0].style.display = 'none';
                }});
        {% endmacro %}
        """)

# Plot Number 1 - Folium Plot
def plot1():
    # We import the geoJSON file. 
    url = 'https://raw.githubusercontent.com/python-visualization/folium/master/examples/data'
    country_shapes = f'{url}/world-countries.json'

    # We read the file and print it.
    geoJSON_df = gpd.read_file(country_shapes)

    # We import the Data for global cases
    df_global_total = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
    df_global_total.head()

    # We change the Country/Region column to name
    df_global_total.rename(columns={'Country/Region':'name'}, inplace=True)

    # We drop the columns Province/State, Lat and Long
    df_global_total = df_global_total.drop(df_global_total.columns[[0, 2, 3]], axis=1)
    df_global_total = df_global_total.groupby(by=["name"]).sum()
    df_global_total = df_global_total

    # Let's check how many entries we have in both data frames
    # List of countries in df_global_total
    country_lst_df_global_total = list(df_global_total.index)

    # list of countries in geoJson file
    country_lst_geoJSON = list(geoJSON_df.name.values)

    # We need to clean the data. As you can see above country names such as US that should be South Korea instead.
    geoJSON_df["name"].replace({'United States of America':'US'}, inplace = True)
    geoJSON_df["name"].replace({'South Korea':'Korea, South'}, inplace = True)
    geoJSON_df["name"].replace({'The Bahamas':'Bahamas'}, inplace = True)
    geoJSON_df["name"].replace({'Ivory Coast':'Cote d\'Ivoire'}, inplace = True)
    geoJSON_df["name"].replace({'Republic of the Congo':'Congo (Brazzaville)'}, inplace = True)
    geoJSON_df["name"].replace({'Democratic Republic of the Congo':'Congo (Kinshasa)'}, inplace = True)
    geoJSON_df["name"].replace({'United Republic of Tanzania':'Tanzania'}, inplace = True)
    geoJSON_df["name"].replace({'Czech Republic':'Czechia'}, inplace = True)
    geoJSON_df["name"].replace({'Republic of Serbia':'Serbia'}, inplace = True)

    # Next we merge our df_global_total and the geoJSON data frame on the key name.
    final_total_cases = geoJSON_df.merge(df_global_total,how="left",on = "name")
    final_total_cases = final_total_cases.fillna(0)

    # We import the Data for global deaths
    df_global_death = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")

    # We change the Country/Region column to name
    df_global_death.rename(columns={'Country/Region':'name'}, inplace=True)

    # We drop the columns Province/State, Lat and Long
    df_global_death = df_global_death.drop(df_global_death.columns[[0, 2, 3]], axis=1)
    df_global_death = df_global_death.groupby(by=["name"]).sum()
    df_global_death = df_global_death
    df_global_death = df_global_death.fillna(0)

    # Next we create our dataframe for the folium map. 
    # We want the country names, the geometry and total number of cases and total number of deaths. 
    df_global_folium = final_total_cases
    df_global_folium = df_global_folium.iloc[:,[1,2,-1]]

    # We change the column name for the date to total cases 
    df_global_folium.rename(columns={ df_global_folium.columns[-1]: "covid_total" }, inplace = True)

    # We need to add the total deaths to df_global_folium
    # We reset the index
    df_global_death.reset_index(level=0,inplace=True)

    # We grab only the name column and the last column
    df_global_death_name_last_column = df_global_death.iloc[:,[0,-1]]

    # We change the column name for the date to total cases 
    df_global_death_name_last_column.rename(columns={ df_global_death_name_last_column.columns[-1]: "covid_deaths" }, inplace = True)

    # Next we merge the total deaths to the df_global_folium
    df_global_folium = df_global_folium.merge(df_global_death_name_last_column,how="left", on = "name")

    # Next we need to grab the population for each country so we can calculate the rates per 100k population.
    pop_df = pd.read_csv("population_by_country_2020.csv")

    # We grab only the first two columns
    pop_df = pop_df[["Country (or dependency)","Population (2020)"]]

    # We will change the column name of country to name
    pop_df.rename(columns={'Country (or dependency)':'name'}, inplace=True)

    # We need to clean the data. As you can see above country names such as US that should be South Korea instead.
    pop_df["name"].replace({'United States':'US'}, inplace = True)
    pop_df["name"].replace({'South Korea':'Korea, South'}, inplace = True)
    pop_df["name"].replace({'DR Congo':'Congo (Brazzaville)'}, inplace = True)
    pop_df["name"].replace({'Congo':'Congo (Kinshasa)'}, inplace = True)
    pop_df["name"].replace({'Czech Republic (Czechia)':'Czechia'}, inplace = True)
    pop_df["name"].replace({'Côte d\'Ivoire':'Cote d\'Ivoire'}, inplace = True)

    # Now we can merge the pop_df with df_global_folium
    df_global_folium = df_global_folium.merge(pop_df,on = "name")
    df_global_folium = df_global_folium .fillna(0)

    # We change the column name of Population (2020) to Population
    df_global_folium.rename(columns={'Population (2020)':'Population'}, inplace=True)

    # Change the order of the columns
    df_global_folium = df_global_folium[['name', 'Population', 'geometry', 'covid_total', 'covid_deaths']]

    # We now calculate the the Total Cases and Total Deaths by 100k
    df_global_folium['covid_cases_per_100k'] = df_global_folium.apply(lambda x: (x.covid_total/x.Population * 100000), axis = 1)
    df_global_folium['covid_deaths_per_100k'] = df_global_folium.apply(lambda x: (x.covid_deaths/x.Population * 100000), axis = 1)

    # Let's round the values as well 
    df_global_folium[["covid_cases_per_100k","covid_deaths_per_100k"]] = df_global_folium[["covid_cases_per_100k","covid_deaths_per_100k"]].round(0)

    # Let's turn them into integers
    df_global_folium[["covid_total","covid_deaths","covid_cases_per_100k","covid_deaths_per_100k"]] = df_global_folium[["covid_total","covid_deaths","covid_cases_per_100k","covid_deaths_per_100k"]].applymap(np.int64)

    # We create the colors for the custom legends
    colors = ["YlGn","OrRd","BuPu","GnBu"]

    # create a custom legend using branca
    cmap1 = branca.colormap.StepColormap(
        colors=['#ffffcc','#d9f0a3','#addd8e','#78c679','#238443'],
        vmin=0,
        vmax=df_global_folium['covid_total'].max(),  
        caption='Covid Total')

    cmap2 = branca.colormap.StepColormap(
        colors=["#fef0d9",'#fdcc8a','#fc8d59','#d7301f'],
        vmin=0,
        vmax=df_global_folium['covid_deaths'].max(),  
        caption='Covid Deaths')
        
    cmap3 = branca.colormap.StepColormap(
        colors=branca.colormap.step.BuPu_09.colors,
        vmin=0,
        vmax=df_global_folium['covid_cases_per_100k'].max(),  
        caption='covid_cases_per_100k')
        
    cmap4 = branca.colormap.StepColormap(
        colors=branca.colormap.step.GnBu_09.colors,
        vmin=0,
        vmax=df_global_folium['covid_deaths_per_100k'].max(),  
        caption='covid_deaths_per_100k')

    cmaps = [cmap1, cmap2,cmap3,cmap4]
    country_lists_global_map = ["covid_total","covid_deaths","covid_cases_per_100k","covid_deaths_per_100k"]

    sample_map = folium.Map(location=[51,10], zoom_start=2)

    # Set up Choropleth map
    for color, cmap, i in zip(colors, cmaps, country_lists_global_map):
        
        choropleth = folium.Choropleth(
        geo_data=df_global_folium,
        data=df_global_folium,
        name=i,
        columns=['name',i],
        key_on="feature.properties.name",
        fill_color=color,
        colormap= cmap,
        fill_opacity=1,
        line_opacity=0.2,
        show=False
        )
        
        # this deletes the legend for each choropleth you add
        for child in choropleth._children:
            if child.startswith("color_map"):
                del choropleth._children[child]

        style_function1 = lambda x: {'fillColor': '#ffffff', 
                            'color':'#000000', 
                            'fillOpacity': 0.1, 
                            'weight': 0.1}
        highlight_function1 = lambda x: {'fillColor': '#000000', 
                                'color':'#000000', 
                                'fillOpacity': 0.50, 
                                'weight': 0.1}
        NIL1 = folium.features.GeoJson(
            data = df_global_folium,
            style_function=style_function1, 
            control=False,
            highlight_function=highlight_function1, 
            tooltip=folium.features.GeoJsonTooltip(
                fields=['name',"covid_total","covid_deaths","covid_cases_per_100k","covid_deaths_per_100k"],
                aliases=['name',"covid_total","covid_deaths","covid_cases_per_100k","covid_deaths_per_100k"],
                style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;") 
            )
        )
        sample_map.add_child(NIL1)
        sample_map.keep_in_front(NIL1)

        # add cmap to `sample_map`
        sample_map.add_child(cmap)
                
        # add choropleth to `sample_map`
        sample_map.add_child(choropleth)
        
        # bind choropleth and cmap
        bc = BindColormap(choropleth, cmap)
        
        # add binding to `m`
        sample_map.add_child(bc)
    
    # Add dark and light mode. 
    folium.TileLayer('cartodbdark_matter',name="dark mode",control=True).add_to(sample_map)
    folium.TileLayer('cartodbpositron',name="light mode",control=True).add_to(sample_map)

    sample_map.add_child(folium.LayerControl())
    return sample_map


# Plot Number 2 - Bubble Map with animation total cases.
@st.cache
def plot2():
    # We grab the data
    df_timeseries = pd.read_csv(who_global_data)

    # We change the date column to a datetime type
    df_timeseries["Date_reported"] = pd.to_datetime(df_timeseries["Date_reported"])

    # We groupby months and aggregate the cases 
    x = (df_timeseries.groupby([pd.Grouper(key='Date_reported', freq='MS'), 'Country'])['New_cases']
    .sum()
    .reset_index())

    x["New_cases"] = x["New_cases"].abs()
    x["Date_reported"] = x["Date_reported"].dt.strftime('%m/%Y')
    x["Date_reported"] = x['Date_reported'].astype(object)

    # Here we plot bubble map with Plotly Express
    fig = px.scatter_geo(x, locations="Country", color="Country",
                        locationmode='country names',hover_name="Country", size="New_cases",
                        animation_frame="Date_reported",
                        projection="natural earth")
    fig.update_layout(title_text = "Covid19 Cases Globally Per Month - Time Series Bubble Map Animation",showlegend=False)
    return fig

# Plot Number 3 - Bubble Map with animation total deaths
@st.cache
def plot3():
    # Now we create a bubble map for the total deaths
    # We groupby months and aggregate the deaths 
    df_timeseries = pd.read_csv(who_global_data)

    # We change the date column to a datetime type
    df_timeseries["Date_reported"] = pd.to_datetime(df_timeseries["Date_reported"])

    x1 = (df_timeseries.groupby([pd.Grouper(key='Date_reported', freq='MS'), 'Country'])['New_deaths']
    .sum()
    .reset_index())

    x1["New_deaths"] = x1["New_deaths"].abs()
    x1["Date_reported"] = x1["Date_reported"].dt.strftime('%m/%Y')
    x1["Date_reported"] = x1['Date_reported'].astype(object)

    # Here we plot bubble map with Plotly Express
    fig1 = px.scatter_geo(x1, locations="Country", color="Country",
                        locationmode='country names',hover_name="Country", size="New_deaths",
                        animation_frame="Date_reported",
                        projection="natural earth")
    fig1.update_layout(title_text = "Covid19 Deaths Globally Per Month - Time Series Bubble Map Animation" ,showlegend=False)
    return fig1


@st.cache
# Plot Number 4 - Time Series Bar Plot 1
def plot4():
    # We import the data
    df_WHO = pd.read_csv(who_global_data)

    # We group by the data
    df_WHO = df_WHO.groupby(['Date_reported'])[['New_cases', 'New_deaths','Cumulative_cases','Cumulative_deaths']].sum()

    # We reset the index
    df_WHO = df_WHO.reset_index()

    df = df_WHO

    # Create lists to iterate over
    lst = ['New_cases','Cumulative_cases']

    # one trace for each df column
    fig2 = px.bar(x=df["Date_reported"].values, y=df["New_cases"].values)

    # one button for each df column
    updatemenu= []
    buttons=[]

    for i in lst:
        buttons.append(dict(method='restyle',label = str(i),args=[{'x':[df["Date_reported"].values],'y':[df[i].values]},[0]])
                    )
    
    # some adjustments to the updatemenus
    button_layer_1_height = 1.25
    updatemenu = list([dict(
        buttons = buttons,
        direction="down",
        pad={"r":10,"t":10},
        showactive=True,
        x= 0.37,
        xanchor="left",
        y=button_layer_1_height,
        yanchor="top",  font = dict(color = "green"))])

    fig2.update_traces(marker_color='green')
    fig2.update_layout(showlegend=True, updatemenus=updatemenu, title_text = "Global Cases",xaxis_title="Dates",yaxis_title="Values")
    fig2.update_xaxes(categoryorder= 'array', categoryarray= df.index)
    
    return fig2 

@st.cache
# Plot Number 4a - WHO Pie Chart 
def plot4a():
    df_cont = pd.read_csv("https://covid19.who.int/WHO-COVID-19-global-data.csv")
    df_cont = df_cont.groupby(['Date_reported','WHO_region'])[['New_cases', 'New_deaths','Cumulative_cases','Cumulative_deaths']].sum()
    df_cont = df_cont.unstack()
    
    # We grab the Cumulative_cases column
    df_cont_Cumulative_cases = df_cont["Cumulative_cases"]

    # We change the column names with the appropriate region names
    df_cont_Cumulative_cases.rename(columns={'AFRO':'Africa','AMRO':'Americas','EMRO':'Eastern Mediterranean','EURO':'Europe',"SEARO":'South-East Asia','WPRO':'Western Pacific'}, inplace=True)

    # We drop the other column
    df_cont_Cumulative_cases.drop("Other", axis=1, inplace = True)

    # We grab the last row
    df_cont_Cumulative_cases = df_cont_Cumulative_cases.tail(1)

    # We take the transpose
    df_cont_Cumulative_cases = df_cont_Cumulative_cases.transpose()

    # We rename the column to Total Cases
    df_cont_Cumulative_cases.set_axis(['Total_Cases'], axis=1, inplace=True)

    # We grab the Cumulative_deaths column
    df_cont_Cumulative_deaths = df_cont["Cumulative_deaths"]

    # We change the column names with the appropriate region names
    df_cont_Cumulative_deaths.rename(columns={'AFRO':'Africa','AMRO':'Americas','EMRO':'Eastern Mediterranean','EURO':'Europe',"SEARO":'South-East Asia','WPRO':'Western Pacific'}, inplace=True)

    # We drop the other column
    df_cont_Cumulative_deaths.drop("Other", axis=1, inplace = True)

    # We grab the last row
    df_cont_Cumulative_deaths = df_cont_Cumulative_deaths.tail(1)

    # We take the transpose
    df_cont_Cumulative_deaths = df_cont_Cumulative_deaths.transpose()

    # We change the column name
    df_cont_Cumulative_deaths.set_axis(['Total_Deaths'], axis=1, inplace=True)

    # We now merge the two dataframes
    cont_totals = pd.concat([df_cont_Cumulative_cases, df_cont_Cumulative_deaths], axis=1)
    cont_totals = cont_totals.reset_index()
    
    # Here we import the population data from WHO.
    df_who_pop = pd.read_csv("https://apps.who.int/gho/athena/data/xmart.csv?target=GHO/WHS9_86,WHS9_88,WHS9_89,WHS9_92,WHS9_96,WHS9_97,WHS9_90&profile=crosstable&filter=COUNTRY:-;REGION:*&x-sideaxis=REGION&x-topaxis=GHO;YEAR")
    
    # We grab the 3 columns in interest.
    df_who_pop = df_who_pop[["Unnamed: 0","Population (in thousands) total","Annual population growth rate (%)"]]
    df_who_pop.drop([0,1], inplace = True)

    # We need to convert Population (in thousands) total and Annual population growth rate (%) to numeric types.

    # We remove the white spaces
    df_who_pop["Population (in thousands) total"] = df_who_pop["Population (in thousands) total"].str.replace(' ', '')

    # We convert them to numeric columns
    df_who_pop["Population (in thousands) total"] = pd.to_numeric(df_who_pop["Population (in thousands) total"])
    df_who_pop["Annual population growth rate (%)"] = pd.to_numeric(df_who_pop["Annual population growth rate (%)"])

    df_who_pop["2021_Population (in thousands)"] = round((df_who_pop["Population (in thousands) total"] * (df_who_pop["Annual population growth rate (%)"]/100)*5)+ df_who_pop["Population (in thousands) total"]) 
    
    # We convert the 2021 population in thousands to millions again.
    df_who_pop["2021_Population (in thousands)"] = (df_who_pop["2021_Population (in thousands)"] / 1000)*1000000

    pd.set_option('display.float_format', '{:.0f}'.format)
    df_who_pop.rename(columns={"2021_Population (in thousands)": "Population"}, inplace = True)

    # We now merge the population number with our cont_totals data frame

    # First we need to change the column name of Unnamed:0 to WHO_region so we can merge
    df_who_pop.rename(columns={"Unnamed: 0": "WHO_region"}, inplace = True)
    cont_totals = pd.merge(cont_totals,df_who_pop, on = ["WHO_region"])

    # We select the columns in interest.
    cont_totals = cont_totals[["WHO_region","Population","Total_Cases","Total_Deaths"]]

    # Next we calculate the cases and deaths per 1 million per continent
    # We now calculate the the Total Cases and Total Deaths by 100 million.
    cont_totals['Total_Cases_Per_100mill'] = cont_totals.apply(lambda x: (x.Total_Cases/x.Population * 100000000), axis = 1)
    cont_totals['Total_Deaths_Per_100mill'] = cont_totals.apply(lambda x: (x.Total_Deaths/x.Population  * 100000000), axis = 1)
    
    labels = cont_totals.WHO_region.values
    colors = ['gold', 'mediumturquoise', 'darkorange', 'lightgreen']

    # Create subplots: use 'domain' type for Pie subplot
    fig = make_subplots(rows=2, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}],[{'type':'domain'}, {'type':'domain'}]])
    fig.add_trace(go.Pie(labels=labels, values=cont_totals.Total_Cases.values, name="Total Cases"),
                1, 1)
    fig.add_trace(go.Pie(labels=labels, values=cont_totals.Total_Deaths.values, name="Total Deaths"),
                1, 2)
              
    fig.add_trace(go.Pie(labels=labels, values=cont_totals.Total_Cases_Per_100mill.values, name="Total_Cases_Per_100mil"),
                2, 1)
    fig.add_trace(go.Pie(labels=labels, values=cont_totals.Total_Deaths_Per_100mill.values, name="Total_Deaths_Per_100mil"),
                2, 2)

    # Use `hole` to create a donut-like pie chart
    fig.update_traces(hole=.4, hoverinfo="label+percent+name",marker=dict(colors=colors, line=dict(color='#000000', width=2)))

    fig.update_layout(
        width=920, height=820,
        title_text="WHO Regions in Compairson",
        # Add annotations in the center of the donut pies.
        annotations=[dict(text='Cases', x=0.19, y=0.81, font_size=14, showarrow=False),
                    dict(text='Deaths', x=0.82, y=0.81, font_size=14, showarrow=False),
                    dict(text='Cases Per', x=0.17, y=0.2, font_size=14, showarrow=False),
                    dict(text='100 Mil', x=0.18, y=0.15, font_size=14, showarrow=False),
                    dict(text='Deaths Per', x=0.84, y=0.2, font_size=14, showarrow=False),
                    dict(text='100 Mil', x=0.82, y=0.15, font_size=14, showarrow=False)])
    return fig

@st.cache
# Plot Number 5 - Time Series Bar Plot 2
def plot5():
    # We import the data
    df_WHO = pd.read_csv(who_global_data)

    # We group by the data
    df_WHO = df_WHO.groupby(['Date_reported'])[['New_cases', 'New_deaths','Cumulative_cases','Cumulative_deaths']].sum()

    # We reset the index
    df_WHO = df_WHO.reset_index()

    df = df_WHO

    # We set up the second plot
    lst2 = ['New_deaths', 'Cumulative_deaths']
    
    fig3 = px.bar(x=df["Date_reported"].values, y=df["New_deaths"].values)

    updatemenu2= []
    buttons2=[]

    for i in lst2:
        buttons2.append(dict(method='restyle',label = str(i),args=[{'x':[df["Date_reported"].values],'y':[df[i].values]},[0]])
                    )

    button_layer_1_height = 1.25
    updatemenu2 = list([dict(
        buttons = buttons2,
        direction="down",
        pad={"r":10,"t":10},
        showactive=True,
        x= 0.37,
        xanchor="left",
        y=button_layer_1_height,
        yanchor="top",  font = dict(color = "red"))])

    fig3.update_traces(marker_color='red')
    fig3.update_layout(showlegend=True, updatemenus=updatemenu2, title_text = "Global Deaths", xaxis_title="Dates",yaxis_title="Values")
    fig3.update_xaxes(categoryorder= 'array', categoryarray= df.index)
    return fig3

# Plot Number 8 - Folium Map US Situation
def plot8():
    # Grab US Cases
    us_data_cases = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv")
    us_data_cases = us_data_cases.groupby("Province_State").sum()
    us_data_cases = us_data_cases.iloc[:,-1:]
    us_data_cases.columns = ["total_cases"]
    
    # Grab US deaths 
    us_data_deaths = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv")
    us_data_deaths = us_data_deaths.groupby("Province_State").sum()
    us_data_deaths = us_data_deaths.iloc[:,-1:]
    us_data_deaths.columns = ["total_deaths"]
   
    US_df = pd.concat([us_data_cases, us_data_deaths], axis=1).reset_index()

    # Need to get vaccine data by state
    us_vaccine_data = pd.read_csv("https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/us_state_vaccinations.csv")

    # We grab the latest date
    d1 = us_vaccine_data["date"].iloc[-1]

    us_vaccine_data_state = us_vaccine_data.loc[us_vaccine_data["date"] == d1]

    us_vaccine_data_state = us_vaccine_data_state[["location","total_distributed","people_fully_vaccinated","people_vaccinated_per_hundred"]]
    us_vaccine_data_state = us_vaccine_data_state.reset_index()

    # We change the column name of location
    us_vaccine_data_state.rename(columns={'location':'Province_State'}, inplace=True)

    # Need to change New York State to New York
    us_vaccine_data_state["Province_State"].replace({'New York State':'New York'}, inplace = True)

    # We add it the vaccine info to our US_df
    US_df = US_df.merge(us_vaccine_data_state,on = "Province_State")
    
    # We grab the geoJSON
    url = (
        "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data"
    )
    state_geo = f"{url}/us-states.json"

    # We read the file and print it.
    geoJSON_df = gpd.read_file(state_geo)
    geoJSON_df.rename(columns={'name':'Province_State'}, inplace=True)

    # Let's check which states are missing.
    states_list = list(US_df.Province_State.unique())

    # Need to remove American Samoa, Guam, Northern Mariana Islands, Puerto Rico, Virgin Islands,District of Columbia
    US_df.drop(index=US_df[US_df['Province_State'] == 'American Samoa'].index, inplace=True)
    US_df.drop(index=US_df[US_df['Province_State'] == 'Guam'].index, inplace=True)
    US_df.drop(index=US_df[US_df['Province_State'] == 'Northern Mariana Islands'].index, inplace=True)
    US_df.drop(index=US_df[US_df['Province_State'] == 'Puerto Rico'].index, inplace=True)
    US_df.drop(index=US_df[US_df['Province_State'] == 'Virgin Islands'].index, inplace=True)
    US_df.drop(index=US_df[US_df['Province_State'] == 'District of Columbia'].index, inplace=True)

    states_list = list(US_df.Province_State.unique())
    #print(len(states_list))

    geoJSON_states = list(geoJSON_df.Province_State.values)
    #print(len(geoJSON_states))

    # Check if any states are missing.
    missing_states = np.setdiff1d(geoJSON_states,states_list)
   
    # We merge the data frames now.
    final_us_df = geoJSON_df.merge(US_df, on = "Province_State")

    # We need to grab the population for each state.
    US_pop_df = pd.read_html("https://www.infoplease.com/us/states/state-population-by-rank")
    US_pop_df = US_pop_df[0]
    US_pop_df.rename(columns={'State':'Province_State'}, inplace=True)
    US_pop_df = US_pop_df[["Province_State","July 2019 Estimate"]]
   
    # We add the population now to the final_us_df.
    # We merge the data frames now.
    final_us_df = final_us_df.merge(US_pop_df, on = "Province_State")
    final_us_df.rename(columns={'July 2019 Estimate':'Population'}, inplace=True)

    # We now calculate the the Total Cases and Total Deaths by 100k
    final_us_df['total_cases_per_100k'] = final_us_df.apply(lambda x: (round(x.total_cases/x.Population * 100000)), axis = 1)
    final_us_df['total_deaths_per_100k'] = final_us_df.apply(lambda x: (round(x.total_deaths/x.Population * 100000)), axis = 1)
    
    # Let's rearrange the columns 
    final_us_df = final_us_df[["id","Province_State","geometry","total_cases","total_deaths","total_cases_per_100k","total_deaths_per_100k","total_distributed","people_fully_vaccinated","people_vaccinated_per_hundred","Population"]]
    
    colors = ['YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'PuBuGn','YlGn']

    # create a custom legend using branca
    cmap1 = branca.colormap.StepColormap(
        colors=["#ffffd4","#fee391","#fec44f","#fe9929","#d95f0e"],
        vmin=0,
        vmax=final_us_df['total_cases'].max(),  # setting max value for legend
        caption='Total Cases')

    cmap2 = branca.colormap.StepColormap(
        colors=branca.colormap.step.YlOrRd_09.colors,
        vmin=0,
        vmax=final_us_df['total_deaths'].max(),  # setting max value for legend
        caption='Total Deaths')
        
    cmap3 = branca.colormap.StepColormap(
        colors=branca.colormap.step.OrRd_09.colors,
        vmin=0,
        vmax=final_us_df['total_cases_per_100k'].max(),  # setting max value for legend
        caption='Total Cases Per 100k')
        
    cmap4 = branca.colormap.StepColormap(
        colors=branca.colormap.step.PuRd_09.colors,
        vmin=0,
        vmax=final_us_df['total_deaths_per_100k'].max(),  # setting max value for legend
        caption='Total Deaths Per 100k')

    cmap5 = branca.colormap.StepColormap(
        colors=['#fff7f3','#fde0dd','#fcc5c0','#fa9fb5',"#f768a1"],
        vmin=0,
        vmax=final_us_df['total_distributed'].max(),  # setting max value for legend
        caption='Total Distributed')

    cmap6 = branca.colormap.StepColormap(
        colors=["#fff7fb","#ece2f0","#d0d1e6","#a6bddb","#02818a"],
        vmin=0,
        vmax=final_us_df['people_fully_vaccinated'].max(),  # setting max value for legend
        caption='People Fully Vaccinated')

    cmap7 = branca.colormap.StepColormap(
        colors=branca.colormap.step.YlGn_09.colors,
        vmin=0,
        vmax=final_us_df['people_vaccinated_per_hundred'].max(),  # setting max value for legend
        caption='People Vaccinated Per 100')

    cmaps = [cmap1,cmap2,cmap3,cmap4,cmap5,cmap6,cmap7]

    country_lists_global_map = ["total_cases","total_deaths","total_cases_per_100k","total_deaths_per_100k",'total_distributed','people_fully_vaccinated','people_vaccinated_per_hundred']

    sample_map = folium.Map(location=[48, -102], zoom_start=3)

    # Set up Choropleth map
    for color, cmap, i in zip(colors, cmaps, country_lists_global_map):
        
        choropleth = folium.Choropleth(
        geo_data=final_us_df,
        data=final_us_df,
        name=i,
        columns=['Province_State',i],
        key_on="feature.properties.Province_State",
        fill_color=color,
        colormap= cmap,
        fill_opacity=1,
        line_opacity=0.2,
        show=False
        )
        
        # this deletes the legend for each choropleth you add
        for child in choropleth._children:
            if child.startswith("color_map"):
                del choropleth._children[child]

        style_function1 = lambda x: {'fillColor': '#ffffff', 
                            'color':'#000000', 
                            'fillOpacity': 0.1, 
                            'weight': 0.1}
        highlight_function1 = lambda x: {'fillColor': '#000000', 
                                'color':'#000000', 
                                'fillOpacity': 0.50, 
                                'weight': 0.1}
        NIL1 = folium.features.GeoJson(
            data = final_us_df,
            style_function=style_function1, 
            control=False,
            highlight_function=highlight_function1, 
            tooltip=folium.features.GeoJsonTooltip(
                fields=["Province_State","total_cases","total_deaths","total_cases_per_100k","total_deaths_per_100k",'total_distributed','people_fully_vaccinated','people_vaccinated_per_hundred'],
                aliases=["Province_State","total_cases","total_deaths","total_cases_per_100k","total_deaths_per_100k",'total_distributed','people_fully_vaccinated','people_vaccinated_per_hundred'],
                style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;") 
            )
        )
        sample_map.add_child(NIL1)
        sample_map.keep_in_front(NIL1)
        sample_map.add_child(cmap)
        sample_map.add_child(choropleth)
        
        # bind choropleth and cmap
        bc = BindColormap(choropleth, cmap)
        sample_map.add_child(bc)

        # Add dark and light mode. 
        folium.TileLayer('cartodbdark_matter',name="dark mode",control=True).add_to(sample_map)
        folium.TileLayer('cartodbpositron',name="light mode",control=True).add_to(sample_map)

    sample_map.add_child(folium.LayerControl())
    return sample_map

# Create a function to create the global cases.
@st.cache
def get_global_cases():
    # We import the geoJSON file. 
    url = 'https://raw.githubusercontent.com/python-visualization/folium/master/examples/data'
    country_shapes = f'{url}/world-countries.json'

    # We read the file and print it.
    geoJSON_df = gpd.read_file(country_shapes)

    # We import the Data for global cases
    df_global_total = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
    df_global_total.head()

    # We change the Country/Region column to name
    df_global_total.rename(columns={'Country/Region':'name'}, inplace=True)

    # We drop the columns Province/State, Lat and Long
    df_global_total = df_global_total.drop(df_global_total.columns[[0, 2, 3]], axis=1)
    df_global_total = df_global_total.groupby(by=["name"]).sum()
    df_global_total = df_global_total

    # Let's check how many entries we have in both data frames
    # List of countries in df_global_total
    country_lst_df_global_total = list(df_global_total.index)

    # list of countries in geoJson file
    country_lst_geoJSON = list(geoJSON_df.name.values)

    # We need to clean the data. As you can see above country names such as US that should be South Korea instead.
    geoJSON_df["name"].replace({'United States of America':'US'}, inplace = True)
    geoJSON_df["name"].replace({'South Korea':'Korea, South'}, inplace = True)
    geoJSON_df["name"].replace({'The Bahamas':'Bahamas'}, inplace = True)
    geoJSON_df["name"].replace({'Ivory Coast':'Cote d\'Ivoire'}, inplace = True)
    geoJSON_df["name"].replace({'Republic of the Congo':'Congo (Brazzaville)'}, inplace = True)
    geoJSON_df["name"].replace({'Democratic Republic of the Congo':'Congo (Kinshasa)'}, inplace = True)
    geoJSON_df["name"].replace({'United Republic of Tanzania':'Tanzania'}, inplace = True)
    geoJSON_df["name"].replace({'Czech Republic':'Czechia'}, inplace = True)
    geoJSON_df["name"].replace({'Republic of Serbia':'Serbia'}, inplace = True)

    # Next we merge our df_global_total and the geoJSON data frame on the key name.
    final_total_cases = geoJSON_df.merge(df_global_total,how="left",on = "name")
    final_total_cases = final_total_cases.fillna(0)

    # We import the Data for global deaths
    df_global_death = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")

    # We change the Country/Region column to name
    df_global_death.rename(columns={'Country/Region':'name'}, inplace=True)

    # We drop the columns Province/State, Lat and Long
    df_global_death = df_global_death.drop(df_global_death.columns[[0, 2, 3]], axis=1)
    df_global_death = df_global_death.groupby(by=["name"]).sum()
    df_global_death = df_global_death
    df_global_death = df_global_death.fillna(0)

    # Next we create our dataframe for the folium map. 
    # We want the country names, the geometry and total number of cases and total number of deaths. 
    df_global_folium = final_total_cases
    df_global_folium = df_global_folium.iloc[:,[1,2,-1]]

    # We change the column name for the date to total cases 
    df_global_folium.rename(columns={ df_global_folium.columns[-1]: "covid_total" }, inplace = True)

    # We need to add the total deaths to df_global_folium
    # We reset the index
    df_global_death.reset_index(level=0,inplace=True)

    # We grab only the name column and the last column
    df_global_death_name_last_column = df_global_death.iloc[:,[0,-1]]

    # We change the column name for the date to total cases 
    df_global_death_name_last_column.rename(columns={ df_global_death_name_last_column.columns[-1]: "covid_deaths" }, inplace = True)

    # Next we merge the total deaths to the df_global_folium
    df_global_folium = df_global_folium.merge(df_global_death_name_last_column,how="left", on = "name")
    return df_global_folium["covid_total"].sum()

# Create a function to create the global cases.
@st.cache
def get_global_deaths():
    # We import the geoJSON file. 
    url = 'https://raw.githubusercontent.com/python-visualization/folium/master/examples/data'
    country_shapes = f'{url}/world-countries.json'

    # We read the file and print it.
    geoJSON_df = gpd.read_file(country_shapes)

    # We import the Data for global cases
    df_global_total = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
    df_global_total.head()

    # We change the Country/Region column to name
    df_global_total.rename(columns={'Country/Region':'name'}, inplace=True)

    # We drop the columns Province/State, Lat and Long
    df_global_total = df_global_total.drop(df_global_total.columns[[0, 2, 3]], axis=1)
    df_global_total = df_global_total.groupby(by=["name"]).sum()
    df_global_total = df_global_total

    # Let's check how many entries we have in both data frames
    # List of countries in df_global_total
    country_lst_df_global_total = list(df_global_total.index)

    # list of countries in geoJson file
    country_lst_geoJSON = list(geoJSON_df.name.values)

    # We need to clean the data. As you can see above country names such as US that should be South Korea instead.
    geoJSON_df["name"].replace({'United States of America':'US'}, inplace = True)
    geoJSON_df["name"].replace({'South Korea':'Korea, South'}, inplace = True)
    geoJSON_df["name"].replace({'The Bahamas':'Bahamas'}, inplace = True)
    geoJSON_df["name"].replace({'Ivory Coast':'Cote d\'Ivoire'}, inplace = True)
    geoJSON_df["name"].replace({'Republic of the Congo':'Congo (Brazzaville)'}, inplace = True)
    geoJSON_df["name"].replace({'Democratic Republic of the Congo':'Congo (Kinshasa)'}, inplace = True)
    geoJSON_df["name"].replace({'United Republic of Tanzania':'Tanzania'}, inplace = True)
    geoJSON_df["name"].replace({'Czech Republic':'Czechia'}, inplace = True)
    geoJSON_df["name"].replace({'Republic of Serbia':'Serbia'}, inplace = True)

    # Next we merge our df_global_total and the geoJSON data frame on the key name.
    final_total_cases = geoJSON_df.merge(df_global_total,how="left",on = "name")
    final_total_cases = final_total_cases.fillna(0)

    # We import the Data for global deaths
    df_global_death = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")

    # We change the Country/Region column to name
    df_global_death.rename(columns={'Country/Region':'name'}, inplace=True)

    # We drop the columns Province/State, Lat and Long
    df_global_death = df_global_death.drop(df_global_death.columns[[0, 2, 3]], axis=1)
    df_global_death = df_global_death.groupby(by=["name"]).sum()
    df_global_death = df_global_death
    df_global_death = df_global_death.fillna(0)

    # Next we create our dataframe for the folium map. 
    # We want the country names, the geometry and total number of cases and total number of deaths. 
    df_global_folium = final_total_cases
    df_global_folium = df_global_folium.iloc[:,[1,2,-1]]

    # We change the column name for the date to total cases 
    df_global_folium.rename(columns={ df_global_folium.columns[-1]: "covid_total" }, inplace = True)

    # We need to add the total deaths to df_global_folium
    # We reset the index
    df_global_death.reset_index(level=0,inplace=True)

    # We grab only the name column and the last column
    df_global_death_name_last_column = df_global_death.iloc[:,[0,-1]]

    # We change the column name for the date to total cases 
    df_global_death_name_last_column.rename(columns={ df_global_death_name_last_column.columns[-1]: "covid_deaths" }, inplace = True)

    # Next we merge the total deaths to the df_global_folium
    df_global_folium = df_global_folium.merge(df_global_death_name_last_column,how="left", on = "name")
    return df_global_folium["covid_deaths"].sum()


# Create top 5 cases plot.
@st.cache(suppress_st_warning=True)
def plot9():
    df_global_total = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")

    # We change the Country/Region column to name
    df_global_total.rename(columns={'Country/Region':'name'}, inplace=True)
    df_global_total.head()

    # We drop the columns Province/State, Lat and Long
    df_global_total = df_global_total.drop(df_global_total.columns[[0, 2, 3]], axis=1)
    df_global_total = df_global_total.groupby(by=["name"]).sum()
    df_global_total = df_global_total
    top10_cases = df_global_total.sort_values(df_global_total.columns[-1],ascending=False).head(5)
    top10_cases = top10_cases.transpose()
    
    # top10_cases.rename(columns=top10_cases.iloc[0],inplace= True)
    # top10_cases = top10_cases[1:]
    fig1 = px.line(top10_cases, x=top10_cases.index, y=top10_cases.columns)
    fig1.update_layout(title="Top 5 Countries - Total Cases",xaxis_showgrid=False, yaxis_showgrid=False)
    fig1.update_xaxes(title="Dates")
    fig1.update_yaxes(title="Values")

    return fig1

# Create top 5 cases plot.
@st.cache(suppress_st_warning=True)
def plot10():
    # We import the Data for global deaths
    df_global_death = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")
   
    # We change the Country/Region column to name
    df_global_death.rename(columns={'Country/Region':'name'}, inplace=True)
    
    # We drop the columns Province/State, Lat and Long
    df_global_death = df_global_death.drop(df_global_death.columns[[0, 2, 3]], axis=1)
    df_global_death = df_global_death.groupby(by=["name"]).sum()
    df_global_death = df_global_death
    df_global_death = df_global_death.fillna(0)
    top10_deaths = df_global_death.sort_values(df_global_death.columns[-1],ascending=False).head(5)
    top10_deaths = top10_deaths.transpose()
    
    fig2 = px.line(top10_deaths, x=top10_deaths.index, y=top10_deaths.columns)
    fig2.update_layout(title="Top 5 Countries - Total Deaths",xaxis_showgrid=False, yaxis_showgrid=False)
    fig2.update_xaxes(title="Dates")
    fig2.update_yaxes(title="Values")

    return fig2

# Create US Vaccine data.
@st.cache(suppress_st_warning=True)
def plot11():
    vaccine_data = pd.read_csv("https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/us_state_vaccinations.csv")

    us_people_vac_data = vaccine_data[["date","location","people_fully_vaccinated",'people_fully_vaccinated_per_hundred',"total_distributed"]]
    us_people_vac_data  = us_people_vac_data .fillna(0)
    
    todays_date = us_people_vac_data["date"].iloc[-1]
    us_people_vac_data = us_people_vac_data[us_people_vac_data["date"] == todays_date]
    
    a = ['American Samoa','Bureau of Prisons','Dept of Defense','Federated States of Micronesia','Indian Health Svc','Long Term Care','Puerto Rico','Republic of Palau','United States','Veterans Healht']

    us_people_vac_data = us_people_vac_data[~us_people_vac_data['location'].isin(a)]

    # We plot the data now per   
    df = us_people_vac_data

    # Create lists to iterate over
    lst = ["people_fully_vaccinated",'people_fully_vaccinated_per_hundred',"total_distributed"]

    # Sort the column people fully vaccinated.
    df = df.sort_values("people_fully_vaccinated", ascending=False)

    # one trace for each df column
    fig = px.bar(x=df["location"].values, y=df["people_fully_vaccinated"].values)

    # one button for each df column
    updatemenu= []
    buttons=[]

    for i in lst:
        df = df.sort_values(i, ascending=False)
        buttons.append(dict(method='restyle',label = str(i),args=[{'x':[df["location"].values],'y':[df[i].values],},[0]]))

    # some adjustments to the updatemenus
    button_layer_1_height = 1.25
    updatemenu = list([dict(
        buttons = buttons,
        direction="down",
        pad={"r":10,"t":10},
        showactive=True,
        x= 0.37,
        xanchor="left",
        y=button_layer_1_height,
        yanchor="top",  font = dict(color = "black"))])

    fig.update_traces(marker_color= "grey")
    fig.update_layout(showlegend=False, updatemenus=updatemenu,title = "Vaccine Information by State")
    fig.update_xaxes(categoryorder= 'array', categoryarray= df.index)
    fig.update_xaxes(title="States") 
    fig.update_yaxes(title="Values")
    return fig

# Create US Variant Plot States Comparison.
@st.cache(suppress_st_warning=True)
def plot12():
    # Second plot
    cdc_vairants_data2 = pd.read_csv("https://www.cdc.gov/coronavirus/2019-ncov/downloads/transmission/03112021_Web-UpdateCSV-TABLE.csv")
    
    cdc_vairants_data2.columns = ["State", "UK Variant", "Brazil Variant", "South Africa Variant"]

    # Check for states to remove. we need 50
    cdc_vairants_data2_state_lst = cdc_vairants_data2.State.values
   
    # Remove AS,GU,MH,FM,MP,PW,PR,DC
    cdc_vairants_data2["State"].replace({
        'AL': 'Alabama',
        'AK': 'Alaska',
        'AZ': 'Arizona',
        'AR': 'Arkansas',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'HI': 'Hawaii',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'IA': 'Iowa',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'ME': 'Maine',
        'MD': 'Maryland',
        'MA': 'Massachusetts',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MS': 'Mississippi',
        'MO': 'Missouri',
        'MT': 'Montana',
        'NE': 'Nebraska',
        'NV': 'Nevada',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NY': 'New York',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VT': 'Vermont',
        'VA': 'Virginia',
        'WA': 'Washington',
        'WV': 'West Virginia',
        'WI': 'Wisconsin',
        'WY': 'Wyoming',
    }
    , inplace = True)

    # Removing some States that aren't part of the 50 current US States. Thos are territories.
    cdc_vairants_data2 = cdc_vairants_data2[cdc_vairants_data2["State"]!= "AS"]
    cdc_vairants_data2 = cdc_vairants_data2[cdc_vairants_data2["State"]!= "DC"]
    cdc_vairants_data2 = cdc_vairants_data2[cdc_vairants_data2["State"]!= "GU"]
    cdc_vairants_data2 = cdc_vairants_data2[cdc_vairants_data2["State"]!= "MH"]
    cdc_vairants_data2 = cdc_vairants_data2[cdc_vairants_data2["State"]!= "FM"]
    cdc_vairants_data2 = cdc_vairants_data2[cdc_vairants_data2["State"]!= "MP"]
    cdc_vairants_data2 = cdc_vairants_data2[cdc_vairants_data2["State"]!= "PW"]
    cdc_vairants_data2 = cdc_vairants_data2[cdc_vairants_data2["State"]!= "PR"]
    cdc_vairants_data2 = cdc_vairants_data2[cdc_vairants_data2["State"]!= "VI"]

    # Take the transpose
    cdc_vairants_data = cdc_vairants_data2.transpose()

    # Take the first row and make it the column.
    cdc_vairants_data.columns = cdc_vairants_data.iloc[0]
    cdc_vairants_data = cdc_vairants_data[1:]

    df = cdc_vairants_data

    # plotly figure setup
    fig = go.Figure()

    # one trace for each df column
    fig.add_trace(go.Bar(name="Selection 1",x=df.index, y=df["Alabama"].values))

    # one trace for each df column
    fig.add_trace(go.Bar(name="Selection 2",x=df.index, y=df["Alabama"].values))

    # one button for each df column
    updatemenu= []
    buttons=[]

    # add second buttons
    buttons2 = []

    for i in list(df.columns):
        buttons.append(dict(method='restyle',label = str(i),args=[{'x':[df.index],'y':[df[i].values]},[0]])
                    )
    
    for i in list(df.columns):
        buttons2.append(dict(method='restyle',label = str(i),args=[{'x':[df.index],'y':[df[i].values]},[1]])
                    )

    # some adjustments to the updatemenus
    button_layer_1_height = 1.23
    updatemenu = list([dict(
        buttons = buttons,
        direction="down",
        pad={"r":10,"t":10},
        showactive=True,
        x= 0.1,
        xanchor="left",
        y= button_layer_1_height,
        yanchor="top",
        font = dict(color = "blue")
    ),dict(
        buttons = buttons2,
        direction="down",
        pad={"r":10,"t":10},
        showactive=True,
        x= 0.37,
        xanchor="left",
        y=button_layer_1_height,
        yanchor="top",font = dict(color = "red"))])


    fig.update_layout(showlegend=True, updatemenus=updatemenu)
    return fig



# Create variant summary table
@st.cache(suppress_st_warning=True)
def vairant_summary():
    # Pull in the data from the cdc 
    cdc_vairants_data = pd.read_csv("https://www.cdc.gov/coronavirus/2019-ncov/downloads/transmission/03112021_Web-UpdateCSV-TABLE.csv")

    # Change the column names
    cdc_vairants_data.columns = ["State", "UK Variant", "Brazil Variant", "South Africa Variant"]
    
    # Let's create a table:
    reported_cases_in_us = cdc_vairants_data.sum(axis=0)
    reported_cases_in_us = pd.DataFrame(reported_cases_in_us)
    reported_cases_in_us = reported_cases_in_us[1:]
    reported_cases_in_us.columns = ['Reported Cases in US']
    
    # Lets get the numbers of states reporting each of the variant
    number_of_states_reporting_uk_v = np.count_nonzero(cdc_vairants_data["UK Variant"])
    number_of_states_reporting_br_v = np.count_nonzero(cdc_vairants_data["Brazil Variant"])
    number_of_states_reporting_sa_v = np.count_nonzero(cdc_vairants_data["South Africa Variant"])

    d = {'UK Variant': [number_of_states_reporting_uk_v], 'Brazil Variant': [number_of_states_reporting_br_v],'South Africa Variant': [number_of_states_reporting_sa_v]}
    variant_summary_df = pd.DataFrame(data=d)
    variant_summary_df = variant_summary_df.transpose()
    variant_summary_df.columns = ["Number of Jurisdictions Reporting"]
 
    variant_summary_df["Reported Cases in US"] = reported_cases_in_us['Reported Cases in US']
    return variant_summary_df 

# function to get the current date
def get_pst_time():
    date_format="%B %d, %Y"
    date = datetime.now(tz=pytz.utc)
    date = date.astimezone(pytz.timezone('US/Pacific'))
    pstDateTime=date.strftime(date_format)
    return pstDateTime

# We create our Streamlit App
def main():
    st.set_page_config(layout="wide")
    st.title("COVID-19 - Dashboard")
    st.markdown('A Web App by [Navid Mashinchi](http://www.navidma.com)') 
    st.markdown("[![Follow](https://img.shields.io/github/followers/navido89?style=social)](https://github.com/navido89)&nbsp[![Follow](https://img.shields.io/twitter/follow/NMashinchi?style=social)](https://twitter.com/NMashinchi)") 

    # First Row
    row0_spacer1, row0_1, row0_spacer2, row0_2, row0_spacer3 = st.beta_columns((.1, 2, .2, 1, .1))

    # Create the sidebar.
    st.sidebar.image('./images/streamlit-logo.png')
    st.sidebar.title("Navigation")
    options = st.sidebar.radio("Go to",['Home','Global Situation', 'Situation by WHO Region', 'Situation in the United States'], key='1')
    st.sidebar.markdown("")
    st.sidebar.image('https://media.giphy.com/media/dVuyBgq2z5gVBkFtDc/giphy.gif')
    
    # Date for side bar
    date_current = get_pst_time()

 

    
    # Global cases and deaths for side bar
    global_cases_side_bar = round(get_global_cases())
    global_deaths_side_bar = round(get_global_deaths())   
    st.sidebar.info("Date: **{}**".format(date_current))
    st.sidebar.info("Global Cases: **{}**".format(global_cases_side_bar))
    st.sidebar.info("Global Deaths: **{}**".format(global_deaths_side_bar))

    # Main Page.
    if options == "Home":
        row1_spacer1, row1_1, row1_spacer2 = st.beta_columns((.1, 3.2, .1))

        with row1_1:
            st.markdown("![COVID-19 Picture](https://d2jx2rerrg6sh3.cloudfront.net/image-handler/ts/20200420091641/ri/674/picture/2020/4/%40shutterstock_1647268288.jpg)")
            st.markdown("Welcome to my COVID-19 data visualization web app. The purpose of this project is to have a look at the current state of COVID-19 using visualizations from different geographical perspectives. The plots have been created by using data visualization tools such as Plotly and Folium. The project is broken down into three parts.")
            st.markdown("**1. Global COVID-19 Situation**: We will display a folium map that shows the total cases, total deaths, total cases per 100,000, and total deaths per 100,000. In addition to that, we will display various time series plots to understand better how the disease spreads over time across the globe.")
            st.markdown("**2. COVID-19 Situation by World Health Organization Region (WHO)**: In the following section, we look at the disease from the World Health Organization's regional perspective. We will compare the different regions based on their total cases, total deaths, total cases per 100 million and total deaths per 100 million deaths.")
            st.markdown("**3. COVID-19 Situation in the United States**: Last but not least, we pay our attention to the United States and explore the current situation in the US based on the cases, deaths (with and without per capita), vaccine status, and the status of the different variants spreading across the states. ")
            st.markdown("The data is pulled from various resources, as you can see below in the Data Source section, and it will be updated daily by the various organizations listed below.")
            st.markdown("If you have any questions regarding this project or require any further information, feel free to [contact me](https://www.navidma.com/contact).")
            #We will write the GitHub link here.
            st.subheader('GitHub Link:')
            st.markdown('* [GitHub Repo](https://github.com/navido89/covid19-dashboard-dataviz)')
            
            #We will list the libraries here.
            st.subheader('Technologies:')
            st.markdown("Streamlit, Plotly, Folium, Pandas, GeoPandas, NumPy, Branca, Jinja2, Date.")
    
            #We will list the data source.
            st.subheader('Data Source:')
            
            # Covid data source.
            st.markdown('**COVID-19 - Data:**')
            st.markdown('* [Global Cases](https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv) by Johns Hopkins CCSE.')
            st.markdown('* [Global Deaths](https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv) by Johns Hopkins CCSE.')
            st.markdown('* [US Cases](https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv) by Johns Hopkins CCSE.')
            st.markdown('* [US Deaths](https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv) by Johns Hopkins CCSE.')
            st.markdown("* [Global Data](https://covid19.who.int/WHO-COVID-19-global-data.csv) by World Health Organization")
            st.markdown("* [US Vaccine Data](https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/us_state_vaccinations.csv) by Our World in Data.")
            st.markdown("* [US COVID-19 Cases Variants Data](https://www.cdc.gov/coronavirus/2019-ncov/downloads/transmission/03112021_Web-UpdateCSV-TABLE.csv) by Centers for Disease Control and Prevention (CDC).")

            # Population Data:
            st.markdown('**Population - Data:**')
            st.markdown('* [2020 Population by country](https://www.kaggle.com/tanuprabhu/population-by-country-2020?select=population_by_country_2020.csv) from Kaggle.')
            st.markdown('* [Population by WHO region](https://apps.who.int/gho/athena/data/xmart.csv?target=GHO/WHS9_86,WHS9_88,WHS9_89,WHS9_92,WHS9_96,WHS9_97,WHS9_90&profile=crosstable&filter=COUNTRY:-;REGION:*&x-sideaxis=REGION&x-topaxis=GHO;YEAR) by World Health Organization.')
        
            # Geography Date
            st.markdown('**GeoJSON - Data:**')
            st.markdown('* [World geoJSON file](https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json)')
            st.markdown('* [US geoJSON file](https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/us-states.json)')

    # Global Situation Page
    if options == "Global Situation":
        # We create the third row.
        row3_spacer1, row3_1, row3_spacer2 = st.beta_columns((.1, 3.2, .1))  
        with row3_1:
            # We get the date 
            date_current = get_pst_time()
            st.title('1. Global Situation:')
            global_cases = round(get_global_cases())
            global_deaths = round(get_global_deaths())
            st.markdown("As of **{}**, there have been **{}** positive COVID-19 cases and **{}** deaths globally. Below is a Folium Choropleth that shows the total cases, total deaths, total cases per capita (100,000), and total deaths per capita (100,000). **Please click on the layer control to select the different maps**. In addition to that, you can hover over each country to see more information.".format(date_current,global_cases,global_deaths))
            folium_plot1 = plot1()
            folium_static(folium_plot1)
            
            # Adding Top 5 Cases plot
            top5_country_cases = plot9()
            st.plotly_chart(top5_country_cases)

            # Adding Top 5 Deaths plot
            top5_country_deaths = plot10()
            st.plotly_chart(top5_country_deaths)

            # Adding Time Series Bar Plot.
            tsa_plot1 = plot4()
            st.plotly_chart(tsa_plot1)
            tsa_plot2 = plot5()
            st.plotly_chart(tsa_plot2)

            # Adding time series bubble maps with animation.
            bubble_plot1 = plot2()
            st.plotly_chart(bubble_plot1)
            bubble_plot2 = plot3()
            st.plotly_chart(bubble_plot2)
    
    # WHO Region Page
    if options == "Situation by WHO Region":
        # We create the third row.
        row3_spacer1, row3_1, row3_spacer2 = st.beta_columns((.1, 3.2, .1))  
        with row3_1:
            # Adding bar plots for WHO regions.
            st.title('2. Situation by WHO Regions:')
            st.markdown("The World Health Organization (WHO) divides its regions into 6 separate regions. The division is for the purposes of reporting, analysis, and administration. Below is a picture that shows the 6 different regions.")
            st.markdown("![WHO Regions](https://www.researchgate.net/profile/Anna-Lena-Lopez/publication/277779794/figure/fig3/AS:339883563470854@1458045964167/World-Health-Organization-regions.png)")
            who_plot1 = plot4a()
            st.plotly_chart(who_plot1)
           
    # US Situation Page
    if options == "Situation in the United States":
        row4_spacer1, row4_1, row4_spacer2 = st.beta_columns((.1, 3.2, .1))  
        with row4_1:
            st.title('3. Situation in the United States:')
            st.markdown("![USA Covid Picture](https://989bull.com/wp-content/uploads/2020/06/expert-warns-us-could-see-up-to-400000-covid-19-deaths-by-spring-2021.jpg)")
            st.markdown("Here the focus is on the United States and its current state regarding COVID-19, its Vaccine situation, and the different variants of the disease. To better understand the vaccine variables, please read below.")
            st.markdown("* **people_fully_vaccinated**: total number of people who received all doses prescribed by the vaccination protocol. If a person receives the first dose of a 2-dose vaccine, this metric stays the same. If they receive the second dose, the metric goes up by 1.")
            st.markdown("* **people_fully_vaccinated_per_hundred**: people_fully_vaccinated per 100 people in the total population of the state. ")
            st.markdown("* **total_distributed**: cumulative counts of COVID-19 vaccine doses recorded as shipped in CDC's Vaccine Tracking System. ")
            st.markdown('**Please click on the layer control to select the different maps**. In addition to that, you can hover over each state to see more information.')
            folium_plot8 = plot8()
            folium_static(folium_plot8)

            # add the Vertical Bar Plots
            US_vacc = plot11()
            st.plotly_chart(US_vacc)

            # Add Variant Table
            st.subheader("US COVID-19 Cases Caused by Variants")
            st.table(vairant_summary())

            # Add State Comparison of different Variants plot.
            st.subheader("Comparison COVID-19 Cases (Caused by Variants) by States")
            US_variant_comp = plot12()
            st.plotly_chart(US_variant_comp)
   
if __name__ == '__main__':
    main()
