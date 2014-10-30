from django.conf.urls import url
from tastypie.resources import ModelResource
from API.models import questionanswers
from tastypie.utils import trailing_slash
import MySQLdb
import numpy as np
import pandas as pd
from django.http import Http404
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

class QuestAnswerResource(ModelResource):
    qa = questionanswers()
    db = MySQLdb.connect(host=DATABASES['production']['host'],
                         user=DATABASES['production']['username'],
                         passwd=DATABASES['production']['password'],
                         db=DATABASES['production']['database'],
                         port=DATABASES['production']['port'])
    # DEFINE THE DB CONNECTION & THE CURSOR - THIS WILL NEED TO BE UPDATED WHEN INTEGRATING WITH ANOTHER SYSTEM
    #db = MySQLdb.connect(host='localhost',
    #                     user='root',
    #                     passwd='',
    #                     db='branching_minds',
    #                     )
    cur = db.cursor()

    class Meta:
        queryset = questionanswers.objects.all()
        resource_name = 'questionanswers'

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
        data = data.dropna()
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

    def prepend_urls(self):
        """Add the following array of urls to the QualAssessResource base urls"""
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/assess%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('assess'),
                name="api_Assess")
        ]

    def assess(self, request, **kwargs):
        """ proxy for the questionanswers.Assess() method """

        # you can do a method check to avoid bad requests
        self.method_check(request, allowed=['get'])
        # create a basic bundle object for self.get_cached_obj_get.
        basic_bundle = self.build_bundle(request=request)

        #self.cur.execute("SHOW TABLES;")
        #return self.create_response(request, self.cur.fetchall())

        # using the primary key defined in the url, obtain the data
        #qa = self.obj_get(
        #    bundle=basic_bundle,
        #    **self.remove_api_resource_names(kwargs))

        # Return what the method output, tastypie will handle the serialization
        return self.create_response(request, self.issue_id(int(kwargs['pk'])))
        #return self.create_response(request, qa.assess(int(kwargs['pk'])))

