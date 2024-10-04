from database.connection import create_connection, close_connection
import pymysql
import streamlit as st

class TableOperator():
    def __init__(self, table):
        self.table = table
        self.op = {
                'create_one': self.op_create_one,
                'read_all': self.op_read_all,
                'read_where': self.op_read_where,
                'update_where': self.op_update_where,
                'get_cols': self.get_columns
                }
    
    def operate(self, op_key, feature=None, value=None):
        # execution: 원하는 처리를 하기 위한 함수, 'op_---(connection)'형태
        connection = create_connection()
        
        try:
            # print(">>>HERE", op_key)
            result = self.op[op_key](connection, feature, value)
        except pymysql.MySQLError as e:
            hypen = 15
            code, msg = e.args
            print("-"*hypen, "ERROR", "-"*hypen)
            print(f">> Error Code: {code}\n>> Error MSG: {msg}\n>> in TABLE: {self.table}")
            print("-"*(2 * hypen + 5))
            result = code
        finally:
            connection.cursor().close()
            close_connection(connection)
        return result

    def op_read_all(self, connection, feature, value):
        # operator.operate(op_key)
        cursor = connection.cursor()
        query = "SELECT * FROM %s" % self.table
        cursor.execute(query)
        results = cursor.fetchall()
        return results
    
    def op_read_where(self, connection, features, values):
        # op_key='read_where'
        # feature과 value를 list로
        # operator.operate(op_key, feature, value)
        cursor = connection.cursor()
        conditions = []
        for i in range(len(features)):
            # print(">>> FEATURE TO READ: ", values[i])
            conditions.append(f"{features[i]}='{values[i]}'")
        condition_query = " AND ".join(conditions)
        # print(">>>>CONDITIOM QUERY",condition_query)
        query = "SELECT * FROM %s WHERE %s" %(self.table, condition_query)
        cursor.execute(query)
        results = cursor.fetchall()
        # print(">>>>>>>>>>>", results)
        if results:
            return results
        else:
            print("결과없음")
            return 'apple'

    def op_create_one(self, connection, feature, value):
        # op_key: 'create_one', value: list, feature: id제외 나머지
        # operator.operate(op_key, value)
        cursor = connection.cursor()
        feature_list = list(self.get_columns(connection, ).keys())[1:]
        feature_query = ", ".join(feature_list)
        value_query = "\'" + "', '".join(value) + "\'"
        query = f"""
        INSERT INTO {self.table} ({feature_query})
        VALUES ({value_query})
        """
        cursor.execute(query)
        connection.commit()
        return None
    
    def op_update_where(self, connection, feature, value):
        # feature = {'update': feat1, 'where': feat2}
        # value = {'update': val1, 'where': val2}
        cursor = connection.cursor()
        query = f"""UPDATE {self.table} 
                    SET {feature['update']}='{value['update']}'
                    WHERE {feature['where']}='{value['where']}'"""
        cursor.execute(query)
        connection.commit()
    
    def get_columns(self, connection, feature=None, value=None):
        columns = {}
        t_cur = connection.cursor(pymysql.cursors.DictCursor)
        t_cur.execute(f"SHOW COLUMNS from {self.table}")
        fetched = t_cur.fetchall()
        for col in fetched:
            columns[col['Field']] = col['Type']
        t_cur.close()
        return columns




def save_symptom_to_db(child_name, symptom, description=""):
    # MySQL DB에 증상 데이터 저장
    connection = create_connection()
    cursor = connection.cursor()
    
    query = """
    INSERT INTO symptom_reports (child_name, symptom, description) 
    VALUES (%s, %s, %s)
    """
    values = (child_name, symptom, description)
    
    try:
        cursor.execute(query, values)
        connection.commit()
        # print(">> 증상이 데이터베이스에 성공적으로 저장되었습니다. (database.operations.save_symptom_to_db)")
    except pymysql.MySQLError as e:
        print(f"Failed to insert record into MySQL table {e} (database.operations.save_symptom_to_db)")
    finally:
        cursor.close()
        close_connection(connection)

