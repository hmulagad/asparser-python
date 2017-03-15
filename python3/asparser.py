import os
import re
import sqlite3
import zipfile
import shutil

global filename
global errorandwarn
filename = 'analysisserverdetails.txt'
errorandwarn = 'errorsandwarns.txt'

##Delete all previously extracted folders
def cleanup():

    cwd = os.getcwd()

    print('Deleting folders...')
    
    for fdname in os.listdir(cwd):
        if os.path.isdir(os.path.abspath(fdname)):
            print('Deleting folder',os.path.abspath(fdname))
            shutil.rmtree(os.path.abspath(fdname),ignore_errors=False)

    print('Removing prior',filename)

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

    c.execute('SELECT state,count(*) as agentcount FROM process group by state order by state')

    list = c.fetchall()
    msg = 'Agentcount by state : '

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
                    print('Processing ',logfile)
                    errorsandwarns(logfile)

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
    fobj = openfile(conffile)

    fwrite = open(filename,'a')
    fwrite.write('\n***** Core files ***** \n')

    for i in fobj:
        fwrite.write(i)

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


##Function to search for all Errors and Warnings in log files
def errorsandwarns(logfile):

    searchstrings = ['ERROR','WARN']

    try:
        fobj = open(logfile)
        fwrite = open(errorandwarn,'a')
        fwrite.write('\n'+'******Errors and Warnings in file '+ str(logfile)+'******' + '\n\n')

        for i in fobj:
            for string in searchstrings:
                if string in i.strip():
                    fwrite.write(i)

        fobj.close()
        fwrite.close()
            
    except FileNotFoundError:
        print(logfile,'File does not exist...\n')
    
##Main function
def main():

    cleanup()
    
    print('Enter the full path to AS bundle zip file :')
    path = input()

    unzip(path)
    dbconnect(path)

    conn, c = dbconnect(path)

    if ((conn != ' ') and (c !=' ')):

        agentcount(conn,c)
        agentsonline(conn,c)
        agentsonffline(conn,c)

        processcount(conn,c)
        processcountlist(conn,c)

        processmonikercount(conn,c)
        processmonikertoinstr(conn,c)
        processmonikernotinstr(conn,c)

        
        dbclose(conn)
    navigatefolders()
    
main()
