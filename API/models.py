from django.db import models
from django.http import Http404
import pandas as pd
import MySQLdb
import numpy as np
import os
import yaml

#USE BELOW TO DEBUG ON LOCAL MACHINE
#dirc = os.path.dirname(__file__)
#db_path = os.path.join(dirc, 'database_config.example.yml')
#db_file = open(db_path, 'r')
#DATABASES = yaml.load(db_file)

dirc = os.path.dirname(__file__)
db_path = os.path.join(dirc, 'database.yml')
db_file = open(db_path, 'r')
DATABASES = yaml.load(db_file)


class questionanswers(models.Model):
    # DEFINE THE DB CONNECTION & THE CURSOR - THIS WILL NEED TO BE UPDATED WHEN INTEGRATING WITH ANOTHER SYSTEM
    #db = MySQLdb.connect(host='localhost',
    #                     user='root',
    #                     passwd='',
    #                     db='branching_minds',
    #                     )

    db = MySQLdb.connect(host=DATABASES['production']['host'],
                         user=DATABASES['production']['username'],
                         passwd=DATABASES['production']['password'],
                         db=DATABASES['production']['database'],
                         port=DATABASES['production']['port'])
    cur = db.cursor()

    def issue_id(self, set_id):
        """
        This function is the first version of the Qualitative IssueID system, this should work for any set of questions.
        :rtype : object
        """

        # EXECUTE QUERY TO GET FORM ANSWER DATA, JOIN WITH COG_ISSUES_QUESTIONS TO IDENTIFY COG AREAS
        self.cur.execute("""
        SELECT
            a.value, b.cog_issue_id
        FROM
            question_answers a LEFT JOIN cog_issues_questions b
        ON
            a.question_id = b.question_id
        WHERE
            a.answer_set_id = {}""".format(set_id))

        # THIS IS A CHECK IF THERE IS INDEED DATA, IF NOT WE RETURN SOME ERROR TEXT.
        # I MAY WANT TO CHANGE THIS TO ACTUALLY THROW AN ERROR
        data = [np.array(x) for x in self.cur.fetchall()]
        if len(data) != 0:
            data = pd.DataFrame(data, columns=[i[0] for i in self.cur.description])
        else:
            return "Error: there is no data associated with that answer_set_id"
            #raise Http404

        # GRAB UNIQUE COG_ISSUE_IDs SO WE CAN OPERATE ON THEM
        cog_unique = data.cog_issue_id.unique()

        # THIS LIST COMPREHENSION IS USED TO CREATE THE ASSESSMENT OUTPUT, I DECIDED TO DO IT THIS WAY SO THAT
        # I COULD EASILY PUT THE LOGICAL CHECK IN THERE. ALSO LIST COMPS ARE PRETTY FAST OPERATING OVER A SET OF DATA
        issue_id = [
            {'cog_issue_id': ID,
             'value': data.value.loc[data.cog_issue_id == ID].dropna().mean() / 3}
            if not np.isnan(data.value.loc[data.cog_issue_id == ID].dropna().mean() / 3)
            else {'cog_issue_id': ID, 'value': None}
            for ID in cog_unique
        ]

        return issue_id

    def recommendation(self, cog_id):
        """
        This function will house the component that returns support ids for both quantitative & qualitative assessments.
        This function will have to be updated with a more intelligent system once we have data!
        """
        self.cur.execute("""
        SELECT
            support_id
        FROM
            supports_cognitive_weaknesses
        WHERE
            cog_issue_id = {}""".format(cog_id))

        rec = [int(x[0]) for x in self.cur.fetchall()]

        return rec

    def assess(self, set_id, threshold=0.4):
        #return 'test'
        """
        This function is the client facing function that delivers the IssueID and recommendation together in one piece.
        """
        # GET THE ISSUE ID DATA BY CALLING THE ISSUE_ID FUNCTION, SET_ID IS THE PARAMETER.
        issues = self.issue_id(set_id)

        # USE THIS MAP TO DETERMINE WHETHER OR NOT EACH COG AREA NEEDS TO GET A RECOMMENDATION
        # IF THE COG AREA DOES NEED A RECOMMENDATION, ADD IT TO ITS DICTIONARY, OTHERWISE GIVE IT A 'NONE'
        map(lambda x: x.update({'support_id': self.recommendation(x['cog_issue_id'])})
            if (x['value'] <= threshold) else x.update({'support_id': None}), issues)

        return issues

    class Meta:
        managed = False
        db_table = 'question_answers'

        #def __unicode__(self):
        #    return self.student_name