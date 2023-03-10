"""SQLAlchemy wrapper around a database."""
from __future__ import annotations

from typing import Iterable, List, Optional

import psycopg2
import subprocess


class PostgreSQL:

    def __init__(
        self,
        schema: Optional[str] = None,
        user: str = None,
        password: str = None,
        host: str = None,
        port: str = 5432,
        database: str = None,
        ignore_tables: Optional[List[str]] = None,
        include_tables: Optional[List[str]] = None,
        sample_rows_in_table_info: int = 3,
    ):
        """Create engine from database URI."""
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database
        self.available_tables = set()
        self._schema = schema
        if include_tables and ignore_tables:
            raise ValueError("Cannot specify both include_tables and ignore_tables")

        self._include_tables = set(include_tables) if include_tables else set()

        with psycopg2.connect(user=self.user, password=self.password, host=self.host, port=self.port,
                              database=self.database) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{self._schema}'")
            for table in cursor.fetchall():
                self.available_tables.update(table)

        if self._include_tables:
            missing_tables = self._include_tables - self.available_tables
            if missing_tables:
                raise ValueError(
                    f"include_tables {missing_tables} not found in database"
                )
        self._ignore_tables = set(ignore_tables) if ignore_tables else set()
        if self._ignore_tables:
            missing_tables = self._ignore_tables - self.available_tables
            if missing_tables:
                raise ValueError(
                    f"ignore_tables {missing_tables} not found in database"
                )

        if not isinstance(sample_rows_in_table_info, int):
            raise TypeError("sample_rows_in_table_info must be an integer")

        self._sample_rows_in_table_info = sample_rows_in_table_info

    @property
    def dialect(self) -> str:
        """Return string representation of dialect to use."""
        return "postgresql"

    def get_table_names(self) -> Iterable[str]:
        """Get names of tables available."""
        if self._include_tables:
            return self._include_tables
        return self.available_tables - self._ignore_tables

    @property
    def table_info(self) -> str:
        """Information about all tables in the database."""
        return self.get_table_info()

    def get_table_info(self, table_names: Optional[List[str]] = None) -> str:
        """Get information about specified tables.

        Follows best practices as specified in: Rajkumar et al, 2022
        (https://arxiv.org/abs/2204.00498)

        If `sample_rows_in_table_info`, the specified number of sample rows will be
        appended to each table description. This can increase performance as
        demonstrated in the paper.
        """
        all_table_names = self.get_table_names()
        if table_names is not None:
            missing_tables = set(table_names).difference(all_table_names)
            if missing_tables:
                raise ValueError(f"table_names {missing_tables} not found in database")
            all_table_names = table_names

        tables = []
        for table in all_table_names:
            # add create table command
            ps = subprocess.Popen(('pg_dump', '-h',  f'{self.host}', '-U', f'{self.user}', f'--table={self._schema}.{table}',
                                   '--schema-only', f'{self.database}'), stdout=subprocess.PIPE)
            create_table = subprocess.check_output(('awk', '/CREATE TABLE/,/;/'), stdin=ps.stdout)

            if self._sample_rows_in_table_info:
                # build the select command
                command = f"SELECT * FROM {table} LIMIT {self._sample_rows_in_table_info}"

                # save the command in string format
                select_star = (
                    f"SELECT * FROM {table} LIMIT "
                    f"{self._sample_rows_in_table_info}"
                )

                # save the columns in string format
                with psycopg2.connect(user=self.user, password=self.password, host=self.host, port=self.port,
                                      database=self.database) as conn:
                    col_cmd = f"SELECT column_name FROM information_schema.columns "\
                              f"WHERE table_schema = '{self._schema}' AND table_name = '{table}'"
                    cursor = conn.cursor()
                    cursor.execute(col_cmd)
                    columns = cursor.fetchall()
                    columns = [row[0] for row in columns]
                    # shorten values in the sample rows
                    columns_str = " ".join([col for col in columns])

                try:
                    # get the sample rows
                    with psycopg2.connect(user=self.user, password=self.password, host=self.host, port=self.port,
                                          database=self.database) as conn:
                        cursor = conn.cursor()
                        cursor.execute(command)
                        sample_rows = cursor.fetchall()
                        # shorten values in the sample rows
                        sample_rows = list(
                            map(lambda ls: [str(i)[:100] for i in ls], sample_rows)
                        )
                    # save the sample rows in string format
                    sample_rows_str = "\n".join([" ".join(row) for row in sample_rows])
                # in some dialects when there are no rows in the table a
                # 'ProgrammingError' is returned
                except:
                    sample_rows_str = ""

                # build final info for table
                tables.append(
                    create_table.decode(encoding='utf_8')
                    + select_star
                    + ";\n"
                    + sample_rows_str
                    + "\n"
                    + columns_str
                )

            else:
                tables.append(create_table)

        final_str = "\n\n".join(tables)
        return final_str

    def run(self, command: str, fetch: str = "all") -> str:
        """Execute a SQL command and return a string representing the results.

        If the statement returns rows, a string of the results is returned.
        If the statement returns no rows, an empty string is returned.
        """
        with psycopg2.connect(user=self.user, password=self.password, host=self.host, port=self.port,
                              database=self.database) as connection:
            cursor = connection.cursor()
            if self._schema is not None:
                cursor.execute(f"SET search_path TO {self._schema}")
            cursor.execute(command)
            if cursor is not None:
                if fetch == "all":
                    result = cursor.fetchall()
                elif fetch == "one":
                    result = cursor.fetchone()[0]
                else:
                    raise ValueError("Fetch parameter must be either 'one' or 'all'")
                return str(result)
        return ""
