from .utils import get_to_set, normalize
from typing import List, Dict, Optional, Any, Callable, Literal, Tuple

import psycopg2

from time import sleep
from datetime import datetime

from core.settings import settings


def connect(tentative: int = 10) -> psycopg2.extensions.connection:
    try:
        host = settings.POSTGRES_SERVER
        user = settings.POSTGRES_USER
        password = settings.POSTGRES_PASSWORD
        port = settings.DB_PORT or 5432
        dbname = "postgres"
        conn_string = f"host={host} user={user} dbname={dbname} password={password} port={port}"
        return psycopg2.connect(conn_string)
    except Exception as e:
        if tentative > 0:
            sleep(3)
            return connect(tentative - 1)
        else:
            raise e


class Connection:
    def __init__(self):
        self.conn = connect()

    def _cursor(self, try_times=5) -> psycopg2.extensions.cursor:
        if self.is_alive():
            return self.conn.cursor()
        elif try_times > 0:
            self.reconnect()
            return self._cursor()
        raise ConnectionRefusedError("Error getting cursor, connection is dead")

    def is_alive(self) -> bool:
        try:
            self.conn.cursor().execute("select 1")
            return True
        except Exception:
            return False

    def reconnect(self, try_times=5) -> None:
        try:
            self.conn = connect()
            if not self.is_alive() and try_times > 0:
                self.reconnect(try_times - 1)
        except Exception:
            if try_times > 0:
                sleep(1)
                self.reconnect(try_times - 1)

    def execute(self, query: str, *params) -> Optional[List[Dict[str, Any]]]:
        try:
            result = ""
            cursor = self._cursor()
            cursor.execute(query, params)
            self.commit()
            try:
                result = cursor.fetchall()
            except Exception:
                result = None
            cursor.close()
            return result
        except Exception as e:
            self.rollback()
            raise e

    def execute_raw(self, query: str, trys: int = 5) -> Optional[List[Dict[str, Any]]]:
        try:
            result = ""
            cursor = self._cursor()
            cursor.execute(query)
            self.commit()
            try:
                result = cursor.fetchall()
            except Exception:
                result = None
            cursor.close()
            return result
        except Exception as e:
            try:
                self.rollback()
                self.commit()
            except Exception:
                pass
            if trys > 0:
                return self.execute(query, trys - 1)
            else:
                raise e

    def close(self):
        self.conn.close()

    def insert_dict(
        self, table: str, data: Dict[str, Any], key: str = None
    ) -> Optional[int]:
        try:
            cursor = self._cursor()
            to_return = None
            columns = '", "'.join(data.keys())
            values = ", ".join(normalize(data.values()))
            query = 'insert into {0} ("{1}") values ({2})'.format(
                table, columns, values
            )
            if key:
                query += f" returning {key}"
                cursor.execute(query)
                to_return = cursor.fetchone()[0]
            else:
                cursor.execute(query)
            self.commit()
            cursor.close()
            return to_return
        except Exception as e:
            self.rollback()
            self.close()
            raise e

    def insert_list(self, table: str, data: List[Dict[str, Any]]) -> None:
        try:
            columns = data[0].keys()
            values = []
            for row in data:
                for value in row.values():
                    values.append(value)
                self.insert(table, columns, values)
                values = []

        except Exception as e:
            raise e

    def insert(self, table: str, columns: List[str], values: List[str]) -> None:
        try:
            cursor = self._cursor()
            columns = '","'.join(columns)
            values = ", ".join(normalize(values))
            query = 'insert into {0} ("{1}") values ({2})'.format(
                table, columns, values
            )
            cursor.execute(query)
            self.commit()
            cursor.close()
        except Exception as e:
            self.rollback()
            self.close()
            raise e

    def insert_or_update(
        self, table: str, data: Dict[str, Any], primary_key: List[str]
    ) -> None:
        try:
            cursor = self._cursor()
            columns = '", "'.join(data.keys())
            values = ", ".join(normalize(data.values()))
            to_set = get_to_set(data, primary_key)
            primary_key = '", "'.join(primary_key)
            query = """
                    insert into {0} ("{1}") values ({2}) on conflict ("{3}") do update set {4}
                """.format(
                table, columns, values, primary_key, to_set
            )
            cursor.execute(query)
            self.commit()
            cursor.close()
        except Exception as e:
            self.rollback()
            self.close()
            raise e

    def delete(self, table: str, data: Dict[str, Any] = {}) -> None:
        try:
            cursor = self._cursor()
            where = []
            for k, v in data.items():
                if isinstance(v, list):
                    where.append('"{0}" in ({1})'.format(k, ", ".join(normalize(v))))
                else:
                    where.append('"{0}" = {1}'.format(k, normalize([v])[0]))
            where = " and ".join(where)
            query = "delete from {0} where {1}".format(table, where)
            cursor.execute(query)
            self.commit()
            cursor.close()
        except Exception as e:
            self.rollback()
            self.close()
            raise e

    def update(
        self, table: str, data: Dict[str, Any], where_dict: Dict[str, Any]
    ) -> None:
        try:
            cursor = self._cursor()
            to_set = get_to_set(data)
            where = []
            for k, v in where_dict.items():
                if isinstance(v, list):
                    where.append('"{0}" in ({1})'.format(k, ", ".join(normalize(v))))
                else:
                    where.append('"{0}" = {1}'.format(k, normalize([v])[0]))
            where = " and ".join(where)
            query = "update {0} set {1} where {2}".format(table, to_set, where)
            cursor.execute(query)
            self.commit()
            cursor.close()
        except Exception as e:
            self.rollback()
            self.close()
            raise e

    def select_dict(self, query: str, *params) -> Optional[List[Dict[str, Any]]]:
        try:
            cursor = self._cursor()
            cursor.execute(query, params)
            columns = [column[0] for column in cursor.description]
            prevent_datetime = lambda arr: [
                x if not isinstance(x, datetime) else x.strftime("%Y-%m-%d %H:%M:%S")
                for x in arr
            ]
            result = [
                dict(zip(columns, prevent_datetime(row))) for row in cursor.fetchall()
            ]
            cursor.close()
            return result
        except Exception as e:
            self.rollback()
            self.close()
            raise e

    def select(
        self,
        table: str,
        where: dict,
        order_by: Optional[Tuple[str, Literal["asc", "desc"]]] = None,
        clause: Optional[Literal["and", "or"]] = "and",
    ) -> Optional[List[Dict[str, Any]]]:
        query = f"SELECT * FROM {table} WHERE {self.get_where(where, clause=clause)} {self.get_order_by(order_by)}"
        return self.select_dict(query)

    def commit(self) -> None:
        self.conn.commit()

    def rollback(self) -> None:
        self.conn.rollback()

    @staticmethod
    def get_where(
        where_dict: Dict[str, str], clause: Literal["and", "or"] = "and"
    ) -> str:
        where = []
        for k, v in where_dict.items():
            if isinstance(v, list):
                where.append('"{0}" in ({1})'.format(k, ", ".join(normalize(v))))
            else:
                where.append('"{0}" = {1}'.format(k, normalize([v])[0]))
        where = f" {clause} ".join(where)
        return where

    @staticmethod
    def get_order_by(order_by: Optional[Tuple[str, Literal["asc", "desc"]]]) -> str:
        if not order_by:
            return ""

        return f'ORDER BY "{order_by[0]}" {order_by[1]}'