from datetime import datetime, date

import streamlit as st
import pandas as pd

from database.operations import TableOperator
from streamlit_ops. dialogs import add_recipe_by_user

def main():
    prod_operator = TableOperator('product')
    recipe_operator = TableOperator('recipes')


    # 레시피 ----------------------------------------------------------------------------------------

    # 재고가 있는 product와 Ingredient 리스트 만들기
    prod_in_stock_records = prod_operator.operate('read_where', feature=['in_stock'], value=[1])
    prod_in_stock = []
    ing_in_stock = []
    ing_not_in_stock = []
    cat_list = []

    # 재고가 있는 product의 리스트를 prod_in_stock에, 그 product의 ingredient 정보를 ing_in_stock에
    for record in prod_in_stock_records:
        prod_in_stock.append(record[1])
        ing = record[2]
        if ing not in ing_in_stock: ing_in_stock.append(ing)
    

    # 디비의 레시피 딕셔너리 리스트로 가져오기
    recipe_records = recipe_operator.operate('read_all')
    recipes = []
    for record in recipe_records:
        # 재고 유무에 따라 메인재료와 서브재료 나누기
        main_ings_list = record[2].split(", ")
        main_ings = {'stocked': [], 'unstocked': []}
        for main_ing in main_ings_list:
            if main_ing not in ing_in_stock: main_ings['unstocked'].append(main_ing)
            else: main_ings['stocked'].append(main_ing)
        sub_ings_list = record[3].split(", ")
        sub_ings = {'stocked': [], 'unstocked': []}
        for sub_ing in sub_ings_list:
            if sub_ing not in ing_in_stock: sub_ings['unstocked'].append(sub_ing)
            else: sub_ings['stocked'].append(sub_ing)

        # 카테고리를 리스트로 만들어 전체 카테고리리스트 cat_list에 추가하기
        categories = record[6].split(', ')
        for cat in categories: 
            if cat not in cat_list: cat_list.append(cat)

        recipes.append({
            'title': record[1],
            'main_stocked': main_ings['stocked'],
            'main_unstocked': main_ings['unstocked'],
            'sub_stocked': sub_ings['stocked'],
            'sub_unstocked': sub_ings['unstocked'],
            'recipe': record[4],
            'feedback': record[5],
            'category': categories,
        })

        ing_not_in_stock += main_ings['unstocked']
        ing_not_in_stock += sub_ings['unstocked']
        ing_not_in_stock = list(set(ing_not_in_stock))

    
    st.write(f"님 지금 없는 재료: {', '.join(ing_not_in_stock)}")
    # 없는 메인재료가 적은 순으로 정렬한 리스트를 순서대로 출력
    sorted_recipes = sorted(recipes, key=lambda recipe: (len(recipe['main_unstocked'])))
    
    for recipe in sorted_recipes:
        st.header(recipe['title'])
        st.caption("#" + " #".join(recipe['category']))
        st.write(len(recipe['main_unstocked']))
        st.subheader("Ingredients")
        col1, col2 = st.columns(2)
        col1.write("**" + ", ".join(recipe['main_stocked']) + "**")
        col1.write( ", ".join(recipe['main_unstocked']))
        col2.write("**" + ", ".join(recipe['sub_stocked']) + "**")
        col2.write( ", ".join(recipe['sub_unstocked']))
        st.subheader("Recipe")
        st.markdown(recipe['recipe'])
        prev_feedback = recipe['feedback']
        new_feedback = st.text_area(label=f"feedback: {recipe['title']}",
                                    value=prev_feedback)
        if new_feedback != prev_feedback:
            if st.button(f"({recipe['title'][0]}) 피드백 업뎃"):
                recipe_operator.operate('update_where',
                                        feature={'update': 'feedback', 'where': 'title'},
                                        value={'update': new_feedback, 'where': record[1]})
                st.toast("피드백 업뎃 완료!") 
        st.divider()




    # 기능 --------------------------------------------------------------------------------------

    # product 추가 버튼
    if st.sidebar.button("Recipe 추가하기"):
        add_recipe_by_user(prod_operator, recipe_operator, cat_list)

    







main()