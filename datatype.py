from datetime import datetime

class DataType:
    def __init__(self, short_desc, long_desc, invalid_msg=None,
                 allows_blank=False, marks_completion=False, default_col_name=None):
        self.short_desc = short_desc
        self.long_desc = long_desc
        self.invalid_msg = invalid_msg
        self.allows_blank = allows_blank
        self.marks_completion = marks_completion
        self.default_col_name = default_col_name

    def validate(self, value):
        """Return a tuple (is_valid, error_message_if_any)."""
        if not self.allows_blank and value == "":
            return (False, "This value can't be left blank")
        # if self.allows_blank and value == "":
        #     return
        return (True, "")



class TextType(DataType):
    def __init__(self, max_len, case=None, default_col_name=None):
        self.max_len = max_len
        self.case = case
        short_desc = f'must be a text of {self.max_len} characters or less'
        long_desc = f'Text field that should not exceed {self.max_len} characters.'
        if self.case == 'title':
            long_desc += "It will be stored in Title Case, independently of how's introduced."
        else:
            long_desc += "The case would be left as introduced."
        super().__init__(short_desc, long_desc, default_col_name=default_col_name)

    def validate(self, value):
        blank_validation, msg = super().validate(value)
        if not blank_validation or msg != "":
            return (blank_validation, msg)

        if len(value) <= self.max_len:
            return (True, "")
        else:
            invalid_msg = f'Text is too long. Must be {self.max_len} characters or less.'
            return (False, invalid_msg)

# DATES
class DateType(DataType):
    def __init__(self, short_desc, long_desc, default_col_name, marks_completion=False,
                 allow_future=True, allow_past=True, allows_blank=False ):
        self.allow_future = allow_future
        self.allow_past = allow_past
        super().__init__(short_desc=short_desc, long_desc=long_desc, default_col_name=default_col_name, marks_completion=marks_completion,
                         allows_blank=allows_blank, invalid_msg='Make sure your input is a date in the format YYYY-MM-DD')

    def validate(self, value):
        blank_validation, msg = super().validate(value)
        if not blank_validation or msg != "":
            return (blank_validation, msg)
        if value == "":
            return True, ""

        try:
            value_date = datetime.strptime(value, '%Y-%m-%d').date()
            if not self.allow_future and value_date > datetime.now().date():
                return False, 'This value can not be a date in the future'
            if not self.allow_past and value_date < datetime.now().date():
                return False, 'You must choose a time in the future for this value'
            return True, ""
        except ValueError:
            return False, self.invalid_msg


class OptionsType(DataType):
    def __init__(self, short_desc, long_desc, default_col_name, options, allows_blank=False, colors=None, marks_completion=False):

        if not isinstance(options, list):
            raise TypeError("options must be a list")
        if colors:
            if not isinstance(colors, list):
                raise TypeError("colors must be a list")
            if len(colors) != len(options):
                raise TypeError("length of colors should match length of options")
            self.colors_map = dict(zip(options, colors))
        self.options = options

        # super().__init__(short_desc, long_desc, invalid_msg='You must choose one of the options', allows_blank=False, marks_completion=marks_completion )
        super().__init__(short_desc=short_desc, long_desc=long_desc, invalid_msg='You must choose one of the options', allows_blank=allows_blank, marks_completion=marks_completion, default_col_name=default_col_name)

    def validate(self, value):
        blank_validation, msg = super().validate(value)
        if not blank_validation or msg != "":
            return (blank_validation, msg)
        if value == "":
            return True, ""

        if value.lower() not in self.options:
            return False, self.invalid_msg
        return True, ""


class IntType(DataType):
    def __init__(self, short_desc, long_desc, marks_completion, allows_blank=False, min_value=None, max_value=None, default_col_name=None):
        self.min_value = min_value
        self.max_value = max_value
        self.short_desc = short_desc
        if min_value is not None and max_value is not None:
            short_desc += f" must be between {min_value} and {max_value}"
        elif min_value is not None:
            short_desc += f" must be greater than or equal to {min_value}"
        elif max_value is not None:
            short_desc += f" must be less than or equal to {max_value}"
        else:
            long_desc = "Integer field with no specific limits."
        super().__init__(short_desc, long_desc, marks_completion=marks_completion, allows_blank=allows_blank, default_col_name=default_col_name)

    def validate(self, value):
        # First, validate against the base class's logic for blank values
        is_valid, msg = super().validate(value)
        if not is_valid or msg:
            return is_valid, msg
        if value == "":
            return True, ""

        # Check if the value is an integer
        try:
            int_value = int(value)
        except ValueError:
            return False, "Value must be an integer."

        # Check the limits
        if self.min_value is not None and int_value < self.min_value:
            return False, f"Value must be greater than or equal to {self.min_value}."
        if self.max_value is not None and int_value > self.max_value:
            return False, f"Value must be less than or equal to {self.max_value}."

        return True, ""

type_registry = {


    '(@ID)': lambda: NotImplementedError('SYSTEM ONLY'),

    '(@TEXT)': TextType(max_len=86),

    '(@TEXTLONG)': TextType(max_len=172),

    '(@TITLE)': TextType(max_len=43,
                         case='title',
                         default_col_name='title'),

    '(@DUEDATE)': DateType(short_desc='must be a date in format YYYY-MM-DD, is the due date for this item',
                           long_desc='Is a due date for the item in the format YYYY-MM-DD. It can\'t be setted to before the current day, once passed it turns red and suggests to reschedule.',
                           allow_past=False,
                           default_col_name='due date'),

    '(@SDATE)': DateType(short_desc='Is the date you started with this item (YYYY-MM-DD) up to today, can be left blank',
                         long_desc='It\'s the date the item was started. It must be a date in the past or today\'s date, in the format YYYY-MM-DD. It can be left blank. Accepts past or future dates.',
                         allow_future=False,
                         allows_blank=True,
                         default_col_name='started'),


    '(@FDATE)': DateType(short_desc='Is the date you finished with this item (YYYY-MM-DD), if just creating it can left it blank',
                         long_desc='Stores the date when the item was finished, in the format YYYY-MM-DD. It does not accept a date in the future.',
                         allows_blank=True,
                         allow_future=False,
                         marks_completion=True,
                         default_col_name='finished'),

    '(@PRIORITY)': OptionsType(short_desc='must be "low", "medium" or "high"',
                               long_desc='Provides three options to rank the priority of the item, "Low", "Medium", and "High".',
                               options=['low', 'medium', 'high'],
                               colors=['cadet_blue', 'orange3', 'bright_yellow'],
                               default_col_name='priority'),

    '(@DONE)': OptionsType(short_desc='must be "done" or "failed"',
                           long_desc='Provides two options, "Done" or "Failed". The table will display [green]✓[/green] or [red]✗[/red].',
                           allows_blank=True,
                           options=['done', 'failed'],
                           colors=['green', 'red'],
                           marks_completion=True,
                           default_col_name='completed'),

    '(@STATUS)':  OptionsType(short_desc='must be "not started", "in progress", or "completed"',
                              long_desc='Provides three options to specify the status of the item, "not started", "in progress", or "completed".',
                              options=['not started', 'in progress', 'completed'],
                              marks_completion=True,
                              default_col_name='status'),

    '(@RATING5)': IntType(short_desc='must be a number from 1 to 5',
                          long_desc='Give a rating to the item (like a book or show). You will input a number from 1 to 5, the table will display it as star emojis',
                          allows_blank=True,
                          min_value=1,
                          max_value=5,
                          default_col_name='my rate',
                          marks_completion=True)

}
