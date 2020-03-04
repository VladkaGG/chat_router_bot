import psycopg2
import logging

from table_create import create_tables
from psycopg2.extras import DictCursor, execute_values
from psycopg2 import sql, OperationalError


class DbConnection:
    def __init__(self):
        self.conn = None

    def __enter__(self):
        try:
            self.conn = psycopg2.connect(
                database="roma",
                user="roma",
                password="roma",
                host="127.0.0.1",
                port="5432"
            )
        except OperationalError as e:
            logging.exception("DbConnection failed")
            return self.conn
        self.cursor = self.conn.cursor(cursor_factory=DictCursor)
        return self.cursor

    def __exit__(self, exp_type, exp_value, exp_tr):
        if exp_type and self.conn:
            logging.error(f"Exception occurred\n{exp_tr}\n{exp_type}: {exp_value}")
            self.conn.close()
            return True
        elif exp_type and not self.conn:
            logging.error(f"Exception occurred\n{exp_tr}\n{exp_type}: {exp_value}")
            return True
        self.conn.commit()
        self.conn.close()


class DbModel:
    """Примеры работы функций DbModel приведены в конце"""
    def __init__(self):
        create_tables(DbConnection())
        logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s] %(message)s', level=logging.DEBUG,
                            filename=u'mylog.log')

    def select_all_data(self, table_name):
        """Функция для вывода всех данных из одной таблицы, имя которой передается в table_name"""
        with DbConnection() as cursor:
            query = sql.SQL('SELECT * FROM {}').format(
                sql.Identifier(table_name))
            cursor.execute(query)
            return cursor.fetchall()

    def select_some_data(self, table_name, column, value):
        """Функция для вывода всех данных с конкретным значением
         из одной таблицы, имя которой передается в table_name, название колонки в column,
         а значение колонки в value"""
        with DbConnection() as cursor:
            query = sql.SQL('SELECT * FROM {} WHERE {}=%s').format(
                sql.Identifier(table_name),
                sql.Identifier(column))
            cursor.execute(query, (value,))
            return cursor.fetchall()

    def insert_data(self, table_name, columns, values):
        """Функция для вставки данных в таблицу, имя таблицы передается в table_name,
        в columns передается любая коллекция из названий колонок куда необходимо вставить данные,
        в values передается двумерный массив, в каждом вложенном массиве значения для вставки в заданные колонки"""
        with DbConnection() as cursor:
            query = sql.SQL('INSERT INTO {} ({}) VALUES %s').format(
                sql.Identifier(table_name),
                sql.SQL(',').join(map(sql.Identifier, columns)))
            execute_values(cursor, query, values)

    def delete_data(self, table_name, column, value):
        """Функция для удаления данных из таблицы table_name, где значения колонки column равно value"""
        with DbConnection() as cursor:
            query = sql.SQL('DELETE FROM {} WHERE {}=%s').format(
                sql.Identifier(table_name),
                sql.Identifier(column))
            cursor.execute(query, (value,))

    def update_data(self, table_name, change_column, change_value, column, value):
        """Функция для изменения данных в таблице table_name, в change_column задается столбец в котором надо
        изменить значение, в change_value измененное значение. В column и value передаем колонку и значение,
        в которых надо поменять данные"""
        with DbConnection() as cursor:
            query = sql.SQL('UPDATE {} SET {}=%s WHERE {}=%s').format(
                sql.Identifier(table_name),
                sql.Identifier(change_column),
                sql.Identifier(column))
            cursor.execute(query, (change_value, value))


if __name__ == '__main__':
    Model = DbModel()  # Лучше передавать все кортежах, так как они не изменяемые
    list_of_values = [('First',), ('Second',)]  # Для передачи одного значения [('First',)]
    Model.insert_data('Groups', ('Name',), list_of_values)  # Для передачи нескольких колонок ('Name', 'Id')
    Model.delete_data('Groups', 'Name', 'First')
    Model.update_data('Groups', 'Name', 'Good', 'Name', 'Third')
    print(Model.select_all_data('Groups'))