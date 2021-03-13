# We import the libraries
import streamlit as st


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

    
   
if __name__ == '__main__':
    main()
