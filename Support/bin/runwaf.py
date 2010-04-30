#!/usr/bin/python
# -*- coding: utf-8 -*-

# You should run this from the directory containing waf.

import sys, os, os.path
import htmlentitydefs # for html special char support

rootdir = os.getcwd()

# find waf
filenames = os.listdir( rootdir )
filenames = [ filename for filename in filenames if filename[0:4] == "waf-" ]
filenames = [ filename for filename in filenames if os.path.isfile( filename ) ]

if len( filenames ) > 1:
	print "More than one potential waf instance (" + ','.join( filenames ) + ") found.  Quitting."
	sys.exit( -1 )
elif len( filenames ) == 0:
	print "No potential waf instances found.  Quitting."
	sys.exit( -1 )

waf_filename = filenames[0]
waf_command = "cd " + rootdir + " && ./" + waf_filename + " -pp" # ide mode output.

sys.stdout.write(
"""<html>
	<head>
		<style type="text/css">
			div#errors > div {
				border: 1px solid red ;
				margin: 2px ;
				padding: 4px ;
			}
			
			#diagnostics > div {
				width: 100px;
				height: 10px;
				margin-left: 10px;
				float: left ;
				font-size: 10px ;
			}
		</style>
		<script>
			function getElement( name ) {
				return document.getElementById( name ) ;
			}

			function appendToElt( elt, text ) {
				div = document.createElement( 'div' ) ;
				div.innerText = text ;
				getElement( elt ).appendChild( div ) ;
			}

			var waf_progress_line_regexp = /^\|Total ([0-9]*)\|Current ([0-9]*)\|Inputs ([^|]*)\|Outputs ([^|]*)\|Time ([^|]*)\|/
			var waf_finished_regexp = /.*finished successfully/
			var gcc_warning_regexp = /[^:]*: warning:/
			var gcc_error_regexp = /[^:]*: error:/
			var link_error_regexp = /ld returned ([0-9]*) exit status/
			var file_location_regex = /([^:]*):([0-9]+):(.*)/

			var buffer = "" ;
			var warnings = new Array() ;
			var errors = new Array() ;
			
			function endHandler( object ) {
				outputHandler( object.outputString ) ;
			}
			
			function outputHandler( line ) {
				if( line.search( waf_progress_line_regexp ) != -1 ) {
					var line_data = {
						
					}
					var total = parseInt( line.replace( waf_progress_line_regexp, '$1' ) ) ;
					var current = parseInt( line.replace( waf_progress_line_regexp, '$2' ) ) ;
					
					var ratio = current / total ;
					getElement( 'bar' ).style.width = ( ratio * 496 ) + "px" ;
					getElement( 'progresscount' ).innerText = current + '/' + total ;
					
					getElement( 'timedisplay' ).innerText = line.replace( waf_progress_line_regexp, '($5)' )
				}
				else if( line.search( waf_finished_regexp ) != -1 ) {
					getElement( 'bar' ).style.width = ( 496 ) + "px" ;
					getElement( 'progresscount' ).innerText = 'finished' ;
					
				}
				else if( line.substring( 0, 3 ) == 'Waf' ) {
					appendToElt( 'output', line ) ;
				}
				else {
					buffer += line ;
				}
				
				if( line.search( gcc_error_regexp ) != -1 || line.search( link_error_regexp ) != -1 ) {
					errors[ errors.length ] = buffer ;
					getElement( 'error_count' ).innerText = errors.length + " errors" ;

					errorDiv = document.createElement( 'div' )
					lines = buffer.split( '\\n' ) ;
					for( var i = 0; i < lines.length; ++i ) {
						d = document.createElement( 'div' ) ;
						if( lines[i].search( file_location_regex ) != -1 ) {
							a = document.createElement( 'a' ) ;
							a.href = lines[i].replace( file_location_regex, "txmt://open/?url=file://%s/$1&line=$2" ) ;
							a.innerText = lines[i].replace( file_location_regex, "$1:$2" ) ;
							d.appendChild( a ) ;
							p = document.createElement( 'p' ) ;
							p.innerText = lines[i].replace( file_location_regex, ":$3" ) ;
							d.appendChild( p ) ;
						}
						else {
							d.innerText = lines[i] ;
						}
						errorDiv.appendChild( d ) ;
					}
					getElement( "errors" ).appendChild( errorDiv ) ;
					getElement( "errors" ).style.visibility = "visible" ;
					buffer = "" ;
				}
				else if( line.search( gcc_warning_regexp ) != -1 ) {
					warnings[ warnings.length ] = buffer ;
					buffer = "" ;
					getElement( 'warning_count' ).innerText = warnings.length + " warnings" ;
				}
			}
			
			function runWaf() {
				cmd = "%s" ;
				pretty_cmd = "%s" ;
				subtitle = document.createElement( 'div' ) ;
				subtitle.innerText = "Running command " + pretty_cmd + "...";
				getElement( "overview" ).appendChild( subtitle ) ;
				process = TextMate.system( cmd, endHandler ) ;
				process.onreadoutput = outputHandler ;
				process.onreaderror = outputHandler ;
			}
			
			function showWarnings() {
				getElement( "warnings" ).style.visibility = "visible" ;
			}
		</script>
	</head>
	<body onLoad="runWaf() ; ">
		<div id="overview">
			<h1>Building project...</h1>
		</div>
		<div id="progress" style="width: 800px; height: 20px" >
			<div style="width: 500px; height: 10px; border: 1px solid black; float: left;">
				<div id="bar" style="width:0px; height: 6px; margin: 1px ; border: 1px dotted black; background-color: #AA99EE; " >
				</div>
			</div>
			<div id="progresscount" style = "width: 70px; height: 10px ; margin-left: 10px; float: left ; font-size: 10px ;" >
			</div>
			<div id="timedisplay" style = "width: 70px ; height: 10px ; margin-left: 10px; float:left ; font-size: 10px ;">
			</div>
		</div>
		<div id="diagnostics" style="width: 800px; height: 20px">
			<div id="error_count" >
			</div>
			<div id="warning_count" onClick = "showWarnings() ;" >
			</div>
		</div>
		<div id="output">
			<div id="errors" style="visibility:hidden ; border: 5px solid grey; margin: 5px ; padding: 5px ;">
			</div>
			<div id="warnings" style="visibility:hidden ; border: 5px solid grey; margin: 5px ; padding: 5px ;">
			</div>
		</div>
		<div id="outcome">
		</div>
	</body>
</html>
""" % ( os.path.join( rootdir, 'build' ), waf_command, "\\\"" + waf_filename + " -pp\\\"" )
)
