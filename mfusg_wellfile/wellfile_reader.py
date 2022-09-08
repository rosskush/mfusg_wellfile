import numpy as np
import pandas as pd
import os
from collections import OrderedDict
import platform


def read_USG_well_file(fn,start_yr=2011, extra_cols=None,verbose=False, start_sp = 0, end_sp=None):
    # returns well stress period data in dict form, (1 based nodes because who uses zero based for Cell ID's?)
    # extra_cols are to inculde extra data from the well file like wellids or layer
    with open(fn, 'r') as file:
        stress_period_data = {}
        sp = 0
        lines = file.readlines()
        cnt = 0
        while lines[cnt].startswith('#'):
            cnt+=1
        if len(lines[cnt].split()) > 1:
            maxwels, ipakcb = lines[cnt].split()[0:2]
        else:
            maxwels = lines[cnt]
        cnt+=1

        data = []
        year = start_yr# 1929#, 2011
        while cnt < len(lines):
            stress_period_data[year] = []
            # print(days)
            # date = pd.to_datetime(f'01/01/{year}')
            numwells = int(lines[cnt].split()[0])
            # if numwells == -1:
            for w in range(numwells): # todo write something for when stress period is coppied from the last with a negative one (-1)
                cnt += 1
                line = lines[cnt].split()
                nodeid = line[0]
                flux = line[1]

                if nodeid.startswith('open'):
                    if "window" in platform.platform().lower():
                        model_ws = os.path.join(*fn.split('\\')[:-1])
                    else:
                        model_ws = os.path.join(*fn.split('/')[:-1])
                    refdf = pd.read_csv(os.path.join(model_ws,flux),delim_whitespace=True,names=['Node','Flux'])
                    for i, dfrow in refdf.iterrows():
                        stress_period_data[year].append([int(dfrow['Node']), float(dfrow['Flux'])])
                        row = [year, sp + 1, int(dfrow['Node']), float(dfrow['Flux'])]

                        if extra_cols is None:
                            data.append(row)
                        else:
                            col_len = len(extra_cols)
                            for col in range(col_len):
                                row.append(dfrow[col])
                            data.append(row)
                    year+=1
                    stress_period_data[year] = []
                    cnt +=1
                    if cnt+1 == len(lines):
                        break
                    # cnt += -numwells +1
                else:
                    stress_period_data[year].append([int(nodeid),float(flux)])

                    row = [year, sp+1,int(nodeid),float(flux)]
                    if sp >= start_sp-1:
                        if extra_cols is None:
                            data.append(row)
                        else:
                            col_len = len(extra_cols)
                            for col in range(col_len):
                                row.append(line[2+col])
                            data.append(row)

            sp += 1
            cnt += 1
            year += 1
            if verbose:
                print(cnt+1, sp,year)
            if end_sp == sp:
                break

        if extra_cols is None:
            columns = ['Year','SP','Node','Flux']
        else:
            columns = ['Year','SP','Node','Flux'] + extra_cols

        df = pd.DataFrame(data, columns = columns)
        # df['Date'] = pd.to_datetime(df['Date'])
        return stress_period_data, df

def read_struct_well_file(fn,start_yr=2011, extra_cols=None, sp2yr=None, nper=None):
    # returns well stress period data in dict form, (1 based nodes because who uses zero based for Cell ID's?)
    # extra_cols are to inculde extra data from the well file like wellids or layer
    with open(fn, 'r') as file:
        stress_period_data = {}
        sp = 0
        lines = file.readlines()
        cnt = 0
        while lines[cnt].startswith('#'):
            cnt+=1
        if len(lines[cnt].split()) > 1:
            maxwels, ipakcb = lines[cnt].split()[0:2]
        else:
            maxwels = lines[cnt]
        cnt+=1

        data = []
        year = start_yr# 1929#, 2011
        while cnt < len(lines):
            stress_period_data[year] = []
            # print(days)
            # date = pd.to_datetime(f'01/01/{year}')
            # if numwells == -1:

            # if lines[cnt].replace(' ','').startswith('-1'): # use previous stress period
            # print(year)
            if int(lines[cnt].split()[0]) == -1:
                # print(sp)
                stress_period_data[year] = stress_period_data[year-1]
                spcnt_i = spcnt
                for w in range(numwells):
                    # cnt += 1
                    spcnt_i+=1
                    line = lines[spcnt_i].split()
                    lay = int(line[0])
                    row = int(line[1])
                    col = int(line[2])
                    flux = float(line[3])

                    stress_period_data[year].append([int(lay),row,col,float(flux)])
                    if isinstance(sp2yr, dict):
                        row = [sp2yr[sp+1],  sp + 1, int(lay), row, col, float(flux)]
                    else:
                        row = [year, sp+1,int(lay),row,col,float(flux)]
                    if extra_cols is None:
                        data.append(row)
                    else:
                        col_len = len(extra_cols)
                        for col in range(col_len):
                            row.append(line[2+col])
                        data.append(row)
            else:
                numwells = int(lines[cnt].split()[0])
                spcnt = cnt
                for w in range(numwells): # todo write something for when stress period is coppied from the last with a negative one (-1)
                    cnt += 1

                    line = lines[cnt].split()
                    lay = int(line[0])
                    row = int(line[1])
                    try:
                        col = int(line[2])
                        flux = float(line[3])
                    except:
                        col, flux = line[2].split('-')
                        col = int(col)
                        flux = float(flux)
                    

                    stress_period_data[year].append([int(lay),row,col,float(flux)])

                    if isinstance(sp2yr, dict):
                        row = [sp2yr[sp + 1], sp + 1, int(lay), row, col, float(flux)]
                    else:
                        row = [year, sp + 1, int(lay), row, col, float(flux)]

                    if extra_cols is None:
                        data.append(row)
                    else:
                        col_len = len(extra_cols)
                        for c in range(col_len):
                            row.append(line[4+c])
                        data.append(row)

            sp += 1
            cnt += 1
            year += 1
            if isinstance(nper, int):
                if sp >= nper:
                    break


        if extra_cols is None:
            columns = ['Year','SP','Layer','Row','Column','Flux']
        else:
            columns = ['Year','SP','Layer','Row','Column','Flux'] + extra_cols

        df = pd.DataFrame(data, columns = columns)
        # df['Date'] = pd.to_datetime(df['Date'])
        return stress_period_data, df

def write_usg_wellfile(fn,welldf):
    formats = OrderedDict([('Node', '{:>10d}'.format),
                           ('Flux', '{:>10d}'.format),
                           ('Layer', '{:>10d}'.format),
                           ('Aquifer', '{:>10d}'.format),
                           ('County', '{>:30}'.format),
                           ('GCD', '{>:30}'.format)])

    years = np.arange(2011, 2071)
    pak_spd = {}
    for year in years:
        temp_welldf = welldf.loc[welldf['Year'] == year]
        pak_spd[year] = temp_welldf[list(formats.keys())].to_records(index=False)
    print('made rec arrays')
    # print(pak_spd)
    pak_spd = {key: pak_spd[key].tolist() for key in pak_spd.keys()}
    max_wells = 0
    for yr in pak_spd.keys():
        if len(pak_spd[yr]) > max_wells:
            max_wells = len(pak_spd[yr])

    with open(fn, 'w') as f:
        f.write(f'{max_wells} 50 AUTOFLOWREDUCE  IUNITAFR 166 AUX C01    NOPRINT\n')
        for y, rows in sorted(pak_spd.items()):
            f.write('{} 0 YR{}\n'.format(len(rows), y))
            for r in rows:
                n, cfd = r[0], r[1]
                lay, aq = r[2], r[3]
                co = r[4]
                gcd = r[5]
                f.write(f'{n} {cfd} {lay} {aq} {co} {gcd}\n')
    f.close()

def write_struct_wellfile(fn,welldf, strt_yr, end_yr):
    formats = OrderedDict([('Layer', '{:>10d}'.format),
                           ('Row', '{:>10d}'.format),
                           ('Column', '{:>10d}'.format),
                           ('Flux', '{:>10d}'.format)])

    years = np.arange(strt_yr, end_yr)
    pak_spd = {}
    for year in years:
        temp_welldf = welldf.loc[welldf['Year'] == year]
        pak_spd[year] = temp_welldf[list(formats.keys())].to_records(index=False)
    print('made rec arrays')
    # print(pak_spd)
    pak_spd = {key: pak_spd[key].tolist() for key in pak_spd.keys()}
    max_wells = 0
    for yr in pak_spd.keys():
        if len(pak_spd[yr]) > max_wells:
            max_wells = len(pak_spd[yr])

    with open(fn, 'w') as f:
        f.write(f'{max_wells} 50 AUTOFLOWREDUCE  IUNITAFR 166 AUX C01    NOPRINT\n')
        for y, rows in sorted(pak_spd.items()):
            f.write('{} 0 YR{}\n'.format(len(rows), y))
            for r in rows:
                n, cfd = r[0], r[1]
                lay, aq = r[2], r[3]
                co = r[4]
                gcd = r[5]
                f.write(f'{n} {cfd} {lay} {aq} {co} {gcd}\n')
    f.close()

#if __name__ == '__main__':
    # wellfile = os.path.join('model_ws','S1.wel.2011.2070','S1.GMA12.2011.2071.wel')

    # _, df = read_USG_well_file(wellfile,2011,['Layer','Aquifer','County','Source'])

#    GMA12_wellfile = os.path.join('model_ws','base.wel.Skiles.BRAA.1929-2010','gma12.Skiles.wel')
#    _, df = read_USG_well_file(GMA12_wellfile,1929)
#
#
#    print(df.head())
