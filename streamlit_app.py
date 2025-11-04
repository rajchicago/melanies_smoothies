# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Write directly to the app
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input name
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit options
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"), col("SEARCH_ON"))
pd_df = my_dataframe.to_pandas()

# Show available fruits
st.dataframe(pd_df, use_container_width=True)

# Multiselect fruit names
fruit_options = pd_df["FRUIT_NAME"].tolist()
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,
    max_selections=5
)

# If user chose fruits
if ingredients_list:
    ingredients_string = ", ".join(ingredients_list)
    st.write(f"You selected: {ingredients_string}")

    # For each chosen fruit, show nutrition info
    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.subheader(f"{fruit_chosen} Nutrition Information")

        # Get fruit nutrition info from external API
        api_url = f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        smoothiefroot_response = requests.get(api_url)

        if smoothiefroot_response.status_code == 200:
            nutrition_data = smoothiefroot_response.json()
            st.json(nutrition_data)
        else:
            st.error(f"Could not retrieve nutrition info for {fruit_chosen}")

    # Prepare SQL insert
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """
    st.write(my_insert_stmt)

    # Button to submit order
    if st.button("Submit Order"):
        session.sql(my_insert_stmt).collect()
        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")
