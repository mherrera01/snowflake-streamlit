import streamlit
import pandas
import requests
import snowflake.connector
from urllib.error import URLError

## Functions ##

def get_fruityvice_data(this_fruit_choice):
    # Get API response and normalize its JSON
    fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + this_fruit_choice)
    fruityvice_normalized = pandas.json_normalize(fruityvice_response.json())

    return fruityvice_normalized

def get_fruit_load_list():
    # Get the fruit list from snowflake
    with my_cnx.cursor() as my_cur:
        my_cur.execute("select * from fruit_load_list")
        return my_cur.fetchall()

def insert_row_snowflake(new_fruit):
    # Insert a fruit to snowflake
    with my_cnx.cursor() as my_cur:
        my_cur.execute("insert into fruit_load_list values ('" + new_fruit + "')")
        return "Thanks for adding " + new_fruit

## Main workflow ##

streamlit.title('My Parents New Healthy Diner')

streamlit.header('Breakfast Favorites')
streamlit.text('🥣 Omega 3 & Blueberry Oatmeal')
streamlit.text('🥗 Kale, Spinach & Rocket Smoothie')
streamlit.text('🐔 Hard-Boiled Free-Range Egg')
streamlit.text('🥑🍞 Avocado Toast')

streamlit.header('🍌🥭 Build Your Own Fruit Smoothie 🥝🍇')

# Read the fruit list csv file
my_fruit_list = pandas.read_csv("https://uni-lab-files.s3.us-west-2.amazonaws.com/dabw/fruit_macros.txt")
my_fruit_list = my_fruit_list.set_index('Fruit')

# Create a pick list so the users can pick the fruit they want to include 
fruits_selected = streamlit.multiselect("Pick some fruits:", list(my_fruit_list.index), ['Avocado', 'Strawberries'])

# Filter the fruit list depending on user input
fruits_to_show = my_fruit_list.loc[fruits_selected]

# Display the table on the page
streamlit.dataframe(fruits_to_show)

# New section for the fruityvice API
streamlit.header("Fruityvice Fruit Advice!")
try:
    # Request user input for getting the API response
    fruit_choice = streamlit.text_input('What fruit would you like information about?')
    if not fruit_choice:
        streamlit.error("Please select a fruit to get information.")
    else:
        fruityvice = get_fruityvice_data(fruit_choice)

        # Display the API response as a table
        streamlit.dataframe(fruityvice)

except URLError as e:
    streamlit.error()

# New section for the snowflake fruit list
streamlit.header("The fruit load list contains:")

# Add the button to load the fruit
if streamlit.button('Get Fruit Load List'):
    # Connect to the snowflake account
    my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])

    # Get and display the fruit list
    my_data_rows = get_fruit_load_list()
    streamlit.dataframe(my_data_rows)

# Request user input for adding a fruit to the list
add_my_fruit = streamlit.text_input('What fruit would you like to add?')

# Add the button to include a new fruit to the lsit
if streamlit.button('Add a Fruit to the List'):
    # Connect to the snowflake account
    my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])

    new_fruit_msg = insert_row_snowflake(add_my_fruit)
    streamlit.text(new_fruit_msg)
