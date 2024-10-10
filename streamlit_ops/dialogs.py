import streamlit as st
from database.operations import TableOperator

from .get_input import get_ing_values_input

@st.dialog("Add an ingredient")
def add_ing_by_user(operator, ing_type_list):
    """
    입력받은 ingredient name의 중복여부 확인 후 등록하는 입력창
    """

    value_list = get_ing_values_input(ing_type_list)
    cols = st.columns(2)
    with cols[0]:
        if st.button("등록") and value_list[0] and value_list[1]:
            result = operator.operate(op_key='create_one',
                            value=value_list
                            )
            if result:
                st.write("이미 등록된 재료입니다.")
            else:
                st.write(f"{value_list[0]} 등록완료!")
    with cols[1]:
        if st.button("종료"):
            st.rerun()

@st.dialog("Product 추가하기")
def add_prod_by_user(prod_operator, ingredient_operator, ing_types):
    """
    입력받은 ingredient name의 등록여부 확인 후 있으면 재고 있음으로 돌리고, 없으면 생성
    """
    storages = ['냉장','냉동','상온']
    cols = st.columns(spec=(0.4, 0.6))

    # ing_types 선택
    with cols[0]:
        st.subheader("ingredient type")
        selected_ing_type = st.radio(label="ingredient type",
                                    options=ing_types.keys(),
                                    index=None,
                                    label_visibility="collapsed")

    # 기존 product 선택
    with cols[1]:
        st.subheader("products")
        if selected_ing_type:
            prods_to_show = []
            for prod in ing_types[selected_ing_type]:
                if prod[3]: prods_to_show.append(prod[1])
                else: prods_to_show.append(prod[1])
            
            selected_product = st.selectbox(label='기존 제품 중 선택', placeholder='기존 제품 중 선택', options=prods_to_show, index=None, label_visibility='collapsed')
            if selected_product:
                record = prod_operator.operate('read_where', feature=['name'], value=[selected_product])[0]
                expired_on = st.date_input(label="유통기한", value=record[5])
                for i in range(3):
                    if storages[i] == record[6]:
                        prev_storage_idx = i
                stored_in = st.selectbox(label="보관장소 변경", options=storages, index=prev_storage_idx)
                
            if st.button("재고 업뎃"):
                prod_operator.operate('update_where', 
                                        feature={'update': 'expired_on', 'where': 'name'},
                                        value={'update': expired_on, 'where': selected_product})
                prod_operator.operate('update_where', 
                                        feature={'update': 'stored_in', 'where': 'name'},
                                        value={'update': stored_in, 'where': selected_product})
                prod_operator.operate('update_where', 
                                        feature={'update': 'in_stock', 'where': 'name'},
                                        value={'update': 1, 'where': selected_product})
                st.rerun()
            
            st.subheader("새로 추가하기")
            name = st.text_input("제품 이름")
            ing_type_records = ingredient_operator.operate('read_where', feature=['type'], value=[selected_ing_type])
            ing_type_options = []
            for ing_type_record in ing_type_records:
                ing_type_options.append(ing_type_record[1])
            ingredient = st.selectbox("재료", ing_type_options)
            ing_type = selected_ing_type
            brand = st.text_input("브랜드")
            expired_on = st.date_input("유통기한").strftime("%Y-%m-%d")
            stored_in = st.selectbox(label="보관장소",
                                    options=storages)
            memo = st.text_input("메모")
                
            if st.button("등록"):
                if name and ingredient and expired_on and stored_in:
                    prod_operator.operate('create_one',
                                    value = [name, ingredient, ing_type, brand, expired_on, stored_in, memo, '1'])
                    st.rerun()
    

@st.dialog("Recipe 추가하기")
def add_recipe_by_user(prod_operator, recipe_operator, categories):
    # ingredient 목록 읽어오기
    ing_operator = TableOperator('ingredient')
    all_ing_records = ing_operator.operate('read_all')
    ingredients = []
    for ing_record in all_ing_records:
        ingredients.append(ing_record[1])

    title = st.text_input("레시피 이름")
    cats_selected = st.multiselect(label="카테고리", options=categories)
    category = ', '.join(cats_selected)
    main_ings_selected = st.multiselect(label="메인재료", options=ingredients)
    main_ings = ', '.join(main_ings_selected)
    sub_ings_selected = st.multiselect(label="서브재료", options=ingredients)
    sub_ings = ', '.join(sub_ings_selected)
    recipe = st.text_area(label="recipe")
    feedback = st.text_input(label="feedback")

    if st.button("레시피 등록"):
        if title and main_ings_selected and recipe:
            recipe_operator.operate('create_one',
                                    value= [title, main_ings, sub_ings, recipe, feedback, category])
            st.rerun()

@st.dialog("Recipe 수정하기")
def update_recipe_by_user(prod_operator, recipe_operator, cat_list):
    # ingredient 목록 읽어오기
    ing_operator = TableOperator('ingredient')
    all_ing_records = ing_operator.operate('read_all')
    ingredients = []
    for ing_record in all_ing_records:
        ingredients.append(ing_record[1])

    recipe_records = recipe_operator.operate('read_all')
    recipe_titles = [recipe_record[1] for recipe_record in recipe_records]
    reci_title_tochange = st.selectbox(label='어느 레시피?', label_visibility='collapsed', options=recipe_titles, index=None)
    if reci_title_tochange:
        target_reci_rec = recipe_operator.operate('read_where', feature=['title'], value=[reci_title_tochange])[0]
        if target_reci_rec:
            id_num = target_reci_rec[0]
            title = st.text_input(label='레시피 이름', value=target_reci_rec[1], label_visibility='collapsed')
            main_ing = st.multiselect(label="main_ing", options=ingredients, default=target_reci_rec[2].split(', '), label_visibility='collapsed')
            sub_ing = st.multiselect(label="sub_ing", options=ingredients, default=target_reci_rec[3].split(', '), label_visibility='collapsed')
            recipe = st.text_area(label='recipe', value=target_reci_rec[4], label_visibility='collapsed')
            feedback = st.text_input(label='feedback', value=target_reci_rec[5])
            categories = target_reci_rec[6]
            recently_cooked = st.date_input(label='recently_cooked', value=target_reci_rec[7])
            if st.button("수정"):
                recipe_operator.operate('update_where', 
                                        feature={'update': 'title', 'where': 'id'},
                                        value={'update': title, 'where': id_num})
                recipe_operator.operate('update_where', 
                                        feature={'update': 'main_ing', 'where': 'id'},
                                        value={'update': ', '.join(main_ing), 'where': id_num})
                recipe_operator.operate('update_where', 
                                        feature={'update': 'sub_ing', 'where': 'id'},
                                        value={'update': ', '.join(sub_ing), 'where': id_num})
                recipe_operator.operate('update_where', 
                                        feature={'update': 'recipe', 'where': 'id'},
                                        value={'update': recipe, 'where': id_num})    
                recipe_operator.operate('update_where', 
                                        feature={'update': 'feedback', 'where': 'id'},
                                        value={'update': feedback, 'where': id_num})
                recipe_operator.operate('update_where', 
                                        feature={'update': 'category', 'where': 'id'},
                                        value={'update': categories, 'where': id_num})
                recipe_operator.operate('update_where', 
                                        feature={'update': 'recently_cooked_on', 'where': 'id'},
                                        value={'update': recently_cooked, 'where': id_num})
                st.rerun()
            