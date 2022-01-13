{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "from obspy import *\n",
    "import struct\n",
    "import os\n",
    "import numpy as np\n",
    "\n",
    "def unpackAfile(infile):\n",
    "\n",
    "# == opening Afile ==\n",
    "    b= os.path.getsize(infile)\n",
    "    FH = open(infile, 'rb')\n",
    "    line = FH.read(b)\n",
    "    fileHeader= struct.unpack(\"<4s3h6bh6s\", line[0:24])\n",
    "    \n",
    "    fileLength = fileHeader[3]\n",
    "    port = fileHeader[10]\n",
    "    FirstStn = fileHeader[11][0:4].decode('ASCII').rstrip()\n",
    "    #print(fileHeader)\n",
    "# =================================Header===================================\n",
    "    \n",
    "    portHeader = []\n",
    "    for i in range(24,port*32,32):\n",
    "        port_data = struct.unpack(\"<4s4s3sbh2b4s12b\",line[i:i+32])\n",
    "        portHeader.append(port_data)\n",
    "\n",
    "# =================================Data===================================    \n",
    "\n",
    "    dataStartByte = 24+int(port)*32\n",
    "    dataPoint = 3*int(port)*int(fileLength)*100\n",
    "    times = int(port)*3*4\n",
    "    data=[]\n",
    "\n",
    "    data = struct.unpack(\"<%di\"%dataPoint,line[dataStartByte:dataStartByte+dataPoint*4])\n",
    "\n",
    "    \n",
    "    portHeader = np.array(portHeader)    \n",
    "    data = np.array(data)    \n",
    "    idata =data.reshape((3,port,fileLength*100),order='F')\n",
    "    \n",
    "#== write to obspy Stream --\n",
    "    #print(fileHeader)\n",
    "    #print(len(idata[0][0]))\n",
    "    sttime = UTCDateTime(fileHeader[1],fileHeader[4],fileHeader[5],fileHeader[6],fileHeader[7],fileHeader[8],fileHeader[2])\n",
    "    npts = fileHeader[3]*fileHeader[9]\n",
    "    samp = fileHeader[9]\n",
    "    #print(sttime)\n",
    "    # afst = Afile's Stream\n",
    "    afst = Stream()\n",
    "    \n",
    "    for stc in range(fileHeader[10]):\n",
    "        stn = portHeader[stc][0].decode('ASCII').rstrip()\n",
    "        instrument = portHeader[stc][1].decode('ASCII').rstrip()\n",
    "        loc = '0'+str(portHeader[stc][6].decode('ASCII'))\n",
    "        #net = \"TW\"\n",
    "        net = str(portHeader[stc][7].decode('ASCII')).rstrip()\n",
    "        GPS = int(portHeader[stc][3])\n",
    "        \n",
    "        # remove GPS unlock or broken station\n",
    "        if ( GPS == 1 or GPS == 2 ):\n",
    "            chc = 0\n",
    "            if instrument == 'FBA':\n",
    "                chc = 1\n",
    "            elif instrument == 'SP':\n",
    "                chc = 4\n",
    "            elif instrument == 'BB':\n",
    "                chc = 7\n",
    "            \n",
    "            #print(chc,instrument)\n",
    "            \n",
    "            # for each channel in port\n",
    "            for ch in range(3):\n",
    "                #print(num,ch,chc)\n",
    "                chn = 'Ch'+str(chc+ch)\n",
    "                #print(stc,channel)\n",
    "                \n",
    "                stats = {'network': net, 'station': stn, 'location': loc,\n",
    "                        'channel': chn, 'npts': npts, 'sampling_rate': samp,\n",
    "                        'starttime': sttime}\n",
    "                \n",
    "                data = np.array(idata[ch][stc], dtype=float)\n",
    "                sttmp = Stream([Trace(data=data, header=stats)])\n",
    "                afst += sttmp\n",
    "    \n",
    "    #stst = stms[0]\n",
    "    #stst.detrend('linear').plot()\n",
    "    #stms.write('test.mseed', format='MSEED')    \n",
    "    \n",
    "    return afst, FirstStn, fileHeader"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import csv\n",
    "import codecs\n",
    "import time\n",
    "\n",
    "#start_time = time.time()\n",
    "weather = dict()\n",
    "weather1 = dict()\n",
    "with open ('network20.csv', 'w', newline = '',encoding='big5') as csvfile:\n",
    "    datanames=['network','station','location','channel','npts','sampling_rate','starttime','delta','calib']\n",
    "    writer = csv.DictWriter(csvfile , fieldnames = datanames)\n",
    "    #writer.writeheader()\n",
    "    for j in range(0,5556):\n",
    "        for i in range(0,36):\n",
    "            #print(unpackAfile('05290646.40C')[0][i].stats['network'])\n",
    "            #print(type(unpackAfile('05290646.40C')[0][i].stats['network']))\n",
    "            net=str(unpackAfile('05290646.40C')[0][i].stats['network'])\n",
    "            stn=str(unpackAfile('05290646.40C')[0][i].stats['station'])\n",
    "            loc=str(unpackAfile('05290646.40C')[0][i].stats['location'])\n",
    "            chn=str(unpackAfile('05290646.40C')[0][i].stats['channel'])\n",
    "            npts=str(unpackAfile('05290646.40C')[0][i].stats['npts'])\n",
    "            samp=str(unpackAfile('05290646.40C')[0][i].stats['sampling_rate'])\n",
    "            sttime=str(unpackAfile('05290646.40C')[0][i].stats['starttime'])\n",
    "            delt=str(unpackAfile('05290646.40C')[0][i].stats['delta'])\n",
    "            cal=str(unpackAfile('05290646.40C')[0][i].stats['calib'])\n",
    "            weather['network']=net\n",
    "            weather['station']=stn\n",
    "            weather['location']=loc\n",
    "            weather['channel']=chn\n",
    "            weather['npts']=npts\n",
    "            weather['sampling_rate']=samp\n",
    "            weather['starttime']=sttime\n",
    "            weather['delta']=delt\n",
    "            weather['calib']=cal\n",
    "            writer.writerow(weather)\n",
    "            \n",
    "#創造地震資料"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "from pyhive import hive  # or import hive\n",
    "cursor = hive.connect(host='....',port=10000,auth='LDAP',username='root',password='....', database='default').cursor()\n",
    "#connect hiveserver2\n",
    "#host為ubuntu主機名或ip address\n",
    "#username用建立/user/hive/warehouse的授權名,要不然會出現一些授權上的問題\n",
    "#database為資料庫\n",
    "#password是你在執行beeline時所輸入的密碼"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "#參考資料hive指令手冊網址https://cwiki.apache.org/confluence/display/Hive/LanguageManual+DDL\n",
    "cursor.execute('show tables')\n",
    "print (cursor.fetchall())\n",
    "#顯示table有哪些"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "cursor.execute(\"CREATE TABLE name (network STRING, station STRING, location STRING, channel STRING, npts STRING, sampling_rate STRING, starttime STRING, delta STRING, calib STRING) row format delimited fields terminated by ',' lines terminated by '\\n' stored as textfile\")\n",
    "cursor.execute('show tables')\n",
    "print (cursor.fetchall())\n",
    "#創建 table 地震資料的格式"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "cursor.execute('drop table name')\n",
    "cursor.execute('show tables')\n",
    "print (cursor.fetchall())\n",
    "#刪除table"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "cursor.execute('show databases')\n",
    "print (cursor.fetchall())\n",
    "#顯示database有哪些"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "cursor.execute('create database test1')\n",
    "print (cursor.fetchall())\n",
    "#創建database"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "cursor.execute(\"load data inpath '' into table earthquakedata1\")\n",
    "#load data inpath 是用在hdfs系統中的資料放入在earthquake1 table 中 , 而 ''是放路徑"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "cursor.execute(\"load data local inpath '' into table earthquakedata1\")\n",
    "\n",
    "#load data inpath 是用在ubuntu主機中的資料放入在earthquake1 table 中 , 而 ''是放路徑"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "cursor.execute(\"insert into table earthquakedata2 select * from earthquakedata1\")\n",
    "#插入資料到Table"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
