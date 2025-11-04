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
        search_on = pd_df.loc[pd_df["FRUIT_NAME"] == fruit_chosen, "SEARCH_ON"].iloc[0]
        api_url = f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        response = requests.get(api_url)

        # Collapsible expander for each fruit
        with st.expander(f"🍎 {fruit_chosen} Nutrition Information"):
            if response.status_code == 200:
                fruit_data = response.json()

                if "nutritions" in fruit_data:
                    nutrition_dict = fruit_data["nutritions"]
                    nutrition_df = pd.DataFrame(
                        nutrition_dict.items(), columns=["Nutrient", "Value"]
                    )
                    st.table(nutrition_df)
                else:
                    st.warning("⚠️ No nutrition details available for this fruit.")
            else:
                st.error(f"❌ Could not retrieve data for {fruit_chosen} (Status {response.status_code})")

    # Create SQL insert for order
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    st.write("📋 SQL Preview:")
    st.code(my_insert_stmt, language="sql")

    # Submit order button
    if st.button("Submit Order"):
        session.sql(my_insert_stmt).collect()
        st.success(f"✅ Your Smoothie has been ordered, {name_on_order}!")
