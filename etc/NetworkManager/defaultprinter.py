#!/usr/bin/python3 -u

import argparse
import sys
import subprocess
import socket
import os
import errno

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

class SetPrinterError(Error):
    def __init__(self):
        print("ERROR - Setting default printer" )
    pass

class Config():
    def __init__(self,nmconf='/etc/NetworkManager/NetworkManager.conf',conn='', setprinter='unset'):
        self.printer = None
        self.setprinter = setprinter
        self.nmcfile = nmconf
        self.concfile = conn
        #self.nmcfile = '/tmp/nmc'
        #self.concfile = '/tmp/conc'
        self.nmconf = ConfigParser()
        self.nmconf.read(nmconf)

        self.conn = conn
        self.conconf = ConfigParser()

        if os.path.exists(nmconf): 
            self.nmconf.read(nmconf)
        else:
            print('Missing config: %s' % (self.nmconf))
        
        if os.path.exists(conn): 
            self.conconf.read(self.conn)
        self.dp = self.getNMDefaultPrinter()

    def getNMDefaultPrinter(self):
        ret = list()
        for i in self.nmconf:
            if i == 'custom' and self.nmconf.has_option('custom','DefaultPrinter'):
                ret.append(self.nmconf.get(i,'DefaultPrinter').strip('''"' '''))
        return None if len(ret) == 0 else ret[len(ret)-1]
            

    def getPrinter(self,nm=False):
        if self.conn != '' or self.setprinter == 'unset':
            for i in self.conconf:
                if i == 'custom':
                    self.printer = self.conconf.get(i,'DefaultPrinter').strip('''"' ''')
            return(self.dp if self.printer == None else self.printer)
        else:
            return(self.dp)

    def setPrinter(self,printer=None,nm=False):
        if printer == None:
            if nm:
                self.nmconf.remove_option('custom','DefaultPrinter')
                if len(self.nmconf.options('custom')) == 0:
                    self.nmconf.remove_section('custom')
            else:
                self.conconf.remove_option('custom','DefaultPrinter')
                if len(self.conconf.options('custom')) == 0:
                    self.conconf.remove_section('custom')
        else:
            if nm:
                self.nmconf['custom'] = {'DefaultPrinter':printer}
            else:
                self.conconf['custom'] = {'DefaultPrinter':printer}
        self.WriteConfig(nm=nm) #Write config directly to file

    def changePrinter(self):
        cmd = ['lpadmin','-d',self.getPrinter()]
        #print(cmd)
        try:
            res = subprocess.Popen(cmd,stdout=subprocess.PIPE,
                    stderr=None)
            output,error = res.communicate()
            if res.returncode > 0:
                raise SetPrinterError
            else:
                print("Default-printer set to: %s" % (self.getPrinter()))
        except:
            raise

    def PrintConfig(self,nm=False):
        for i in self.nmconf if nm else self.conconf:
            print(i)
            for j in self.nmconf[i] if nm else self.conconf[i]:
                print(j+':',self.nmconf[i][j] if nm else self.conconf[i][j])

    def WriteConfig(self,nm=False):
        with open(self.nmcfile if nm else self.concfile, 'w') as configfile:
            try:
                if nm:
                    self.nmconf.write(configfile)
                else:
                    self.conconf.write(configfile)
            except:
                exit("Failure during write config: %s" % (configfile))


def setPrinter(args):
    for i in args.cf:
        if args.setprinter == 'set':
            X = Config(conn=i,setprinter='set')
            nm = False
    if args.setprinter == 'unset':
        X = Config()
        nm = True
    X.setPrinter(printer=args.printer,nm=nm)

def getPrinter(args):
    for i in args.cf:
        if args.setprinter == 'set':
            X = Config(conn=i,setprinter='set')
            nm = False
            print(X.getPrinter(nm=nm))
    if args.setprinter == 'unset':
        X = Config()
        nm = True
        print(X.getPrinter(nm=nm))
    
    #X = Config(setprinter='set')
    #print(X.getPrinter())

def changePrinter(args):
    if args.setprinter == 'set':
        X = Config(conn=args.cf[0],setprinter='set')
    else:
        X = Config()
    X.changePrinter()



parser = argparse.ArgumentParser()
parser.add_argument('--version', action='version', version='0.1.0')
parser.add_argument('-u', '--conn-uuid', dest='connuuid', metavar='CON_UUID',
        nargs='+', action='append', help="""one or more uuids of nm-connections""")
parser.add_argument('-n', '--conn-name', dest='connname', metavar='CON_NAME', 
        nargs='+', action='append', help="""one or more names of nm-connections""")
parser.add_argument('-f', '--conn-file', dest='connfile', metavar='CON_FILE', 
        nargs='+', action='append', help="""one or more files of nm-connections, absolute or relative to
        /etc/NetworkManager/systemd-connections""")
parser.add_argument('-p', '--printer', metavar='CUPS-Printer-Name',
        dest='printer', help='''CUPS Printer-Name to set default-Printer for
        connections''')
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
        nmconfiles[i] = ConfigParser()
        nmconfiles[i].read(args.scpath+'/'+i)

    #print(args.connname, args.connuuid)
    for i in nmconfiles.keys():
        #print('A',i,nmconfiles[i]['connection']['id'],nmconfiles[i]['connection']['uuid'])
        for n in args.connname:
            #print('B',n[0],nmconfiles[i]['connection']['id'])
            if n == nmconfiles[i]['connection']['id']: 
                args.connfile.append(i)
        for u in args.connuuid:
            #print('C',u)
            if u == nmconfiles[i]['connection']['uuid']: 
                args.connfile.append(i)

    args.cf = list()

    for f in set(args.connfile):
        if f[1] == '/':
            if os.path.isfile(f):
                args.cf.append(f)
                continue
        elif os.path.isfile(args.scpath+'/'+f):
            args.cf.append(args.scpath+'/'+f)
            continue
        else:
            print('not found: %s' % (f))

    #print(args.setprinter)
    if args.C:
        #print('Change Printer')
        changePrinter(args)
    elif args.S:
        #print('Set Printer')
        setPrinter(args)
    elif args.G:
        #print('Get Printer')
        getPrinter(args)

#    if args.P and setprinter == 'set':
#        for i in args.connfile:
#            X = Config(conn=i,setprinter=setprinter)
#            print(X.changePrinter())
#    elif args.P and setprinter == 'unset':
#        X = Config()
#        print(X.changePrinter())
#    else:
#        print('irgendwas anderes')
