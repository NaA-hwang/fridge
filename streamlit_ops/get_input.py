import streamlit as st

def get_ing_values_input(cur_ing_types):
    """
    ing name을 입력받고, ingredient types를 나열해 보여주고 그 중에 선택해 리스트로 반환
    """
    
    ing_name = st.text_input("ingredient의 이름을 입력하세요.")
    selected = st.selectbox(
        label="ing_type을 고르세요",
        options=cur_ing_types,
        index=None,
        placeholder="ing_type을 선택하세요",
        label_visibility="collapsed"
    )
    value_list = [ing_name, selected]

    return value_list