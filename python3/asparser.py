#############################################################################################################
##
## 03/23/17 - Added agent count grouped by version,
##            Changed processcountlist function to count(id) from count(*)
##            Changed processcountlist function to use correct wording as process count and not agent count
##            Added SEVERE in the list of search strings
##
## 03/25/17 - Added latest core files to be written to details output file along with total count of core files
##
## 03/28/17 - Python 2.x does support 'encoding' option for 'open(file, encoding='utf8')'. Removed encoding
##            Find a way to open trace file with out encoding error
##
## 03/31/17 - Added silostatus function to check if status of stitcher/aggregator input buffer is keeping up
##            or lagging. Anything which has GiB should be an issue. Few hundred MB should be fine
##            Added 'HTTPError' as on of the search words
##
## 04/03/17 - Added section to write latest purge details from silo_dispatch.log
##
## 04/14/17 - Added case number to be entered which is appended to output files
##            Cleaning up unzipped folder
##            Moving output files to location of the dump file
##            If the file exists remove the existing file and move the new file
## 04/14/17 - Ran into 'UnicodeDecodeError' while reading a file from AR11 sysdump
##            Added try catch block to catch the exception and skip the file which have different encoding
## 05/19/17 - Added check for case number. If entered case number is not numeric do not proceed until
##            until valid numeric value is enetered
## 06/20/17 - isnumeric is not recognized function in Python 2. Changed it to isdigit
## 07/23/17 - Errors in upgrade.log now in errorandwarns file.
## 08/01/17 - Added logic to check JOURNAL_DIR_STX_STORE_IN buffer to see if processing of data is lagging
## 08/27/17 - Added logic to get the appliance type from the ljsystem file.
#############################################################################################################

#############################################################################################################
                                    ##########TO DO##########

## ENH-1 - If the error/warning is repeating, write the error/warn once and count on how many time it occurred in that day

#############################################################################################################

import os
import re
import sqlite3
import zipfile
import shutil


##Delete all previously extracted folders
def cleanup():

    cwd = os.getcwd()

    print('Deleting folders...')
    
    for fdname in os.listdir(cwd):
        if os.path.isdir(os.path.abspath(fdname)):
            print('Deleting folder',os.path.abspath(fdname))
            shutil.rmtree(os.path.abspath(fdname),ignore_errors=False)


    for fname in os.listdir(cwd):
        if fname.endswith('.txt'):
            os.remove(fname)            

##Unzip the diag bundle zip file
def unzip(filepath):

    print('Unzipping bundle..')
    
    zfile = zipfile.ZipFile(filepath)
    zfile.extractall()
    zfile.close()

    print('Finished unzipping the bundle...')

##Use to open a file for any function
def openfile(file):
    print ('Reading file',file+'\n')
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
    try:

        for logfile in filelist:
            for foldername in folderstoread:
                if foldername in logfile:
                    if logfile.find('coretrace')==-1:
                        print('Processing ',logfile)
                        errorsandwarns(logfile)
                        if ((logfile.find('silo_dispatch-performance.log')!=-1) or (logfile.find('silo_dispatch.log')!=-1)):
                            silostatus(logfile)
                            
                            
    except FileNotFoundError:
        print(logfile,'File does not exist...\n')

##    try:    
##
##        print('\n***************CONFIG FILE LIST*****************\n')
##
##        for conffile in configfiles:
##            for fdrname in folderstoread_config:
##                if fdrname in conffile:
##                    print(conffile)
##
##    except FileNotFoundError:
##        print(conffile,'File does not exist...\n')

    for conffile in configfiles:
        configdetails(conffile)

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
    fobj = openfile(conffile)

    fwrite = open(filename,'a')
    fwrite.write('\n***** List of corrupt odb files ***** \n')

    for i in fobj:
        fwrite.write(i)        

    fwrite.close()
    fobj.close()

##Function to get disk usage details on AS    
def dfh(conffile):
    fobj = openfile(conffile)

    fwrite = open(filename,'a')
    fwrite.write('\n***** Disk Usage details ***** \n')

    for i in fobj:
        if(i.find('Filesystem')== -1):
            fwrite.write(i)
            
    fwrite.close()
    fobj.close()

##Function to get supervisor status
def syctlstatus(conffile):
    fobj = openfile(conffile)

    fwrite = open(filename,'a')
    fwrite.write('\n***** Supervisor service status ***** \n')

    for i in fobj:
        fwrite.write(str(i[:i.index(',')])+'\n')

    fwrite.close()
    fobj.close()

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

    fobj = openfile(conffile)

    fwrite = open(filename,'a')
    fwrite.write('\n***** Appliance type *****\n')

    for i in fobj:
        if(i.find('"install_type":')!=-1):
            x = i[i.index(':'):]

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

##Function to get latest status of silo statistics
def silostatus(logfile):
    silostats = {}

    fobj = openfile(logfile)
    fwrite = open(filename,'a')

    if(logfile.find('silo_dispatch-performance.log')!=-1):
        fwrite.write('\n****** Stitcher/Aggregator input buffer ***** \n')

        for line in fobj:
            if(line.find('JOURNAL_DIR_STITCHER_IN')!=-1 or line.find('JOURNAL_DIR_STX_STORE_IN')!=-1):
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
                if value.find('GiB') != -1:
                    fwrite.write('Might be lagging in processing data..'+key+'-'+value)
                else:
                    fwrite.write('(OK) '+key+'-'+value)
            else:
                fwrite.write('Number of Records: '+value)
    else:
        lines = fobj.readlines()
        purge_details=lines[-15:]

        fwrite.write('\n****** Latest purge details ***** \n')
        for x in purge_details:
            if ((x.find('DIAG:')!=-1) or x.find('Retired')!=-1):
                fwrite.write(x)

    fwrite.close()
    fobj.close()
    
    
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
                            crptapptraces(conffile)
                        else:
                            if(conffile.find('corrupt_emx_traces.txt')!=-1 and conffile.find('num')==-1):
                                crptemxtraces(conffile)
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
            except IOError:
                 print(file+' already exists...Removing file')
                 os.remove(os.path.join(dst,file))
                 shutil.move(os.path.abspath(file),dst)        
    
##Main function
def main():
    global filename
    global errorandwarn    

    cleanup()
    
    print('Enter the full path to AS bundle zip file :')
    path = input()

    while True:
        print('Enter valid case number :')
        casenum = input()

        if casenum.isdigit():
            break

    filename = str(casenum)+'_'+'analysisserverdetails.txt'
    errorandwarn = str(casenum)+'_'+'errorsandwarns.txt'

    unzip(path)
    conn, c = dbconnect(path)

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
    movefiles(path)
    cleanup()
    
main()
