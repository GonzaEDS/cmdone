from rich.table import Table
from helpers import split_type
from datatype import type_registry
from datetime import datetime
from titlecase import titlecase
from helpers import file_name_to_title, unstyle
from db import Db
from dao import Dao
import re


def checklist_table(data_list, sorting_key=None):

    dtypes_list = []
    columns_list=[]
    table_name, _ = data_list[0][0].split('_')
    title = f'{table_name}'
    table = Table(title=title.title(), show_header=True, header_style="bold magenta", border_style="grey53")
    for column in data_list[1]:
        c_title, dtype = split_type(column)
        columns_list.append(c_title)

        dtypes_list.append(dtype)
        header = c_title.title()
        justify = 'start' if dtype == '(@RATING5)' else 'center'
        table.add_column(header, justify=justify, vertical="middle")


    items_rows = data_list[2:]

    name_type_dict = (dict(zip(columns_list, dtypes_list)))
    if sorting_key:
        for column, dtype in name_type_dict.items():
                dtype_obj = type_registry[dtype]
                if sorting_key == column:
                    if dtype == "(@ID)":
                        items_rows = sorted(items_rows, key=lambda x: x[columns_list.index(sorting_key)])
                    elif dtype == "(@PRIORITY)":
                        priority_order= {'high':1,'medium':2,'low': 3}
                        items_rows = sorted(items_rows, key=lambda x: priority_order[x[columns_list.index(sorting_key)]])
                    else:
                        reverse = True if dtype_obj.marks_completion else False
                        items_rows = sorted(items_rows, key=lambda x: x[columns_list.index(sorting_key)], reverse=reverse)



    for item in items_rows:
        item_data = item.copy()
        item[0] = f'[dark_goldenrod]{item[0]}[/dark_goldenrod]'
        data_and_types = dict(zip(dtypes_list, item))
        item = [f'[light_steel_blue3]{value}[light_steel_blue3]' if value not in item[:2] else value for value in item]

        if '(@PRIORITY)' in dtypes_list:
            priority_type_obj = type_registry['(@PRIORITY)']
            priority_item = data_and_types['(@PRIORITY)']
            idx = item_data.index(priority_item)
            if all(elem not in item for elem in ['completed', 'done']):
                compare = priority_item.lower()
                color = priority_type_obj.colors_map[compare]
                styled_priority = f"[{color}]{unstyle(item[idx]).title()}[/{color}]"
                item[idx] = styled_priority
        if '(@SDATE)' in dtypes_list:
            sdate_item = data_and_types['(@SDATE)']
            sdate_idx = item_data.index(sdate_item)
            item[sdate_idx] = f'[light_steel_blue3]{item[sdate_idx]}[/light_steel_blue3]'

        if '(@FDATE)' in dtypes_list:
            try:
                fdate = data_and_types['(@FDATE)']
                datetime.strptime(fdate, r'%Y-%m-%d').date()
                item = [unstyle(value) for value in item]
                item = [f'[green]{value}[/green]' for value in item]
            except (KeyError, ValueError):
                pass
        if '(@RATING5)' in dtypes_list:
            try:
                rate = data_and_types['(@RATING5)']
                rate_index = item_data.index(rate)
                stars = int(rate)
                item[rate_index] = '⭐'*stars
                item =[unstyle(value) for value in item]
                item = [f'[green]{value}[/green]' for value in item]
            except (ValueError, KeyError):
                pass

        if '(@DUEDATE)' in dtypes_list:
            duedate_type_obj = type_registry['(@DUEDATE)']
            due_date_item = data_and_types['(@DUEDATE)']
            due_date_idx = item_data.index(due_date_item)


            valid_duedate, _ = duedate_type_obj.validate(due_date_item)
            if not valid_duedate and 'completed' not in item:
                expired_item = f'{due_date_item}\n[italic](reschedule)[/italic]'
                item = [unstyle(value) for value in item]
                item = [expired_item if current_field == due_date_item else current_field for current_field in item]
                item = [f'[red]{value}[/red]' for value in item]

            else:
                styled_due_date = f'[light_steel_blue3]{due_date_item}[/light_steel_blue3]'
                item[due_date_idx] = styled_due_date


        if '(@STATUS)' in dtypes_list:
            status_item = data_and_types['(@STATUS)']

            status_idx = item_data.index(status_item)
            item[status_idx] = re.sub(f'{status_item}', status_item.title(), item[status_idx])
            if status_item.lower() == 'completed':
                item =[unstyle(value) for value in item]
                item = [f'[green]{value}[/green]' for value in item]
            else:
                item[status_idx] = f'[light_steel_blue3]{item[status_idx]}[/light_steel_blue3]'



        if '(@DONE)' in dtypes_list:
            done_item = data_and_types['(@DONE)']
            done_index = item_data.index(done_item)
            if done_item:
                item = [unstyle(value) for value in item]
            if done_item == 'done':
                item[done_index] = '✓'
                item = [f'[green]{value}[/green]' for value in item]
            if done_item == 'failed':
                item[done_index] = '✗'
                item = [f'[red]{value}[/red]' for value in item]

        table.add_row(*item, end_section=True)

    return table


def templates_table(data_list):
    table = Table(title=data_list[0][0].title(), show_header=True, header_style="bold magenta", border_style="grey53")
    for header_title in data_list[1]:
        justify = "center" if header_title == "columns" else "start"
        table.add_column(titlecase(header_title), justify=justify)

    max_len_cols_col = max(list(map(lambda x:len(re.sub(r'-', ' - ' ,re.sub(r'\(@\w+\)', '', x[2]))), data_list[2:])))

    for item in data_list[2:]:
        row = item.copy()
        row[0] = f'[dark_goldenrod]{row[0]}[/dark_goldenrod]'
        row[1] = titlecase(row[1])
        row[2] = re.sub(r'\(@\w+\)', '', row[2])

        num_of_cols = len(row[2].split('-'))

        mlcc_by_noc = max_len_cols_col//num_of_cols

        cols_listed = row[2].split("-")



        row[2] = list(map(lambda x: ' '*((mlcc_by_noc-(len(x)+3))//2)+x+' '*((mlcc_by_noc-(len(x)+3))//2), cols_listed))
        styled_columns = [f'[light_steel_blue3]{el.title()}[/light_steel_blue3]' for el in row[2]]
        row[2] = ' | '.join(styled_columns)
        table.add_row(*row, end_section=True)
    return table

def view_checklists_table(files):
    title = 'My Checklists'
    table = Table(title=title.title(), show_header=True, header_style="bold magenta", border_style="grey53")
    for header in [' n° ', 'Name', 'Class']:
        justify = "center" if header == ' n° ' else "left"
        table.add_column(header, justify=justify)

    for index, file in enumerate(files, start=1):
        checklist_dao = Dao(Db(f'./db/{file}'))
        checklist_title = file_name_to_title(file)
        checklist_type = f'[light_steel_blue3]{titlecase(checklist_dao.get_first_row().split("_")[1])}[/light_steel_blue3]'

        table.add_row(f'[dark_goldenrod]{index}[/dark_goldenrod]', checklist_title, checklist_type, end_section=True)
    return table


def data_types_descriptions(type_registry):
    type_registry.pop('(@ID)', None)
    types_of_columns = "[gold3][italic]Types for Columns[/italic][/gold3]\n\n"
    marks_completion_c = "\n[gold3][italic]Columns that Mark Completion[/italic][/gold3]\n\n"

    for type_name, type_obj in type_registry.items():
        dtype = re.search(r"\(@(\w+)\)", type_name).group(1)

        description = f'[blue]●[/blue] [sky_blue1][bold]{dtype}[/bold][/sky_blue1]: {type_obj.long_desc}'
        description += f' [gray3]Default Name:[/gray3] [orchid]{type_obj.default_col_name.title() }[/orchid]\n\n' if type_obj.default_col_name else '\n\n'

        if not type_obj.marks_completion:
            types_of_columns += description
        else:
            marks_completion_c += description

    return f"{types_of_columns+marks_completion_c}"


def new_template_table(new_template, headers):
    table = Table(title='new template'.title(), show_header=True, header_style="bold magenta", border_style="grey53")
    for header_title in headers:
        table.add_column(header_title.capitalize(), justify="center")

    row = new_template.copy()
    row[0] = f'[dark_goldenrod]{row[0]}[/dark_goldenrod]'
    row[1] = row[1].title()
    row[2] = " | ".join(new_template[2].split("-"))
    row[2] = re.sub(r'\(@\w+\)', '', row[2]).title()
    table.add_row(*row, end_section=True)

    return table


def info_page(pages_map):
    table = Table(show_header=True, header_style="bold magenta", border_style="grey53")
    for header in ["Go to...", "Command"]:
        table.add_column(header)
    for item in pages_map.items():
        page, command = item
        page = f'[sky_blue1]{page}[/sky_blue1]'
        command = f'[bold]{command}[/bold]'
        table.add_row(page, command, end_section=True)
    return table
