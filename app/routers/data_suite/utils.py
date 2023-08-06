# query from string to data
import sqlparse
def get_db(query_string: str, Session, limit: int):
   

    parsed = sqlparse.parse(query_string)
    print(parsed[0].get_type())
    if not parsed:
        return 400, 'Invalid query'
    if parsed[0].get_type() != 'SELECT':

        return 400, 'Only support SELECT query'
    print(f"query_string: {query_string}")
    if limit != -1:
        limit_query_string = query_string.strip() + f" LIMIT {limit}"
    else:
        limit_query_string = query_string.strip()
    print(f"limit_query_string: {limit_query_string}")
    
    with Session() as session:
        result = session.execute(limit_query_string)
        column_names = result.keys()
        data = []
        for row in result:
            row_dict = {}
            for column_name in column_names:
                value = row[column_name]  
                row_dict[column_name] = value
            data.append(row_dict)
    
    return list(column_names), data

import pandas as pd
import pygsheets
def write_to_google_sheet(df,
                          sheet,
                          start_cell: str,
                          include_header: bool
                          ):
    # get data
    sheet.clear()
    sheet.set_dataframe(df, start=start_cell, copy_index=False, copy_head=include_header)
