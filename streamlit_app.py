# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Streamlit UI
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input name
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"), col("SEARCH_ON"))
pd_df = my_dataframe.to_pandas()

# Display available fruits
st.dataframe(pd_df, use_container_width=True)

# Multiselect fruit names
fruit_options = pd_df["FRUIT_NAME"].tolist()
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,
    max_selections=5
)

# When fruits are selected
if ingredients_list:
    ingredients_string = ", ".join(ingredients_list)
    st.write(f"You selected: {ingredients_string}")

    # Loop through each fruit and display nutrition info
    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.subheader(f"{fruit_chosen} Nutrition Information")

        # Fetch data from external API
        api_url = f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        response = requests.get(api_url)

        if response.status_code == 200:
            fruit_data = response.json()

            # Convert the JSON to a table-like format
            # (Assumes JSON has structure like {"name": ..., "nutritions": {...}})
            if isinstance(fruit_data, dict) and "nutritions" in fruit_data:
                nutrition_dict = fruit_data["nutritions"]
                nutrition_df = pd.DataFrame(nutrition_dict.items(), columns=["Nutrient", "Value"])
                st.table(nutrition_df)
            else:
                st.warning("No nutrition details available for this fruit.")
        else:
            st.error(f"⚠️ Could not retrieve data for {fruit_chosen} (status code: {response.status_code})")

    # Insert order into Snowflake
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    if st.button("Submit Order"):
        session.sql(my_insert_stmt).collect()
        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")
