#!/usr/bin/python3 -u

import argparse
import sys
import subprocess
import socket
import os
import errno
import cups


__author__ = "Jakobus Schuerz <jakobus.schuerz@gmail.com>"
__version__ = "0.01.0"


# Useful for very coarse version differentiation.
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
PY34 = sys.version_info[0:2] >= (3, 4)


if PY3:
    from configparser import ConfigParser
else:
    from ConfigParser import ConfigParser

def s2bool(s):
    return s.lower() in ['true','yes','y','1'] if s else False

class Error(Exception):
    pass

class ESETPRINTER(Error):
    def __init__(self):
        print("ERROR - Setting default printer" )
    pass

class ENOCFILE(Error):
    def __init__(self):
        print("ERROR - No connection-file found" )
    pass

class CaseConfigParser(ConfigParser): 
    def optionxform(self, optionstr): 
        return optionstr

class Config():
    def __init__(self, conf='', nmconf='/etc/NetworkManager/NetworkManager.conf'):
        if nmconf == None: 
            raise ENOCFILE
        elif conf == nmconf:
            #print("Work on NetworkManager.conf")
            self.won = True #won = work on NetworkManager.conf
        else:
            self.won = False

        if os.path.exists(nmconf): 
            self.nmconf = CaseConfigParser()
            self.nmconf.read(nmconf)
        else:
            print('Missing config: %s' % (nmconf))
            raise ENOCFILE

        if os.path.exists(conf): 
            self.conffile = conf
            self.conf = CaseConfigParser()
            self.conf.read(conf)
        else:
            print('Missing config: %s' % (conf))
            raise ENOCFILE

        self.nmpr = self.getDefaultPrinter(c=self.nmconf)
        self.cpr = self.getDefaultPrinter(c=self.conf)

    def getDefaultPrinter(self,c=None):
        if 'custom' in c:
            if 'DefaultPrinter' in c['custom']:
                return(c['custom']['DefaultPrinter'])
            else:
                return(None)

    def getPrinter(self):
        #print(self.cpr,self.nmpr)
        if self.cpr == None:
            if self.nmpr == None:
                return None
            else:
                return self.nmpr
        else:
            return self.cpr

    def setPrinter(self,printer=None,nm=False):
        if printer == None:
            self.conf.remove_option('custom','DefaultPrinter')
            if len(self.conf.options('custom')) == 0:
                self.conf.remove_section('custom')
        else:
            if not self.conf.has_section('custom'):
                self.conf.add_section('custom')
            self.conf.set('custom','DefaultPrinter',printer)
        self.WriteConfig(nm=nm) #Write config directly to file

    def changePrinter(self,printer=None):
        if printer == None and self.getPrinter() == None:
            print("No printer to set a default")
        else:
            cmd = ['lpadmin','-d',self.getPrinter() if printer == None else printer]
            #print(cmd)
            try:
                res = subprocess.Popen(cmd,stdout=subprocess.PIPE, stderr=None)
                #res = subprocess.Popen(cmd,stdout=None, stderr=None)
                output,error = res.communicate()
                if res.returncode > 0:
                    raise ESETPRINTER
                else:
                    print("Default-printer set to: %s" % (self.getPrinter() if printer == None else printer))
            except:
                raise

    def PrintConfig(self,nm=False):
        for i in self.nmconf if nm else self.conconf:
            print(i)
            for j in self.nmconf[i] if nm else self.conconf[i]:
                print(j+':',self.nmconf[i][j] if nm else self.conconf[i][j])

    def WriteConfig(self,nm=False):
        with open(self.conffile, 'w') as configfile:
            try:
                    self.conf.write(configfile)
            except:
                #raise ESETPRINTER
                exit("Failure during write config: %s" % (configfile))


def setPrinter(args):
    for i in args.cf:
        CONF = Config(conf = i)
        CONF.setPrinter(printer=args.printer)

def getPrinter(args):
    for i in args.cf:
        CONF = Config(conf=i)
        print(CONF.getPrinter())

def changePrinter(args):
    for i in args.cf:
        CONF = Config(conf = i)
        CONF.changePrinter(printer=args.printer)

con= cups.Connection()

parser = argparse.ArgumentParser()
parser.add_argument('--version', action='version', version='0.1.0')
parser.add_argument('-u', '--conn-uuid', dest='connuuid', metavar='CON_UUID',
        nargs='+', action='append', help="""one or more uuids of nm-connections""")
parser.add_argument('-i', '--conn-name', dest='connname', metavar='CON_ID', 
        nargs='+', action='append', help="""one or more id's of nm-connections""")
parser.add_argument('-f', '--conn-file', dest='connfile', metavar='CON_FILE', 
        nargs='+', action='append', help="""one or more files of nm-connections, absolute or relative to
        /etc/NetworkManager/systemd-connections""")
parser.add_argument('-p', '--printer', metavar='CUPS-Printer-Name',
        dest='printer', default=None, help="""CUPS Printer-Name to set default-Printer for
        connections. This printers are: %s""" % ('\n'.join(con.getPrinters().keys())))
#parser.add_argument('-p', '--printer', metavar='CUPS-Printer-Name',
#        dest='printer', default=None, help="""CUPS Printer-Name to set default-Printer for
#        connections.""")
parser.add_argument('-C', action='store_true', default=False, help="""Change
        the DefaultPrinter according to settings in
        network-manager-config-files""")
parser.add_argument('-S', action='store_true', default=False, help="""Set
        the DefaultPrinter for Network-Manager or Connection (if CONN_FILE is
        given)""")
parser.add_argument('-G', action='store_true', default=False, help="""Get
        the DefaultPrinter""")

if __name__ == '__main__':
    args = parser.parse_args()
    args.nmpath = '/etc/NetworkManager'
    args.scpath = args.nmpath+'/system-connections'
    args.nmcpath = args.nmpath+'/NetworkManager.conf'
    
    if args.connuuid == None: 
        args.connuuid = list()
    else:
        args.connuuid =  [item for sublist in args.connuuid for item in sublist]

    if args.connname == None: 
        args.connname = list()
    else:
        args.connname =  [item for sublist in args.connname for item in sublist]

    if args.connfile == None: 
        args.connfile = list()
    else:
        args.connfile =  [item for sublist in args.connfile for item in sublist]

    if len(args.connuuid) == 0 and len(args.connname) == 0 and len(args.connfile) == 0:
        args.setprinter = 'unset'
    else:
        args.setprinter = 'set'

    nmconfiles = dict()
    for i in os.listdir(args.scpath):
        nmconfiles[i] = CaseConfigParser()
        nmconfiles[i].read(args.scpath+'/'+i)

    for i in nmconfiles.keys():
        for n in args.connname:
            if n == nmconfiles[i]['connection']['id']: 
                args.connfile.append(i)
        for u in args.connuuid:
            if u == nmconfiles[i]['connection']['uuid']: 
                args.connfile.append(i)

    args.cf = list()

    if len(args.connfile) == 0:
        args.cf.append(args.nmcpath)
    else:
        for f in set(args.connfile):
            if f[0] == '/' and os.path.isfile(f):
                args.cf.append(f)
                continue
            elif os.path.isfile(args.scpath+'/'+f):
                args.cf.append(args.scpath+'/'+f)
                continue
            else:
                print('not found: %s' % (f))

    #print(args)
    if args.S:
        #print('Set Printer')
        setPrinter(args)
    elif args.C:
        #print('Change Printer')
        changePrinter(args)
    elif args.G:
        #print('Get Printer')
        getPrinter(args)

#print("--- finished ---")
