# query from string to data
import sqlparse
def get_db(query_string: str, Session, limit: int):
    #print(query_string)
    print(f"query_string: {query_string}")

    parsed = sqlparse.parse(query_string)
    print(parsed[0].get_type())
    if not parsed:
        return 400, 'Invalid query'
    if parsed[0].get_type() != 'SELECT':

        return 400, 'Only support SELECT query'
    
    with Session() as session:
        result = session.execute(query_string)
        column_names = result.keys()
        data = []
        for row in result:
            row_dict = {}
            for column_name in column_names:
                value = row[column_name]  
                row_dict[column_name] = value
            data.append(row_dict)
    
    return list(column_names), data