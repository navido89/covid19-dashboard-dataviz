# We import the libraries
import streamlit as st
import plotly.express as px # This is for bubble maps and bar plots
import pandas as pd 

# WHO Global Data
who_global_data = "https://covid19.who.int/WHO-COVID-19-global-data.csv"

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
    fig2.update_layout(showlegend=True, updatemenus=updatemenu, title_text = "Global Cases",xaxis_title="Date",yaxis_title="Values")
    fig2.update_xaxes(categoryorder= 'array', categoryarray= df.index)
    return fig2 

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
    fig3.update_layout(showlegend=True, updatemenus=updatemenu2, title_text = "Global Deaths", xaxis_title="Date",yaxis_title="Values")
    fig3.update_xaxes(categoryorder= 'array', categoryarray= df.index)
    return fig3


@st.cache(suppress_st_warning=True)
# Plot Number 6 - Bart Plot WHO Regions 1
def plot6():
    df_cont = pd.read_csv(who_global_data)
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
    
    # We plot the data now per   
    df = cont_totals

    # Create lists to iterate over
    lst = ['Total_Cases','Total_Deaths']

    # one trace for each df column
    fig = px.bar(x=df["WHO_region"].values, y=df["Total_Cases"].values)

    # one button for each df column
    updatemenu= []
    buttons=[]

    for i in lst:
        buttons.append(dict(method='restyle',label = str(i),args=[{'x':[df["WHO_region"].values],'y':[df[i].values]},[0]])
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
        yanchor="top",  font = dict(color = "black"))])

    fig.update_traces(marker_color=['orange','green','purple','brown','blue','pink'])
    fig.update_layout(showlegend=False, updatemenus=updatemenu,title_text = "Actual Numbers",xaxis_title="WHO_Region",
    yaxis_title="Values")
    fig.update_xaxes(categoryorder= 'array', categoryarray= df.index)
    return fig


@st.cache(suppress_st_warning=True)
# Plot Number 7 - Bart Plot WHO Regions 2
def plot7():
    df_cont = pd.read_csv(who_global_data)
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
    
    # We plot the data now per   
    df = cont_totals

    # We set up the second plot
    lst2 = ['Total_Cases_Per_100mill', 'Total_Deaths_Per_100mill']
   
    fig2 = px.bar(x=df["WHO_region"].values, y=df["Total_Deaths"].values)

    updatemenu2= []
    buttons2=[]

    for i in lst2:
        buttons2.append(dict(method='restyle',label = str(i),args=[{'x':[df["WHO_region"].values],'y':[df[i].values]},[0]])
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
        yanchor="top",  font = dict(color = "black"))])

    fig2.update_traces(marker_color=['orange','green','purple','brown','blue','pink'])
    fig2.update_layout(showlegend=False, updatemenus=updatemenu2,title_text = "Numbers Per Capita",xaxis_title="WHO_Region",yaxis_title="Values")
    fig2.update_xaxes(categoryorder= 'array', categoryarray= df.index)
    return fig2


# We create our Streamlit App
def main():
    st.set_page_config(layout="wide")
    
    st.title("Covid19 - Dashboard")
    
    # First Row
    row0_spacer1, row0_1, row0_spacer2, row0_2, row0_spacer3 = st.beta_columns((.1, 2, .2, 1, .1))
    st.markdown('A Web App by [Navid Mashinchi](http://www.navidma.com)')

    # Create the sidebar
    st.sidebar.title("Covid19 - Dashboard")
    st.sidebar.markdown("Hey there! Welcome to my Covid19 data visualization web app. The purpose of this project is to have a look at the current state of Covid19 using visualizations from different geographical perspectives. The project is broken down into three parts.")
    st.sidebar.markdown("**1.** Global Covid19 Situation")
    st.sidebar.markdown("**2.** Covid19 Situation by World Health Organization Region (WHO)")
    st.sidebar.markdown("**3.** Covid19 Situation in the United States")

    st.sidebar.title("Navigator")
   
    options = st.sidebar.selectbox("Please Select A Page",['Home','Global Situation', 'Situation by WHO Region', 'Situation in the United States'], key='1')
    
    # Main Page
    if options == "Home":
        row1_spacer1, row1_1, row1_spacer2 = st.beta_columns((.1, 3.2, .1))

        with row1_1:
            st.markdown("![Covid 19 Picture](http://www.pharmatimes.com/__data/assets/image/0010/1347742/p42_image.jpg)")
            st.markdown("Hey there! Welcome to my Covid19 data visualization web app. The purpose of this project is to have a look at the current state of Covid19 using visualizations from different geographical perspectives. The project is broken down into three parts.")
            st.markdown("**1.** Global Covid19 Situation")
            st.markdown("**2.** Covid19 Situation by World Health Organization Region (WHO)")
            st.markdown("**3.** Covid19 Situation in the United States")
            
            #We will list the data source.
            st.subheader('Data Source:')
            
            # Covid data source.
            st.markdown('**Covid19 - Data:**')
            st.markdown('* [Global Cases](https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv) by Johns Hopkins CCSE.')
            st.markdown('* [Global Deaths](https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv) by Johns Hopkins CCSE.')
            st.markdown('* [US Cases](https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv) by Johns Hopkins CCSE.')
            st.markdown('* [US Deaths](https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv) by Johns Hopkins CCSE.')
            st.markdown("* [Global Data](https://covid19.who.int/WHO-COVID-19-global-data.csv) by World Health Organization")
            st.markdown("* [US Vaccine Data](https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/us_state_vaccinations.csv) by Our World in Data")

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
            # today = date.today()
            # current_date = today.strftime("%B %d, %Y")
            # st.subheader('1. Global Situation:')
            # global_cases = round(get_global_cases())
            # global_deaths = round(get_global_deaths())
            # st.markdown("As of **{}**, there have been **{}** positive Covid19 cases and **{}** deaths globally. Below is a Folium Choropleth that shows the total cases, total deaths, total cases per capita (100,000), and total deaths per capita (100,000). **Please click on the layer control to select the different maps**. In addition to that, you can hover over each country to see more information.".format(current_date,global_cases,global_deaths))
            # folium_plot1 = plot1()
            # folium_static(folium_plot1)
            
            
            # Adding time series bubble maps with animation.
            bubble_plot1 = plot2()
            st.plotly_chart(bubble_plot1)
            bubble_plot2 = plot3()
            st.plotly_chart(bubble_plot2)
            
            # Adding Time Series Bar Plot.
            tsa_plot1 = plot4()
            st.plotly_chart(tsa_plot1)
            tsa_plot2 = plot5()
            st.plotly_chart(tsa_plot2)
    
    # WHO Region Pge
    if options == "Situation by WHO Region":
        # We create the third row.
        row3_spacer1, row3_1, row3_spacer2 = st.beta_columns((.1, 3.2, .1))  
        with row3_1:
            # Adding bar plots for WHO regions.
            st.subheader('2. Situatoin by WHO Regions:')
            st.markdown("The World Health Organization (WHO) divides its regions into 6 separate regions. The division is for the purposes of reporting, analysis, and administration. Below is a picture that shows the 6 different regions.")
            st.markdown("![WHO Regions](https://www.researchgate.net/profile/Anna-Lena-Lopez/publication/277779794/figure/fig3/AS:339883563470854@1458045964167/World-Health-Organization-regions.png)")
            who_plot1 = plot6()
            st.plotly_chart(who_plot1)
            who_plot2 = plot7()
            st.plotly_chart(who_plot2)

    
   
if __name__ == '__main__':
    main()
