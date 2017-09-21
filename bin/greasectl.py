#! /usr/bin/env python
import os
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
from tgt_grease_daemon.GreaseRouter import Router


class AppServerSvc (win32serviceutil.ServiceFramework):

    _svc_name_ = "GreaseDaemon"
    _svc_display_name_ = "GREASE Daemon Server"
    _svc_description_ = "GREASE Async Daemon Server for Automation Work"

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_,''))
        self.main()

    def main(self):
        if 'install' not in sys.argv:
            s = Router()
            s.job_processor(self)
        else:
            return

if os.name == 'nt':
        print sys.argv
        if 'install' not in sys.argv:
            win32serviceutil.HandleCommandLine(AppServerSvc, argv=['', 'start'])
        else:
            win32serviceutil.HandleCommandLine(AppServerSvc)
else:
    s = Router()
    s.entry_point()