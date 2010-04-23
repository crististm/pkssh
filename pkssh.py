#!/usr/bin/env python


# Copyright (c) 2010 by Cristian Stoica <crististm@gmail.com>
#
# This program is distributed under the terms of the
# GNU General Public License version 2


"""This module allows you to run processes and perform file operations
on a remote machine using a secured SSH connection.
The interface tries to mimic that of subprocess module."""


import os
import paramiko


class SSH(paramiko.SSHClient):
    def __init__(self, *args, **kwargs):
        super(SSH, self).__init__()
        self.load_system_host_keys()
        self.connect(*args, **kwargs)

    def Popen(self, *args, **kwargs):
        return _Popen(self, *args, **kwargs)

    def SFTP(self, *args, **kwargs):
        return _SFTP.from_transport(self.get_transport())

    def __enter__(self):
        """Support for with statement. Returns the connection"""
        return self

    def __exit__(self, type, value, traceback):
        """Support for with statement. Closes the connection"""
        self.close()

    def __del__(self):
        """Attempt to clean up if not explicitly closed."""
        self.close()


class _Popen(object):
    def __init__(self, ssh, cmd, user=None, sudo_opts="-n"):
        self.chan = ssh.get_transport().open_session()
        self.returncode = None
        if user:
            cmd = "sudo -u %s %s %s" % (user, sudo_opts, cmd)
        self._exec_command(cmd)

    def _exec_command(self, cmd, bufsize=-1):
        self.chan.exec_command(cmd) 
        self.stdin = self.chan.makefile('wb', bufsize) 
        self.stdout = self.chan.makefile('rb', bufsize) 
        self.stderr = self.chan.makefile_stderr('rb', bufsize) 

    def poll(self):
        if self.returncode is None:
            if self.chan.exit_status_ready():
                self.returncode = self.chan.recv_exit_status()
        return self.returncode

    def wait(self):
        if self.returncode is None:
            self.returncode = self.chan.recv_exit_status()
        return self.returncode


class _SFTP(paramiko.SFTPClient):
    def put(self, localpath, remotepath=None, callback=None):
        """Wrapper for paramiko put method - sets default paths"""
        if not remotepath:
            remotepath = os.path.basename(localpath)
        super(_SFTP, self).put(localpath, remotepath, callback)

    def get(self, remotepath, localpath=None, callback=None):
        """Wrapper for paramiko get method - sets default paths"""
        if not localpath:
            localpath = os.path.basename(remotepath)
        super(_SFTP, self).get(remotepath, localpath, callback)



def _demo_test():
    remote = SSH("localhost")
   
    p = remote.Popen("whoami")
    p.wait()
    print p.stdout.read()
    print p.stderr.read()

    sftp = remote.SFTP()
    sftp.chdir("/")
    print sftp.listdir()


if __name__ == "__main__":
    _demo_test()
