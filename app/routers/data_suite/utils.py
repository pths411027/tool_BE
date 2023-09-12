from datetime import datetime, timedelta

import sqlparse


def get_db(query_string: str, Session, limit: int):
    print(f"流程: {query_string}")
    parsed = sqlparse.parse(query_string)
    print(parsed)
    # print(parsed[0].get_type())
    if not parsed:
        return 400, "Invalid query"
    if parsed[0].get_type() != "SELECT":
        return 400, "Only support SELECT query"
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
                print(f"{column_name}值:{value}")
                row_dict[column_name] = str(value)
            data.append(row_dict)

    return list(column_names), data


def write_to_google_sheet(df, sheet, start_cell: str, include_header: bool):
    # get data
    sheet.clear()
    sheet.set_dataframe(
        df, start=start_cell, copy_index=False, copy_head=include_header
    )


def next_runtime_calculator(active, frequency):
    if active != "active":
        return "Freeze"
    fre, timing = frequency.split(",")
    hour = int(timing.strip())
    now = datetime.now()

    if fre == "daily":
        expected_runtime = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        if expected_runtime < now:
            return str(expected_runtime + timedelta(days=1))
        else:
            return str(expected_runtime)
    else:
        return now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)


def unix_time_transformer(time):
    if time is None:
        return "未執行"
    else:
        return datetime.fromtimestamp(time).strftime("%Y-%m-%d %H:%M:%S")
