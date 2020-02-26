#!/opt/support/python37/bin/python3
#############################################
## Author: Harikishan Mulagada
## Role  : Staff Engineer SteelCentral
##
##############################################

import os
import re
import sqlite3
import zipfile
import shutil
import json
import time
import sys
import datetime
from bokeh.plotting import figure, output_file, save
from bokeh.layouts import column
from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.palettes import Dark2_5 as palette
import itertools

start = time.time()

##Function to create a directory to extract the zip file
def createdir(filepath):
        try:
                print('Creating folder to extract... ')
                os.chdir(os.path.dirname(os.path.abspath(filepath)))

                workdir = os.path.abspath(os.path.dirname(os.path.abspath(filepath))+'/'+os.path.basename(filepath).split('.zip')[0])
                if not os.path.exists(workdir):
                        os.makedirs(workdir)
        except OSError as e:
                if e.errno !=errno.EEXIST:
                        raise
        return workdir

##Delete all previously extracted folders
def cleanup(filepath,filename,errorandwarn):

    os.chdir(os.path.dirname(os.path.abspath(filepath)))

    extrctdir = os.path.basename(filepath).split('.zip')[0]
    folderstodelete = ['appserver_logs','commands','cores','files',extrctdir]
    cwd = os.getcwd()
    
    for fdname in os.listdir(cwd):
        if (os.path.isdir(os.path.abspath(fdname)) and (fdname in folderstodelete)):
            print('Deleting folder',os.path.abspath(fdname))
            shutil.rmtree(os.path.abspath(fdname),ignore_errors=False)


    for fname in os.listdir(cwd):
        if (fname.endswith('.txt') and (fname.find(filename)!=-1 or fname.find(errorandwarn)!=-1)):
            os.remove(fname)            

##Unzip the diag bundle zip file
def unzip(filepath):
    filesizedict = {}
      
    tmp_dir = createdir(filepath)

    print('Unzipping bundle..')
    
    zfile = zipfile.ZipFile(filepath)
    zfile.extractall(tmp_dir)
   
    os.chdir(os.path.abspath(tmp_dir))
 
    try:
        for file_name in zfile.namelist():
                info = zfile.getinfo(file_name)
                if (float(info.file_size)/1000000)>50.0:
                        filesizedict.update({info.filename:float(info.file_size)/1000000})
    except Exception as e:
        print(e)
   
    zfile.close()

    print('Finished unzipping the bundle...')

    return(tmp_dir)

##Use to open a file for any function
def openfile(file):
    fobj = open(file)
##    fobj = open(file, encoding='utf8')
    return fobj

##Connect to agentconfig database
def dbconnect(path):

    ##fileloc = os.path.join(r'files\var\lib\appinternals-yarder\lumberjack-svc-agentconfig\config\initial')
    fileloc = os.path.join('files/var/lib/appinternals-yarder/lumberjack-svc-agentconfig/config/initial')
    abspath = os.path.abspath(os.path.join('.',fileloc,'cfg_db'))
    
    if (os.path.exists(abspath)):

        print('Connection to db succeeded...')
        
        conn = sqlite3.connect(abspath)
        c = conn.cursor()
        
    else:

        print('Database File does not exists..\n')
        conn = ' '
        c = ' '

    return conn, c

##Close database connection
def dbclose(conn):
    conn.close()

##Write output file
def writefile(filename,cnt,msg):

    fwrite = open(filename,'a')
    fwrite.write(msg+ str(cnt) + '\n')
    fwrite.close()

    return 0

##Get number of agents    
def agentcount(conn,c):

    c.execute('SELECT count(*) FROM agent')
    count = c.fetchone()

    cnt_agents = count[0]
    msg = 'Total number of agents : '

    writefile(filename,cnt_agents,msg)

    return count[0]    

##Get number of offline agents
def agentsonffline(conn,c):

    flag = (0,)
    
    c.execute('SELECT count(*) FROM agent where online = ?',flag)
    count = c.fetchone()

    cnt_agents = count[0]
    msg = 'Total number of agents offline : '

    writefile(filename,cnt_agents,msg)

    return count[0]     

##Get number of online agents
def agentsonline(conn,c):

    flag = (1,)
    
    c.execute('SELECT count(*) FROM agent where online = ?',flag)
    count = c.fetchone()

    cnt_agents = count[0]
    msg = 'Total number of agents online : '

    writefile(filename,cnt_agents,msg)

    return count[0]

##Get number of processes
def processcount(conn,c):

    c.execute('SELECT count(*) FROM process')
    count = c.fetchone()

    cnt_process = count[0]
    msg = 'Total number of processes : '

    writefile(filename,cnt_process,msg)

    return count[0]

##Get number of processcount by state
def processcountlist(conn,c):

    c.execute('SELECT state,count(id) as agentcount FROM process group by state order by state')

    list = c.fetchall()
    msg = 'Process count by state : '

    writefile(filename,str(' '),msg)

    for x in range(0,len(list)):
        msg = ' '
        writefile(filename,list[x],msg)

    return list

##Get number of agents based on version
def agtcntversion(conn,c):

    c.execute('SELECT version, count(id) as agentcount  FROM agent group by version order by version')

    list = c.fetchall()
    msg = 'Agent count by version : '

    writefile(filename,str(' '),msg)

    for x in range(0,len(list)):
        msg = ' '
        writefile(filename,list[x],msg)

    return list

##Get number of processmoniker count
def processmonikercount(conn,c):

    c.execute('SELECT count(*) FROM processmoniker')
    count = c.fetchone()

    cnt_processmnk = count[0]
    msg = 'Total number of process monikers : '

    writefile(filename,cnt_processmnk,msg)

    return count[0]

##Get number instrumented process count
def processmonikertoinstr(conn,c):

    flag = (1,)
    
    c.execute('SELECT count(*) FROM processmoniker where to_instrument = ?',flag)
    count = c.fetchone()

    cnt_processmnk = count[0]
    msg = 'Total number of process monikers enabled to instrument : '

    writefile(filename,cnt_processmnk,msg)

    return count[0]

##Get number non instrumented process count
def processmonikernotinstr(conn,c):

    flag = (0,)
    
    c.execute('SELECT count(*) FROM processmoniker where to_instrument = ?',flag)
    count = c.fetchone()

    cnt_processmnk = count[0]
    msg = 'Total number of process monikers disabled to instrument : '

    writefile(filename,cnt_processmnk,msg)

    return count[0]
        
#Directory walk of the extracted bundle
def navigatefolders():
    
    cwd = os.getcwd()
    filelist = []
    configfiles = []
    gnrlfiles = []
    folderstoread = ['appinternals','nginx']
    folderstoread_config = ['commands']
    
    for fdname in os.listdir(cwd):
        if os.path.isdir(fdname):
            for path,subdirs,files in os.walk(os.path.abspath(fdname)):
                for x in files:
                    if (x.endswith('.txt') or x.endswith('.cfg')):
                        configfiles.append(os.path.join(os.path.abspath(path),x))
                    else:
                        if ((x.endswith('.log') or x.endswith('.out'))):
                            filelist.append(os.path.join(os.path.abspath(path),x))
                        elif(x.find('messages')!=-1):
                                gnrlfiles.append(os.path.join(os.path.abspath(path),x))
                                
    try:

        for conffile in configfiles:
                configdetails(conffile)

        for logfile in filelist:
            for foldername in folderstoread:
                if foldername in logfile:
                    if logfile.find('coretrace')==-1:
                        print('Processing ',logfile)
                        errorsandwarns(logfile)
                        if ((logfile.find('silo_dispatch-performance.log')!=-1) or (logfile.find('silo_dispatch.log')!=-1)):
                            silostatus(logfile)
                            silodiskusage(logfile)
                        elif(logfile.find('silo_dispatch-retire.log')!=-1):
                                 silostatus(logfile)
                        elif(logfile.find('silo_dispatch-calibration.log')!=-1):
                                siloperf(logfile)
                        elif(logfile.find('silo_dispatch-0.stderr.log')!=-1):
                            bug299149(logfile)
                            sid(logfile)
                            invalidstrtime(logfile)
                            emxtraceparse(logfile)
                        elif(logfile.find('silo_apptx_store.log')!=-1):
                                callsperseg(logfile)
                        elif(logfile.find('silo_query-queries.log')!=-1):
                                siloqueryissues(logfile)
                        elif(logfile.find('silo_stitcher.log')!=-1):
                                stitcherhash(logfile)
                        elif(logfile.find('wsproxy2.log')!=-1):
                                agentreconnect(logfile)
                        elif(logfile.find('ferryman3.log')!=-1):
                                offset(logfile)
                        elif(logfile.find('odb_server-0.stderr')!=-1):
                                sharedmem(logfile)
                                odbmemalloc(logfile)
                        elif(logfile.find('ERROR: file_size')!=-1):
                                filesize(logfile)
                        elif(logfile.find('odb_server.log')!=-1):
                                odbclientcrash(logfile)
                        elif(logfile.find('silo_aggr.metrics_')!=-1):
                                siloaggr_deadlock(logfile)
                        elif(logfile.find('appinternals-webui.log')!=-1):
                                webuih2db(logfile)
                        elif(logfile.find('sensor-0.stderr.log')!=-1):
                                nospace(logfile)

        for logfile in gnrlfiles:
                if (logfile.find('messages')!=-1):
                        OOM_killer(logfile)
                        segfault(logfile)
                            
    except FileNotFoundError:
        print(logfile,'File does not exist...\n')


##Function to look into issues in silo_query-queries.log
def siloqueryissues(logfile):
        try:
                cnt = 0
                queries_done_min = []

                fobj = openfile(logfile)
                fwrite = open(filename,'a')

                for line in fobj:
                        if (line.find('done in')!=-1):
                                match = re.findall('done in [0-9]+m? ',line)
                                ##print(line,match)
                                queries_done_min.append(match)
        
                if (len(queries_done_min)>0):
                        fwrite.write('\n***** Silo queries taking long time ******\n')
                        fwrite.write('{0} queries took more than 60s to run\n'.format(len(queries_done_min)))
                        fwrite.write('Please take a look into silo_query-queries.log for more details on long running queries\n')


                fobj.close()
                fwrite.close()

        except Exception as e:
                print(e)

        
##Function to catch 1M default limit of calls per segement in txns
def callsperseg(logfile):
        try:
                cnt = 0
                lkup_str = ['hit configured limit of 1,000,000']

                fobj = openfile(logfile)
                fwrite = open(filename,'a')

                for x in range(0,len(lkup_str)):
                        for line in fobj:
                                if lkup_str[x] in line:
                                        cnt+=1

                if cnt>0:
                        fwrite.write('\n***** Calls hitting configured limit *****\n')
                        fwrite.write('Number of calls in transaction hit configured limit of 1M occurred {0} times\n'.format(cnt))
                        fwrite.write('Check/Analyze silo_apptx_store.log for possible nocollects \n')
                        fwrite.write('Also a good idea to decrease the "calls_per_seg" from 1M to 100K...\n')

                fobj.close()
                fwrite.close()

        except Exception as e:
                print(e)


##Function to catch no space issue in sensor log
def nospace(logfile):
        try:
                cnt = 0
                lkup = ['IOError: [Errno 28] No space left on device']

                fobj = openfile(logfile)
                fwrite = open(filename,'a')

                for line in fobj:
                        for key in lkup:
                                if key.strip() in line:
                                        cnt+=1

                if cnt>0:
                        fwrite.write('\n***** Possible Space issue *****\n')
                        fwrite.write('No Space left on device message occurred {0} time(s)\n'.format(cnt))
                        fwrite.write('Check if root partition or any other partition is low on space...\n')

                fobj.close()
                fwrite.close()

        except Exception as e:
                print(e)
        


##Function to catch bug#299268
def webuih2db(logfile):
        cnt = 0
        try:
                fobj = openfile(logfile)
                fwrite = open(filename,'a')

                for line in fobj:
                        if(('WARN' in line) and ('Could not obtain connection metadata : IO Exception:' in line)):
                                cnt+=1
                if cnt>0:
                        fwrite.write('\n***** Bug 299268 *****\n')
                        fwrite.write('Could not obtain connection metadata : IO Exception occurred {0} time(s)\n'.format(cnt))
                        fwrite.write('To fix the issue please do the following:\n1) Log into AS as root\n2) Delete /var/lib/appinternals-webui/webui_data\n3) Restart webUI\n\n')
                        fwrite.write('For more details please take a look at Bug#299268 - https://bugzilla.nbttech.com/show_bug.cgi?id=299268\n')

        except Exception as e:
                print(e)

        fobj.close()
        fwrite.close()

##Function to catch deadlocks in silo aggr
def siloaggr_deadlock(logfile):
        cnt = 0
        try:
                fobj = openfile(logfile)
                fwrite = open(filename,'a')

                for line in fobj:
                        if(('ERROR' in line) and ('potential deadlock' in line)):
                                cnt+=1
                if cnt>0:
                        fwrite.write('\n***** Silo Aggregator Deadlocks *****\n')
                        fwrite.write('Unexpected deadlock encountered {0} times\n'.format(cnt))
                        fwrite.write('Please check {0} log for details...\n'.format(logfile))

        except Exception as e:
                print(e)

        fobj.close()
        fwrite.close()

##Function to catch segfaults in messages log
def segfault(logfile):
        cnt = 0
        try:
                fobj = openfile(logfile)
                fwrite = open(filename,'a')

                for line in fobj:
                        if (('segfault at' in line) and 'error' in line):
                                cnt+=1

                if cnt>0:
                        fwrite.write('\n***** Segmentation faults *****\n')
                        fwrite.write('Process termination via segfault occurred {0} times\n'.format(cnt))
                        fwrite.write('Please check /var/log/messages for details...\n')


        except Exception as e:
                print(e)

        fobj.close()
        fwrite.close()

##Function to catch the OOM killer in messages log
def OOM_killer(logfile):
        cnt = 0
        try:
                fobj = openfile(logfile)
                fwrite = open(filename,'a')

                for line in fobj:
                        if (line.find('Out of memory: Kill process')!=-1):
                                cnt+=1

                if cnt>0:
                        fwrite.write('\n***** OOM Killer invoked *****\n')
                        fwrite.write('out of memory killer / OOM killer activated (picks process to kill when system runs out of memory) {0} times\n'.format(cnt))
                        fwrite.write('Please check /var/log/messages for details...\n')

        except Exception as e:
                print(e)

        fobj.close()
        fwrite.close()

##Function to find if client crashed and sent corrupt data in odb server log
def odbclientcrash(logfile):
        srchstrng = ['Some data received from crashed client appears to be corrupt & has not been written']
        x = 0
        
        try:
                fobj = openfile(logfile)
                fwrite = open(filename,'a')

                for line in fobj:
                        for strng in srchstrng:
                                if ((strng in line) and ('ERROR in line')):
                                        x+=1
                
                if x>0:
                        fwrite.write('\n***** ODB Server:client crash *****\n')
                        fwrite.write('Client crashed and sent corrupt data'+' occurred- '+str(x)+' times\n')
                        fwrite.write('Please check odb_server.log for details...\n')
        except Exception as e:
                print(e)

        fwrite.close()
        fobj.close()

##Function to find if we are running into BUG 299149
def bug299149(logfile):
        srchstrng = ['points to itself as x-thread parent']
        x = 0

        try:
                fobj = openfile(logfile)
                fwrite = open(filename,'a')

                for line in fobj:
                        for strng in srchstrng:
                                if((strng in line) and ('ERROR' in line)):
                                        x+=1
                if x>=5:
                        fwrite.write('\n***** Bug 299149 ******\n')
                        fwrite.write('APPTX points to itself as x-thread parent (possibly related to bug 299149)- '+str(x)+' times\n')
                        fwrite.write('Please check silo_dispatch-0.stderr.log for details...\n')

        except Exception as e:
                print(e)

        fwrite.close()
        fobj.close()

##Function to find string with sid 0
def sid(logfile):
        srchstrng = ['unable to find string with sid=[0]']
        x = 0

        try:
                fobj = openfile(logfile)
                fwrite = open(filename,'a')

                for line in fobj:
                        for strng in srchstrng:
                                if((strng in line) and ('ERROR' in line)):
                                        x+=1

                if x>0:
                        fwrite.write('\n***** Silo:unable to find string with sid ******\n')
                        fwrite.write('unable to find string with sid=[0] occurred- '+str(x)+' times\n')
                        fwrite.write('Please check silo_dispatch-0.stderr.log for details...\n')

        except Exception as e:
                print(e)

        fwrite.close()
        fobj.close()


##Function to find invalid start_time
def invalidstrtime(logfile):
        srchstrng = 'invalid query; msg=[invalid start time;'
        srchstrng1 = 'Start stack is unexpectedly empty'
        x = 0
        y = 0

        try:
                fobj = openfile(logfile)
                fwrite = open(filename,'a')

                for line in fobj:
                        if 'ERROR:' in line:
                                if(srchstrng in line):
                                        x+=1
                                elif(srchstrng1 in line):
                                        y+=1

                if x>0:
                        fwrite.write('\n***** Silo_query:invalid start_time; does not match granularity ******\n')
                        fwrite.write('Invalid start time - '+str(x)+' times\n')
                        fwrite.write('Please check silo_dispatch-0.stderr.log for details...\n')
                if y>0:
                        fwrite.write('\n***** Silo_store:Tracefile parsing failing *****\n')
                        fwrite.write('Exception detected when parsing files because of empty start stacks- '+str(y)+' times\n')
                        fwrite.write('Please check silo_dispatch-0.stderr.log for details...\n')


        except Exception as e:
                print(e)

        fwrite.close()
        fobj.close()


##Function to get the particle hash collision errors in stitcher log
def stitcherhash(logfile):
        srchstrng = ['DIAG: Particle hash collision x-thread-self:']
        x = 0

        try:
                fobj = openfile(logfile)
                fwrite = open(filename,'a')

                for line in fobj:
                        for strng in srchstrng:
                                if(strng in line):
                                        x+=1
                if x>0:
                        fwrite.write('\n***** Particle Hash Collisions ******\n')
                        fwrite.write('particle hash collision (could indicate transactions are not stitching properly)(possibly related to bug 299068) - '+str(x)+' times\n')
                        fwrite.write('Please check silo_stitcher.log for details...\n')
        except Exception as e:
                print(e)

        fwrite.close()
        fobj.close()

##Function to check active agents reconnecting
def agentreconnect(logfile):
        srchstrng = 'connected but request matches active iid; stopping internal proxy'
        srchstrng1 = 'ERROR: empty/invalid dsaInfo encountered for uid'
        srchstrng2 = 'json: can''t unmarshal; error='
                
        x = 0
        y = 0
        z = 0

        try:
                fobj = openfile(logfile)
                fwrite = open(filename,'a')

                for line in fobj:
                        if(srchstrng in line):
                                x+=1
                        elif(srchstrng1 in line):
                                y+=1
                        elif(srchstrng2 in line):
                                z+=1

                if x>0:
                        fwrite.write('\n***** Agents reconnecting with Active IID ******\n')
                        fwrite.write('Active Agents reconnecting with active iid;(i.e. agent already exists; IP may be different)- '+str(x)+' time(s)\n')
                        fwrite.write('DSA is trying to connect but appears to be already connected \n')
                        fwrite.write('Please check wsproxy2.log for details...\n')

                if y>0:
                        fwrite.write('\n***** Empty response from dsainfo ******\n')
                        fwrite.write('Empty or Invalid dsainfo response from agent (should investigate)- '+str(y)+' time(s)\n')
                        fwrite.write('Please check wsproxy2.log for details...\n')
                
                if z>0:
                        fwrite.write('\n*****wsproxy2:Unable to parse json *****\n')
                        fwrite.write('JSON can not unmarshal error occurred '+str(z)+' time(s)\n')
                        fwrite.write('Typically agent response is an error in html format. These might be noisy messages though.\n')
                        fwrite.write('Please check wsproxy2.log for details... \n')

        except Exception as e:
                print(e)

        fwrite.close()
        fobj.close()


##Function to check if data download error because of high offset
def offset(logfile):
        srchstrng = 'ERROR: Offset for data too high when requesting file'
        x = 0

        try:
                fobj = openfile(logfile)
                fwrite = open(filename,'a')

                for line in fobj:
                        if(srchstrng in line):
                                x+=1

                if x>0:
                        fwrite.write('\n****** Ferryman unable to download data *****\n')
                        fwrite.write('Offset for data too high when requesting file- '+str(x)+' time(s) \n')
                        fwrite.write('Please check ferryman3.log for details...\n')

        except Exception as e:
                print(e)

        fwrite.close()
        fobj.close()

##function to check if ODB (DB node) in cluster is overloaded
def odbmemalloc(logfile):
        srchstrng = 'ERROR: Memory allocation of'
        x = 0

        try:
                fobj = openfile(logfile)
                fwrite = open(filename,'a')

                for line in fobj:
                        if(srchstrng in line) and ('failed' in line):
                                x+=1

                if x>0:
                        fwrite.write('\n****** Memory allocation failed for ODB *****\n')
                        fwrite.write('Memory allocation failed occurred {0} time(s)\n'.format(x))
                        fwrite.write('Please check odb_server-0.stderr for details...\n')
        except Exception as e:
                print(e)

        fwrite.close()
        fobj.close()

##Function to check if ODB is running into shared memory errors
def sharedmem(logfile):
        srchstrng = 'ERROR: Unable to allocate shared memory block of'
        x = 0

        try:
                fobj = openfile(logfile)
                fwrite = open(filename,'a')
                
                for line in fobj:
                        if(srchstrng in line):
                                x+=1

                if x>0:
                        fwrite.write('\n*****Unable to start ODB shared memory issues *****\n')
                        fwrite.write('Unable to allocate shared memory block of- '+str(x)+' time(s) \n')
                        fwrite.write('Please check odb_server-0.stderr for details...\n')
        except Exception as e:
                print(e)

        fwrite.close()
        fobj.close()

##Function to check if there are issues with EMX trace parsing
def emxtraceparse(logfile):
        srchstrng = 'ERROR: Exception parsing emx trace'
        x = 0

        try:
                fobj = openfile(logfile)
                fwrite = open(filename,'a')

                for line in fobj:
                        if (srchstrng in line):
                                x+=1

                if x>0:
                        fwrite.write('\n***** silo_emx_store: Issues parsing environmental metrics ******\n')
                        fwrite.write('Error parsing environmental metrics file - '+str(x)+' time(s) \n')
                        fwrite.write('Possible corrupt files? Please check silo_dispatch-0.stderr.log for details...\n')
        except Exception as e:
                print(e)

        fwrite.close()
        fobj.close()

##Function to check bug 299625
def fizesize(logfile):
        srchstrng = 'ERROR: file_size'
        x = 0

        try:
                fobj = openfile(logfile)
                fwrite = open(filename,'a')

                for line in fobj:
                        if (srchstrng in line):
                                x+=1

                if x>5:
                        fwrite.write('\n*****silo_dispatch: File size failure *****\n')
                        fwrite.write('file_size failed - '+str(x)+' time(s) \n')
                        fwrite.write('Possibly bug 299625. File sizes for [/var/lib/appinternals/silo/data/journal/*/*/*.pbm] files \n')
                        fwrite.write('Please take a look at silo_dispatch.log for details... \n')
        except Exception as e:
                print(e)

        fwrite.close()
        fobj.close()


##Function to get appinternals AS version
def version(conffile):
    fobj = openfile(conffile)

    fwrite = open(filename,'a')
    fwrite.write('\n***** Version *****')

    for i in fobj:
        fwrite.write('\n'+i+'\n')
        
    fwrite.close()
    fobj.close()

##Function to get the hostname of AS
def hostname(conffile):
    fobj = openfile(conffile)

    fwrite = open(filename,'a')
    fwrite.write('\n***** Hostname *****')

    for i in fobj:
        fwrite.write('\n'+i)

    fwrite.close()
    fobj.close()

##Function to get the last reboot of AS    
def lastreboot(conffile):
    fobj = openfile(conffile)

    fwrite = open(filename,'a')
    fwrite.write('\n***** Last Reboot *****\n')
    fwrite.write(fobj.readline())
    
    fwrite.close()
    fobj.close()

##Function to list top 5 CPU using processes on AS    
def procbycpu(conffile):
    fobj = openfile(conffile)
    n = 7
    
    fwrite = open(filename,'a')
    fwrite.write('\n***** Top CPU users ***** \n')

    for i in range(1,n):
        line = fobj.readline()
        fwrite.write(line)

    fwrite.close()
    fobj.close()

##Function to list top 5 memory using processes on AS        
def procbymem(conffile):
    fobj = openfile(conffile)
    n = 7

    fwrite = open(filename,'a')
    fwrite.write('\n***** Top Mem users ***** \n')

    for i in range(1,n):
        line = fobj.readline()
        fwrite.write(line)

    fwrite.close()
    fobj.close()

##Function to get list of corrupt app traces    
def crptapptraces(conffile):
    fobj = openfile(conffile)

    fwrite = open(filename,'a')
    fwrite.write('\n***** List of corrupt app traces ***** \n')

    for i in fobj:
        fwrite.write(i)

    fwrite.close()
    fobj.close()

##Function to get list of corrupt emx traces    
def crptemxtraces(conffile):
    fobj = openfile(conffile)

    fwrite = open(filename,'a')
    fwrite.write('\n***** List of corrupt emx traces ***** \n')

    for i in fobj:
        fwrite.write(i)

    fwrite.close()
    fobj.close()

##Function to get list of corrupt odb files
def crptodbfiles(conffile):
    try:
        fobj = openfile(conffile)

        fwrite = open(filename,'a')
        fwrite.write('\n***** List of corrupt odb files ***** \n')

        for i in fobj:
            fwrite.write(i)        

        fwrite.close()
        fobj.close()
    except Exception as e:
        print(e)

##Function to get disk usage details on AS    
def dfh(conffile):
    try:
        fobj = openfile(conffile)

        fwrite = open(filename,'a')
        fwrite.write('\n***** Disk Usage details ***** \n')

        for i in fobj:
            if(i.find('Filesystem')== -1):
                fwrite.write(i)
            
        fwrite.close()
        fobj.close()

    except Exception as e:
        print(e)

##Function to get supervisor status
def syctlstatus(conffile):
    try:
        fobj = openfile(conffile)

        fwrite = open(filename,'a')
        fwrite.write('\n***** Supervisor service status ***** \n')

        for i in fobj:
            fwrite.write(str(i)+'\n')
        ##fwrite.write(str(i[:i.index(',')])+'\n')

        fwrite.close()
        fobj.close()

    except Exception as e:
        print(e)

##Function to get num of TIME_WAIT,CLOSE_WAIT and FIN_WAIT's
def netstataon(conffile):
    fobj = openfile(conffile)

    fwrite = open(filename,'a')
    fwrite.write('\n***** Netstat Output summary ***** \n')
    
    TIME_WAIT = 0
    CLOSE_WAIT = 0
    FIN_WAIT = 0

    for x in fobj:
        if(x.find('TIME_WAIT') and x.find('tcp')):
            TIME_WAIT = TIME_WAIT+1
        else:
            if(x.find('CLOSE_WAIT') and x.find('tcp')):
                CLOSE_WAIT = CLOSE_WAIT+1
            else:
                if(x.find('FIN_WAIT') and x.find('tcp')):
                    FIN_WAIT = FIN_WAIT+1
                    
    fwrite.write('TIME_WAITs :'+str(TIME_WAIT)+'\n')
    fwrite.write('CLOSE_WAITs :'+str(CLOSE_WAIT)+'\n')
    fwrite.write('FIN_WAITs :'+str(FIN_WAIT)+'\n')

    fwrite.close()
    fobj.close()

##Function to list of core files
def cores(conffile):
    corefilelist = []
    corefilecnt = 0
    dict = {}
    
    fobj = openfile(conffile)

    fwrite = open(filename,'a')
    fwrite.write('\n***** Core files ***** \n')

##Get count of core files and write the total count
    for i in fobj:
        corefilecnt = corefilecnt + 1
        corefilelist.append(i)
        
    fwrite.write('total '+str(corefilecnt))

##Adding latest core files to a dictionary
    for s in corefilelist:
        x = s.split(':')
        dict.update({x[0]:x[1]})


##Writing latest core file details to output file
    fwrite.write('\nLatest core files : \n')
    for key,value in dict.items():
        fwrite.write(key+':'+value+'(yyyy-mm-dd hh)'+'\n')

        
    fwrite.close()
    fobj.close()

##Function to get the appliance type
def appliancetype(conffile):

        try:
                lre = ''
                fobj = openfile(conffile)
                fwrite = open(filename,'a')
                fwrite.write('\n***** Appliance type *****\n')

                for i in fobj:
                        if(i.find('"install_type":')!=-1):
                                x = i[i.index(':'):]
                        if(i.find('"is_lre":')!=-1):
                                lre = i[i.index(':'):]
                if len(x)>0:
                        if x.find('vm')!=-1:
                                fwrite.write('Virtual Machine\n')
                        elif x.find('azure')!=-1:
                                fwrite.write('Microsoft Azure\n')
                        elif x.find('linux')!=-1:
                                fwrite.write('Linux Installer\n')
                        elif x.find('amazon')!=-1 and x.find('saas')==-1:
                                fwrite.write('Amazon\n')
                        elif x.find('saas')!=-1:
                                fwrite.write('SaaS\n')

                if 'true' in lre:
                        fwrite.write('LRE is enabled\n')
                elif 'false' in lre:
                        fwrite.write('LRE is disabled\n')

                fwrite.close()
                fobj.close()

        except Exception as e:
                print(e)

def siloperf(logfile):
        try:
                lookuplist = ['APP:','BMX:','EMX:','STITCHER:','STX:','UTX:','MAP:']

                fobj = openfile(logfile)
                fwrite = open(filename,'a')

                lines = fobj.readlines()
                perf_details = lines[-13:]

                fwrite.write('\n***** Silo Calibration Details *****\n')
                fwrite.write('(Cores for incoming or backlog should not be more than available cores) \n')
                
                for x in perf_details:
                        if (x.find('======')==-1):
                                ##fwrite.write(x.strip()+'\n')
                                if(x.find('TOTAL:')!=-1 and x.find('RT_CORES:')!=-1 and x.find('PREF_CORES:')!=-1):
                                        tmp = x.split(',')
                                        ##print(str(tmp[0]).strip())
                                        ##print(str(tmp[0].split('TOTAL:')[1]).strip())
                                        ##print(str(str(tmp[1]).split('[')[0]).strip())
                                        ##print(str(tmp[0].split('TOTAL:')[1]).strip().replace('RT_CORES','Cores needed for incoming data'))
                                        ##print(str(str(tmp[1]).split('[')[0]).strip().replace('PREF_CORES','Cores needed for backlog data'))
                                        ##print(str(str(str(tmp[1]).split('[')[1].split(']')[0]).split(' ')[0]).strip())
                                        fwrite.write('\n'+str(tmp[0].split('TOTAL:')[1]).strip().replace('RT_CORES','Cores needed for incoming data')+'\n')
                                        fwrite.write(str(str(tmp[1]).split('[')[0]).strip().replace('PREF_CORES','Cores needed for backlog data')+'\n')
                                        fwrite.write('Cores available: '+str(str(str(tmp[1]).split('[')[1].split(']')[0]).split(' ')[0]).strip()+'\n \n')

                                for lkup in lookuplist:
                                        if (x.find(lkup)!=-1 and (x.find('RT_CORES')==-1 or x.find('PREF_CORES')==-1)):
                                                fwrite.write(x.strip()+'\n')

                fobj.close()
                fwrite.close()

        except Exception as e:
                print(e)

##Function to get latest status of silo statistics
def silostatus(logfile):
    silostats = {}

    fobj = openfile(logfile)
    fwrite = open(filename,'a')

    if(logfile.find('silo_dispatch-performance.log')!=-1):
        fwrite.write('\n****** Stitcher/Aggregator input buffer ***** \n')

        for line in fobj:
            if(line.find('JOURNAL_DIR_STITCHER')!=-1 or line.find('JOURNAL_DIR_STX_STORE')!=-1):
                x = line.split(':')
                silostats.update({x[0]:x[1]})
            else:
                if (line.find('JOURNAL_DIR_AGGR')!=-1):
                    x = line.split(':')
                    silostats.update({x[0]:x[1]})
                else:
                    if(line.find('DB:APP:')!=-1):
                        x = line.split('DB:')
                        silostats.update({x[0]:x[1]})
                        
        for key,value in silostats.items():
            if key.find('JOURNAL')!=-1:
                if (value.find('GiB')!= -1 or value.find('TiB')!= -1):
                    fwrite.write('Might be lagging in processing data..'+key+'-'+value)
                else:
                    fwrite.write('(OK) '+key+'-'+value)
            else:
                fwrite.write('Number of Records: '+value)
    else:
        tmp = []
        lines = fobj.readlines()
        purge_details=lines[-15:]

        for x in purge_details:
            if ((x.find('DIAG: Will try to retire')!=-1) or x.find('Retired')!=-1):
                ##fwrite.write(x)
                tmp.append(x)

        if len(tmp)!=0:
                fwrite.write('\n****** Latest purge details ***** \n')
                for n in tmp:
                        fwrite.write(n)

    fwrite.close()
    fobj.close()

def silodiskusage(logfile):
    try:
        fobj = openfile(logfile)
        fwrite = open(filename,'a')

        lines = fobj.readlines()
        silodisk_details = lines[-5:]

        for x in silodisk_details:
            if (x.find('DISK USE:')!=-1):
                if (x.find('transaction data')!=-1 and x.find('environmental data')!=-1):
                    x1 = str(x.split(':')[1])
                    x2 = x1.split(',')
                elif (x.find('free on disk')!=-1):
                    n1 = str(x.split(':')[1])
                    n2 = n1.split(' [')

        if len(x2)>0:
            fwrite.write('\n***** Silo Disk Usage Details *****\n')
            for i in range(0,len(x2)):
                fwrite.write('{0}\n'.format(str(x2[i].strip())))

        if len(n2)>0:
            for i in range(0,len(n2)):
                fwrite.write('{0}\n'.format(str(n2[i]).strip().replace(']','')))

        fobj.close()
        fwrite.close()

    except Exception as e:
        print('Unable to find file...')

##Function to get the silo settings
def silo_settings(logfile):
        try:
                fobj = openfile(logfile)
                fwrite = open(filename,'a')

                fwrite.write('\n****** Silo Settings ******\n')


                for line in fobj:
                        if (line.find('aggr_utx_thrds')!=-1 or line.find('max_parser_processes')!=-1 or line.find('aggr_stx_thrds')!=-1 or line.find('max_indexer_processes')!=-1):
                                fwrite.write((str(line).strip()).strip(',')+'\n')

                fobj.close()
                fwrite.close()

        except Exception as e:
                print(e)

##Function to get resource information - #cores, memory details etc
def resourceinfo(logfile):
        try:
                fobj = openfile(logfile)
                fwrite = open(filename,'a')

                fwrite.write('\n***** Resource Details *****\n')

                for line in fobj:
                        if ((line.find('MemTotal:')!=-1 or line.find('MemFree:')!=-1 or line.find('system.cpu cores :')!=-1 or line.find('system.num_processors:')!=-1)and line.find('#')==-1):
                                fwrite.write(str(line).strip(' '))
                fobj.close()
                fwrite.close()
        except Exception as e:
                print(e)

##Function to get the count of transaction types defined
def txntypes(logfile):
        try:
                config  = json.load(open(logfile))
                txncnt = 0
                fwrite = open(filename,'a')

                for ttype in config['items']:
                        if ttype['id']!='':
                                txncnt+=1
                
                fwrite.write('\n***** Number of Transaction Types Defined ******\n')
                fwrite.write(str(txncnt)+'\n')

                fwrite.close()
                return

        except Exception as e:
                print(e)
                

##Function to get the count of applications defined
def definedapps(logfile):
        try:
                config = json.load(open(logfile))
                apps = 0
                fwrite = open(filename,'a')

                for app in config['items']:
                        if app['id']!='':
                                apps+=1

                fwrite.write('\n***** Number of applications defined *****\n')
                fwrite.write(str(apps)+'\n')

                fwrite.close()
                return

        except Exception as e:
                print(e)


##Function to get cluster node information
def clusterinfo(logfile):
        try:
                config = json.load(open(logfile))
                cluster_role = ''
                cluster_node = ''

                fwrite = open(filename,'a')
                fwrite.write('\n*****Cluster Information *****\n')

                for n in config['items']:
                        if n['cluster_role']!='':
                                cluster_role = n['cluster_role']
                        if n['name']!='':
                                cluster_node = n['name']

                        ##print(cluster_role,cluster_node)
                        fwrite.write(str(cluster_role)+':       '+str(cluster_node)+'\n')
                
                fwrite.close()
                return

        except Exception as e:
                print(e)

def journalsizecheck(conffile):
    try:
        odb1k = ''
        journal1k = ''
        disksize1k = ''

        fobj = openfile(conffile)
        file_to_read = os.path.dirname(conffile)+'/df_kb.txt'

        for line in fobj:
            if (line.find('/var/lib/appinternals/silo/data/journal')!=-1):
                journal1k = line.split('\t')[0]
            elif (line.find('/var/lib/appinternals/silo/data/odb_store')!=-1):
                odb1k = line.split('\t')[0]

        fobj.close()

        if os.path.isfile(file_to_read):
            fobj = openfile(file_to_read)

            for n in fobj:
                if '/mnt/data' in n:
                    disksize1k = str(n.strip()).split()

            fobj.close()


        if (odb1k!='' or journal1k!=''):
            fwrite = open(filename,'a')
            fwrite.write('\n***** Journal/ODB size check *****\n')
 
            if len(disksize1k) == 5:
                disksize = disksize1k[0]
            else:
                disksize = disksize1k[1]

            if (disksize1k!=-1):
                journalpercent = int(journal1k)*100/int(disksize)
                odbpercent     = int(odb1k)*100/int(disksize)

                fwrite.write('/mnt/data size: {0}kb\n'.format(disksize))
                fwrite.write('Journal size: {0}kb ({1}% of /mnt/data)\n'.format(journal1k,journalpercent))
                fwrite.write('ODB store size: {0}kb ({1}% of /mnt/data)\n'.format(odb1k,odbpercent))

            else:
                fwrite.write('Journal size: {0}kb\n'.format(journal1k))
                fwrite.write('ODB store size: {0}kb\n'.format(odb1k))
                fwrite.write('Could not determine /mnt/data size')

            fwrite.close()

    except Exception as e:
        print(e)

##Function to get configuration and other system details
def configdetails(conffile):

    if(conffile.find('appinternals_version.txt')!=-1):
        version(conffile)
    else:
        if(conffile.find('hostname.txt')!=-1):
            hostname(conffile)
        else:
            if(conffile.find('last_reboot.txt')!=-1):
                lastreboot(conffile)
            else:
                if(conffile.find('processes_sorted_by_cpu.txt')!=-1):
                    procbycpu(conffile)
                else:
                    if(conffile.find('processes_sorted_by_resident_size.txt')!=-1):
                        procbymem(conffile)
                    else:
                        if(conffile.find('corrupt_app_traces.txt')!=-1 and conffile.find('num')==-1):   
                            print('Skipping writing the list...')
                            ##crptapptraces(conffile)
                        else:
                            if(conffile.find('corrupt_emx_traces.txt')!=-1 and conffile.find('num')==-1):
                                print('Skipping writing the list...')
                                ##crptemxtraces(conffile)
                            else:
                                if(conffile.find('corrupt_odb_files.txt')!=-1 and conffile.find('num')==-1):
                                    crptodbfiles(conffile)
                                else:
                                    if(conffile.find('df_h.txt')!=-1):
                                        dfh(conffile)
                                    else:
                                        if(conffile.find('supervisor_status.txt')!=-1):
                                            syctlstatus(conffile)
                                        else:
                                            if(conffile.find('netstat_-aon.txt')!=-1):
                                                netstataon(conffile)
                                            else:
                                                if(conffile.find('corefiles.txt')!=-1):
                                                    cores(conffile)
                                                else:
                                                    if(conffile.find('lj.machine.json.txt')!=-1):
                                                        appliancetype(conffile)
                                                    else:
                                                        if(conffile.find('lj.silo_settings.json.txt')!=-1):
                                                                silo_settings(conffile)
                                                        else:
                                                            if(conffile.find('lj.transaction_types_ALL.json.txt')!=-1):
                                                                txntypes(conffile)
                                                            else:
                                                                if(conffile.find('lj.application_definitions.json.txt')!=-1):
                                                                        definedapps(conffile)
                                                                else:
                                                                    if(conffile.find('system_details.txt')!=-1):
                                                                        resourceinfo(conffile)
                                                                    else:
                                                                        if (conffile.find('lj.cluster.cluster_nodes.json.txt')!=-1):
                                                                                clusterinfo(conffile)
                                                                        else:
                                                                            if (conffile.find('disk_usage_silo_data.txt')!=-1):
                                                                                journalsizecheck(conffile)


                    
##Function to search for all Errors and Warnings in log files
def errorsandwarns(logfile):

    if(logfile.find('upgrade.log')!=-1):
        searchstrings = ['Error:']
    else:
        searchstrings = ['SEVERE','ERROR','WARN','FATAL','HTTPError']

    try:
        fobj = open(logfile)
        fwrite = open(errorandwarn,'a')
        fwrite.write('\n'+'******Errors and Warnings in file '+ str(logfile)+'******' + '\n\n')

        try:
            for i in fobj:
                for string in searchstrings:
                    if string in i.strip():
                        fwrite.write(i)

            fobj.close()
            fwrite.close()

        except UnicodeDecodeError:
            print('Skipping ',logfile)
            
    except FileNotFoundError:
        print(logfile,'File does not exist...\n')

##Function to move files to location where the bundle is present
def movefiles(path):
    cwd = os.getcwd()
    dst = os.path.abspath(os.path.dirname(path))
    
    for file in os.listdir(os.getcwd()):
        filelist = (os.path.join(os.path.abspath(file),dst))
        if (file.endswith('.txt') and (file.find('errorsandwarns')!=-1 or file.find('analysisserverdetails')!=-1)):
            try:
                print('Moving '+os.path.abspath(file)+' to '+dst)
                shutil.move(os.path.abspath(file),dst)
            except Exception as e:
                 print(file+' already exists...Removing file')
                 os.remove(os.path.join(dst,file))
                 shutil.move(os.path.abspath(file),dst)        

##Function to generate weblinks for output files
def weblinks(file_create_dir,path,filename,errorandwarn):
        baseURL = 'http://support.nbttech.com/data'
        sysURL = ''
        errURL = ''


        ##tmpPath = str(os.path.dirname(path))[str(os.path.dirname(path)).index('data/'):]
        tmpPath = str(file_create_dir).split('/data')[1]

        sysURL = baseURL+tmpPath+'/'+filename
        errURL = baseURL+tmpPath+'/'+errorandwarn
        logURL = baseURL+tmpPath

        print('Creating Web Link to files...\n')
        print('*****************************\n')
        print('    WEB LINKS                \n')

        print('Browse Logs: '+logURL+'\n')
        print('Analysis Server Details: '+sysURL+'\n')
        print('Errors log: '+errURL+'\n')

        print('\n*****************************\n')

#Function to do the plots
def plots(casenum,file_create_dir,path):
    print('Plotting charts...')
    try:
        cpuplots(casenum,file_create_dir,path)
        memplots(casenum,file_create_dir,path)
        diskplots(casenum,file_create_dir,path)
        siloplots(casenum,file_create_dir,path)
    except Exception as e:
        print(e)

def siloplots(casenum,file_create_dir,path):
    try:
        silo_plot = casenum+'_silo.html'
        date_key = ''
        apptx_values = {}
        dispatch_values = {}
        query_values = {}
        stxstore_values = {}
        stitcher_values = {}
        emx_values = {}
        odb_values = {}

        file_to_read = os.path.abspath(file_create_dir)+'/files/var/log/appinternals/sensor/today/top_by_cpu.out'
        fobj = open(file_to_read)

        date_prog = re.compile('^\d{4}-\d{2}-\d{2}[ ]\d{2}:\d{2}:\d{2}')
        date_prog1 = re.compile('^\d{2}\/\d{2}\/\d{2}[ ]\d{2}:\d{2}:\d{2}')
        query_prog = re.compile('^[ ]*(\d+)[ ]+([^ ]+[ ]+){7}([^ ]+)[ ].*(bin/silo_query).*-port[ ]([^ ]+)')
        dispatch_prog = re.compile('^[ ]*(\d+)[ ]+([^ ]+[ ]+){7}([^ ]+)[ ].*(bin/silo_dispatch).*-data_path[ ]([^ ]+)')
        apptx_prog = re.compile('^[ ]*(\d+)[ ]+([^ ]+[ ]+){7}([^ ]+)[ ].*(bin/silo_apptx_store).*-port[ ]([^ ]+)')
        stxstore_prog = re.compile('^[ ]*(\d+)[ ]+([^ ]+[ ]+){7}([^ ]+)[ ].*(bin/silo_stx_store).*-port[ ]([^ ]+)')
        stitcher_prog = re.compile('^[ ]*(\d+)[ ]+([^ ]+[ ]+){7}([^ ]+)[ ].*(bin/silo_stitcher).*-port[ ]([^ ]+)')
        emx_prog = re.compile('^[ ]*(\d+)[ ]+([^ ]+[ ]+){7}([^ ]+)[ ].*(bin/silo_emx_store).*-port[ ]([^ ]+)')
        odb_prog = re.compile('^[ ]*(\d+)[ ]+([^ ]+[ ]+){7}([^ ]+)[ ].*(bin/odb_server).*-config_dir[ ]([^ ]+)')

        for line in fobj:
            if(date_prog.findall(line)):
                date_key = date_prog.findall(line)
            elif(date_prog1.findall(line)):
                date_key = date_prog1.findall(line)
            elif(query_prog.findall(line) and date_key!=''):
                query_stage = query_prog.findall(line)
                if(query_stage[0][0] not in query_values.keys()):
                    query_values.update({query_stage[0][0]:{}})
                query_values[query_stage[0][0]].update({datetime.datetime.strptime(date_key[0],'%Y-%m-%d %H:%M:%S'):float(query_stage[0][2])})
            elif(dispatch_prog.findall(line) and date_key!=''):
                dispatch_stage = dispatch_prog.findall(line)
                if(dispatch_stage[0][0] not in dispatch_values.keys()):
                    dispatch_values.update({dispatch_stage[0][0]:{}})
                dispatch_values[dispatch_stage[0][0]].update({datetime.datetime.strptime(date_key[0],'%Y-%m-%d %H:%M:%S'):float(dispatch_stage[0][2])})
            elif(apptx_prog.findall(line) and date_key!=''):
                apptx_stage = apptx_prog.findall(line)
                if(apptx_stage[0][0] not in apptx_values.keys()):
                    apptx_values.update({apptx_stage[0][0]:{}})
                apptx_values[apptx_stage[0][0]].update({datetime.datetime.strptime(date_key[0],'%Y-%m-%d %H:%M:%S'):float(apptx_stage[0][2])})
            elif(stxstore_prog.findall(line) and date_key!=''):
                stxstore_stage = stxstore_prog.findall(line)
                if(stxstore_stage[0][0] not in stxstore_values.keys()):
                    stxstore_values.update({stxstore_stage[0][0]:{}})
                stxstore_values[stxstore_stage[0][0]].update({datetime.datetime.strptime(date_key[0],'%Y-%m-%d %H:%M:%S'):float(stxstore_stage[0][2])})
            elif(stitcher_prog.findall(line) and date_key!=''):
                stitcher_stage = stitcher_prog.findall(line)
                if(stitcher_stage[0][0] not in stitcher_values.keys()):
                    stitcher_values.update({stitcher_stage[0][0]:{}})
                stitcher_values[stitcher_stage[0][0]].update({datetime.datetime.strptime(date_key[0],'%Y-%m-%d %H:%M:%S'):float(stitcher_stage[0][2])})
            elif(emx_prog.findall(line) and date_key!=''):
                emx_stage = emx_prog.findall(line)
                if(emx_stage[0][0] not in emx_values.keys()):
                    emx_values.update({emx_stage[0][0]:{}})
                emx_values[emx_stage[0][0]].update({datetime.datetime.strptime(date_key[0],'%Y-%m-%d %H:%M:%S'):float(emx_stage[0][2])})
            elif(odb_prog.findall(line) and date_key!=''):
                odb_stage = odb_prog.findall(line)
                if(odb_stage[0][0] not in odb_values.keys()):
                    odb_values.update({odb_stage[0][0]:{}})
                odb_values[odb_stage[0][0]].update({datetime.datetime.strptime(date_key[0],'%Y-%m-%d %H:%M:%S'):float(odb_stage[0][2])})

        fobj.close()

        output_file(silo_plot, title="Silo CPU")
        datetime_tick_formats = {
            key: ["%a %b %d %H:%M:%S"]
            for key in ("seconds", "minsec", "minutes", "hourmin", "hours", "days")}

        p1 = figure(title="Silo DISPATCH CPU",plot_width=800, plot_height=350,x_axis_type="datetime")
        p1.xaxis.axis_label="Time"
        p1.yaxis.axis_label="CPU %"
        p1.xaxis.formatter = DatetimeTickFormatter(**datetime_tick_formats)

        p2 = figure(title="Silo APPTX CPU",plot_width=800, plot_height=350,x_axis_type="datetime")
        p2.xaxis.axis_label="Time"
        p2.yaxis.axis_label="CPU %"
        p2.xaxis.formatter = DatetimeTickFormatter(**datetime_tick_formats)

        p3 = figure(title="Silo QUERY CPU",plot_width=800, plot_height=350,x_axis_type="datetime")
        p3.xaxis.axis_label="Time"
        p3.yaxis.axis_label="CPU %"
        p3.xaxis.formatter = DatetimeTickFormatter(**datetime_tick_formats)

        p4 = figure(title="Silo STX_STORE CPU",plot_width=800, plot_height=350,x_axis_type="datetime")
        p4.xaxis.axis_label="Time"
        p4.yaxis.axis_label="CPU %"
        p4.xaxis.formatter = DatetimeTickFormatter(**datetime_tick_formats)

        p5 = figure(title="Silo STITCHER CPU",plot_width=800, plot_height=350,x_axis_type="datetime")
        p5.xaxis.axis_label="Time"
        p5.yaxis.axis_label="CPU %"
        p5.xaxis.formatter = DatetimeTickFormatter(**datetime_tick_formats)

        p6 = figure(title="Silo EMX_STORE CPU",plot_width=800, plot_height=350,x_axis_type="datetime")
        p6.xaxis.axis_label="Time"
        p6.yaxis.axis_label="CPU %"
        p6.xaxis.formatter = DatetimeTickFormatter(**datetime_tick_formats)

        p7 = figure(title="ODB CPU",plot_width=800, plot_height=350,x_axis_type="datetime")
        p7.xaxis.axis_label="Time"
        p7.yaxis.axis_label="CPU %"
        p7.xaxis.formatter = DatetimeTickFormatter(**datetime_tick_formats)

        colors = itertools.cycle(palette)

        for k, color in zip(dispatch_values.keys(),colors):
            stage = dispatch_values[k]
            p1.line(list(stage.keys()),list(stage.values()),legend_label=k,line_width=2,color=color)

        for k, color in zip(apptx_values.keys(),colors):
            stage = apptx_values[k]
            p2.line(list(stage.keys()),list(stage.values()),legend_label=k,line_width=2,color=color)

        for k, color in zip(query_values.keys(),colors):
            stage = query_values[k]
            p3.line(list(stage.keys()),list(stage.values()),legend_label=k,line_width=2,color=color)

        for k, color in zip(stxstore_values.keys(),colors):
            stage = stxstore_values[k]
            p4.line(list(stage.keys()),list(stage.values()),legend_label=k,line_width=2,color=color)

        for k, color in zip(stitcher_values.keys(),colors):
            stage = stitcher_values[k]
            p5.line(list(stage.keys()),list(stage.values()),legend_label=k,line_width=2,color=color)

        for k, color in zip(emx_values.keys(),colors):
            stage = emx_values[k]
            p6.line(list(stage.keys()),list(stage.values()),legend_label=k,line_width=2,color=color)

        for k, color in zip(odb_values.keys(),colors):
            stage = odb_values[k]
            p7.line(list(stage.keys()),list(stage.values()),legend_label=k,line_width=2,color=color)


        p = column(p1,p2,p3,p4,p5,p6,p7)

        save(p)
            
    except Exception as e:
        print(e)

def diskplots(casenum,file_create_dir,path):
    try:
        disk_plot = casenum+'_diskplot.html'
        disk_values = {}
        date_key = ''
     
        file_to_read = os.path.abspath(file_create_dir)+'/files/var/log/appinternals/sensor/today/iostat.out'
        fobj = open(file_to_read)

        disk_prog = re.compile('^([^ ]+)[ ]+([^ ]+[ ]+){12}([0-9]*\.[0-9]+|[0-9]+)[ %]*$')
        datematch = re.compile('^\d{2}\/\d{2}\/\d{4}[ ]\d{2}:\d{2}:\d{2}')
        date_prog = re.compile('^\d{2}\/\d{2}\/\d{2}[ ]\d{2}:\d{2}:\d{2}')

        for line in fobj:
            if(datematch.findall(line)):
                date_key = datematch.findall(line)
            elif(disk_prog.findall(line) and date_key!=''):
                disk_stage = disk_prog.findall(line)
                if(disk_stage[0][0] not in disk_values.keys()):
                    disk_values.update({disk_stage[0][0]:{}})
                disk_values[disk_stage[0][0]].update({datetime.datetime.strptime(date_key[0],'%m/%d/%Y %H:%M:%S'):float(disk_stage[0][2])})

        fobj.close()
 
        output_file(disk_plot, title="DISK UTILIZATION")
        datetime_tick_formats = {
            key: ["%a %b %d %H:%M:%S"]
            for key in ("seconds", "minsec", "minutes", "hourmin", "hours", "days")}

        p = figure(title="Disk Utilization",plot_width=800, plot_height=350,x_axis_type="datetime")
        p.xaxis.axis_label="Time"
        p.yaxis.axis_label="Disk %"
        p.xaxis.formatter = DatetimeTickFormatter(**datetime_tick_formats)

        colors = itertools.cycle(palette)

        for k, color in zip(disk_values.keys(),colors):
            stage = disk_values[k]
            p.line(list(stage.keys()),list(stage.values()),legend_label=k,line_width=2,color=color)

        save(p)

    except Exception as e:
        print(e)


def memplots(casenum,file_create_dir,path):
    try:
        mem_plot = casenum+'_memplot.html'
        pltvalues = {}
        pltvalues_final = []

        file_to_read = os.path.abspath(file_create_dir)+'/files/var/log/appinternals/sensor/today/vmstat.out'
        fobj = open(file_to_read)

        for line in fobj:
            if(line.find('memory')!=-1 or line.find('free')!=-1):
                continue
            else:
                k = re.findall('^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',line)[0]

                prog = re.compile('^([^ ]+[ ]+){5}(([0-9]*\.[0-9]+|[0-9]+[ ]+){3})([^ ]+[ ]+){10}[^ ]+[ ]*$')
                match = prog.findall(line)
                result = re.findall('[0-9]*[0-9]*[0-9]*[0-9]',match[0][1])
                for x in range(0,len(result)):
                    result[x] = int(result[x])

                v = sum(result)/1000
                pltvalues.update({k:v})

        fobj.close()

        pltvalues_sorted = sorted(pltvalues)
        for x in pltvalues_sorted:
            pltvalues_final.append(pltvalues.get(x))

        pltvalues_final = [float(i) for i in pltvalues_final]
        pltvalues_sorted = [datetime.datetime.strptime(x.strip(),'%Y-%m-%d %H:%M:%S') for x in pltvalues_sorted]

        output_file(mem_plot, title="Memory Usage")
        datetime_tick_formats = {
            key: ["%a %b %d %H:%M:%S"]
            for key in ("seconds", "minsec", "minutes", "hourmin", "hours", "days")}

        p = figure(title="Free Memory",plot_width=800, plot_height=350,x_axis_type="datetime")
        p.xaxis.axis_label="Time"
        p.yaxis.axis_label="Memory(mb)"
        p.xaxis.formatter = DatetimeTickFormatter(**datetime_tick_formats)
        p.line(pltvalues_sorted,pltvalues_final,line_width=2,color='red')

        save(p)

    except Exception as e:
     print(e)

def cpuplots(casenum,file_create_dir,path):
    try:
        cpu_plot = casenum+'_cpuplot.html'

        pltvalues = {}
        cpuidle = {}
        cpuuser = {}
        cpusys = {}
        cpuidle_final = []
        cpuuser_final = []
        cpusys_final = []

        file_to_read = os.path.abspath(file_create_dir)+'/files/var/log/appinternals/sensor/today/top-15s.out'

        fobj = open(file_to_read)

        for line in fobj:
            match = re.search(r'\d\d\d\d-\d\d-\d\d',line)
            if match:
                k = line
            elif (line.find('Cpu(s):')!=-1):
                v = line.split(':')[1]

                pltvalues.update({k:v})

        fobj.close()

        for k,v in pltvalues.items():
            k_id = k
            v_idle = v.split(',')[3]
            v_user = v.split(',')[0]
            v_sys = v.split(',')[1]

            cpuidle.update({k_id:v_idle.strip('%id')})
            cpuuser.update({k_id:v_user.strip('%us')})
            cpusys.update({k_id:v_sys.strip('%sy')})

        cpuidle_sorted = sorted(cpuidle)
        cpuuser_sorted = sorted(cpuuser)
        cpusys_sorted = sorted(cpusys)

        for x in cpuidle_sorted:
            cpuidle_final.append(cpuidle.get(x))

        for x in cpuuser_sorted:
            cpuuser_final.append(cpuuser.get(x))

        for x in cpusys_sorted:
            cpusys_final.append(cpusys.get(x))

        cpuidle_final = [float(i) for i in cpuidle_final]
        cpuidle_sorted = [datetime.datetime.strptime(x.strip(),'%Y-%m-%d %H:%M:%S') for x in cpuidle_sorted]

        cpuuser_final = [float(i) for i in cpuuser_final]
        cpuuser_sorted = [datetime.datetime.strptime(x.strip(),'%Y-%m-%d %H:%M:%S') for x in cpuuser_sorted]

        cpusys_final = [float(i) for i in cpusys_final]
        cpusys_sorted = [datetime.datetime.strptime(x.strip(),'%Y-%m-%d %H:%M:%S') for x in cpusys_sorted] 


        output_file(cpu_plot, title="CPU Usage")
        datetime_tick_formats = {
            key: ["%a %b %d %H:%M:%S"]
            for key in ("seconds", "minsec", "minutes", "hourmin", "hours", "days")}

        p1 = figure(title="CPU Idle",plot_width=800, plot_height=350,x_axis_type="datetime")
        p1.xaxis.axis_label="Time"
        p1.yaxis.axis_label="CPU %"
        p1.xaxis.formatter = DatetimeTickFormatter(**datetime_tick_formats)
        p1.line(cpuidle_sorted,cpuidle_final, line_width = 2, color = 'red')

        p2 = figure(title="CPU User",plot_width=800, plot_height=350,x_axis_type="datetime")
        p2.xaxis.axis_label="Time"
        p2.yaxis.axis_label="CPU %"
        p2.xaxis.formatter = DatetimeTickFormatter(**datetime_tick_formats)
        p2.line(cpuuser_sorted,cpuuser_final, line_width = 2, color = 'red')

        p3 = figure(title="CPU System",plot_width=800, plot_height=350,x_axis_type="datetime")
        p3.xaxis.axis_label="Time"
        p3.yaxis.axis_label="CPU %"
        p3.xaxis.formatter = DatetimeTickFormatter(**datetime_tick_formats)
        p3.line(cpusys_sorted,cpusys_final, line_width = 2, color = 'red')

        p = column(p1,p2,p3)
        save(p)

    except Exception as e:
        print(e)

##Function to upload bundle to logalyzer using R
def upload(casenum,path):
    try:
        script_name = 'logalyze'
        print('Uploading bundle to logalyzer.... ')
  
        execute_string = ('{0} {1} {2}'.format(script_name,casenum,path))
        os.system(execute_string)
        
    except Exception as e:
        print(e)

def permfix(file_create_dir):
    try:
       perms = 'chmod -R 777'
       execute_string = ('{0} {1}/'.format(perms,file_create_dir)) 
       os.system(execute_string)

    except Exception as e:
        print(e)

##Function to set details when we have 4 arguments
def setdetails4(argv):
        try:
                if argv[1].isdigit():
                        if argv[2]!='':
                                path = argv[0]
                                casenum = argv[1]
                                errorandwarn = str(casenum)+'_'+str(argv[2])+'_errorsandwarns.txt'
                                filename = str(casenum)+'_'+str(argv[2])+'_systemdetails.txt'
                                title = str('AIX_logs_'+str(casenum)+'_'+str(argv[2])).rstrip()

                        else:
                                path = argv[0]
                                casenum = argv[1]
                                errorandwarn = str(casenum)+'_errorsandwarns.txt'
                                filename = str(casenum)+'_systemdetails.txt'
                                title = str('AIX_logs_'+str(casenum)).rstrip()
                else:
                        print('\nCase number should be numeric only')
                        print('Usage: python script_name path_to_diagbundle case_number <optional Desc>')
                        exit()

        except Exception as e:
                print(e)

        return path,casenum,filename,errorandwarn,title

##Function to set details when we have 3 arguments
def setdetails3(argv):
        try:
                if argv[1].isdigit():
                        path = argv[0]
                        casenum = argv[1]
                        errorandwarn = str(casenum)+'_errorsandwarns.txt'
                        filename = str(casenum)+'_systemdetails.txt'
                        title = str('AIX_logs_'+str(casenum)).rstrip()
                else:
                        print('\nCase number should be numeric only')
                        print('Usage: python script_name path_to_diagbundle case_number <optional Desc>')
                        exit()

        except Exception as e:
                print(e)

        return path,casenum,filename,errorandwarn,title
   
##Main function
def main():
    global filename
    global errorandwarn    
    
    if len(sys.argv)==4:
        try:
                path,casenum,filename,errorandwarn,title = setdetails4(sys.argv[1:])
        except Exception as e:
                print(e)
    elif len(sys.argv)==3:
        try:
                path,casenum,filename,errorandwarn,title = setdetails3(sys.argv[1:])
        except Exception as e:
                print(e)
    else:
        print('\nUsage: python script_name path_to_diagbundle case_number <optional Desc>')
        exit()

    email = str(casenum)+'@riverbedsupport.com'
    customer = 'Global Support'
    file_name = os.path.abspath(path)

    try:

        cleanup(path,filename,errorandwarn)
        file_create_dir = unzip(path)
        conn, c = dbconnect(path)

    except Exception as e:
        print(e)

    if ((conn != ' ') and (c !=' ')):

        agentcount(conn,c)
        agentsonline(conn,c)
        agentsonffline(conn,c)
        agtcntversion(conn,c)

        processcount(conn,c)
        processcountlist(conn,c)

        processmonikercount(conn,c)
        processmonikertoinstr(conn,c)
        processmonikernotinstr(conn,c)

        
        dbclose(conn)

    navigatefolders()
    weblinks(file_create_dir,path,filename,errorandwarn)
    plots(casenum,file_create_dir,path)
    upload(casenum,path)
    permfix(file_create_dir)    

    end = time.time()
    print('Took '+str(end-start)+'s'+' for the script to finish.... ')

if __name__=="__main__":
    main()
