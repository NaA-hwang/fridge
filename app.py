import streamlit as st

pages = st.navigation([
        st.Page('./pages/products.py', title="Products", icon="🍾"),
        st.Page('./pages/ingredients.py', title="Ingredients", icon="🥣"),
        st.Page('./pages/recipes.py', title="Recipes", icon="🧑🏻‍🍳"),
        st.Page('./pages/search_recipe.py', title="Search Recipes", icon="🧑🏻‍🍳")
    ])

pages.run()
