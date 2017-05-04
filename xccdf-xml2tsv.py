#!/usr/bin/env python

###
# (C) 2010 Adam Crosby
# Licensed under:
#  http://creativecommons.org/licenses/by-sa/3.0/
##
import csv
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import xml.etree.ElementTree as ET
xmlns = "http://checklists.nist.gov/xccdf/1.1"

if len(sys.argv) != 2:
	print "  XCCDF-xml2tsv converts XCCDF XML documents (such as DISA STIGs)"
	print "    into easier to use Tab-Separated documents."
	print "  Please run as '%s' <filename> and redirect output as needed." % sys.argv[0]
	print "  Files should open easily in Excel."
	print "  E.g.:\n\t %s U_Perimeter_Router_v8R2_manual.xccdf.xml > output.tsv" % sys.argv[0]
	sys.exit(0)
try:
	xml = ET.parse(sys.argv[1])
except Exception,e:
	print "Error, unable to parse XML document.  Are you sure that's XCCDF?"
	sys.exit(-1)

benchmark = xml.getroot()
check_list = []
profile_name = "MAC-1_Classified"
profiles = benchmark.findall("{%s}Profile" % xmlns)
for profile in profiles:
	if profile.get("id") == profile_name:
		#<select idref="V-761" selected="true"/>
		selects = profile.findall("{%s}select" % xmlns)
		for select_tag in selects:
			if select_tag.get("selected") == "true":
				check_list.append(select_tag.get('idref'))
					
groups = benchmark.findall("{%s}Group" % xmlns)



csvfile = open('tmp.csv', 'wb')
output = csv.writer(csvfile, dialect='excel')
output.writerow(('STIG ID', 'Version', 'Rule Title', 'Title', 'Severity', 'Check Text', 'Fix Text', 'CCI'))
for group in groups:
	group_id = group.get("id")
	if group_id in check_list:
		title = group.find("{%s}title" % xmlns).text
		severity = group.find("{%s}Rule" % xmlns).get("severity")
		version = group.find("{%s}Rule/{%s}version" % (xmlns, xmlns)).text
		rule_title = group.find("{%s}Rule/{%s}title" % (xmlns, xmlns)).text
		desctag = "{%s}Rule/{%s}description" % (xmlns, xmlns)
		fixtext = group.find("{%s}Rule/{%s}fixtext" % (xmlns, xmlns)).text
		try:
			check = group.find("{%s}Rule/{%s}check/{%s}check-content" % (xmlns, xmlns, xmlns)).text
			cci = group.find("{%s}Rule/{%s}ident" % (xmlns, xmlns)).text
		except:
			check = "(Missing - did you use an OVAL benchmark instead of a Manual XCCDF?)"
			cci = "(Missing CCI Number may be an older STIG)"
		descriptiontext = group.find(desctag).text
		encodedDesc = descriptiontext.replace("&gt;", ">").replace("&lt;", "<").replace("&", "&amp;")
		innerXML = "<desc>%s</desc>" % format(encodedDesc)
		xml = ET.XML(innerXML)
		iacontrols = xml.find("IAControls").text
		vulndisc = xml.find("VulnDiscussion").text

		output.writerow( (group_id.replace('\n', '##').replace('V-',''), version.replace('\n', '##'), rule_title.replace('\n', '##'), title.replace('\n', '##'), severity.replace('\n', '##'), check, fixtext, cci) )
