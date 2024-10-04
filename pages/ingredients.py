import streamlit as st
import pandas as pd

from database.operations import TableOperator
from streamlit_ops.get_input import get_ing_values_input
from streamlit_ops.dialogs import add_ing_by_user


def main():
    ing_type_operator = TableOperator('ing_type')
    ingredients_operator = TableOperator('ingredient')

    # ingredient 추가 버튼
    add_ing_btn = st.button("ingredient 추가하기")

    # ing type마다 탭 생성
    ing_types_records = ing_type_operator.operate(op_key='read_all')
    ing_types = []
    for record in ing_types_records:
        ing_types.append(record[1])
    type_tabs = st.tabs(ing_types)

    # 각 ing type마다 해당하는 ingredient 띄우기
    for i in range(len(ing_types)):
        ing_records = ingredients_operator.operate(op_key='read_where', 
                                                feature=['type'],
                                                value=[ing_types[i]]
                                                )
        ing_names = [record[1] for record in ing_records]
        ing_is_selecteds = [False for i in range(len(ing_names))]
        ing_df = pd.DataFrame({
            'ingredient': ing_names,
            'is_selected': ing_is_selecteds
        })
        with type_tabs[i]:
            edited_ing_df = st.data_editor(ing_df, disabled=('ingredient', None),
                                            height=700)
            print(edited_ing_df[edited_ing_df['is_selected']==True])

    if add_ing_btn:
        add_ing_by_user(ingredients_operator, ing_types)
    
    # print("TEST:", type_tabs)
    print(">>", type_tabs[0])
    print(">>", type_tabs[1])


main()