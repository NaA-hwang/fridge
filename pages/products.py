import datetime

import streamlit as st
import pandas as pd
import numpy as np

from database.operations import TableOperator
from streamlit_ops. dialogs import add_prod_by_user

def main():
    prod_operator = TableOperator('product')
    ingredient_operator = TableOperator('ingredient')
    ing_type_operator = TableOperator('ing_type')

    # 탭 만들기 -----------------------------------------------------------------
    # ing_type마다 탭 생성
    ing_types_records = ing_type_operator.operate(op_key='read_all')
    # print(ing_types_records)
    ing_types_stocked, ing_types_unstocked = {}, {}
    for record in ing_types_records:
        ing_types_stocked[record[1]] = []
        ing_types_unstocked[record[1]] = []
    

    # 각 product마다 해당하는 ingredient의 ing_type을 추가: stocked
    stocked_product_records = prod_operator.operate('read_where',
                                            feature=['in_stock'],
                                            value=[1]) 
    stocked_products = []
    for product in stocked_product_records:
        product = list(product)
        stocked_products.append(product)
        
        ing_type_of_stocked_product = ingredient_operator.operate('read_where',
                                    feature=['name'],
                                    value=[product[2]])[0][2]
        # ing_types_stocked 딕셔너리에 해당하는 product 추가
        ing_types_stocked[ing_type_of_stocked_product].append(product)
    
    # 재고가 없는 상품들
    unstocked_product_records = prod_operator.operate('read_where',
                                            feature=['in_stock'],
                                            value=[0]) 
    unstocked_products = []
    for product in unstocked_product_records:
        product = list(product)
        unstocked_products.append(product)
        
        ing_type_of_unstocked_product = ingredient_operator.operate('read_where',
                                    feature=['name'],
                                    value=[product[2]])[0][2]
        # ing_types_unstocked 딕셔너리에 해당하는 product 추가
        ing_types_unstocked[ing_type_of_unstocked_product].append(product)


    # 어떤 ing_type의 product를 볼건지
    col1, col2 = st.columns([8.5, 1.5], vertical_alignment='bottom')
    ing_type_options = ['all'] + list(ing_types_stocked.keys())
    with col1:
        ing_type_selected = st.selectbox(label="ingredient type", options=ing_type_options)
    with col2:
        st.write("")
        btn_unstock = st.button("재고 삭제")
    table_cont = st.empty()
    if ing_type_selected:
        product_table_cols = prod_operator.operate('get_cols')
        if ing_type_selected == 'all':
            all_stocked = []
            for stocked_prod_per_ing_type in ing_types_stocked:
                prods = ing_types_stocked[stocked_prod_per_ing_type]
                if prods:
                    all_stocked += prods
            tab_product_df = pd.DataFrame(all_stocked, columns=product_table_cols)
        else: 
            tab_product_df = pd.DataFrame(ing_types_stocked[ing_type_selected], columns=product_table_cols)
            tab_product_df.drop(columns=['ing_type'], inplace=True)
        tab_product_df.drop(columns=['_id', 'in_stock', 'memo'], inplace=True)
        tab_product_df.fillna('', inplace=True)
        # 남은 날짜 계산 후 그 순서로 정렬
        tab_product_df['days_left'] = - ((tab_product_df['expired_on'] - pd.Timestamp.now().date())/1000000/60/60/24)
        tab_product_df['select'] = False
        tab_product_df = tab_product_df.sort_values(by='expired_on')
        # data_editor로 표시
        df = table_cont.data_editor(tab_product_df,
                            use_container_width=True,
                            hide_index=True,
                            height=800,
                            disabled=("icon", "name", "ingredient", "brand", "expired_on", "stored_in", "memo", "days_left")
                        )
        # 유통기한이 임박했거나 좀 지난 제품들 따로 띄우기
        prods_urgent = []
        urgent_left = pd.Timestamp.now().date() + datetime.timedelta(days=3)
        urgent_passed = pd.Timestamp.now().date() + datetime.timedelta(days=-10)
        prods_urgent.append(tab_product_df[(tab_product_df['expired_on']<= urgent_left) & (tab_product_df['expired_on']>= urgent_passed)]['name'])
        with st.sidebar:
            st.write("**급함**")
            for prod_urgent in prods_urgent:
                st.write(prod_urgent)
        # 선택한 제품들을 재고 없애기
        prods_to_unstock = df.loc[df['select'] == True]['name']
        if btn_unstock:
            if len(prods_to_unstock):
                for item in prods_to_unstock:
                    prod_operator.operate('update_where',
                                        feature={'update':"in_stock", 'where':'name'},
                                        value={'update':'0', 'where': item})
                st.rerun()
            else:
                st.toast("제품을 고르고 재고를 삭제해주세요")
        


    # 기능 -----------------------------------------------------------------

    # product 추가 버튼
    if st.sidebar.button("Product 추가하기"):
        add_prod_by_user(prod_operator, ingredient_operator, ing_types_unstocked)


main()