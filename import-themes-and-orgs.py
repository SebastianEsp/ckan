#!/usr/bin/env python
import pprint
import ckanapi
# import os
# from xml.dom import minidom
import sys


groups = [
          {'name': u'oevrige',
           'title': u'Ovrige temaer',
           'description': 'Alle andre temaer',
           'image_url': u'all-data.jpg'},
          {'name': 'landbrug-fiskeri-skovbrug-og-fodevarer',
           'title': 'Landbrug, fiskeri, skovbrug og foedevarer',
           'description': 'Landbrug, fiskeri, skovbrug og foedevarer [AGRI]',
           'image_url': 'argiculture.jpg'},
          {'name': 'retfaerdighed-retssystemet-og-offentlig-sikkerhed',
           'title': u'Retfaerdighed, retssystemet og offentlig sikkerhed',
           'description':
              'Retfaerdighed, retssystemet og offentlig sikkerhed [JUST]',
           'image_url': u'justice.jpg'},
          {'name': 'miljo',
           'title': u'Miljoe',
           'description': 'Miljoe [ENVI]',
           'image_url': u'environment.jpg'},
          {'name': 'energi',
           'title': u'Energi',
           'description': 'Energi [ENER]',
           'image_url': u'energy.jpg'},
          {'name': 'internationale-sporgsmal',
           'title': u'Internationale spoergsmaal',
           'description': 'Internationale spoergsmaal [INTR]',
           'image_url': u'international.jpg'},
          {'name': 'okonomi-og-finanser',
           'title': u'Oekonomi og finanser'	,
           'description': 'Oekonomi og finanser [ECON]',
           'image_url': u'economy.jpg'},
          {'name': 'regeringen-og-den-offentlige-sektor',
           'title': u'Regeringen og den offentlige sektor'	,
           'description': 'Regeringen og den offentlige sektor [GOV]',
           'image_url': u'goverment.jpg'},
          {'name': 'regioner-og-byer',
           'title': 'Regioner og byer',
           'description': u'Regioner og byer [REGI]',
           'image_url': u'region.jpg'},
          {'name': 'transport',
           'title': u'Transport'	,
           'description': 'Transport [TRAN]',
           'image_url': u'transport.jpg'},
          {'name': 'sundhed',
           'title': u'Sundhed',
           'description': 'Sundhed [HEAL]',
           'image_url': u'health.jpg'},
          {'name': 'uddannelse-kultur-og-sport',
           'title': u'Uddannelse, kultur og sport',
           'description': 'Uddannelse, kultur og sport [EDUC]',
           'image_url': u'education.jpg'},
          {'name': 'videnskab-og-teknologi',
           'title': u'Videnskab og teknologi',
           'description': 'Videnskab og teknologi [TECH]',
           'image_url': u'science.jpg'}

         ]

# dev-hrh-env: apikey='22c03996-f534-4ca8-9d36-c0eb499309bf',
# admin - test-end: apikey='5f74fd91-c8fa-45fa-9c61-9c5a988bdf93',
# prod-env:    apikey='d06d6cb7-fed4-49bb-bb7d-bd6a352c9f9d',
ckan = ckanapi.RemoteCKAN('http://localhost:5000',
                          apikey='22c03996-f534-4ca8-9d36-c0eb499309bf',
                          user_agent='ckanapiexample/1.0 (+http://ex.com/)')

# res = ckan.action.organization_list()
# pprint.pprint(res)

for group in groups:
    result = ckan.call_action('group_create', group)
    pprint.pprint(result)

# for root, dirs, xmlfiles in os.walk("./dataset-demo",):
#    for xmlfile in xmlfiles:
#        try:
#            if xmlfile.endswith('XML.rdf'):
#                filepath = os.path.join(root, xmlfile)
#                xmldoc = minidom.parse(filepath)
#                title = xmldoc.getElementsByTagName("dcterms:title")
#                titleText = " ".join(t.nodeValue
#                                     for t in title[0].childNodes
#                                     if t.nodeType == t.TEXT_NODE)
#                orgIdent = titleText.lower().strip()
#                desc = xmldoc.getElementsByTagName("dcterms:description")
#                descText = " ".join(t.nodeValue
#                                    for t in desc[0].childNodes
#                                    if t.nodeType == t.TEXT_NODE)
#                descIdent = descText.lower().replace(' ', '_').strip()
#                descIdent = descIdent.replace('.','_')
#                print titleText + " -> " + descIdent

# #           pkg = ckan.action.package_create(name='my-dataset',
# #                                            title='not going to work',
# #                                            owner_org='skat')
# #           pprint.pprint(pkg)
#        except Exception as ex:
#            print "!!!!! " + xmlfile + " ERROR:"
#            pprint.pprint(ex)

# res = ckan.action.organization_list()
# pprint.pprint(res)
