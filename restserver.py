#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#
# restserver.py 
# Author: Albert Lukaszewski
#
# Permission is granted to use this server for any purpose provided
# the following conditions are met:
#
# 1. You notify the author of this server at alukaszewski@gmail.com
#    and briefly let him know how you are using the server.
# 2. You do not remove this licence from the code.
# 3. Changes made to the code do not negate its ability to function as
#    a HTTP server that handles REST-patterned URIs and that processes
#    I/O based on JSON.
# 4. Any changes made to the code of this server become part of the
#    base code of the server.
# 5. All proprietary code should be imported into the server so as to
#    avoid becoming part of the server's base code.
# 6. You avail the base code of the server freely to anyone who asks
#    for it under these same conditions and without any further
#    conditions being stipulated.
'''
A HTTP server that receives a REST request and replies with a JSON
encoded reply.

Usage: restserver.py [options]

Options:
  -h, --help            show this help message and exit

  -p SERVER_PORT
  --port=SERVER_PORT    Set the port on which the server is to run.   (default
                        = 65000)
                        
  -o LOG_OUTPUT
  --log=LOG_OUTPUT      Turn logging on and off.  Must be switched on in order 
                        for other logging options like -l, -v, and -d to work.
                        (1 = yes, 0 = no, default = 0/no)
                        
  -l SERVER_LOG         
  --Logfile=SERVER_LOG  Set the file to which the log is to be written.  Note:
                        LOG_OUTPUT (-o) must be switched on for this file setting
                        to be effective.   (default = "./restserver.log")
                        
  -s NO_SSL
  --ssl-off=NO_SSL      Set whether HTTP is to be used instead of HTTPS.  (1 =
                        SSL off, 0 = SSL on, default = 0/on)
                        
  -d DEV_STATUS
  --development=DEV_STATUS
                        Set whether the server is being used for development.  
                        When switched to development, copious output is written 
                        to the log.  When set for deployment, one line for each 
                        of input and output is written for each request.  Note:
                        LOG_OUTPUT (-o) must be switched on for this setting to 
                        be effective.  (1 = development, 0 = deployment, 
                        default = 0/deployment)
'''


# To create a basic HTTP server.
from BaseHTTPServer import (HTTPServer, BaseHTTPRequestHandler)
# Use SimpleCookie for cookie handling
from Cookie import SimpleCookie
# Use datatime for timing of events
from datetime import datetime
# Use sundry functions from json for serialized I/O
from json import (dumps, loads, JSONDecoder, JSONEncoder)
# Use optparse to parse CLI options
from optparse import OptionParser
# Use wrap_socket to encrypt communication
from ssl import wrap_socket
# Use stdout for output
from sys import stdout,stderr
# Use format_exc to format tracebacks when exceptions occur
from traceback import format_exc
# Use urlparse for rewriting URIs
from urlparse import urlparse

# Retrieve CLI Options
server = OptionParser()

server.add_option('-p', action = 'store', dest = 'server_port', help = 'Set the port on which the server is to run.\n (default = 65000)')
server.add_option('--port', action = 'store', dest = 'server_port', help = 'Set the port on which the server is to run.\n  (default = 65000)')

server.add_option('-l', action = 'store', dest = 'log_output', help = 'Set whether logging should be done.  Must be switched on in order for other logging options like -L, -v, and -d to work.\n (1 = yes, 0 = no, default = 0/no)')
server.add_option('--log', action = 'store', dest = 'log_output', help = 'Set whether logging should be done.  Must be switched on in order for other logging options like -L, -v, and -d to work.\n (1 = yes, 0 = no, default = 0/no)')

server.add_option('-L', action = 'store', dest = 'server_log', help = 'Set to which file the log is to be written.  Note that LOG_OUTPUT must be switched on for this file setting to be effective.\n (default = "./restserver.log")')
server.add_option('--Logfile', action = 'store', dest = 'server_log', help = 'Set to which file the log is to be written.  Note that LOG_OUTPUT must be switched on for this file setting to be effective.\n  (default = "./restserver.log")')

server.add_option('-s', action = 'store', dest = 'no_ssl', help = 'Set whether HTTP is to be used instead of HTTPS.\n (1 = SSL off, 0 = SSL on, default = 0/on)')
server.add_option('--ssl-off', action = 'store', dest = 'no_ssl', help = 'Set whether HTTP is to be used instead of HTTPS.\n (1 = SSL off, 0 = SSL on, default = 0/on)')

server.add_option('-d', action = 'store', dest = 'dev_status', help = 'Set whether the server is being used for development or deployment.  When switched for development, copious output is written to the log.  When switched to deployment, one line for each of input and output is written for each request.  Note that LOG_OUTPUT must be switched on for this setting to be effective.\n (1 = development, 0 = deployment, default = 0/deployment)')
server.add_option('--development', action = 'store', dest = 'dev_status', help = 'Set whether the server is being used for development or deployment.  When switched for development, copious output is written to the log.  When switched to deployment, one line for each of input and output is written for each request.  Note that LOG_OUTPUT must be switched on for this setting to be effective.\n (1 = development, 0 = deployment, default = 0/deployment)')

# Set Defaults
server.set_defaults(server_port = 65000)
server.set_defaults(server_log = 'restserver.log')
server.set_defaults(log_output = 0)
server.set_defaults(no_ssl = 0)
server.set_defaults(dev_status = 0)

# Assign values
opts, args = server.parse_args()
server_port = int(opts.server_port)
server_log = opts.server_log
log_output = int(opts.log_output)
no_ssl = int(opts.no_ssl)
dev_status = int(opts.dev_status)


# Redefine the error message template provided by
# BaseHTTPRequestHandler.  The formatting values are a dictionary with
# the following keys: 
# 1. code: The HTTP error code 
# 2. message: The message appropriate to the code 
# 3. explain: An explanation of what the code and message mean
#
# Each is referenced as follows: "Error code: %(code)"
#
# Here, the client is sent a redirection to Hacker News
#
BaseHTTPRequestHandler.error_message_format = '''
<html>
<head>
<meta http-equiv="Refresh" content="5;URL=http://news.ycombinator.com">
</head>
<body>
You are being redirected.  Please wait...
</body>
</html>
'''

# Redefine the server version and system version of
# BaseHTTPRequestHandler.  This allows us to spoof Apache and protect
# ourselves from potential hackery.
BaseHTTPRequestHandler.server_version = "Apache/2.2.22"
BaseHTTPRequestHandler.sys_version = "Ubuntu 12.04"

# BaseHTTPRequestHandler.responses assigned
BaseHTTPRequestHandler.responses[200] = ('OK', 
                                         'The request was successful.')
BaseHTTPRequestHandler.responses[201] = ('Created', 
                                         'The requested item was successfully created.')
BaseHTTPRequestHandler.responses[204] = ('Request fulfilled', 
                                         'The request was successfully fulfilled.')
BaseHTTPRequestHandler.responses[400] = ('Bad input parameter', 
                                         'Response will indicate details.')
BaseHTTPRequestHandler.responses[401] = ('Unauthorized', 
                                         'Bad or expired token.')
BaseHTTPRequestHandler.responses[403] = ('Bad OAuth request', 
                                         'Wrong key, bad nonce, or expired timestamp.')
BaseHTTPRequestHandler.responses[404] = ('Not found', 
                                         'Requested resource not found.')
BaseHTTPRequestHandler.responses[405] = ('Request method not valid', 
                                         'Incorrect use of GET/POST/PUT).')
#
# The 5xx errors are left at their defaults.
#

class RESTHandler(BaseHTTPRequestHandler):
    """
    In this class, one can implement any method that begins with do_*.
    Client requests that are not explicitly handled in the server code
    will end in an exception that is fielded by BaseHTTPRequestHandler
    by default.  
    """

    # As the JSON format is so similar a Python dictionary, we can use
    # MySQLdb's DictCursor to return dictionaries that can then be
    # converted into JSON.  For more information, see:
    # http://mysql-python.sourceforge.net/MySQLdb.html#using-and-extending
    def makeJSONfromDICT(self, resultsDict):
        """ Convert the dictionary output from the DB to a JSON string. """
        results = resultsDict

        records = {}

        for k,v in results.iteritems():
            records[k] = str(v)

        ajsondecoder = JSONEncoder()
        jsonout = ajsondecoder.encode(records)

        if log_output == 1:
            logfile = open(server_log, 'at')
            logfile.write("OUTPUT: \n")
            logfile.write(jsonout)
            logfile.write("\n\n")
            logfile.close()

        return jsonout

    def logInput(self):
        """ Log request data. Logged information includes the
        request's date, time, IP address, method, URI, and
        protocol."""

        if dev_status == 0:
            status_items = [str(datetime.now()), "IN", self.command, self.path, str(self.client_address)]
            headers = []
            for k in self.headers:
                headers.append(k + ': ' + self.headers[k])
            status_items.append(str(headers))
            status = '\t'.join(status_items)

        else:
            status = '\n#\n#\n'
            status += 'BEGIN REQUEST at %s\n\n' %(str(datetime.now()))
            now = str(datetime.now())
            status += 'INPUT:\n' + self.command + " request received: " + now + "\n"
            status += "SOURCE: " + str(self.client_address) + " using " + self.request_version + "\n"
            status += "URI: " + self.path + "\n"
            status += "HEADERS:\n" + str(self.headers)

        logfile = open(server_log, 'at')
        logfile.write(str(status) + '\n')
        logfile.close()       
        return True

    def logResponse(self,code,output):
        """ Log successful responses for requests received.  Logged
        data includes date, time, method, URI, IP, and status code."""
        if dev_status == 0:
            status_items = [str(datetime.now()), "OUT", self.command, self.path, str(self.client_address), code]
            status = '\t'.join(status_items)

        else:
            current_time = datetime.now()
            status = ('\nRESPONSE: Request succeeded with %s status.\n' %(code))
            status += 'OUTPUT: ' + str(output) + '\n\nEND REQUEST TIME: %s\n#\n#' %(str(datetime.now()))

        logfile = open(server_log, 'at')
        logfile.write(status + '\n')
        logfile.close()   
        return True

    def logFailure(self, code, message, exception):
        """ Log exceptions raised due to failed requests.  CLI options
        determine whether the full error and traceback are logged.
        The following data are always logged: date, time, method, URI,
        IP, error code, and any description of the exception."""
        exception_list = exception.split('\n')
        exception_length = len(exception_list)
        exception_type = exception_list[exception_length - 2]
        if exception_type.find('KeyError') != -1:
            missing_field = exception_list[exception_length-3]
            missing_field = missing_field.split('[')
            missing_field = missing_field[int(len(missing_field)-1)]
            missing_field = missing_field.replace("'", "")
            missing_field = missing_field.replace("]", "")
            message = "The following field are missing: %s" %(missing_field)
        elif exception_type.find('tuple index') != -1:
            message = "No matching data"
        else:
            message = exception_type


        if dev_status == 0:
            status_items = [str(datetime.now()), "OUT", self.command, self.path, str(self.client_address), str(code), str(message)]
            status = '\t'.join(status_items)

        else:
            status = ('\nRESPONSE: REQUEST FAILED WITH STATUS %s.\n'
                      'Check the format of both the URI and the body of your request.\n' %(int(code)))
            status += 'Further information follows:\n\nEXCEPTION: %s\n' %(message)
            status += ('If you receive this error code repeatedly and are certain that '
                       'the URI and data are not malformed, there may be a bug in this '
                       'functionality.  Please report it at somebox@somedomain.someTLD.\n')
            status += '\n\nEND REQUEST\n#\n#'

        logfile = open(server_log, 'at')
        logfile.write(status + '\n')
        logfile.close()
        return

    def do_GET(self):
        """ Process a GET request. """

        logit = self.logInput()
        status = ""

        # Parsing on the question mark allows us to use tags in the
        # URLs that are logged and so allow tracking but that do not
        # impact negatively on the server's functionality.
        self.path = self.path.split('?')[0]

        uriParts = self.path.split('/')

        # All URIs must have four parts.  If they don't, send a 404.
        # Only the first four parts of the URI are used.
        #
        # This server is developed for a REST API call like the following:
        #
        # METHOD http://www.somedomain.com/uriAgent/uriAgentID/uriObject/uriObjectID
        #
        # Effectively, each call is a sentence where the method is the
        # verb, the agent is the subject, and the object is the
        # recipient of the action.  So, for example, a user retrieving
        # a contact could be:
        #
        # GET http://www.restserver.tld/user/00123/contact/012345609
        #
        # In the present server, we use IDs for both agent and object
        # in order to allow us to use caches.  
        try:
            uriAgent = uriParts[1]
            uriAgentID = uriParts[2]
            uriObject = uriParts[3]
            uriObjectID = uriParts[4]
        except:
            self.send_error(404)
            return

        try:
            # Get the length of the data before reading it.  That is
            # contained in the headers of the request.
            inputlength = int(self.headers['content-length'])

            # MUST NOT try to read the rfile attribute without setting
            # the length.  Else the server hangs and waits for
            # unlimited input from the client.
            inputdata = self.rfile.read(inputlength)

            if dev_status != 0:
                status += "RECEIVED DATA: "
                status += inputdata
                status += "\n"
                logfile = open(server_log, 'at')
                logfile.write(status)
                logfile.close()

        # If no data segment is sent with the request, send a 400.
        except Exception as error:
            exc = format_exc()
            logit = self.logFailure('400', error, exc)
            self.send_error(404)
            return

        try:
            decodedata = inputdata
        except Exception as error:
            exc = format_exc()
            logit = self.logFailure('400', error, exc)
            self.send_error(400)
            return

        # Instantiate new JSONDecoder object to decode JSON object
        # into a dictionary.  
        ajsondecoder = JSONDecoder()
        jsondata = ajsondecoder.decode(decodedata)

        if dev_status != 0:
            logfile = open(server_log, 'at')
            logfile.write('DECODED DATA: ' + str(jsondata) + '\n')
            logfile.close()

        # Here we presume on the above example of an agent 'user' and
        # a series of objects on which that user can operate: profile,
        # contact, and sessionID.  Obviously, the details will depend
        # on the API being implemented.
        if uriAgent == 'user' and uriObject == 'profile':
            try:
                from get_user import get_user_profile
                agentID = str(uriAgentID)
                profile = get_user_profile(agentID, jsondata)

                output = self.makeJSONfromLIST("profiles", "profile", profiles)
                output = str(output)
                output_length = len(output)

                self.send_response(200) 
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', output_length)
                self.end_headers()
                self.wfile.write(output)

                logit = self.logResponse('200',output)

            except Exception as error:
                exc = format_exc()
                logit = self.logFailure('403', error, exc)
                self.send_error(403)
                return

        elif uriAgent == 'user' and uriObject == 'contact': 
            try:
                from get_user import get_user_contact
                agentID = str(uriAgentID)
                contact = get_user_contact(agentID, jsondata)
                if contact:

                    output = self.makeJSONfromDICT("contacts", "contact", contact)

                    output = str(output)
                    output_length = len(output)

                    self.send_response(200) 
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Content-Length', output_length)
                    self.end_headers()
                    self.wfile.write(output)

                    logit = self.logResponse('200',output)

                else:
                    error = 'Retrieval failed.'
                    exc = format_exc()
                    logit = self.logFailure('400', error, exc)
                    self.send_error(400)
                    return

            except Exception as error:
                exc = format_exc()
                logit = self.logFailure('403', error, exc)
                self.send_error(403)
                return

        elif uriAgent == 'user' and uriObject == 'sessionID': 
            try:
                from sessions import get_user_sessionID
                agentID = str(uriAgentID)
                sessionID = get_user_sessionID(uriObject)

                output = self.makeJSONfromDICT("sessions", "session", sessiondata)
                output = str(output)
                output_length = len(output)

                self.send_response(200) 
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', output_length)
                self.end_headers()
                self.wfile.write(output)

                logit = self.logResponse('200',output)

            except Exception as error:
                exc = format_exc()
                logit = self.logFailure('403', error, exc)
                self.send_error(403)
                return

        else: 
            self.send_error(404)
            return



    def do_PUT(self):
        """ Process a PUT request."""

        # NB: PUT actions and 204 codes do not allow for further
        # output than the status code.  

        logit = self.logInput()
        status = ""

        # Parsing on the question mark allows us to use tags in the
        # URLs that are logged and so allow tracking but that do not
        # impact negatively on the server's functionality.
        self.path = self.path.split('?')[0]

        uriParts = self.path.split('/')

        # All URIs must have four parts.  If they don't, send a 404.
        # Only the first four parts of the URI are used.
        #
        # This server is developed for a REST API call like the following:
        #
        # METHOD http://www.somedomain.com/uriAgent/uriAgentID/uriObject/uriObjectID
        #
        # Effectively, each call is a sentence where the method is the
        # verb, the agent is the subject, and the object is the
        # recipient of the action.  So, for example, a user retrieving
        # a contact could be:
        #
        # GET http://www.restserver.tld/user/00123/contact/012345609
        #
        # In the present server, we use IDs for both agent and object
        # in order to allow us to use caches.  
        try:
            uriAgent = uriParts[1]
            uriAgentID = uriParts[2]
            uriObject = uriParts[3]
            uriObjectID = uriParts[4]
        except Exception as error:
            self.send_error(404)
            return

        # All URIs must have four parts.  If they don't, send a 404.
        # Only the first four parts of the URI are used.
        #
        # This server is developed for a REST API call like the following:
        #
        # METHOD http://www.somedomain.com/uriAgent/uriAgentID/uriObject/uriObjectID
        #
        # Effectively, each call is a sentence where the method is the
        # verb, the agent is the subject, and the object is the
        # recipient of the action.  So, for example, a user changing
        # the details of a contact could be:
        #
        # PUT http://www.restserver.tld/user/00123/contact/012345609
        #
        # In the present server, we use IDs for both agent and object
        # in order to allow us to use caches.  
        status = '\n'
        now = str(datetime.now())
        status += self.command + " request received: " + now + "\n"
        status += "SOURCE: " + str(self.client_address) + " using " + self.request_version + "\n"
        status += "PATH: " + self.path + "\n"
        status += "HEADERS:\n" + str(self.headers) ## + "\n"


        try:
            # Must get the length of the data before reading it.
            inputlength = int(self.headers['content-length'])

            # MUST NOT try to read the rfile attribute without setting
            # the length.  Else the server hangs and waits for
            # unlimited input from the client.
            inputdata = self.rfile.read(inputlength)

            if dev_status != 0:
                status += "RECEIVED DATA: \n"
                status += inputdata
                status += "\n\n\n"

                logfile = open(server_log, 'at')
                logfile.write(status)
                logfile.close()

        # If no data segment is sent with the request, send a 404.
        except Exception as error:
            logfile = open(server_log, 'at')
            logfile.write(status)
            logfile.close()
            self.send_error(404)
            return

        try:
            # decodedata = loads(inputdata)
            decodedata = inputdata
        except Exception as error:
            exc = format_exc()
            logit = self.logFailure('400', error, exc)
            self.send_error(400)
            return

        # Instantiate new JSONDecoder object to decode JSON object
        # into a dictionary.  
        ajsondecoder = JSONDecoder()
        jsondata = ajsondecoder.decode(decodedata)

        if dev_status != 0:
            logfile = open(server_log, 'at')
            logfile.write('DECODED DATA: ' + str(jsondata) + '\n')
            logfile.close()
        # Here we presume on the above example of an agent 'user' and
        # a series of objects on which that user can operate: profile,
        # contact, and sessionID.  Obviously, the details will depend
        # on the API being implemented.
        if uriAgent == 'user' and uriObject == 'profile':
            try:
                from put_user import put_user_profile
                agentID = str(uriAgentID)
                profile = put_user_profile(agentID, jsondata)

                self.send_response(204) 

                logit = self.logResponse('204',output)

            except Exception as error:
                exc = format_exc()
                logit = self.logFailure('403', error, exc)
                self.send_error(403)
                return

        elif uriAgent == 'user' and uriObject == 'contact': 
            try:
                from put_user import put_user_contact
                agentID = str(uriAgentID)
                contact = put_user_contact(agentID, jsondata)

                self.send_response(204) 

                logit = self.logResponse('204',output)

            except Exception as error:
                exc = format_exc()
                logit = self.logFailure('403', error, exc)
                self.send_error(403)
                return

        elif uriAgent == 'user' and uriObject == 'sessionID': 
            try:
                from sessions import put_user_sessionID
                agentID = str(uriAgentID)
                sessionID = put_user_sessionID(uriObject)

                self.send_response(204) 

                logit = self.logResponse('204',output)

            except Exception as error:
                exc = format_exc()
                logit = self.logFailure('403', error, exc)
                self.send_error(403)
                return

        else:
            self.send_error(404)
            return

        return True


    def do_POST(self):
        """ Process a POST request. """

        # NB: POST actions take a 201 code and should return the
        # identifier of the object they create.

        logit = self.logInput()
        status = ""

        # Rewrite POST requests that use the "_m" argument.  The "_m"
        # stands for "method" and allows clients that cannot use the
        # full range of REST methods to access the REST API through a
        # modified POST call.

        parsed_path = urlparse(self.path)
        try:
            params = dict([p.split('=') for p in parsed_path[4].split('&')])
        except Exception as error:
            params = {}
        if params.get('_m'):
            if params['_m'] ==  'GET':
                self.command='GET'
                self.path=parsed_path.netloc + parsed_path.path
                self.do_GET();
                return True
            if params['_m'] ==  'PUT':
                self.command='PUT'
                self.path=parsed_path.netloc + parsed_path.path
                self.do_PUT();
                return True
            if params['_m'] ==  'DELETE':
                self.command='DELETE'
                self.path=parsed_path.netloc + parsed_path.path
                self.do_DELETE();
                return True
            if params['_m'] ==  'POST':
                self.command='POST'
                self.path=parsed_path.netloc + parsed_path.path
            else:
                self.send_error(404)
                return

        # Parsing on the question mark allows us to use tags in the
        # URLs that are logged and so allow tracking but that do not
        # impact negatively on the server's functionality.
        self.path = self.path.split('?')[0]

        uriParts = self.path.split('/')

        # All URIs must have four parts.  If they don't, send a 404.
        # Only the first four parts of the URI are used.
        #
        # This server is developed for a REST API call like the following:
        #
        # METHOD http://www.somedomain.com/uriAgent/uriAgentID/uriObject/uriObjectID
        #
        # Effectively, each call is a sentence where the method is the
        # verb, the agent is the subject, and the object is the
        # recipient of the action.  So, for example, a user creating
        # a contact could be:
        #
        # POST http://www.restserver.tld/user/00123/contact/0
        #
        # The zeroed out contact ID is because the contact does not
        # have an identifier yet.
        #
        # In the present server, we use IDs for both agent and object
        # in order to allow us to use caches.
        try:
            uriAgent = uriParts[1]
            uriAgentID = uriParts[2]
            uriObject = uriParts[3]
            uriObjectID = uriParts[4]
        except Exception as error:
            self.send_error(404)
            return

        try:
            # Get the length of the data before reading it.  That is
            # contained in the headers of the request.
            inputlength = int(self.headers['content-length'])

            # MUST NOT try to read the rfile attribute without a set
            # length.  Otherwise, the server will hang and wait for
            # unlimited input from the client.
            inputdata = self.rfile.read(inputlength)

            if dev_status != 0:
                status += "RECEIVED DATA: \n"
                status += inputdata
                status += "\n\n\n"
                logfile = open(server_log, 'at')
                logfile.write(status)
                logfile.close()

        # If no data segment is sent with the request, send a 404.
        except Exception as error:
            exc = format_exc()
            logit = self.logFailure('404', error, exc)
            self.send_error(404)
            return

        try:
            decodedata = inputdata
        except Exception as error:
            exc = format_exc()
            logit = self.logFailure('400', error, exc)
            self.send_error(400)
            return

        # Instantiate new JSONDecoder object to decode JSON object
        # into a dictionary.  
        ajsondecoder = JSONDecoder()
        jsondata = ajsondecoder.decode(decodedata)

        if dev_status != 0:
            logfile = open(server_log, 'at')
            logfile.write('DECODED DATA: ' + str(jsondata) + '\n')
            logfile.close()


        # Here we presume on the above example of an agent 'user' and
        # a series of objects on which that user can operate: profile,
        # contact, and sessionID.  Obviously, the details will depend
        # on the API being implemented.
        if uriAgent == 'user' and uriObject == 'profile':
            try:
                from post_user import post_user_profile
                agentID = str(uriAgentID)
                profile = post_user_profile(agentID, jsondata)

                output = self.makeJSONfromLIST("profiles", "profile", profiles)
                output = str(output)
                output_length = len(output)

                self.send_response(201) 
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', output_length)
                self.end_headers()
                self.wfile.write(output)

                logit = self.logResponse('201',output)

            except Exception as error:
                exc = format_exc()
                logit = self.logFailure('401', error, exc)
                self.send_error(401)
                return

        elif uriAgent == 'user' and uriObject == 'contact': 
            try:
                from post_user import post_user_contact
                agentID = str(uriAgentID)
                contact = post_user_contact(agentID, jsondata)
                if contact:

                    output = self.makeJSONfromDICT("contacts", "contact", contact)

                    output = str(output)
                    output_length = len(output)

                    self.send_response(201) 
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Content-Length', output_length)
                    self.end_headers()
                    self.wfile.write(output)

                    logit = self.logResponse('201',output)

                else:
                    error = 'POST failed.'
                    exc = format_exc()
                    logit = self.logFailure('403', error, exc)
                    self.send_error(403)
                    return

            except Exception as error:
                exc = format_exc()
                logit = self.logFailure('401', error, exc)
                self.send_error(401)
                return

        elif uriAgent == 'user' and uriObject == 'sessionID': 
            try:
                from sessions import post_user_sessionID
                agentID = str(uriAgentID)
                sessionID = post_user_sessionID(uriObject)

                output = self.makeJSONfromDICT("sessions", "session", sessiondata)
                output = str(output)
                output_length = len(output)

                self.send_response(201)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', output_length)
                self.end_headers()
                self.wfile.write(output)

                logit = self.logResponse('201',output)

            except Exception as error:
                exc = format_exc()
                logit = self.logFailure('401', error, exc)
                self.send_error(401)
                return

        else: 
            pass




    def do_DELETE(self):
        """ Process a DELETE request.  See the AccessMyTV 2.0 Server
        documentation for the functionality of this method. """

        # DELETE actions respond with a 204 status

        logit = self.logInput()
        status = ""

        # Parsing on the question mark allows us to use tags in the
        # URLs that are logged and so allow tracking but that do not
        # impact negatively on the server's functionality.
        self.path = self.path.split('?')[0]

        uriParts = self.path.split('/')

        # All URIs must have four parts.  If they don't, send a 404.
        # Only the first four parts of the URI are used.
        #
        # This server is developed for a REST API call like the following:
        #
        # METHOD http://www.somedomain.com/uriAgent/uriAgentID/uriObject/uriObjectID
        #
        # Effectively, each call is a sentence where the method is the
        # verb, the agent is the subject, and the object is the
        # recipient of the action.  So, for example, a user retrieving
        # a contact could be:
        #
        # GET http://www.restserver.tld/user/00123/contact/012345609
        #
        # In the present server, we use IDs for both agent and object
        # in order to allow us to use caches.  
        try:
            uriAgent = uriParts[1]
            uriAgentID = uriParts[2]
            uriObject = uriParts[3]
            uriObjectID = uriParts[4]
        except:
            self.send_error(404)
            return


        try:
            # Get the length of the data before reading it.  That is
            # contained in the headers of the request.
            inputlength = int(self.headers['content-length'])


            # MUST NOT try to read the rfile attribute without a set
            # length.  Otherwise, the server will hang and wait for
            # unlimited input from the client.
            inputdata = self.rfile.read(inputlength)

            if dev_status != 0:
                status += "RECEIVED DATA: \n"
                status += inputdata
                status += "\n\n\n"

                logfile = open(server_log, 'at')
                logfile.write(status)
                logfile.close()

        # If no data segment is sent with the request, send a 400.
        except Exception as error:
            logfile = open(server_log, 'at')
            status = "\n\n\n***** BAD REQUEST *****\n" + status + "\n***********************\n"
            logfile.write(status)
            logfile.close()
            self.send_error(400)
            return

        try:
            decodedata = inputdata
        except Exception as error:
            exc = format_exc()
            logit = self.logFailure('400', error, exc)
            self.send_error(400)
            return

        # Instantiate new JSONDecoder object to decode JSON object
        # into a dictionary.  
        ajsondecoder = JSONDecoder()
        jsondata = ajsondecoder.decode(decodedata)

        if dev_status != 0:
            logfile = open(server_log, 'at')
            logfile.write('DECODED DATA: ' + str(jsondata) + '\n')
            logfile.close()

        # Here we presume on the above example of an agent 'user' and
        # a series of objects on which that user can operate: profile,
        # contact, and sessionID.  Obviously, the details will depend
        # on the API being implemented.
        if uriAgent == 'user' and uriObject == 'profile':
            try:
                from delete_user import delete_user_profile
                agentID = str(uriAgentID)
                profile = delete_user_profile(agentID, jsondata)

                self.send_response(204) 

                logit = self.logResponse('204',output)

            except Exception as error:
                exc = format_exc()
                logit = self.logFailure('403', error, exc)
                self.send_error(403)
                return

        elif uriAgent == 'user' and uriObject == 'contact': 
            try:
                from delete_user import delete_user_contact
                agentID = str(uriAgentID)
                contact = delete_user_contact(agentID, jsondata)
                self.send_response(204) 
                logit = self.logResponse('204',output)

            except Exception as error:
                exc = format_exc()
                logit = self.logFailure('403', error, exc)
                self.send_error(403)
                return

        elif uriAgent == 'user' and uriObject == 'sessionID': 
            try:
                from sessions import delete_user_sessionID
                agentID = str(uriAgentID)
                sessionID = delete_user_sessionID(uriObject)
                self.send_response(204)
                logit = self.logResponse('204',output)

            except Exception as error:
                exc = format_exc()
                logit = self.logFailure('403', error, exc)
                self.send_error(403)
                return

        else: 
            pass


def main(server_class=HTTPServer, handler_class=RESTHandler):
    """
    The main() function instantiates the server and takes care of
    binding it to the port set above.  The wrap_socket() function of
    the SSL module is used to encrypt all communication using the
    specified certificate.

    """

    try:
        now = datetime.now()
        logfile = open(server_log, 'at')
        logfile.write("\n\n SERVER STARTED on Port %s : %s \n\n" %(server_port,now))
        logfile.close()
        server_address = ('', server_port)
        httpd = server_class(server_address, handler_class)
        # Wrap the socket for SSL
        #
        # A test certificate can be generated with the following incantation:
        # openssl req -new -x509 -days 30 -nodes -out timecert.pem -keyout restcert.pem
        #
        # Note:  The location of the certificate should be an absolute path.
        if no_ssl == 0:
           httpd.socket = wrap_socket(httpd.socket, certfile='/some/directory/with/an/absolute/path/restcert.pem', server_side=True)
        httpd.serve_forever()
        return True

    except (KeyboardInterrupt, SystemExit):
        now = datetime.now()
        logfile = open(server_log, 'at')
        logfile.write("\n SERVER HALTED : %s \n\n" %(now))
        logfile.close()


# Check whether the program has been called from the command line.  If
# so, call main().  Otherwise, Python allows this program to be
# imported as a module.
if __name__ == '__main__':
    main()


