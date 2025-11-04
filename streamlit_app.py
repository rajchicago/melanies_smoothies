# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# App Title
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input for name
name_on_order = st.text_input("Name on Smoothie:")
if name_on_order:
    st.write(f"The name on your Smoothie will be: **{name_on_order}**")

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit options
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"), col("SEARCH_ON"))
pd_df = my_dataframe.to_pandas()

# Display fruit options
st.dataframe(pd_df, use_container_width=True)

# Create a list of fruit names for selection
fruit_options = pd_df["FRUIT_NAME"].tolist()

# Multiselect for ingredients
ingredients_list = st.multiselect(
    "🍓 Choose up to 5 ingredients:",
    fruit_options,
    max_selections=5
)

# If fruits selected
if ingredients_list:
    ingredients_string = ", ".join(ingredients_list)
    st.success(f"✅ You selected: **{ingredients_string}**")

    # Loop through fruits and show nutrition info
    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df["FRUIT_NAME"] == fruit_chose]()_]()
