import logging
import chardet

import ckan.logic as logic
import ckan.model as model
import ckan.lib.base as base
# import ckan.lib.helpers as h
# import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import pylons.config as config

from ckan.common import _, request, c
from ckan.lib.base import BaseController
import ckanext.stats.stats as stats_lib


LIMIT = 25
log = logging.getLogger(__name__)


def wsgi_app(environ, start_response, data):
    start_response('200 OK', [('Content-type', 'text/csv'), ('Content-Disposition', 'attachment; filename=\"datasets.csv\"')])
    return [data]

class CsvExportController(BaseController):
    def log( self, logText ):
    #    log.info( logText )
       pass

    def serialize_to_digstcsv(self, dataset_dict, withHeader=True):
      csv_lines = []

      package_show_extras = config.get('ckanext.digstdk.package_show_extras', None)

      fields = []
      data = {}
      #Create list of field names
      # - and create dictionary of data
      for field in package_show_extras.split(','):
        fields.append(field)
        data[field] = ''

        if field in dataset_dict:
           data[field]=dataset_dict[field]

        if 'extras' in dataset_dict:
           self.log('we got extras')
           for extraField in dataset_dict['extras']:
               self.log('look for "' +field+ '"')
               if extraField['key'] == field:
                   self.log('we found!! "' + field + '"')
                   if type(extraField['value']) is list:
                       self.log(' - its a list')
                       data[field] = u', '.join(extraField['key'])
                   else:
                       if len(extraField['value']) > 0 and extraField['value'][0] == '[':
                           self.log(' - its got a "["')
                           data[field] =u''+extraField['value'][1:-1]
                       else:
                           self.log(' - data[' + field + '] = ' + extraField['value'])
                           data[field] =u''+ extraField['value']

      #Check to see if first lien should be a header line 
      if withHeader == True:
        self.log('add header')
        csv_lines.append(u';'.join(fields))

      dataFields = []
      for dataField in fields:
        if dataField in data and data[dataField] is not None and not isinstance(data[dataField], dict):
            fieldData = data[dataField]
            fieldData = fieldData.replace("\"", "\"\"")
            # if len(fieldData) > 0 and (fieldData.find(',') or fieldData.find(';')) and fieldData[len(fieldData)-1] != '"':
            fieldData = '"' + fieldData + '"'
            dataFields.append( fieldData )
        else:
            dataFields.append('')

      csv_lines.append(u';'.join(dataFields))

      csvText = u"\n".join(csv_lines).replace(u"\u2018", "'").replace(u"\u2019", "'").replace(u"\u2013", "-") \
          .replace(u"\u201c", "\"").replace(u"\u201d", "\"").replace(u"\u201e", "\"").replace(u"\u201f", "\"")\
          .encode('iso-8859-1')

      return csvText

    def index(self):
      context = {'model': model,
                 'user': c.user or c.author}

      listOfDatasets = logic.action.get.package_list(context, {})
      data = []
      useHeader = True
      for dataset in listOfDatasets:
        self.log('dataset: ' + dataset)
        data_dict = logic.action.get.package_show(context,{'id': dataset})
        self.log('data_dict: ' + str(data_dict))
        data.append(self.serialize_to_digstcsv( data_dict, useHeader))
        self.log('data: ' + str(data))
        useHeader = False

      return wsgi_app(request.environ, self.start_response, "\n".join(data))


class StatsExportController(BaseController):
    def index(self, id):
        stats = stats_lib.Stats()
        rev_stats = stats_lib.RevisionStats()

        data = 'Error\n\'Missing parameter for stat\'\n'

        if id == "most_edited_packages":
            most_edited_packages = stats.most_edited_packages()
            log.debug(" most_edited_packages: %s" % most_edited_packages)
            data = "name, number_of_changes\n"
            for row in most_edited_packages:
                data = data + "'%s', %i\n" % (row[0].title, row[1])
        elif id == "largest_groups":
            largest_groups = stats.largest_groups()
            log.debug(" largest_groups: %s" % largest_groups)
            data = "name,number_of_datasets\n"
            for row in largest_groups:
                data = data + "'%s', %i\n" % (row[0].name, row[1])
        elif id == "top_package_creators":
            top_package_creators = stats.top_package_creators()
            log.debug(" top_package_creators: %s " % top_package_creators)
        elif id == "new_packages_by_week":
            new_packages_by_week = rev_stats.get_by_week('new_packages')
            log.debug(" new_packages_by_week: %s" % new_packages_by_week)
        elif id == "deleted_packages_by_week":
            statname = 'deleted_packages'
            deleted_packages_by_week = rev_stats.get_by_week(statname)
            data = "date,data,deleted_datasets, total_number_of_datasets\n"
            for row in deleted_packages_by_week:
                data = data + "'%s', '%s', %i, %i\n" % row
        elif id == "packages_by_week":
            num_packages_by_week = rev_stats.get_num_packages_by_week()
            log.debug("num_packages_by_week: %s" % num_packages_by_week)
            data = "date,number_of_new_datasets,total_number_of_datasets\n"
            for row in num_packages_by_week:
                data = data + "'%s', %i, %i\n" % row

        return wsgi_app(request.environ, self.start_response, data)


class VocabController(BaseController):
    '''Digstdk vocabulary administrator
    '''

    def __before__(self, action, **env):
        base.BaseController.__before__(self, action, **env)
        try:
            context = {'model': model, 'user': c.user or c.author,
                       'auth_user_obj': c.userobj}
            logic.check_access('site_read', context)
        except logic.NotAuthorized:
            base.abort(401, _('Not authorized to see this page'))

    def new(self):
        name = request.params('name')
        if name:
            toolkit.get_action('create_vocabularies')()

        return toolkit.render('vocabs/new.html')

    def index(self):
        log.info('VocabController: index')
        context = {'model': model, 'user': c.user or c.author,
                   'auth_user_obj': c.userobj}

        # results = logic.get_action('tag_list')(context, data_dict)
        listOfVocabs = toolkit.get_action('vocabulary_list')(context, None)
        # listOfVocabs = [{'Name':'FORM Koder'},{'Name':'Themaer'}]
        return toolkit.render('vocabs/index.html', {'vocabs': listOfVocabs})
