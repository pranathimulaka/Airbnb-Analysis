# Importing Libraries
import pandas as pd
import pymongo
import streamlit as st
import plotly.express as px
from streamlit_option_menu import option_menu
from PIL import Image

# Setting up page configuration
st.set_page_config(page_title= "Airbnb Data Visualization | By Jafar Hussain",
                   page_icon=None,
                   layout= "wide",
                   initial_sidebar_state= "auto",
                   menu_items=None)

# Creating option menu in the side bar
with st.sidebar:
    selected = option_menu("Menu", ["Home","Overview","Explore"], 
                           orientation="vertical",
                           icons=["house","graph-up-arrow","bar-chart-line"],
                           menu_icon= "menu-button-wide",
                           default_index=0,
                           styles={"nav-link": {"font-size": "20px", "text-align": "left", "margin": "-2px", "--hover-color": "#FF5A5F"},
                                   "nav-link-selected": {"background-color": "#FF5A5F"}}
                          )
# HOME PAGE    
if selected == "Home":
    col1,col2 = st.columns(2,gap= 'medium')
    col1.markdown("## :blue[Domain] : Travel Industry, Property Management and Tourism")
    col1.markdown("## :blue[Technologies used] : Python, Pandas, Plotly, Streamlit, MongoDB")
    col1.markdown("## :clipboard: Overview:")
    col1.markdown("### :To analyze Airbnb data using MongoDB Atlas, perform data cleaning and preparation, develop interactive visualizations, and create dynamic plots to gain insights into pricing variations, availability patterns, and location-based trends.")
    col2.markdown("#   ")
    col2.markdown("#   ")
    col2.markdown("#   ")

# CREATING CONNECTION WITH MONGODB ATLAS AND RETRIEVING THE DATA
client = pymongo.MongoClient("mongodb://localhost:27017")
db = client['Airbnb_Analysis']
col = db['listingsAndReviews']

# READING THE CLEANED DATAFRAME
df = pd.read_csv('/Users/mulakapranathi/Downloads/archive (1)/listings_details.csv')

# Clean 'price' column by removing non-numeric characters and converting to float
df['price'] = df['price'].replace('[\$,]', '', regex=True).astype(float)

# Sidebar for user input
st.sidebar.title("Filters")
price_min = df['price'].min()  # Minimum price value
price_max = df['price'].max()  # Maximum price value
price_range = st.sidebar.slider('Select Price Range', price_min, price_max, (price_min, price_max))

# Filter data based on user inputs
filtered_df = df[(df['price'].between(price_range[0], price_range[1]))]

# Displaying filtered data
st.write("Filtered Data:")
st.write(filtered_df)

# Visualization - Example: Price distribution
st.title('Price Distribution')
fig = px.histogram(filtered_df, x='price', nbins=30, title='Price Distribution')
st.plotly_chart(fig)

# OVERVIEW PAGE
if selected == "Overview":
    tab1,tab2 = st.tabs(["$\huge 📝 RAW DATA $", "$\huge🚀 INSIGHTS $"])
    
    # RAW DATA TAB
    with tab1:
        # RAW DATA
        col1,col2 = st.columns(2)
        if col1.button("Click to view Raw data"):
            col1.write(col.find_one())
        # DATAFRAME FORMAT
        if col2.button("Click to view Dataframe"):
            col1.write(col.find_one())
            col2.write(df)
            
       # INSIGHTS TAB
    with tab2:
        # GETTING USER INPUTS
        country = st.sidebar.multiselect('Select a Country', sorted(df['country'].unique()), sorted(df['country'].unique()))
        prop = st.sidebar.multiselect('Select Property_type', sorted(df['property_type'].unique()), sorted(df['property_type'].unique()))
        room = st.sidebar.multiselect('Select Room_type', sorted(df['room_type'].unique()), sorted(df['room_type'].unique()))
        price = st.slider('Select Price', price_min, price_max, (price_min, price_max))
        
        # CONVERTING THE USER INPUT INTO QUERY
        query = f"country in {country} & property_type in {prop} & room_type in {room} & price >= {price[0]} & price <= {price[1]}"

        # FILTERING DATAFRAME BASED ON USER SELECTIONS
        selected_data = df[
            (df['price'] >= price[0]) & (df['price'] <= price[1]) &
            (df['country'].isin(country)) &
            (df['property_type'].isin(prop)) &
            (df['room_type'].isin(room))
        ]
        st.write(selected_data)
        
        with col1:
            
            # TOP 10 PROPERTY TYPES BAR CHART
            df1 = df.query(query).groupby(["property_type"]).size().reset_index(name="Listings").sort_values(by='Listings',ascending=False)[:10]
            fig = px.bar(df1,
                         title='Top 10 Property Types',
                         x='Listings',
                         y='property_type',
                         orientation='h',
                         color='property_type',
                         color_continuous_scale=px.colors.sequential.Agsunset)
            st.plotly_chart(fig,use_container_width=True) 
        
            # TOP 10 HOSTS BAR CHART
            df2 = df.query(query).groupby(["host_name"]).size().reset_index(name="Listings").sort_values(by='Listings',ascending=False)[:10]
            fig = px.bar(df2,
                         title='Top 10 Hosts with Highest number of Listings',
                         x='Listings',
                         y='host_name',
                         orientation='h',
                         color='host_name',
                         color_continuous_scale=px.colors.sequential.Agsunset)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig,use_container_width=True)
            
        with col2:
            
            # TOTAL LISTINGS IN EACH ROOM TYPES PIE CHART
            df1 = df.query(query).groupby(["room_type"]).size().reset_index(name="counts")
            fig = px.pie(df1,
                         title='Total Listings in each room_type',
                         names='room_type',
                         values='counts',
                         color_discrete_sequence=px.colors.sequential.Rainbow
                        )
            fig.update_traces(textposition='outside', textinfo='value+label')
            st.plotly_chart(fig,use_container_width=True)
            
            # TOTAL LISTINGS BY COUNTRY CHOROPLETH MAP
            country_df = df.query(query).groupby(['country'],as_index=False)['name'].count().rename(columns={'name' : 'Total_Listings'})
            fig = px.choropleth(country_df,
                                title='Total Listings in each country',
                                locations='country',
                                locationmode='country names',
                                color='Total_Listings',
                                color_continuous_scale=px.colors.sequential.Plasma
                               )
            st.plotly_chart(fig,use_container_width=True)
            
        # Creating visualizations using selected_data DataFrame
    col1, col2 = st.columns(2, gap='medium')

    with col1:
        # Example: Bar chart showing Price distribution by Room type
        fig_bar = px.bar(selected_data, x='room_type', y='price', title='Price distribution by Room type')
        st.plotly_chart(fig_bar, use_container_width=True)

        # Example: Pie chart showing Property Type distribution
        fig_pie = px.pie(selected_data, names='property_type', title='Property Type distribution')
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        # Example: Box plot showing Price distribution by Property Type
        fig_box = px.box(selected_data, x='property_type', y='price', title='Price distribution by Property Type')
        st.plotly_chart(fig_box, use_container_width=True)

        # Example: Choropleth map showing listings count by Country
        fig_choropleth = px.choropleth(selected_data.groupby('country').size().reset_index(name='listings'),
                                       locations='country', locationmode='country names',
                                       color='listings', hover_name='country',
                                       title='Listings count by Country')
        st.plotly_chart(fig_choropleth, use_container_width=True)
            
# EXPLORE PAGE
if selected == "Explore":
    st.markdown("## Explore more about the Airbnb data")
    
    # GETTING USER INPUTS
    country = st.sidebar.multiselect('Select a Country', sorted(df['country'].unique()), sorted(df['country'].unique()))
    prop = st.sidebar.multiselect('Select Property_type', sorted(df['property_type'].unique()), sorted(df['property_type'].unique()))
    room = st.sidebar.multiselect('Select Room_type', sorted(df['room_type'].unique()), sorted(df['room_type'].unique()))
    price = st.slider('Select Price', df['price'].min(), df['price'].max(), (df['price'].min(), df['price'].max()))

    # CONVERTING THE USER INPUT INTO QUERY
    query = f"country in {country} & property_type in {prop} & room_type in {room} & price >= {price[0]} & price <= {price[1]}"
    # HEADING 1: Price Analysis
    st.markdown("## Price Analysis")
    
    # CREATING COLUMNS
    col1, col2 = st.columns(2, gap='medium')

    with col1:
        # AVG PRICE BY ROOM TYPE BARCHART
        pr_df = df.query(query).groupby('room_type', as_index=False)['price'].mean().sort_values(by='price')
        fig_avg_price_room_type = px.bar(pr_df, x='room_type', y='price', color='price', title='Avg Price in each Room type')
        st.plotly_chart(fig_avg_price_room_type, use_container_width=True)
        
        # HEADING 2: Availability Analysis
        st.markdown("## Availability Analysis")
        
        # AVAILABILITY BY ROOM TYPE BOX PLOT
        fig_avail_room_type = px.box(df.query(query), x='room_type', y='availability_365', color='room_type', title='Availability by Room Type')
        st.plotly_chart(fig_avail_room_type, use_container_width=True)

    with col2:
        # AVG PRICE IN COUNTRIES SCATTERGEO
        avg_price_country = df.query(query).groupby('country', as_index=False)['price'].mean()
        fig_avg_price_country = px.scatter_geo(avg_price_country, locations='country', color='price', hover_data=['price'],
                                               locationmode='country names', size='price', title='Avg Price in each Country',
                                               color_continuous_scale='agsunset')
        st.plotly_chart(fig_avg_price_country, use_container_width=True)
        
        # BLANK SPACE
        st.markdown("#   ")
        st.markdown("#   ")
        
        # AVG AVAILABILITY IN COUNTRIES SCATTERGEO
        avg_avail_country = df.query(query).groupby('country', as_index=False)['availability_365'].mean()
        avg_avail_country['availability_365'] = avg_avail_country['availability_365'].astype(int)
        fig_avg_avail_country = px.scatter_geo(avg_avail_country, locations='country', color='availability_365',
                                               hover_data=['availability_365'], locationmode='country names',
                                               size='availability_365', title='Avg Availability in each Country',
                                               color_continuous_scale='agsunset')
        st.plotly_chart(fig_avg_avail_country, use_container_width=True)
