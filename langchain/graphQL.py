"""SQLAlchemy wrapper around a database."""
from __future__ import annotations

from typing import Iterable, List, Optional

import requests
import json


class GraphQL:

    def __init__(
        self,
        graphql_url: str = None
    ):

        self.graphql_url = graphql_url

    @property
    def dialect(self) -> str:
        """Return string representation of dialect to use."""
        return

    def get_table_names(self) -> Iterable[str]:
        """Get names of tables available."""
        return

    @property
    def table_info(self) -> str:
        """Information about all tables in the database."""
        return

    def get_table_info(self) -> str:
        """Get information about specified tables.

        Follows best practices as specified in: Rajkumar et al, 2022
        (https://arxiv.org/abs/2204.00498)

        If `sample_rows_in_table_info`, the specified number of sample rows will be
        appended to each table description. This can increase performance as
        demonstrated in the paper.
        """
        return


    def run(self, command: str) -> str:
        """Execute a SQL command and return a string representing the results.

        If the statement returns rows, a string of the results is returned.
        If the statement returns no rows, an empty string is returned.
        """
        base_url = self.graphql_url

        # Perform POST request and check status code of response
        # This handles the cases where the Open Targets API is down or our query is invalid
        try:
            response = requests.post(base_url, json={"query": command})
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)

        # Transform API response from JSON into Python dictionary and print in console
        api_response = json.loads(response.text)

        return api_response
