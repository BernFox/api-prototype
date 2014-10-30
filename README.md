issue_id_api
============
This API uses python 2.7

To get this thing going do the following:

First ensure that database_config.example is in the API directory. This houses all the 
credentials for database connections for the entire API.

1. run 'pip install -r requirements.txt'
2. python manage.py syncdb
3. python manage.py runserver
4. use the following url:
   
    ----> http://localhost/api/QuestionAnswers/[answer_set_id]/Assess/?format=json

    ----> replace <answer_set_id> with the actual answer_set_id you'd like to evaluate
5. a json object with be returned in the browser
6. read the json from the url and you're in business
    
