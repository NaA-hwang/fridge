from datetime import datetime, date

import streamlit as st
import pandas as pd

from database.operations import TableOperator
from streamlit_ops.dialogs import add_recipe_by_user, update_recipe_by_user

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
        # 최근 요리된 날짜
        recent_on = record[7]
        if not recent_on:
            recent_on = datetime.strptime('2020-01-01', '%Y-%m-%d').date()
        

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
            'recently_cooked_on': recent_on
        })

        ing_not_in_stock += main_ings['unstocked']
        ing_not_in_stock += sub_ings['unstocked']
        ing_not_in_stock = list(set(ing_not_in_stock))

        
    st.write(f"님 지금 없는 재료: {', '.join(ing_not_in_stock)}")
    # 없는 메인재료가 적은 순으로 정렬한 리스트를 순서대로 출력
    sorted_recipes = sorted(recipes, key=lambda recipe: (len(recipe['main_unstocked']), recipe['recently_cooked_on']))
    
    for recipe in sorted_recipes:

        st.header(recipe['title'])
        col1, col2 = st.columns(2)
        with col1:
            st.caption("#" + " #".join(recipe['category']))
            st.write(f"없는 메인 재료 {len(recipe['main_unstocked'])}개")
        
        with col2:
            recently_cooked_on = st.date_input(label=f"{recipe['title']} recently cooked on", value=recipe['recently_cooked_on'])
            if recently_cooked_on != recipe['recently_cooked_on']:
                recipe_operator.operate('update_where', 
                                        feature={'update': 'recently_cooked_on', 'where': 'title'},
                                        value={'update': recently_cooked_on, 'where': recipe['title']})
        
        st.subheader("Ingredients")
        col3, col4 = st.columns(2)
        col3.write("**" + ", ".join(recipe['main_stocked']) + "**")
        col3.write( ", ".join(recipe['main_unstocked']))
        col4.write("**" + ", ".join(recipe['sub_stocked']) + "**")
        col4.write( ", ".join(recipe['sub_unstocked']))
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

    # recipe 수정 버튼
    if st.sidebar.button("Recipe 수정하기"):
        update_recipe_by_user(prod_operator, recipe_operator, cat_list)

    







main()