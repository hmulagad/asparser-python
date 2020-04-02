#!/opt/support/python37/bin/python3

import os
import re
import time
import sys
import datetime
from bokeh.plotting import figure, output_file, save
from bokeh.layouts import column
from bokeh.models.formatters import DatetimeTickFormatter
#from bokeh.palettes import Dark2_5 as palette
from bokeh.palettes import Category20 as palette
import itertools

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

def machinetype(file_create_dir,path):
    file_to_read = os.path.abspath(file_create_dir)+'/commands/files/lj.machine.json.txt'
    if os.path.exists(file_to_read):
        try:
            lre = ''
            fobj = open(file_to_read)

            for line in fobj:
                if(line.find('"is_lre":')!=-1):
                    lre = line.split(':')[1].strip()
 
            if 'true' in lre:
                lre = 'true'
            else:
                lre = 'false'

            fobj.close()
        except Exception as e:
            print(e) 
    else:
        lre = 'false'
    
    return lre
 

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

        colors = itertools.cycle(palette[20])

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

        LRE = machinetype(file_create_dir,path)
        file_to_read = os.path.abspath(file_create_dir)+'/files/var/log/appinternals/sensor/today/iostat.out'
        fobj = open(file_to_read)

        disk_prog = re.compile('^([^ ]+)[ ]+([^ ]+[ ]+){12}([0-9]*\.[0-9]+|[0-9]+)[ %]*$')

        if LRE == 'true':
            datematch = re.compile('^\d{2}\/\d{2}\/\d{2}[ ]\d{2}:\d{2}:\d{2}')
        else:
            datematch = re.compile('^\d{2}\/\d{2}\/\d{4}[ ]\d{2}:\d{2}:\d{2}')

        for line in fobj:
            if(datematch.findall(line)):
                date_key = datematch.findall(line)
            elif(disk_prog.findall(line) and date_key!=''):
                disk_stage = disk_prog.findall(line)
                if(disk_stage[0][0] not in disk_values.keys()):
                    disk_values.update({disk_stage[0][0]:{}})
                if LRE =='true':
                    disk_values[disk_stage[0][0]].update({datetime.datetime.strptime(date_key[0],'%m/%d/%y %H:%M:%S'):float(disk_stage[0][2])})
                else:
                    disk_values[disk_stage[0][0]].update({datetime.datetime.strptime(date_key[0],'%m/%d/%Y %H:%M:%S'):float(disk_stage[0][2])})

        fobj.close()
 
        output_file(disk_plot, title="DISK UTILIZATION")
        datetime_tick_formats = {
            key: ["%a %b %d %H:%M:%S"]
            for key in ("seconds", "minsec", "minutes", "hourmin", "hours", "days")}

        p = figure(title="Disk Utilization",plot_width=1000, plot_height=500,x_axis_type="datetime")
        p.xaxis.axis_label="Time"
        p.yaxis.axis_label="Disk %"
        p.xaxis.formatter = DatetimeTickFormatter(**datetime_tick_formats)

        colors = itertools.cycle(palette[20])

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
        cpuidle = {}
        cpuuser = {}
        cpusyst = {}
        load = {}

        file_to_read = os.path.abspath(file_create_dir)+'/files/var/log/appinternals/sensor/today/top-15s.out'

        date_prog = re.compile('^\d{4}-\d{2}-\d{2}[ ]\d{2}:\d{2}:\d{2}')
        cpu_prog = re.compile('([0-9]+.[0-9]+)')
        load_prog = re.compile('(load average:)[ ](\d+.\d+)')

        fobj = open(file_to_read)

        for line in fobj:
            if (date_prog.findall(line)):
                date_key = date_prog.findall(line)
            elif(load_prog.findall(line) and date_key!=''):
                load_stage = load_prog.findall(line)
                load.update({datetime.datetime.strptime(date_key[0],'%Y-%m-%d %H:%M:%S'):float(load_stage[0][1])})
            elif(cpu_prog.findall(line) and date_key!='' and line.find('Cpu(s):')!=-1):
                cpu_stage = cpu_prog.findall(line)
                cpuidle.update({datetime.datetime.strptime(date_key[0],'%Y-%m-%d %H:%M:%S'):float(cpu_stage[3])})
                cpuuser.update({datetime.datetime.strptime(date_key[0],'%Y-%m-%d %H:%M:%S'):float(cpu_stage[0])})
                cpusyst.update({datetime.datetime.strptime(date_key[0],'%Y-%m-%d %H:%M:%S'):float(cpu_stage[1])})
                
        fobj.close()

        output_file(cpu_plot, title="CPU Usage")
        datetime_tick_formats = {
            key: ["%a %b %d %H:%M:%S"]
            for key in ("seconds", "minsec", "minutes", "hourmin", "hours", "days")}

        p1 = figure(title="CPU Idle",plot_width=800, plot_height=350,x_axis_type="datetime")        
        p1.xaxis.axis_label="Time"
        p1.yaxis.axis_label="CPU%"
        p1.xaxis.formatter = DatetimeTickFormatter(**datetime_tick_formats)
        p1.line(list(cpuidle.keys()),list(cpuidle.values()),line_width=2,color="red")

        p2 = figure(title="CPU User",plot_width=800, plot_height=350,x_axis_type="datetime")
        p2.xaxis.axis_label="Time"
        p2.yaxis.axis_label="CPU%"
        p2.xaxis.formatter = DatetimeTickFormatter(**datetime_tick_formats)
        p2.line(list(cpuuser.keys()),list(cpuuser.values()),line_width=2,color="red")

        p3 = figure(title="CPU System",plot_width=800, plot_height=350,x_axis_type="datetime")
        p3.xaxis.axis_label="Time"
        p3.yaxis.axis_label="CPU%"
        p3.xaxis.formatter = DatetimeTickFormatter(**datetime_tick_formats)
        p3.line(list(cpusyst.keys()),list(cpusyst.values()),line_width=2,color="red")

        p4 = figure(title="Load Average",plot_width=800, plot_height=350,x_axis_type="datetime")
        p4.xaxis.axis_label="Time"
        p4.yaxis.axis_label="Load"
        p4.xaxis.formatter = DatetimeTickFormatter(**datetime_tick_formats)
        p4.line(list(load.keys()),list(load.values()),line_width=2,color="cyan")

        p = column(p1,p2,p3,p4)
        save(p)

    except Exception as e:
        print(e)

