#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys 

if len( sys.argv ) > 1:
	project_dir = sys.argv[1]
else:
	project_dir = ""

def parse_progress_line( line ):
	bits = line.split('|')
	result = '<p>'
	for bit in bits:
		result += bit + " "
	result += '</p>\n'
	return result

def parse_dir_line( line ):
	openquote = line.find( "`" )
	closequote = line.find( "'" )
	if openquote >= closequote:
		print "Error on \"Entering directory\" line: open quote is after close quote."
		sys.exit(-1)
	return '<p>' + 'dir: ' + line[ openquote + 1: closequote ] + '</p>\n'

def replace_quoted_regions( line ):
	result = u""
	openquote = line.find( u"\u2018" )
	while openquote != -1:
		closequote = line.find( u"\u2019", openquote + 1)
		if closequote != -1:
			quoted_region = line[ openquote + 1: closequote ]
			result += line[0 : openquote] + '<b>' + quoted_region + '</b>'
			line = line[ closequote + 1: ]
		else:
			break
	result += line
	return result 

def read_filename_from_line( filename ):
	if len( filename ) > 3 and filename[0:3] == '../':
		filename = filename[3:]
	filename = project_dir + "/" + filename
	return filename 

def parse_diagnostic_line( line ):
	pos = line.find( ':' )
	if pos != -1:
		filename = read_filename_from_line( line[0:pos] )

		line = line[ pos+1 : ]
		line_number = None
		pos2 = line.find( ':' )
		if pos2 != -1:
			try:
				line_number = int( line[0:pos2] )
				line = line[ pos2 + 1: ]
			except:
				line_number = None
				pass

		line = replace_quoted_regions( line )
		
		if line_number is not None:
			result = (
				'<p><a href="txmt://open/?url=file://'
				+ filename
				+ '&line='
				+ str(line_number)
				+ '">'
				+ filename
				+ ':'
				+ str( line_number )
				+ '</a>: '
				+ line
				+ '</p>\n'
			)
		else:
			result = (
				'<p><b>'
				+ filename
				+ '</b>'
				+ ':'
				+ line
				+ '</p>\n'
			)
			
	else:
		result = '<p>' + line + '</p>\n'

	return result


def main():
	
	
	sys.stdout.write( '<html><head></head><body>')

	for line in sys.stdin:
		line = line.strip()
		line = line.decode( 'utf-8' )
		if len( line ) == 0:
			pass
		elif line[0] == '|':
			sys.stdout.write( parse_progress_line( line ).encode( 'utf-8' ))
		elif line.find( "Entering directory" ) != -1:
			sys.stdout.write( parse_dir_line( line ).encode( 'utf-8' ))
		else:
			sys.stdout.write( parse_diagnostic_line( line ).encode( 'utf-8' ))

		sys.stdout.flush()

	sys.stdout.write( '<html><head></head></body>')

if __name__ == "__main__":
	main()

