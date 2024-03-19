import sys
import os
from rich.layout import Layout
from rich.panel import Panel
from rich.align import Align
from rich.table import Table
from rich.padding import Padding
from rich.console import Console, Group
from rich.prompt import Prompt
from rich.box import HORIZONTALS
from rich.text import Text
from helpers import list_files
from pyfiglet import Figlet
from ascii.ascii import big_title
from db import Db
from dao import Dao
from helpers import split_type
from titlecase import titlecase
from datatype import type_registry, TextType, OptionsType
from tables_rendering import checklist_table, templates_table, view_checklists_table, data_types_descriptions, new_template_table, info_page
import re

# -------------------------------------------------------------------------------------------------------------------
#################################################### PAGES #########################################################
# -------------------------------------------------------------------------------------------------------------------

class Page:
    def __init__(self, height, options, top_content):
        self.height = height
        self.options = options
        self.top_content = top_content
        self.layout = Layout()
        self.console = Console(height=self.height+3)
        self.option_panels = [Align.center(Panel(Text(option)), vertical="middle", style="blue") for option in options]

    def display(self):

        self.layout.split_column(
            Layout(self.top_content, name="top", size=self.height),
            Layout(name="bottom", size=4),
        )

        grid = Table.grid(expand=True)
        grid.add_row(*self.option_panels)
        self.layout["bottom"].update(Padding(grid, (0, 15)))

        self.console.print(Align(Panel(self.layout, box=HORIZONTALS, padding=(3, 0, 2, 0)), vertical="middle"))

    def handle_input(self):

        choice = Prompt.ask("Select an [blue]option[/blue] to continue").lower()
        if global_choice := self.global_nav(choice):
            return global_choice
        else:
            return self.handle_page_input(choice)

    # Handle global navigation options
    def global_nav(self, choice):

        match choice:
            case 'home':
                return HomePage()
            case 'view':
                return ViewChecklists()
            case 'new checklist':
                return CreateChecklist()
            case 'new template':
                return CreateNewTemplate()
            case 'info':
                return Info()
            case _:
                return None

    def handle_page_input(self):
        # To be implemented by subclasses for specific input handling
        raise NotImplementedError


# HOME PAGE
class HomePage(Page):
    def __init__(self):
        super().__init__(height=17,
                         options=["View my Checklists [V]", "Create New Checklist [N]", "Additional Commands [C]"],
                         top_content=Align.center(big_title(), vertical="middle")
                         )

    def handle_page_input(self, choice):

        if choice == 'v':
            no_checklists = len(list_files('./db')) < 1

            if no_checklists:
                return NoChecklists()
            else:
                return ViewChecklists()

        elif choice == 'n':
            return CreateChecklist()
        elif choice == 'c':
            return Info()
        else:
            return self


# INFO PAGE
class Info(Page):
    def __init__(self):
        self.pages_map = {"Home Page": "home", "View/Select checklists": "view",
                          "Create New Checklist": "new checklist", "Create New Template": "new template", "Additional Commands (this page)": "info"}
        self.init_top()
        super().__init__(height=len(self.pages_map)*3+9,
                         options=["Go back to HomePage [H]"],
                         top_content=self.top_content
                         )

    def init_top(self):
        from rich.text import Text
        about_navigation = '[blue]●[/blue] Beside the [blue]options[/blue] listed at the bottom of each page, you can go from any page to any other page using the following commands:'
        about_cancel = '[blue]●[/blue] You can enter \'[bold]cancel[/bold]\' to break out of an [blue]option[/blue] that prompts you for further specifications.\n'
        about_sort = '[blue]●[/blue] When inside a checklist, beside the [blue]sort option [S][/blue], you can enter [bold]\'sort --[/bold]column name\' to directly sort the table by the specified column.'

        grid = Table.grid(expand=False)
        grid.add_column(width=100)
        grid.add_row(Text.from_markup(about_navigation, justify="left"))
        grid.add_row(Align.center(Padding(info_page(self.pages_map), (1, 0, 2, 0)), vertical="middle"))
        grid.add_row(Text.from_markup(about_cancel, justify="left"))
        grid.add_row(Text.from_markup(about_sort, justify="left"))
        self.top_content = Align.center(grid)

    def handle_page_input(self, choice):

        if choice == 'h':
            return HomePage()
        else:
            return self


# VIEW CHECKLISTS PAGE
class ViewChecklists(Page):

    def __init__(self):
        self.path = './db'
        self.files = list_files(self.path)
        self.files_len = len(self.files)
        self.templates_dao = Dao(Db(f'{self.path}/templates.csv'))

        super().__init__(height=(self.files_len+2) * 2 + 4,
                         options=[f"Select a checklist [n°]", "Delete a checklist [D]", "Return to HomePage [H]"],
                         top_content=Align.center(Panel(view_checklists_table(self.files), border_style="grey53")))


    def handle_page_input(self, choice):

        if choice == 'h':
            return HomePage()

        if choice == 'd':
            ###################
            prompt = Text.assemble(Text.from_markup('Select checklist to [red]Delete[/red] '), Text("[n°]", style="magenta"))
            #prompt = Text.from_markup('Select checklist to red]Delete[/red]')
            num_to_delete = Prompt.ask(prompt)
            if num_to_delete == 'cancel':
                return self
            try:
                while True:
                    num_to_delete = int(num_to_delete)
                    if num_to_delete <= self.files_len:
                        confirmation = Prompt.ask(
                            f'Are you sure you want to [red]Delete [italic]{file_name_to_title(self.files[num_to_delete -1])}[/italic] permanently?[/red] y/n').lower()
                        if confirmation in ['y', 'yes']:
                            os.remove(f'./db/{self.files[num_to_delete-1]}')
                            no_checklists = len(list_files(self.path)) < 1
                            if no_checklists:
                                return NoChecklists()
                            return ViewChecklists()
                        elif confirmation in ['n', 'no']:
                            return self
                        elif confirmation == "cancel":
                            break
                        else:
                            continue
                    return self
            except ValueError:
                return self
        # try:
        if int(choice) <= self.files_len:
            db = Db(f'./db/{self.files[int(choice)-1]}')
            return ChecklistPage(db)
        # except ValueError:
        #     return self
        return self


# NO CHECKLISTS PAGE
class NoChecklists(Page):
    def __init__(self):
        self.figlet = Figlet()
        self.figlet.setFont(font='ansi_shadow')

        super().__init__(height=21,
                         options=["Create New Checklist [N]", "Return to HomePage [H]"],
                         top_content=Align.center(self.figlet.renderText("No checklists yet!"), vertical="middle"))

    def handle_page_input(self, choice):
        if choice == 'h':
            return HomePage()
        if choice == 'n':
            return CreateChecklist()
        else:
            return self


# CREATE CHECKLISTS PAGE
class CreateChecklist(Page):
    def __init__(self):
        self.db = Db('./db/templates.csv')
        self.templates_dao = Dao(self.db)
        self.data_list = self.templates_dao.get_all()

        super().__init__(height=len(self.data_list) * 2 + 4,
                         options=["New Checklist from Template [TID]", "Create New Template [T]", "Delete Template [D]"],
                         top_content=Align.center(Panel(templates_table(self.data_list)))
                         )

    def handle_page_input(self, choice):

        if choice == 't':
            return CreateNewTemplate()
        if choice == 'd':
            while True:
                tid = Prompt.ask("Choose a template to [red]Delete[/red][Id]")
                if tid == "cancel":
                    return self
                elif tid in self.templates_dao.get_ids():
                    selected_template = self.templates_dao.get_item(tid)[1]
                    while True:
                        confirmation = Prompt.ask(
                            f"Are you sure you want to [red]Delete [bold italic]{titlecase(selected_template)}[/bold italic][/red] permanently? y/n").lower()
                        if confirmation in ["y", "yes"]:
                            self.templates_dao.delete_item(tid)
                            return CreateChecklist()
                        elif confirmation in ["n", "no", "cancel"]:
                            return self
                        else:
                            error_msg_retry("Not a valid answer")
                            continue
                else:
                    error_msg_retry("Not a valid ID")

        elif choice.upper() in self.templates_dao.get_ids():
            new_checklist = Prompt.ask("Choose a [bold magenta]Name[/bold magenta] for your checklist").lower()
            slug = "_".join(new_checklist.split(' '))
            new_db = Db(f'./db/{slug}.csv')
            selected_template = self.templates_dao.get_item(choice.upper())
            template_name = selected_template[1]
            columns = selected_template[2].split("-")
            columns.insert(0, 'id(@ID)')

            new_db.db_write([[f'{new_checklist}_{template_name}'], columns])
            return ChecklistPage(new_db)

        else:
            error_msg_retry('Invalid choice')
            return self


# NEW TEMPLATE
class CreateNewTemplate(Page):
    def __init__(self):
        self.db = Db('./db/templates.csv')
        self.templates_dao = Dao(self.db)
        self.new_id = self.templates_dao.new_template_id()
        self.new_template = [self.new_id, "", ""]
        self.user_columns = []
        self.user_types = []
        self.contains_completion_c = False
        self.data_types_desc = data_types_descriptions(type_registry)
        self.update_top_content()
        super().__init__(height=(3*3)+len(type_registry)*3+3,
                         options=["Edit Template's Name [N]", "Add New Column [C]", "Save Template [S]"],
                         top_content=self.top_content
                         )

    def update_top_content(self):
        self.top_content = Group(
            Align.center(self.data_types_desc, width=124),
            Align.center(Panel(new_template_table(self.new_template, self.templates_dao.get_columns()), border_style="grey53"))
        )

    def handle_page_input(self, choice):

        if choice == 'n':
            while True:
                template_name = Prompt.ask("Select a [bold magenta]Name[/bold magenta] for your template").lower()
                if len(template_name) < 86:
                    try:
                        self.new_template[1] = template_name
                        self.update_top_content()
                    except IndexError:
                        self.new_template.append(template_name)
                    return self

        if choice == 'c':
            while True:
                column_type = Prompt.ask("Select a [bold sky_blue1]Type[/bold sky_blue1] for the new column").upper()

                try:
                    formated_type = f'(@{column_type})'
                    selected_type = type_registry[formated_type]
                except (KeyError):
                    error_msg_retry('Choose a valid [bold sky_blue1]Type[/bold sky_blue1] from the list above')
                    continue
                if selected_type.marks_completion:
                    if self.contains_completion_c:
                        error_msg_retry('You can only include one of the types that [gold3]Mark Completion[/gold3] of the item')
                    else:
                        self.contains_completion_c = True

                self.user_types.append(formated_type)

                if selected_type.default_col_name:

                    column_name = Prompt.ask(
                        "Select a [bold magenta]Name[/bold magenta] for the new column\nOr press [blue]Enter[/blue] to use the default name")
                    if column_name == '':
                        column_name = selected_type.default_col_name
                else:
                    while True:
                        column_name = Prompt.ask("Select a [bold magenta]Name[/bold magenta] for the new column")
                        if column_name != '':
                            break
                self.user_columns.append(column_name+formated_type)

                self.new_template[2] = '-'.join(self.user_columns)

                self.update_top_content()

                return self

        if choice == 's':
            if self.new_template[1] == "":
                error_msg("You must choose a [bold magenta]Name[/bold magenta] for your template")
                self.handle_page_input(choice='n')
                return self

            if len(self.user_columns) < 2:
                error_msg('You must include at least two columns in your template')
                self.handle_input()

            if not self.contains_completion_c:
                error_msg('Your template must include one of the types that [gold3]Mark Completion[/gold3] of the item')
                self.handle_input()
            else:
                self.templates_dao.append_item(self.new_template)
                return CreateChecklist()

        else:
            return self


# CHECKLIST PAGE
class ChecklistPage(Page):
    def __init__(self, db, sorting_key=None):
        self.db = db
        self.sorting_key = sorting_key
        self.checklist_dao = Dao(self.db)
        self.update_table_display()

        super().__init__(height=self.height,
                         options=["Add New Item [N]", "Update Item [U]", "Delete Item [D]", "Sort Table [S]"],
                         top_content=self.top_content
                         )

    def update_table_display(self):
        data_list = self.checklist_dao.get_all()
        self.height = len(self.checklist_dao.get_all()) * 2 + 4
        self.top_content = Align.center(Panel(checklist_table(data_list, self.sorting_key), border_style="grey53"))

    def handle_page_input(self, choice):
        columns = self.checklist_dao.get_columns()
        if choice == "n":
            new_id = self.checklist_dao.new_id()
            new_row = [new_id]
            for column in columns[1:]:
                title, dtype = split_type(column)
                dtype_obj = type_registry[dtype]
                while True:
                    field = Prompt.ask(
                        f'Enter the [bold magenta]{title}[/bold magenta], [italic]{dtype_obj.short_desc}[/italic]')
                    if field == "cancel":
                        return self
                    if isinstance(dtype_obj, OptionsType):
                        field = field.lower()
                    if isinstance(dtype_obj, TextType):
                        if dtype_obj.case == "title":
                            field = titlecase(field)

                    is_valid, error_msg_ = dtype_obj.validate(field)
                    if is_valid:
                        new_row.append(field)
                        break

                    error_msg_retry(error_msg_)
                    continue
            self.checklist_dao.append_item(new_row)
            return ChecklistPage(self.db)
        if choice == "u":
            while True:
                try:
                    item_id = Prompt.ask(f'Select Item to update [dark_goldenrod][Id][/dark_goldenrod]')
                    if item_id.lower() == 'cancel':
                        return self
                    item = self.checklist_dao.get_item(item_id)
                    item_columns = zip(columns, item)
                    next(item_columns)
                    break
                except TypeError:
                    continue
            for column, field in item_columns:
                c_title, dtype = split_type(column)
                dtype_obj = type_registry[dtype]
                while True:
                    new_field = Prompt.ask(
                        f'Enter the updated [bold magenta]{c_title}[/bold magenta], [italic]{dtype_obj.short_desc}[/italic]\nOr press [blue]Enter[/blue] to keep the same')
                    if new_field.lower() == 'cancel':
                        return self
                    if isinstance(dtype_obj, OptionsType):
                        new_field = new_field.lower()
                    if isinstance(dtype_obj, TextType):
                        if dtype_obj.case == "title":
                            field = titlecase(field)
                    if new_field == '':
                        break
                    is_valid, error_msg_ = dtype_obj.validate(new_field)
                    if is_valid:
                        index = item.index(field)
                        item[index] = new_field
                        break
                    error_msg_retry(error_msg_)
                    continue
            self.checklist_dao.update_item(item_id, item)
            self.update_table_display()

            return self
        if choice == "s":

            while True:

                key = Prompt.ask("Choose a [magenta]column[/magenta] to sort").lower()
                if key == 'cancel':
                    return self

                if key in self.checklist_dao.get_column_names():
                    return ChecklistPage(self.db, sorting_key=key)
                else:
                    columns_str = ', '.join(self.checklist_dao.get_column_names())
                    error_msg_retry(
                        f'You must choose one of the columns of this checklist: [bold italic magenta]{columns_str}[/bold italic magenta]')
        if choice == 'd':
            try:
                item_id = Prompt.ask(f'Select Item to [red]Delete[/red] [dark_goldenrod][Id][/dark_goldenrod]')
                if item_id == 'cancel':
                    return self
                item = self.checklist_dao.get_item(item_id)
                if item == None:
                    raise TypeError
            except TypeError:
                return self
            confirmation = Prompt.ask(f'Are you sure you want to [red]Delete [bold italic]{item[1]}[/bold italic][/red] y/n').lower()
            if confirmation in ['y', 'yes']:
                self.checklist_dao.delete_item(item_id)
                self.update_table_display()
                return self
            else:
                return self
        else:
            import re
            if sort_cmd := re.match(r'sort --([\w+\s?]+)', choice):
                sorting_key = sort_cmd.group(1)
                if sorting_key in self.checklist_dao.get_column_names():
                    return ChecklistPage(self.db, sorting_key=sorting_key)
                else:
                    columns_str = ', '.join(self.checklist_dao.get_column_names())
                    error_msg(
                        f'You must choose one of the columns of this checklist for sorting: [bold italic magenta]{columns_str}[/bold italic magenta]')

            return self


# -------------------------------------------------------------------------------------------------------------------#
################################################## FUNCTIONS ########################################################
# -------------------------------------------------------------------------------------------------------------------#

def file_name_to_title(file_name):
    name = file_name.rsplit('.', 1)[0].replace('_', ' ')
    title = titlecase(name)
    return title


def error_msg_retry(msg):
    console = Console()
    console.print(f'[italic][bright_red]{msg}, try again[bright_red][/italic]')


def error_msg(msg):
    console = Console()
    console.print(f'[italic][bright_red]{msg}[bright_red][/italic]')

def split_type(header):
    search = re.search(r'((?:\w+\s?)+)\((@\w+)\)', header)
    if search:
        title, type_ = search.groups()
        return title, f'({type_})'
    return None, None


# -------------------------------------------------------------------------------------------------------------------#
#################################################### APP ############################################################
# -------------------------------------------------------------------------------------------------------------------#

class AppController:
    def __init__(self):
        self.current_page = HomePage()

    def run(self):
        while True:
            try:
                self.current_page.display()
                self.current_page = self.current_page.handle_input()
            except (EOFError, KeyboardInterrupt):
                sys.exit()


def main():
    app = AppController()
    app.run()


if __name__ == "__main__":
    main()
