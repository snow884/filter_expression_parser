import time
import re

class Parser(object):
    """
    this class hahosts all functions needed for parsing of
    user filter queries
    """

    def __init__(self, parser_params):
        """
        Constructor

        saves parser params as class variable
        """
        self.parser_params = parser_params

    def parse_parentheses(self, str_in):
        """
        This function parses the AND + OR operator inputs based on
        the parentheses present in the expression.

        This basically looks from (...) AND (...) and (...) OR (...)
        types of patterns and their hierarchy
        """
        stack = [{'state':-1,'start1':-1,'end1':-1,'start2':-1,'end2':-1,'log_op':'' }]

        id = 0
        parent_operand = 0
        last_pos = 0
        for i, c in enumerate(str_in):
            
            if ((c == '(') & (not(stack[len(stack)-1]['state'] == 2))):
                
                if (last_pos>0):
                    raise(Exception('Illegal expression "' + str_in[last_pos:i] + '"'))

                stack.append(
                    {
                        'id':id,
                        'state':1,
                        'start1':i,
                        'end1':-1,
                        'start2':-1,
                        'end2':-1,
                        'log_op':'', 
                        'parent':id-1, 
                        'parent_operand': parent_operand
                    }
                    ) 
                id = id + 1
                parent_operand = 0

            elif ((c == ')') & (stack[len(stack)-1]['state'] == 1)):
                stack[len(stack)-1]['state'] = 2
                stack[len(stack)-1]['end1'] = i
                

            elif ((c == '(') & (stack[len(stack)-1]['state'] == 2)):
                last_pos = 0
                stack[len(stack)-1]['state'] = 3
                stack[len(stack)-1]['start2'] = i

                str_between = str_in[stack[len(stack)-1]['end1']+1:stack[len(stack)-1]['start2']]
                str_between = str_between.strip().lower()

                for log_op in self.parser_params['log_ops'].keys():
                    if (str_between==log_op):
                        stack[len(stack)-1]['log_op'] = self.parser_params['log_ops'][log_op]

                if (stack[len(stack)-1]['log_op']==''):
                    raise(Exception('Unknown logical operator "' + str_between + '" at position ' + str(i)))

                parent_operand = 1

            elif ((c == ')') & (stack[len(stack)-1]['state'] == 3)):
                stack[len(stack)-1]['state'] = 4
                stack[len(stack)-1]['end2'] = i

                par_pair = stack.pop()
                yield (par_pair)
                last_pos = i

            elif ((not(c in [' ','\n','\t']))&(stack[len(stack)-1]['state'] in [-1,4])):
                raise(Exception('Illegal character "' + c + '"'))


        if (len(stack)>1):
            if not(stack[len(stack)-1]['state'] == 4):
                raise(Exception('Expression in composed in a forbiden pattern ... () op () op () ... use parenthesis for every operator'))

    def parse_comp_expression(self, str_in):
        """
        This function parses the comparison expression

        an example of expression that this parses would be "distance gt 23.45"
        """
        comp_expression = (
            {
                'variable': '',
                'operation': '',
                'comp_value': ''
            })

        str_in = str_in.strip()

        for variable in self.parser_params['column_list'].keys(): 
            if str_in.lower().startswith(variable + ' '):
                comp_expression['variable']=variable

        if (comp_expression['variable']==''):
            raise(Exception('Connot find column name in "...' + str_in + '"'))

        str_in = str_in[(len(comp_expression['variable'])):]
        str_in = str_in.strip()

        for op in self.parser_params['comp_op_list'].keys(): 
            if str_in.lower().startswith(op + ' '):
                comp_expression['operation']=op

        if (comp_expression['operation']==''):
            raise(Exception('Cannot find valid operation in "...' + str_in + '"'))
        
        str_in = str_in[(len(comp_expression['operation'])):]
        str_in = str_in.strip()

        comp_expression['comp_value'] = self.parser_params['column_list'][comp_expression['variable']]['format_checker'](str_in)

        return(comp_expression)

    def parse_expression(self, str_in):
        """
        Parses a filter expression and creates a dictionary tree describing
        the filter expression
        """

        str_in = str_in.strip().strip('\n').strip('\t')
               
        if (str_in[0]=='('):
            par_pair_list = list(self.parse_parentheses(str_in))

            for par_pair in par_pair_list:
                if (not(par_pair['state']==4)):
                    raise(Exception('Parenthesis theat started at positon ' + str(par_pair['start1']) + ' did not finish in the pattern (...) operator (...)' ))
            
            for pair_id, par_pair in enumerate(par_pair_list):

                par_pair_list[pair_id]['child_index1'] = -1
                par_pair_list[pair_id]['child_index2'] = -1
                
                for potencial_child_id,par_pair_potencial_child in enumerate(par_pair_list): 
                    if (
                        (par_pair_potencial_child['parent'] >= 0)
                        &(par_pair['id'] == par_pair_potencial_child['parent'])
                        &(par_pair_potencial_child['parent_operand']==0)
                        ):
                        par_pair_list[pair_id]['child_index1'] = potencial_child_id
                    elif (
                        (par_pair_potencial_child['parent'] >= 0)
                        &(par_pair['id'] == par_pair_potencial_child['parent'])
                        &(par_pair_potencial_child['parent_operand']==1)
                        ):
                        par_pair_list[pair_id]['child_index2'] = potencial_child_id
                
                par_pair_list[pair_id]['child1_exp'] = ''
                par_pair_list[pair_id]['child2_exp'] = ''

                if (par_pair_list[pair_id]['child_index1'] == -1):
                    #par_pair_list[pair_id]['child1_exp'] = str_in[(par_pair['start1']+1):par_pair['end1']]
                    par_pair_list[pair_id]['child1_exp'] = self.parse_comp_expression(str_in[(par_pair['start1']+1):par_pair['end1']])

                if (par_pair_list[pair_id]['child_index2'] == -1):
                    #par_pair_list[pair_id]['child2_exp'] = str_in[(par_pair['start2']+1):par_pair['end2']]
                    par_pair_list[pair_id]['child2_exp'] = self.parse_comp_expression(str_in[(par_pair['start2']+1):par_pair['end2']])

            return({'expression_type':1,'parsed_expression':par_pair_list})

        else:
            
            comp = self.parse_comp_expression(str_in)

            return({'expression_type':0,'parsed_expression':comp})

    def generate_sql_where(self, str_in):
        """
        Generates a SQL where expression based on a filter expression

        NOTE: I did not end up using this approach
        """
        if (str_in==''):
            return('')

        res = self.parse_expression(str_in)

        if (res['expression_type']==1):

            par_pair_list = res['parsed_expression']

            for par_pair_id, par_pair in enumerate(par_pair_list):
                if (par_pair['parent'] == -1):
                    root_index = par_pair_id

            return(self.traverse_tree(par_pair_list,root_index))

        elif (res['expression_type']==0):

            return(self.translate_child_expression(res['parsed_expression']))
            
    def traverse_tree(self, par_pair_list,index):
        """
        Traverses a tree in order to create a SQL where expression
        """
        ch1_ind = par_pair_list[index]['child_index1']
        ch2_ind = par_pair_list[index]['child_index2']

        if (ch1_ind == -1):
            str1 = self.translate_child_expression(par_pair_list[index]['child1_exp'])
        else:
            str1 = self.traverse_tree(par_pair_list,ch1_ind)

        if (ch2_ind == -1):
            str2 = self.translate_child_expression(par_pair_list[index]['child2_exp'])
        else:
            str2 = self.traverse_tree(par_pair_list,ch2_ind)

        return(
            (
                '(' +
                str1 + 
                ' ' + par_pair_list[index]['log_op']['sql_str'] + ' ' + 
                str2 +
                ')'
            )       
        )

    def translate_child_expression(self, child_exp):
        """
        Converts a comparison expression into a SQL compatible expression
        """
        if (self.parser_params['column_list'][child_exp['variable']]['type'] in ['int','float']):
            return(
                '(' +
                child_exp['variable'] + ' ' +
                self.parser_params['comp_op_list'][child_exp['operation']]['sql_str'] + ' ' +
                str(child_exp['comp_value']) +
                ')'
                )
        else:
            return(
                '(' +
                child_exp['variable'] + ' ' +
                self.parser_params['comp_op_list'][child_exp['operation']]['sql_str'] + ' \'' +
                str(child_exp['comp_value']) +
                '\')'
                )

    def evaluate_expression(self, str_in, list_in):
        """
        This evaluates a filter expression based on a list of 
        data passes to it creating a list of binary values
        specifying if a given set of values passed or failed
        """
        if (str_in==''):
            return([True] * len(list_in))

        res = self.parse_expression(str_in)

        if (res['expression_type']==1):
            
            par_pair_list = res['parsed_expression']

            for par_pair_id, par_pair in enumerate(par_pair_list):
                if (par_pair['parent'] == -1):
                    root_index = par_pair_id

            return(self.traverse_tree_eval(par_pair_list,root_index,list_in))

        elif (res['expression_type']==0):
            
            return(self.translate_child_expression_eval(res['parsed_expression'],list_in))

    def traverse_tree_eval(self, par_pair_list,index, list_in):
        """
        Traverses in order to evaluate a filter expression on data passed to it
        """
        ch1_ind = par_pair_list[index]['child_index1']
        ch2_ind = par_pair_list[index]['child_index2']

        if (ch1_ind == -1):
            res1 = self.translate_child_expression_eval(par_pair_list[index]['child1_exp'], list_in)
        else:
            res1 = self.traverse_tree_eval(par_pair_list,ch1_ind, list_in)

        if (ch2_ind == -1):
            res2 = self.translate_child_expression_eval(par_pair_list[index]['child2_exp'], list_in)
        else:
            res2 = self.traverse_tree_eval(par_pair_list,ch2_ind, list_in)

        return(
            [
                (
                    par_pair_list[index]['log_op']['funciton'](res1[i],res2[i])
                )       
                for i in range(0,len(res1))
            ]
        )

    def translate_child_expression_eval(self, child_exp, list_in):
        """
        Evaluates a comparison expression
        """

        return( 
            [
                (
                    self.parser_params['comp_op_list'][child_exp['operation']]['funciton'] (
                        list_in[i][child_exp['variable']],
                        child_exp['comp_value']
                        )
                )
                for i in range(0,len(list_in))
            ]
        )

    def filter(self, str_in, list_in):
        filt_vals = self.evaluate_expression(str_in, list_in)
        return([el for i,el in enumerate(list_in) if filt_vals[i]])