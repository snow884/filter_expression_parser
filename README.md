# filter_expression_parser
This is a simple class written in python for parsing filter expressions of the following types:
```python
distance eq 10
```
```python
age lt 5
```
```python
( (name eq 'adam') AND (age lt 60) ) OR (user_name ne 'gorgo_and_mormo')
```

I am presenting an example in example.py on how to configure the class. Basicly you need to give it the names of the columns, operations that are allowed, lambda functions defining the what they represent and lambda functions for format checks.

Note that I think the code could be a lot more compact. Feel free to improve this further if you want to. If you have any quesrions about this feel free to drop me a message.