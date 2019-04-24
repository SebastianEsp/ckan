import ckan.plugins as plugins
import ckan.plugins.toolkit as tk
from ckan.lib.plugins import DefaultTranslation
import ckan.lib.helpers as helpers
import ckan.model as model

import pylons.config as config
import logging
from webhelpers.html.tags import *
from ckan.common import g
import ConfigParser
import StringIO
import re

log = logging.getLogger('ckanext.digstdk')

THEME_LEVEL2_MAPPING = {
    '34.30': 'landbrug-fiskeri-skovbrug-og-fodevarer',
    '34.25': 'landbrug-fiskeri-skovbrug-og-fodevarer',
}
THEME_LEVEL1_MAPPING = {
    '56': 'energi',
    '24': 'regioner-og-byer',
    '26': 'regioner-og-byer',
    '58': 'transport',
    '59': 'transport',
    '06': 'okonomi-og-finanser',
    '30': 'okonomi-og-finanser',
    '02': 'internationale-sporgsmal',
    '03': 'internationale-sporgsmal',
    '34': 'regeringen-og-den-offentlige-sektor',
    '52': 'regeringen-og-den-offentlige-sektor',
    '54': 'regeringen-og-den-offentlige-sektor',
    '60': 'regeringen-og-den-offentlige-sektor',
    '62': 'regeringen-og-den-offentlige-sektor',
    '63': 'regeringen-og-den-offentlige-sektor',
    '65': 'regeringen-og-den-offentlige-sektor',
    '67': 'regeringen-og-den-offentlige-sektor',
    '68': 'regeringen-og-den-offentlige-sektor',
    '40': 'retfaerdighed-retssystemet-og-offentlig-sikkerhed',
    '42': 'retfaerdighed-retssystemet-og-offentlig-sikkerhed',
    '44': 'retfaerdighed-retssystemet-og-offentlig-sikkerhed',
    '46': 'retfaerdighed-retssystemet-og-offentlig-sikkerhed',
    '47': 'retfaerdighed-retssystemet-og-offentlig-sikkerhed',
    '37': 'miljo',
    '38': 'miljo',
    '10': 'uddannelse-kultur-og-sport',
    '16': 'uddannelse-kultur-og-sport',
    '17': 'uddannelse-kultur-og-sport',
    '18': 'uddannelse-kultur-og-sport',
    '20': 'sundhed',
    '05': 'befolkning-og-samfund',
    '08': 'befolkning-og-samfund',
    '14': 'befolkning-og-samfund',
    '12': 'videnskab-og-teknologi',
}


def groupForCode(code):
    for key, value in THEME_LEVEL2_MAPPING.iteritems():
        if code.startswith(key):
            return value
    for key, value in THEME_LEVEL1_MAPPING.iteritems():
        if code.startswith(key):
            return value


def sorted_extras(package_extras, auto_clean=False, subs=None, exclude=None):
    package_show_extras = config.get('ckanext.digstdk.package_show_extras',
                                     None)
    if package_show_extras:
        package_show_extras = package_show_extras.split(',')

    if not exclude:
        exclude = g.package_hide_extras
    filteredExtras = {}

    log.error(package_extras)

    for extra in package_extras:
        if extra.get('state') == 'deleted':
            continue
        k, v = extra['key'], extra['value']
        if k in exclude:
            continue
        if package_show_extras and k not in package_show_extras:
            continue
        if subs and k in subs:
            k = subs[k]
        elif auto_clean:
            k = k.replace('_', ' ').replace('-', ' ').title()
        if isinstance(v, (list, tuple)):
            v = ", ".join(map(unicode, v))
        filteredExtras[k] = v

    sortedExtras = []
    for extra_name in package_show_extras:
        if extra_name in filteredExtras:
            sortedExtras.append((extra_name, filteredExtras[extra_name]))

    return sortedExtras


def getMetadataList():
    package_show_extras = config.get('ckanext.digstdk.package_show_extras',
                                     None)
    if package_show_extras:
        return package_show_extras.split(',')
    else:
        return []


def get_vocab_config():
    vocabDef = config.get('ckanext.digstdk.vocabularies', None)
    vocabs = {}
    if vocabDef:
        configParser = ConfigParser.RawConfigParser(allow_no_value=True)
        configParser.readfp(StringIO.StringIO(vocabDef))
        vocabList = configParser.sections()
        for vocabName in vocabList:
            vocabTerms = configParser.get(vocabName, "begreber").split(";")
            vocabFields = configParser.get(vocabName, "felter").split(";")
            vocabFieldsDict = {}
            for fieldName in vocabFields:
                vocabFieldsDict[fieldName] = True
            vocabs[vocabName] = {'terms': vocabTerms,
                                 'fields': vocabFieldsDict}

    return vocabs


def list_vocabs():
    return get_vocab_config()


def get_vocab(vocabName):
    vocabDef = get_vocab_config()
    vocab = {}
    if vocabName in vocabDef:
        vocab = vocabDef[vocabName]

    return vocab


def get_vocab_for_field(fieldName):
    vocabDef = get_vocab_config()
    vocab = None
    for vocabName in vocabDef:
        if fieldName in vocabDef[vocabName]['fields']:
            vocab = vocabDef[vocabName]
            break
    return vocab


def convertToOptions(vocab):
    opt = []
    for t in vocab['terms']:
        pair = t.split("=")
        if len(pair) == 1:
            opt.append({'value': pair[0]})
        else:
            opt.append({'value': pair[0], 'text': pair[1]})
    return opt


def getSelectedTerm(vocab, option):
    output = ''
    for t in vocab['terms']:
        pair = t.split("=")
        if option == pair[0]:
            if len(pair) == 1:
                output = pair[0]
            else:
                output = pair[0]
            break

    return output


def getSelectedText(vocab, option):
    output = ''
    for t in vocab['terms']:
        pair = t.split("=")
        if option == pair[0]:
            if len(pair) == 1:
                output = pair[0]
            else:
                output = pair[1]
            break

    return output


def getFieldValue(field, data):
    output = ''
    if 'extras' in data:
        for f in data['extras']:
            if f['key'] == field:
                output = f['value']
                break

    return output


def getGroups():
    '''Return a list of the groups'''

    # Get a list of all the site's groups from CKAN, sorted by number of
    # datasets.
    groups = tk.get_action('group_list')(
         data_dict={'all_fields': True})

    return groups


def subst(source, searchFor, replaceWith):
    '''search in source for searchFor and replace it with replaceWith'''
    return source.replace(searchFor, replaceWith)


class DigstdkPlugin(plugins.SingletonPlugin,
                    tk.DefaultDatasetForm,
                    DefaultTranslation):
    '''Digst.dk customizations '''

    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.ITranslation)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.IRoutes, inherit=True)

# IConfigurer

    def update_config(self, config_):
        tk.add_template_directory(config, 'local_templates')
        tk.add_public_directory(config_, 'public')
        tk.add_resource('fanstatic', 'digstdk')

    def update_config_schema(self, schema):
        ignore_missing = tk.get_validator('ignore_missing')

        schema.update({
            'ckanext.digstdk.vocabularies': [ignore_missing, unicode]
        })

        return schema

# ITemplateHelpers

    def get_helpers(self):
        return {'get_vocab_lists': list_vocabs,
                'get_vocab': get_vocab,
                'get_vocab_for_field': get_vocab_for_field,
                'convertToOptions': convertToOptions,
                'getGroups': getGroups,
                'subst': subst,
                'getSelectedTerm': getSelectedTerm,
                'getSelectedText': getSelectedText,
                'getMetadataList': getMetadataList,
                'getFieldValue': getFieldValue}

# IDatasetForm
    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return True

    def package_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return []

    def _validUrl(self, url):
        if url is None:
            return True

        startOk = url.lower().startswith('http://')
        startOk = startOk or url.lower().startswith('https://')
        startOk = startOk or url.lower().startswith('ftp://')
        startOk = startOk or url.lower().startswith('ftps://')
        noBlanks = url.find(' ') == -1
        noBlanks = noBlanks or url.find('\t') == -1

        return startOk and noBlanks

    def validate(self, context, data_dict, schema, action):
        errors = {}

        if data_dict['title'] == '':
            errors['title'] = ['Skal udfyldes!']

        if 'private' in data_dict and data_dict['private'] == 'False':
            data_dict['private'] = False

        if 'private' in data_dict and data_dict['private'] == 'True':
            data_dict['private'] = True

        validateFields = ['__page', 'url', '__conforms_to']

        for field in validateFields:
            if 'extra' in data_dict and field.startswith('__'):
                xtraDict = data_dict['extras']
                realField = field[2:]
                for item in xtraDict:
                    if item['key'] == realField:
                        if not self._validUrl(item['value']):
                            errors[realField] = ['Teksten i feltet er ikke'
                                                 + ' en korrekt URL']

            else:
                theDict = data_dict
                if field in theDict and theDict[field] != '':
                    if not self._validUrl(theDict[field]):
                        errors[field] = ['Teksten i feltet er ikke'
                                         + ' en korrekt URL']

        return (data_dict, errors)

    def setup_template_variables(self, context, data_dict):
        return super(DigstdkPlugin, self).setup_template_variables(
                context, data_dict)

#   IRoutes
    def after_map(self, map):
        ctlName = 'ckanext.digstdk.controller:StatsExportController'
        map.connect('statsexport', '/statsexport/{id}',
                    controller=ctlName,
                    action='index')
        ctlName = 'ckanext.digstdk.controller:CsvExportController'
        map.connect('cvsexport', '/csvexport',
                    controller=ctlName,
                    action='index')
        return map

    def _is_export(self):
        return helpers.full_current_url().lower().endswith('.xml')

    # IPackageController
    def after_show(self, context, package_dict):
        #  only execute if after_show is called for .xml-ending url's
        if self._is_export():
            package_show_extras = \
                config.get('ckanext.digstdk.package_show_extras',
                           None)
            if package_show_extras:
                package_show_extras = package_show_extras.split(',')

                itemDeleted = True
                while (itemDeleted):
                    itemDeleted = False
                    for index, value in enumerate(package_dict['extras']):
                        if value['key'] not in package_show_extras:
                            del package_dict['extras'][index]
                            itemDeleted = True

                foundKeys = []
                for val in package_dict:
                    if val != 'extras' and val not in package_show_extras:
                        foundKeys.append(val)

                for key in foundKeys:
                    del package_dict[key]

    def after_update(self, context, data_dict):
        self.do_group_assignement(config, data_dict)

    # IPackageController
    def after_create(self, context, data_dict):
       self.do_group_assignement(config, data_dict)

    def do_group_assignement(self, context, data_dict):
        subject = None
        for extra in data_dict.get('extras', []):
            if extra['key'] == 'subject':
                subject = extra['value']
                break
        if subject is None:
            return

        context = {'ignore_auth': True}
        site_user = plugins.toolkit.get_action('get_site_user')(context, {})

        subject = re.sub('["\]\[]', '', subject)
        codes = subject.split(',')
        dataset_groups = set(map(groupForCode, codes))
        model.repo.commit()

        all_groups = plugins.toolkit.get_action('group_list')(context, {})
        for group_id in all_groups:
            group = model.Group.get(group_id)

            if group is None:
                continue

            member_dict = {
                'id': group_id,
                'object': data_dict['id'],
                'object_type': 'package',
            }
            member_context = {
                'user': site_user['name'],
                'ignore_auth': True,
            }
            if group_id in dataset_groups:
                member_dict['capacity'] = 'public'
                plugins.toolkit.get_action('member_create')(
                    member_context, member_dict)
            else:
                plugins.toolkit.get_action('member_delete')(
                    member_context, member_dict)


class DigstdkThemePlugin(plugins.SingletonPlugin):
    '''Digst.dk Theme/Custom design '''

    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)

    def get_helpers(self):
        return dict(sorted_extras=sorted_extras,)

    def update_config_schema(self, schema):
        ignore_missing = tk.get_validator('ignore_missing')

        schema.update({
            'ckanext.digstdk.package_show_extras': [ignore_missing, unicode],
        })

        return schema

    def update_config(self, config_):
        tk.add_public_directory(config_, 'public')
        tk.add_template_directory(config_, 'templates')
