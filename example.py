import re
import parser
import datetime

def create_setup():
    jog_parser_params = {}

    # define the format checking functions
    def check_jog_id(str_in):

        try:
            val_out = int(str_in)
        except:
            raise(Exception('invalid format of the column jog_id'))

        return(val_out)

    def check_date(str_in):

        comp_value = str_in.strip().strip('\'').strip('"')
        try:
            datetime.datetime.strptime(comp_value, '%Y-%m-%d')
        except:
            raise(Exception('invalid format of the column date'))  

        return(comp_value)

    def check_distance(str_in):
        try:
            val_out = float(str_in)
        except:
            raise(Exception('invalid format of the column jog_id'))

        return(val_out)

    def check_time(str_in):
        try:
            val_out = float(str_in)
        except:
            raise(Exception('invalid format of the column jog_id'))

        return(val_out)

    # define variable types and forma checking functions
    jog_parser_params['column_list']=(
    {
        'jog_id': {
                'type': 'int',
                'format_checker': check_jog_id,
            },
        'date': 
            {
                'type': 'date',
                'format_checker': check_date,
            },
        'distance': 
            {
                'type': 'float',
                'format_checker': check_distance,
            },
        'time': 
            {
                'type': 'float',
                'format_checker': check_time
            }
    }
    )
    
    # define the comparison operators
    jog_parser_params['comp_op_list'] = (
    {
        'eq':{
                'sql_str':'=',
                'funciton': lambda a, b : a == b
            },
        'ne':{
                'sql_str':'!=',
                'funciton': lambda a, b : a != b
            },
        'gt':{
                'sql_str':'>',
                'funciton': lambda a, b : a > b
            },
        'lt':{
                'sql_str':'<',
                'funciton': lambda a, b : a < b
            }
    })

    # define the logical operators
    jog_parser_params['log_ops'] = (
    {
        'or':{
                'sql_str':'or',
                'funciton': lambda a, b : a | b
            },
        'and':{
                'sql_str':'and',
                'funciton': lambda a, b : a & b
            }
    })

    return(jog_parser_params)

list_in = (
    [
    {
        'jog_id': 1,
        'date': '2019-01-03',
        'distance': 10,
        'time': 40
    },
    {
        'jog_id': 2,
        'date': '2019-01-04',
        'distance': 12,
        'time': 40
    },
    {
        'jog_id': 3,
        'date': '2019-01-05',
        'distance': 12,
        'time': 41
    }
    ])

print(parser.Parser(create_setup()).filter('',list_in))

print(parser.Parser(create_setup()).filter('jog_id gt 1',list_in))

print(parser.Parser(create_setup()).filter('date gt \'2019-01-04\'',list_in))

print(parser.Parser(create_setup()).filter('(jog_id eq 1) OR (date gt \'2019-01-04\')',list_in))