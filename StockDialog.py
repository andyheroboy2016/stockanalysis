# coding: utf8
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import tushare as ts
import pandas as pd
import sys
import os
import csv
import time
import threading as th


class testTradeHistoryData():
    def __init__(self, code,  startDate, endDate):
        self.startDate = startDate
        self.endDate = endDate
        self.stockCode = code
        self.stockHisIndex = 0
        self.stockDateIndex=1
        self.stockRealDef = ts.get_realtime_quotes(code)
        self.stockDateDef=ts.get_h_data(code, start=self.startDate, end=self.endDate)
        self.stockHisDef=None
    def getOneHistoryDate(self, code):
        if code!=self.stockCode or code!=self.stockRealDef.ix[0, 'code']:
            return None
        else:
            while(1):
                if (self.stockDateDef is None) or (self.stockDateIndex>=len(self.stockDateDef.index)):
                    return None
                if (self.stockHisDef is None) or (self.stockHisIndex>=len(self.stockHisDef.index)):
                    self.stockHisIndex=0
                    self.stockDateIndex+=1
                    self.startDate=self.stockDateDef.index.astype('str')[len(self.stockDateDef.index)-self.stockDateIndex]
                    if self.startDate>self.endDate:
                        return None
                    self.stockHisDef=ts.get_tick_data(self.stockCode, date=self.startDate)
                    continue
                else:
                    self.stockHisIndex+=1
                    self.stockRealDef.ix[0, 'open']=self.stockDateDef.ix[len(self.stockDateDef.index)-self.stockDateIndex, 'open']
                    self.stockRealDef.ix[0, 'pre_close']=self.stockDateDef.ix[len(self.stockDateDef.index)-self.stockDateIndex+1, 'close']
                    self.stockRealDef.ix[0, 'price']=self.stockHisDef.ix[len(self.stockHisDef.index)-self.stockHisIndex, 'price']
                    self.stockRealDef.ix[0, 'high']=self.stockDateDef.ix[len(self.stockDateDef.index)-self.stockDateIndex, 'high']
                    self.stockRealDef.ix[0, 'low']=self.stockDateDef.ix[len(self.stockDateDef.index)-self.stockDateIndex, 'low']
                    self.stockRealDef.ix[0, 'date']=self.stockDateDef.index.astype('str')[len(self.stockDateDef.index)-self.stockDateIndex]
                    self.stockRealDef.ix[0, 'time']=self.stockHisDef.ix[len(self.stockHisDef.index)-self.stockHisIndex, 'time']
#                    print self.stockRealDef.ix[0, 'open'], self.stockRealDef.ix[0, 'pre_close'], self.stockRealDef.ix[0, 'price'], self.stockRealDef.ix[0, 'date'], self.stockRealDef.ix[0, 'time']
                    return self.stockRealDef

class stockRealTimeInfo():
    def __init__(self):
        self.realCode = ''
        self.updateall = 0
        self.numberList=['000001', '399001', '399006']
        self.updateNumber = 0
        self.numberColumns=['code', 'name', 'change', 'close']
#        self.tmpDateStock = testTradeHistoryData('300133','2010-01-01', '2016-01-01')
#        self.tmpDateStock.getOneHistoryDate('300133')

    def stockUpdateAll(self, codeList):
        try:
#            self.numberDefAll=ts.get_index()
            if (self.numberDefAll is None) or (len(self.numberDefAll) == 0):
                self.updateNumber = 0
            else:
                self.updateNumber = 1
        except:
            self.updateNumber = 0
        if (len(codeList) == 0):
            self.updateall = 0
            return
        try:
            self.realDefAll=ts.get_realtime_quotes(codeList)
            if (self.realDefAll is None) or (len(self.realDefAll.index) == 0):
                self.updateall = 0
            else:
                self.updateall = 1
        except:
            self.updateall = 0

    def stockGetNumberInfo(self):
        tmpNumber=[]
        xIndex=0
        if self.updateNumber == 0:
            return tmpNumber
        for xCode in self.numberDefAll['code'].values:
            for yCode in self.numberList:
                if xCode == yCode:
                    tmpNumber.append(self.numberDefAll.ix[xIndex, self.numberColumns[0]])
                    tmpNumber.append(self.numberDefAll.ix[xIndex, self.numberColumns[1]])
                    tmpNumber.append(self.numberDefAll.ix[xIndex, self.numberColumns[2]])
                    tmpNumber.append(self.numberDefAll.ix[xIndex, self.numberColumns[3]])
            xIndex+=1
        return tmpNumber

    def getNameDateTimeByCode(self, code):
        if self.updateall == 0:
            return ('', '', '')
        for idx in range(len(self.realDefAll.index)):
            if code == self.realDefAll.ix[idx, "code"]:
                return (self.realDefAll.ix[idx, "name"], self.realDefAll.ix[idx, "date"], self.realDefAll.ix[idx, "time"])
        return ('', '', '')

    def getPirceByCode(self, code):
        if self.updateall == 0:
            return 0.0
        for idx in range(len(self.realDefAll.index)):
            if code == self.realDefAll.ix[idx, "code"]:
                return float(self.realDefAll.ix[idx, "price"])
        return 0.0

    def stockUpdate(self, code):
        if code == '':
            self.realCode=''
            return
        if (self.updateall==1) and (self.realCode != ''):
            for idx in range(len(self.realDefAll.index)):
                if self.realDefAll.ix[idx, "code"] == code:
                    for idy in range(len(self.realDefAll.columns)):
                        self.realDef.ix[0, idy]=self.realDefAll.ix[idx, idy]
                    self.realCode=code
                    return
        try:
            self.realDef=ts.get_realtime_quotes(code)
            if (self.realDef is None) or (len(self.realDef.index) == 0):
                self.realCode=''
            else:
                self.realCode=code
        except:
            self.realCode=''

    def stockGetName(self):
        if self.realCode == '':
            return ''
        else:
            return self.realDef.ix[0, "name"]

    def stockGetPrice(self):
        price = 0.0
        if self.realCode != '':
            price=float(self.realDef.ix[0, "price"])
        return price

    def stockGetPrevPrice(self):
        prevPrice = 0.0
        if self.realCode != '':
            prevPrice=float(self.realDef.ix[0, "pre_close"])
        return prevPrice

    def stockGetHighPrice(self):
        highPrice=0.0
        if self.realCode != '':
            highPrice=float(self.realDef.ix[0, "high"])
        return highPrice

    def stockGetLowPrice(self):
        lowPrice=0.0
        if self.realCode != '':
            lowPrice=float(self.realDef.ix[0, "low"])
        return lowPrice

    def stockGetDate(self):
        dates=''
        if self.realCode != '':
            dates=self.realDef.ix[0, "date"]
        return dates

    def stockGetTime(self):
        time=''
        if self.realCode != '':
            time=self.realDef.ix[0, "time"]
        return time

    def stockGetPercent(self):
        percent=0.0
        if self.realCode != '':
            percent=100*(float(self.realDef.ix[0, "price"])-float(self.realDef.ix[0, "pre_close"]))/float(self.realDef.ix[0, "pre_close"])
        return percent

    def stockGetNameByCode(self, code):
        try:
            tmpDef=ts.get_realtime_quotes(code)
            if (tmpDef is None) or (len(tmpDef.index)==0):
                return ''
        except:
            return ''
        return tmpDef.ix[0, "name"]

class StockTradeSaveFile():
    def __init__(self):
        self.stockSaveFile="stocklog.csv"
        self.tradeSaveFile="tradelog.csv"
        self.fundSaveFile="fundlog.csv"
        self.stockColumns=['选择', '股票代码',  '股票名称', '涨幅卖出', '跌幅买入', '交易倍数', '最低买卖']
        self.stockType=['int', 'str', 'str', 'float', 'float', 'int', 'int']
        self.tradeColumns=['交易状态', '股票代码', '股票名称', '买入日期', '买入时间', '交易价格', '交易数量']
        self.tradeType=['str', 'str', 'str', 'str', 'str', 'float', 'int']
        self.fundColumns=['日期', '时间', '状态', '最高资金', '剩余资金']
        self.fundType=['str', 'str', 'str', 'float', 'float']
        self.csvFileExist(self.stockSaveFile)
        self.csvFileExist(self.tradeSaveFile)
        self.csvFileExist(self.fundSaveFile)
        self.readDefInFile(self.stockSaveFile)
        self.readDefInFile(self.tradeSaveFile)
        self.readDefInFile(self.fundSaveFile)

    def csvFileAsType(self, csvFile):
        if csvFile==self.stockSaveFile:
            for idx in range(len(self.stockColumns)):
                self.stockDef[self.stockColumns[idx]]=self.stockDef[self.stockColumns[idx]].astype(self.stockType[idx])
        elif csvFile==self.tradeSaveFile:
            for idx in range(len(self.tradeColumns)):
                self.tradeDef[self.tradeColumns[idx]]=self.tradeDef[self.tradeColumns[idx]].astype(self.tradeType[idx])
        elif csvFile==self.fundSaveFile:
            for idx in range(len(self.fundColumns)):
                self.fundDef[self.fundColumns[idx]]=self.fundDef[self.fundColumns[idx]].astype(self.fundType[idx])

    def csvFileExist(self, csvFile):
        if os.path.exists(csvFile) == False:
            csvFileHandler=file(csvFile, 'w')
            csvWriter=csv.writer(csvFileHandler)
            if csvFile==self.stockSaveFile:
                csvWriter.writerow(self.stockColumns)
            elif csvFile==self.tradeSaveFile:
                csvWriter.writerow(self.tradeColumns)
            elif csvFile==self.fundSaveFile:
                csvWriter.writerow(self.fundColumns)
            csvFileHandler.close()

    def updateListToFile(self, index, csvFileList, csvFile):
        if csvFile==self.stockSaveFile:
            if (index < 0) or (index >= len(self.stockDef.index)):
                rowCount = len(self.stockDef.index)
            else:
                rowCount = index
            for idx in range(len(self.stockColumns)):
                self.stockDef.set_value(rowCount, self.stockColumns[idx], csvFileList[idx])
            self.csvFileAsType(csvFile)
            self.stockDef.to_csv(csvFile, index=False)
        elif csvFile==self.tradeSaveFile:
            if (index < 0) or (index >= len(self.tradeDef.index)):
                rowCount = len(self.tradeDef.index)
            else:
                rowCount = index
            for idx in range(len(self.tradeColumns)):
                self.tradeDef.set_value(rowCount, self.tradeColumns[idx], csvFileList[idx])
            self.csvFileAsType(csvFile)
            self.tradeDef.to_csv(csvFile, index=False)
        elif csvFile==self.fundSaveFile:
            if (index < 0) or (index >= len(self.fundDef.index)):
                rowCount = len(self.fundDef.index)
            else:
                rowCount = index
            for idx in range(len(self.fundColumns)):
                self.fundDef.set_value(rowCount, self.fundColumns[idx], csvFileList[idx])
            self.csvFileAsType(csvFile)
            self.fundDef.to_csv(csvFile, index=False)

    def deleteListToFile(self, index, csvFile):
        if csvFile==self.stockSaveFile:
            if (index < len(self.stockDef.index)):
                self.stockDef.drop(index, inplace=True)
                self.csvFileAsType(csvFile)
                self.stockDef.to_csv(csvFile, index=False)
                self.readDefInFile(csvFile)
        elif csvFile==self.tradeSaveFile:
            if (index < len(self.tradeDef.index)):
                self.tradeDef.drop(index, inplace=True)
                self.csvFileAsType(csvFile)
                self.tradeDef.to_csv(csvFile, index=False)
                self.readDefInFile(csvFile)
        elif csvFile==self.fundSaveFile:
            if (index < len(self.fundDef.index)):
                self.fundDef.drop(index, inplace=True)
                self.csvFileAsType(csvFile)
                self.fundDef.to_csv(csvFile, index=False)
                self.readDefInFile(csvFile)

    def getStockListByIndexInFile(self, index, csvFile):
        tmpStockList=[]
        if csvFile==self.stockSaveFile:
            if (index < len(self.stockDef.index)):
                for columns in self.stockColumns:
                    tmpStockList.append(self.stockDef.ix[index, columns])
        elif csvFile==self.tradeSaveFile:
            if (index < len(self.tradeDef.index)):
                for columns in self.tradeColumns:
                    tmpStockList.append(self.tradeDef.ix[index, columns])
        elif csvFile==self.fundSaveFile:
            if (index < len(self.fundDef.index)):
                for columns in self.fundColumns:
                    tmpStockList.append(self.fundDef.ix[index, columns])
        return tmpStockList

    def updateSelectToFile(self, idx, csvFile):
        for xidx in range(len(self.stockDef.index)):
            if xidx == idx:
                self.stockDef.ix[xidx, self.stockColumns[0]] = 1
            else:
                self.stockDef.ix[xidx, self.stockColumns[0]] = 0
            self.csvFileAsType(csvFile)
            self.stockDef.to_csv(csvFile, index=False)

    def getFileCodeBySelect(self):
        for xidx in range(len(self.stockDef.index)):
            if self.stockDef.ix[xidx, self.stockColumns[0]]:
                return self.stockDef.ix[xidx, self.stockColumns[1]]
        return ''

    def getStockNameByCode(self, code):
        stockName=''
        for xidx in range(len(self.stockDef.index)):
            if code == self.stockDef.ix[xidx, self.stockColumns[1]]:
                stockName=self.stockDef.ix[xidx, self.stockColumns[2]]
        return stockName

    def getStockInfoByCode(self, code):
        for xidx in range(len(self.stockDef.index)):
            if code == self.stockDef.ix[xidx, self.stockColumns[1]]:
                stockRaise=self.stockDef.ix[xidx, self.stockColumns[3]]
                stockDecline=self.stockDef.ix[xidx, self.stockColumns[4]]
                stockMutli=self.stockDef.ix[xidx, self.stockColumns[5]]
                stockTradeNumber=self.stockDef.ix[xidx, self.stockColumns[6]]
                return(stockRaise, stockDecline, stockMutli, stockTradeNumber)
        return (0.0, 0.0, 0, 0)

    def getLastFundInfo(self):
        if len(self.fundDef.index) <= 0:
            return (0.0, 0.0)
        return (self.fundDef.ix[len(self.fundDef.index)-1, self.fundColumns[3]], self.fundDef.ix[len(self.fundDef.index)-1, self.fundColumns[4]])

    def getLastTradeInfoByCode(self, code):
        for xidx in range(len(self.tradeDef.index)):
            xidx = len(self.tradeDef.index)-xidx-1
            if code==self.tradeDef.ix[xidx, self.tradeColumns[1]]:
                lastStockTradeStatus=self.tradeDef.ix[xidx, self.tradeColumns[0]]
                lastStockTradePrice=self.tradeDef.ix[xidx, self.tradeColumns[5]]
                lastStockTradeCount=self.tradeDef.ix[xidx, self.tradeColumns[6]]
                return (lastStockTradeStatus, lastStockTradePrice, lastStockTradeCount)
        return ('remain', 0.0, 0)

    def getNextTradeByCode(self, stockCode):
        tradeBuyCount = 0
        tradeBuyPrice = 0.0
        tradeSellCount = 0
        tradeSellPrice = 0.0
        (lastTradeStatus, lastTradePrice, lastTradeCount)=self.getLastTradeInfoByCode(stockCode)
        (tradeRaise, tradeDecline, stockMulti, stockTradeNumber)=self.getStockInfoByCode(stockCode)
        if lastTradeStatus == 'buy':
            tradeBuyCount=lastTradeCount+100
            tradeBuyPrice=lastTradePrice*(100+tradeDecline)/100
            tradeSellCount=stockTradeNumber
            tradeSellPrice=lastTradePrice*(100+tradeRaise)/100
        elif lastTradeStatus == 'sell':
            tradeBuyCount=stockTradeNumber
            tradeBuyPrice=lastTradePrice*(100+tradeDecline)/100
            tradeSellCount=abs(lastTradeCount-100)
            tradeSellPrice=lastTradePrice*(100+tradeRaise)/100
        return (tradeBuyCount, tradeBuyPrice, tradeSellCount, tradeSellPrice)

    def getTradeStockCount(self, code, tradeStatus, tradeDate):
        tradeStockCount = 0
        for idx in range(len(self.tradeDef.index)):
            if (self.tradeDef.ix[idx, self.tradeColumns[1]]==code):
                if (self.tradeDef.ix[idx, self.tradeColumns[0]]==tradeStatus):
                    if (self.tradeDef.ix[idx, self.tradeColumns[3]]>=tradeDate):
                        continue
                tradeStockCount+=self.tradeDef.ix[idx, self.tradeColumns[6]]
        return tradeStockCount

    def getTradeDayProfit(self, code, currentPrice, previousPrice, tradeDate):
        tradeDayProfit=0.0
        tradeResCount=0
        for idx in range(len(self.tradeDef.index)):
            if (self.tradeDef.ix[idx, self.tradeColumns[1]]==code):
                if self.tradeDef.ix[idx, self.tradeColumns[0]] == 'buy':
                    if (self.tradeDef.ix[idx, self.tradeColumns[3]]>=tradeDate):
                        tradeDayProfit += (currentPrice-self.tradeDef.ix[idx, self.tradeColumns[5]])*abs(self.tradeDef.ix[idx, self.tradeColumns[6]])
                    else:
                        tradeResCount += abs(self.tradeDef.ix[idx, self.tradeColumns[6]])
                elif self.tradeDef.ix[idx, self.tradeColumns[0]] == 'sell':
                    if (self.tradeDef.ix[idx, self.tradeColumns[3]]>=tradeDate):
                        tradeDayProfit += (self.tradeDef.ix[idx, self.tradeColumns[5]]-previousPrice)*abs(self.tradeDef.ix[idx, self.tradeColumns[6]])
                    tradeResCount -= abs(self.tradeDef.ix[idx, self.tradeColumns[6]])
        tradeDayProfit+=tradeResCount*(currentPrice-previousPrice)
        return tradeDayProfit

    def getTradeAsset(self, code, currentPrice):
        tradeAssetCount=0.0
        for idx in range(len(self.tradeDef.index)):
            if (self.tradeDef.ix[idx, self.tradeColumns[1]]==code):
                if self.tradeDef.ix[idx, self.tradeColumns[0]] == 'buy':
                    tradeAssetCount += abs(self.tradeDef.ix[idx, self.tradeColumns[6]])
                elif self.tradeDef.ix[idx, self.tradeColumns[0]] == 'sell':
                    tradeAssetCount -= abs(self.tradeDef.ix[idx, self.tradeColumns[6]])
        return tradeAssetCount*currentPrice

    def getTradeAverPrice(self, code):
        tradeBuyAverPrice=0.0
        tradeSellAverPrice=0.0
        tradeBuyCount=0
        tradeSellCount=0
        tradeBuySum=0.0
        tradeSellSum=0.0
        for idx in range(len(self.tradeDef.index)):
            if (self.tradeDef.ix[idx, self.tradeColumns[1]]==code):
                if self.tradeDef.ix[idx, self.tradeColumns[0]] == 'buy':
                    tradeBuySum += self.tradeDef.ix[idx, self.tradeColumns[5]]*abs(self.tradeDef.ix[idx, self.tradeColumns[6]])
                    tradeBuyCount += abs(self.tradeDef.ix[idx, self.tradeColumns[6]])
                elif self.tradeDef.ix[idx, self.tradeColumns[0]] == 'sell':
                    tradeSellSum += self.tradeDef.ix[idx, self.tradeColumns[5]]*abs(self.tradeDef.ix[idx, self.tradeColumns[6]])
                    tradeSellCount += abs(self.tradeDef.ix[idx, self.tradeColumns[6]])
                else:
                    continue
        if tradeBuyCount > 0:
            tradeBuyAverPrice = tradeBuySum/tradeBuyCount
        if tradeSellCount > 0:
            tradeSellAverPrice = tradeSellSum/tradeSellCount
        return (tradeBuyAverPrice, tradeSellAverPrice)

    def codeIsExist(self, code):
        for i in range(len(self.stockDef.index)):
            if code.encode('raw_unicode_escape')==self.stockDef.ix[i, self.stockColumns[1]]:
                return True
        return False

    def readDefInFile(self, csvFile):
        if csvFile==self.stockSaveFile:
            self.stockDef=pd.read_csv(csvFile)
            self.csvFileAsType(csvFile)
            for xidx in range(len(self.stockDef.index)) :
                self.stockDef.ix[xidx, self.stockColumns[1]]='%06d'%int(self.stockDef.ix[xidx, self.stockColumns[1]])
        elif csvFile==self.tradeSaveFile:
            self.tradeDef=pd.read_csv(csvFile)
            self.csvFileAsType(csvFile)
            for xidx in range(len(self.tradeDef.index)) :
                self.tradeDef.ix[xidx, self.tradeColumns[1]]='%06d'%int(self.tradeDef.ix[xidx, self.tradeColumns[1]])
        elif csvFile==self.fundSaveFile:
            self.fundDef=pd.read_csv(csvFile)
            self.csvFileAsType(csvFile)

    def getCodeListInStockFile(self):
        codeList=[]
        for oneCode in self.stockDef[self.stockColumns[1]].values:
            codeList.append(oneCode)
        return codeList

    def getDefInStockTrade(self, csvFile):
        if csvFile==self.stockSaveFile:
            return self.stockDef
        elif csvFile==self.tradeSaveFile:
            return self.tradeDef

def stockDateTimeIsTrade(osdate, realDate, realTime) :
    if osdate != realDate :
        return 0
    if (realTime <= '09:30:00') :
        return 0
    elif (realTime >= '11:30:00' and realTime <= '13:00:00') :
        return 0
    elif (realTime >= '15:00:00') :
        return 0
    return 1

def stockPyramidTradeOption(selfDialog, saveStockTradeInfo, realStockTradeInfo):
    while (1):
        stockCodeList = saveStockTradeInfo.getCodeListInStockFile()
        realStockTradeInfo.stockUpdateAll(stockCodeList)
        osDate = time.strftime('%Y-%m-%d', time.localtime())
        for stockCode in stockCodeList:
            (realName, realDate, realTime)=realStockTradeInfo.getNameDateTimeByCode(stockCode)
            if not stockDateTimeIsTrade(osDate, realDate, realTime):
                continue
            realPrice=realStockTradeInfo.getPirceByCode(stockCode)
            if realPrice==0.0:
                continue
            tradeStatus='remain'
            tradeCount=0
            tradePrice=0.0
            (tradeRaise, tradeDecline, stockMulti, stockTradeNumber)=saveStockTradeInfo.getStockInfoByCode(stockCode)
            (lastTradeStatus, lastTradePrice, lastTradeCount)=saveStockTradeInfo.getLastTradeInfoByCode(stockCode)
            (stockHighFund, lastResFund)=saveStockTradeInfo.getLastFundInfo()
            if lastTradeStatus == 'remain':
                tradeStatus='buy'
                tradePrice=realPrice
                tradeCount=min(stockTradeNumber, int(lastResFund/realPrice))
            else:
                tradePercent=100*(realPrice-lastTradePrice)/lastTradePrice
                if tradePercent > tradeRaise:
                    if lastTradeStatus == 'buy':
                        tradeCount=stockTradeNumber-100
                    elif lastTradeStatus == 'sell':
                        tradeCount=(abs(lastTradeCount)/(100*stockMulti))*100
                    else:
                        continue
                    sumCount = 0
                    for i in range(int(abs(tradePercent)/abs(tradeRaise))):
                        tradeCount+=100
                        sumCount+=tradeCount
                    tradeStatus = 'sell'
                    tradePrice=realPrice
                    tradeCount=min(sumCount*stockMulti, saveStockTradeInfo.getTradeStockCount(stockCode, 'buy', realDate))
                    tradeCount=0-tradeCount
                elif tradePercent < tradeDecline:
                    if lastTradeStatus=='buy':
                        tradeCount=(abs(lastTradeCount)/(100*stockMulti))*100
                    elif lastTradeStatus=='sell':
                        tradeCount=stockTradeNumber-100
                    else:
                        continue
                    sumCount = 0
                    for i in range(int(abs(tradePercent)/abs(tradeDecline))):
                        tradeCount+=100
                        sumCount+=tradeCount
                    tradeStatus='buy'
                    tradePrice=realPrice
                    tradeCount=min(sumCount*stockMulti, 100*int(lastResFund/(100*realPrice)))
                else:
                    continue
            if tradeCount==0:
                continue
            stockTradeList=[tradeStatus, stockCode, realName.encode('utf8'), realDate, realTime, tradePrice, tradeCount]
            stockFundList=[realDate, realTime, tradeStatus, stockHighFund , lastResFund-tradeCount*tradePrice]
            saveStockTradeInfo.updateListToFile(-1, stockTradeList, saveStockTradeInfo.tradeSaveFile)
            saveStockTradeInfo.updateListToFile(-1, stockFundList, saveStockTradeInfo.fundSaveFile)
            tmpRemindStr = ''
            tmpRemindStr += "交易状态：    "+tradeStatus+'\n'
            tmpRemindStr += "交易股票的名称："+realName.encode('utf8')+'\n'
            tmpRemindStr += "交易股票的数量："+str(tradeCount)+'\n'
            tmpRemindStr += "交易股票的价格："+str(tradePrice)+'\n'
            selfDialog.emit(SIGNAL("doTradeRemind"), tmpRemindStr) 
        time.sleep(0.1)

def stockPillarTradeOption(selfDialog, saveStockTradeInfo, realStockTradeInfo):
    while (1):
        stockCodeList = saveStockTradeInfo.getCodeListInStockFile()
        realStockTradeInfo.stockUpdateAll(stockCodeList)
        osDate = time.strftime('%Y-%m-%d', time.localtime())
        for stockCode in stockCodeList:
            (realName, realDate, realTime)=realStockTradeInfo.getNameDateTimeByCode(stockCode)
            if not stockDateTimeIsTrade(osDate, realDate, realTime):
                continue
            realPrice=realStockTradeInfo.getPirceByCode(stockCode)
            if realPrice==0.0:
                continue
            tradeStatus='remain'
            tradeCount=0
            tradePrice=0.0
            (tradeRaise, tradeDecline, stockMulti, stockTradeNumber)=saveStockTradeInfo.getStockInfoByCode(stockCode)
            (lastTradeStatus, lastTradePrice, lastTradeCount)=saveStockTradeInfo.getLastTradeInfoByCode(stockCode)
            (stockHighFund, lastResFund)=saveStockTradeInfo.getLastFundInfo()
            if lastTradeStatus == 'remain':
                tradeStatus='buy'
                tradePrice=realPrice
                tradeCount=min(stockTradeNumber, int(lastResFund/realPrice))
            else:
                tradePercent=100*(realPrice-lastTradePrice)/lastTradePrice
                if tradePercent > tradeRaise:
                    sumCount = 0
                    for i in range(int(abs(tradePercent)/abs(tradeRaise))):
                        sumCount+=stockTradeNumber
                    tradeStatus = 'sell'
                    tradePrice=realPrice
                    tradeCount=min(sumCount*stockMulti, saveStockTradeInfo.getTradeStockCount(stockCode, 'buy', realDate))
                    tradeCount=0-tradeCount
                elif tradePercent < tradeDecline:
                    sumCount = 0
                    for i in range(int(abs(tradePercent)/abs(tradeDecline))):
                        sumCount+=stockTradeNumber
                    tradeStatus='buy'
                    tradePrice=realPrice
                    tradeCount=min(sumCount*stockMulti, 100*int(lastResFund/(100*realPrice)))
                else:
                    continue
            if tradeCount==0:
                continue
            stockTradeList=[tradeStatus, stockCode, realName.encode('utf8'), realDate, realTime, tradePrice, tradeCount]
            stockFundList=[realDate, realTime, tradeStatus, stockHighFund , lastResFund-tradeCount*tradePrice]
            saveStockTradeInfo.updateListToFile(-1, stockTradeList, saveStockTradeInfo.tradeSaveFile)
            saveStockTradeInfo.updateListToFile(-1, stockFundList, saveStockTradeInfo.fundSaveFile)
            tmpRemindStr = ''
            tmpRemindStr += "交易状态：    "+tradeStatus+'\n'
            tmpRemindStr += "交易股票的名称："+realName.encode('utf8')+'\n'
            tmpRemindStr += "交易股票的数量："+str(tradeCount)+'\n'
            tmpRemindStr += "交易股票的价格："+str(tradePrice)+'\n'
            selfDialog.emit(SIGNAL("doTradeRemind"), tmpRemindStr) 
        time.sleep(0.1)

class StockDialog(QDialog):
    def __init__(self, parent=None):
        QTextCodec.setCodecForTr(QTextCodec.codecForName("utf8"))
        super(StockDialog,  self).__init__(parent)
        self.stockTradeSave=StockTradeSaveFile()
        self.stockRealTrade=stockRealTimeInfo()
        self.stockTradeThread=th.Thread(target= stockPillarTradeOption, args= (self, self.stockTradeSave, self.stockRealTrade))
        self.stockTradeThread.start()
        self.connect(self, SIGNAL("doTradeRemind"), self.stockTradeRemindHandler)
        self.setWindowTitle("Stock Analysis")
        self.setWindowFlags(Qt.Window)
        self.stockLabel=QLabel(self.tr("自选股"))
        self.stockRadioButtonList = []
        self.stockTableWidget=QTableWidget()
#        self.stockTableWidget.resizeColumnsToContents()
        self.stockHeader = QStringList()
        for idx in range(len(self.stockTradeSave.stockColumns)):
            self.stockHeader<<self.tr(self.stockTradeSave.stockColumns[idx])
        self.stockTableWidget.setColumnCount(len(self.stockTradeSave.stockColumns))
        self.stockTableWidget.setHorizontalHeaderLabels(self.stockHeader)
        self.stockTableWidget.setEditTriggers(QAbstractItemView.EditTriggers(0))
        self.stockTableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.stockTableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.stockTableWidget.horizontalHeader().setStretchLastSection(True)
        self.stockTableWidget.horizontalHeader().setResizeMode(QHeaderView.Stretch);
        self.stockTableWidget.horizontalHeader().setDefaultAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        self.stockTableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.stockTableWidget.customContextMenuRequested.connect(self.stockShowMenu)
        self.stockMenu=QMenu(self)
        self.stockMenuAdd=self.stockMenu.addAction("Add...")
        self.stockMenuDelete=self.stockMenu.addAction("Delete...")
        self.stockMenuAlter=self.stockMenu.addAction("Alter...")
        self.stockMenuFund=self.stockMenu.addAction("Fund...")
        self.stockMenuAdd.triggered.connect(self.addActionHandler)
        self.stockMenuAlter.triggered.connect(self.alterActionHandler)
        self.stockMenuDelete.triggered.connect(self.deleteActionHandler)
        self.stockMenuFund.triggered.connect(self.fundActionHandler)
        self.tradeLabel=QLabel(self.tr("历史交易"))
        self.tradeTableWidget=QTableWidget()
        self.tradeHeader = QStringList()
        for idx in range(len(self.stockTradeSave.tradeColumns)):
            self.tradeHeader<<self.tr(self.stockTradeSave.tradeColumns[idx])
        self.tradeTableWidget.setColumnCount(len(self.stockTradeSave.tradeColumns))
        self.tradeTableWidget.setHorizontalHeaderLabels(self.tradeHeader)
        self.tradeTableWidget.setEditTriggers(QAbstractItemView.EditTriggers(0))
        self.tradeTableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tradeTableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tradeTableWidget.horizontalHeader().setStretchLastSection(True)
        self.tradeTableWidget.horizontalHeader().setResizeMode(QHeaderView.Stretch);
        self.shNumberLabel=QLabel(self.tr("上证指数:"))
        self.shNumberValueLabel=QLabel()
        self.szNumberLabel=QLabel(self.tr("深证指数:"))
        self.szNumberValueLabel=QLabel()
        self.cybNumberLabel=QLabel(self.tr("创业板指数:"))
        self.cybNumberValueLabel=QLabel()
        self.stockNameLabel=QLabel(self.tr("股票名称:"))
        self.stockNameValueLabel=QLabel()
        self.assetLabel=QLabel(self.tr("总资产:"))
        self.assetValueLabel=QLabel()
        self.fundLabel=QLabel(self.tr("总资金:"))
        self.fundValueLabel=QLabel()
        self.resFundLabel=QLabel(self.tr("剩余资金:"))
        self.resFundValueLabel=QLabel()
        self.dayProfitLabel=QLabel(self.tr("当日盈利:"))
        self.dayProfitValueLabel=QLabel()
        self.totalProfitLabel=QLabel(self.tr("总体盈利:"))
        self.totalProfitValueLabel=QLabel()
        self.averBuyPriceLabel=QLabel(self.tr("平均买价格:"))
        self.averBuyPriceValueLabel=QLabel()
        self.averSellPriceLabel=QLabel(self.tr("平均卖价格:"))
        self.averSellPriceValueLabel=QLabel()
        self.currentPriceLabel=QLabel(self.tr("当日价格:"))
        self.currentPriceValueLabel=QLabel()
        self.currentPercentLabel=QLabel(self.tr("当日涨幅:"))
        self.currentPercentValueLabel=QLabel()
        self.fluctuationRangeLabel=QLabel(self.tr("振动幅度:"))
        self.fluctuationRangeValueLabel=QLabel()
        self.oneAssetLabel=QLabel(self.tr("个股资产:"))
        self.oneAssetValueLabel=QLabel()
        self.oneDayProfitLabel=QLabel(self.tr("个股日盈利:"))
        self.oneDayProfitValueLabel=QLabel()
        self.oneTotalProfitLabel=QLabel(self.tr("个股总盈利:"))
        self.oneTotalProfitValueLabel=QLabel()
        self.currentDateLabel=QLabel(self.tr("当前日期:"))
        self.currentDateValueLabel=QLabel()
        self.currentTimeLabel=QLabel(self.tr("当前时间:"))
        self.currentTimeValueLabel=QLabel()
        self.nextBuyPriceLabel=QLabel(self.tr("挂牌买价格:"))
        self.nextBuyPriceValueLabel=QLabel()
        self.nextBuyNumberLabel=QLabel(self.tr("挂牌买数量:"))
        self.nextBuyNumberValueLabel=QLabel()
        self.nextSellPriceLabel=QLabel(self.tr("挂牌卖价格:"))
        self.nextSellPriceValueLabel=QLabel()
        self.nextSellNumberLabel=QLabel(self.tr("挂牌卖数量:"))
        self.nextSellNumberValueLabel=QLabel()
        layout=QGridLayout()
        layout.addWidget(self.stockLabel,          0,  0,   1,  1)
        layout.addWidget(self.stockTableWidget,    1,  0,   5, 15)
        layout.addWidget(self.tradeLabel,          6,  0,   1,  1)
        layout.addWidget(self.tradeTableWidget,    7,  0,  10, 15)
        layout.addWidget(self.shNumberLabel,       0,  4,   1,  1)
        layout.addWidget(self.shNumberValueLabel,  0,  5,   1,  1)
        layout.addWidget(self.szNumberLabel,       0,  7,   1,  1)
        layout.addWidget(self.szNumberValueLabel,  0,  8,   1,  1)
        layout.addWidget(self.cybNumberLabel,      0, 10,   1,  1)
        layout.addWidget(self.cybNumberValueLabel, 0, 11,   1,  1)
        layout.addWidget(self.fundLabel,           0, 16,   1,  1)
        layout.addWidget(self.fundValueLabel,      0, 17,   1,  1)
        layout.addWidget(self.resFundLabel,        0, 18,   1,  1)
        layout.addWidget(self.resFundValueLabel,   0, 19,   1,  1)
        layout.addWidget(self.assetLabel,            1, 16,   1,  1)
        layout.addWidget(self.assetValueLabel,       1, 17,   1,  1)
        layout.addWidget(self.dayProfitLabel,        1, 18,   1,  1)
        layout.addWidget(self.dayProfitValueLabel,   1, 19,   1,  1)
        layout.addWidget(self.totalProfitLabel,      1, 20,   1,  1)
        layout.addWidget(self.totalProfitValueLabel, 1, 21,   1,  1)
        layout.addWidget(self.stockNameLabel,        2, 16,   1,  1)
        layout.addWidget(self.stockNameValueLabel,   2, 17,   1,  1)
        layout.addWidget(self.currentDateLabel,      3, 16,   1,  1)
        layout.addWidget(self.currentDateValueLabel, 3, 17,   1,  1)
        layout.addWidget(self.currentTimeLabel,      3, 18,   1, 1)
        layout.addWidget(self.currentTimeValueLabel, 3, 19,   1, 1)
        layout.addWidget(self.averBuyPriceLabel,      4, 16,  1,  1)
        layout.addWidget(self.averBuyPriceValueLabel, 4, 17,  1, 1)
        layout.addWidget(self.averSellPriceLabel,     4, 18,  1, 1)
        layout.addWidget(self.averSellPriceValueLabel,4, 19,  1, 1)
        layout.addWidget(self.currentPriceLabel,          5, 16, 1, 1)
        layout.addWidget(self.currentPriceValueLabel,     5, 17, 1, 1)
        layout.addWidget(self.currentPercentLabel,        5, 18, 1, 1)
        layout.addWidget(self.currentPercentValueLabel,   5, 19, 1, 1)
        layout.addWidget(self.fluctuationRangeLabel,      5, 20, 1, 1)
        layout.addWidget(self.fluctuationRangeValueLabel, 5, 21, 1, 1)
        layout.addWidget(self.oneAssetLabel,            6, 16, 1, 1)
        layout.addWidget(self.oneAssetValueLabel,       6, 17, 1, 1)
        layout.addWidget(self.oneDayProfitLabel,        6, 18, 1, 1)
        layout.addWidget(self.oneDayProfitValueLabel,   6, 19, 1, 1)
        layout.addWidget(self.oneTotalProfitLabel,      6, 20, 1, 1)
        layout.addWidget(self.oneTotalProfitValueLabel, 6, 21, 1, 1)
        layout.addWidget(self.nextBuyPriceLabel, 7, 16, 1, 1)
        layout.addWidget(self.nextBuyPriceValueLabel, 7, 17, 1, 1)
        layout.addWidget(self.nextBuyNumberLabel, 7, 18, 1, 1)
        layout.addWidget(self.nextBuyNumberValueLabel, 7, 19, 1, 1)
        layout.addWidget(self.nextSellPriceLabel, 8, 16, 1, 1)
        layout.addWidget(self.nextSellPriceValueLabel, 8, 17, 1, 1)
        layout.addWidget(self.nextSellNumberLabel, 8, 18, 1, 1)
        layout.addWidget(self.nextSellNumberValueLabel, 8, 19, 1, 1)
        self.setRealTradeLabelColor(self.stockNameLabel,QColor(0, 0, 0))
        self.setRealTradeLabelColor(self.stockNameValueLabel, QColor(0, 0, 0))
        self.setRealTradeLabelColor(self.currentDateLabel,QColor(0, 0, 0))
        self.setRealTradeLabelColor(self.currentDateValueLabel, QColor(0, 0, 0))
        self.setRealTradeLabelColor(self.currentTimeLabel,QColor(0, 0, 0))
        self.setRealTradeLabelColor(self.currentTimeValueLabel, QColor(0, 0, 0))
        self.setRealTradeLabelColor(self.averBuyPriceLabel, QColor(0, 0, 0))
        self.setRealTradeLabelColor(self.averSellPriceLabel, QColor(0, 0, 0))
        self.setRealTradeLabelColor(self.currentPriceLabel, QColor(0, 0, 0))
        self.setRealTradeLabelColor(self.currentPercentLabel, QColor(0, 0, 0))
        self.setRealTradeLabelColor(self.fluctuationRangeLabel, QColor(0, 0, 0))
        self.setRealTradeLabelColor(self.oneAssetLabel, QColor(0, 0, 0))
        self.setRealTradeLabelColor(self.oneDayProfitLabel, QColor(0, 0, 0))
        self.setRealTradeLabelColor(self.oneTotalProfitLabel, QColor(0, 0, 0))
        self.setRealTradeLabelColor(self.nextBuyPriceLabel,QColor(127, 0, 127))
        self.setRealTradeLabelColor(self.nextBuyPriceValueLabel, QColor(255, 0, 127))
        self.setRealTradeLabelColor(self.nextBuyNumberLabel, QColor(127, 0, 127))
        self.setRealTradeLabelColor(self.nextBuyNumberValueLabel, QColor(255, 0, 127))
        self.setRealTradeLabelColor(self.nextSellPriceLabel, QColor(127, 0, 127))
        self.setRealTradeLabelColor(self.nextSellPriceValueLabel, QColor(255, 0, 127))
        self.setRealTradeLabelColor(self.nextSellNumberLabel, QColor(127, 0, 127))
        self.setRealTradeLabelColor(self.nextSellNumberValueLabel, QColor(255, 0, 127))
        self.stockTableWidgetUpdate();
        self.tradeTableWidgetUpdate();
        self.labelRealTradeUpdate()
        self.setLayout(layout)
        self.stockLabelTimer=QTimer(self)
        self.connect(self.stockLabelTimer, SIGNAL("timeout()"), self.labelRealTradeUpdate)
        self.stockLabelTimer.start(500)

    def stockShowMenu(self,  pos):
        self.stockMenu.move(QCursor.pos())
        self.stockMenu.show()

    def stockTradeRemindHandler(self, *args):
        tmpRemindStr = ''
        for argv in args:
            tmpRemindStr += argv
        QMessageBox.information(self, self.tr("交易提醒"), self.tr(tmpRemindStr))

    def addActionHandler(self):
        qStockCode, ok=QInputDialog.getText(self, self.tr("自选股"), self.tr("请输入新的股票代码:"), QLineEdit.Normal, '')
        if ok and (not qStockCode.isEmpty()):
            stockCode=qStockCode.__str__()
            if self.stockTradeSave.codeIsExist(stockCode):
                QMessageBox.information(self, self.tr("自选股"), self.tr("查询的股票已存在:"+qStockCode))
                return
            stockName=self.stockRealTrade.stockGetNameByCode(stockCode)
            if len(stockName) == 0:
                QMessageBox.information(self, self.tr("自选股"), self.tr("查询不到股票代码:"+qStockCode))
                return
            while(1):
                qStockBuyRise, ok = QInputDialog.getText(self, self.tr("自选股"), self.tr("请输入卖出的涨幅%:"),  QLineEdit.Normal, '3.0')
                if ok and (not qStockBuyRise.isEmpty()):
                    stockBuyRise = float(qStockBuyRise.__str__())
                else:
                    stockBuyRise = 3.0
                if stockBuyRise <= 0:
                    QMessageBox.information(self, self.tr("自选股"), self.tr("您设置的涨幅参数可能引起资产损失，请重新设置卖出涨幅参数:"))
                else:
                    break
            while(1):
                qStockBuyDecline, ok = QInputDialog.getText(self, self.tr("自选股"), self.tr("请输入买入的跌幅%:"),  QLineEdit.Normal, '-3.0')
                if ok and (not qStockBuyDecline.isEmpty()):
                    stockBuyDecline = float(qStockBuyDecline.__str__())
                else:
                    stockBuyDecline = -3.0
                if stockBuyDecline >= 0:
                    QMessageBox.information(self, self.tr("自选股"), self.tr("您设置的跌幅参数可能引起资产损失，请重新设置卖出跌幅参数:"))
                else:
                    break
            while(1):
                qStockMulti, ok = QInputDialog.getText(self, self.tr("自选股"), self.tr("请输入买股票的倍数:"),  QLineEdit.Normal, '1')
                if ok and (not qStockMulti.isEmpty()):
                    stockMulti = int(qStockMulti.__str__())
                else:
                    stockMulti = 1
                if stockMulti <= 0:
                    QMessageBox.information(self, self.tr("自选股"), self.tr("您设置的交易倍数不能少于0，请重新输入参数:"))
                else:
                    break
            while(1):
                qStockTradeNumber, ok = QInputDialog.getText(self, self.tr("自选股"), self.tr("请输入最低交易的股票数量:"),  QLineEdit.Normal, '100')
                if ok and (not qStockTradeNumber.isEmpty()):
                    stockTradeNumber = int(qStockTradeNumber.__str__())/100*100
                else:
                    stockTradeNumber = 100
                if stockTradeNumber<100:
                    QMessageBox.information(self, self.tr("自选股"), self.tr("您设置的交易数量不能少于100，请重新输入参数:"))
                else:
                    break
            tempStockList=[0, stockCode, stockName.encode('utf8'), stockBuyRise, stockBuyDecline, stockMulti, stockTradeNumber]
            self.stockTradeSave.updateListToFile(-1, tempStockList, self.stockTradeSave.stockSaveFile)
            self.stockTableWidgetUpdate()
        else:
            QMessageBox.information(self, self.tr("自选股"), self.tr("未输入股票代码"))

    def deleteActionHandler(self):
        xidx = self.stockTableWidget.currentRow()
        if (xidx == -1):
            QMessageBox.information(self, self.tr("自选股"), self.tr("未选中当前行"))
            return
        tmpStockList = self.stockTradeSave.getStockListByIndexInFile(xidx, self.stockTradeSave.stockSaveFile)
        tmpSelected = QMessageBox.question(self, self.tr("自选股"), self.tr("确定删除股票："+tmpStockList[2]), QMessageBox.Ok|QMessageBox.Cancel, QMessageBox.Cancel)
        if tmpSelected== QMessageBox.Ok:
            self.stockTradeSave.deleteListToFile(xidx, self.stockTradeSave.stockSaveFile)
            self.stockTableWidgetUpdate()

    def alterActionHandler(self):
        xidx = self.stockTableWidget.currentRow()
        if (xidx == -1):
            QMessageBox.information(self, self.tr("自选股"), self.tr("未选中当前行"))
            return
        tmpStockList = self.stockTradeSave.getStockListByIndexInFile(xidx, self.stockTradeSave.stockSaveFile)
        while(1):
            qStockBuyRise, ok = QInputDialog.getText(self, self.tr("自选股"), self.tr("请输入卖出的涨幅%:"),  QLineEdit.Normal, str(tmpStockList[3]))
            if ok and (not qStockBuyRise.isEmpty()):
                if float(qStockBuyRise.__str__()) <= 0:
                    QMessageBox.information(self, self.tr("自选股"), self.tr("您设置的涨幅参数可能引起资产损失，请重新设置卖出涨幅参数:"))
                    continue
                else:
                    tmpStockList[3] = float(qStockBuyRise.__str__())
            break
        while(1):
            qStockBuyDecline, ok = QInputDialog.getText(self, self.tr("自选股"), self.tr("请输入买入的跌幅%:"),  QLineEdit.Normal, str(tmpStockList[4]))
            if ok and (not qStockBuyDecline.isEmpty()):
                if float(qStockBuyDecline.__str__()) >= 0:
                    QMessageBox.information(self, self.tr("自选股"), self.tr("您设置的跌幅参数可能引起资产损失，请重新设置卖出跌幅参数:"))
                    continue
                else:
                    tmpStockList[4] = float(qStockBuyDecline.__str__())
            break
        while(1):
            qStockMulti, ok = QInputDialog.getText(self, self.tr("自选股"), self.tr("请输入买股票的倍数:"),  QLineEdit.Normal, str(tmpStockList[5]))
            if ok and (not qStockMulti.isEmpty()):
                if int(qStockMulti.__str__()) <= 0:
                    QMessageBox.information(self, self.tr("自选股"), self.tr("您设置的交易倍数不能少于0，请重新输入参数:"))
                    continue
                else:
                    tmpStockList[5] = int(qStockMulti.__str__())
            break
        while(1):
            qStockTradeNumber, ok = QInputDialog.getText(self, self.tr("自选股"), self.tr("请输入最低交易的股票数量:"),  QLineEdit.Normal, str(tmpStockList[6]))
            if ok and (not qStockTradeNumber.isEmpty()):
                if int(qStockTradeNumber.__str__()) < 100:
                    QMessageBox.information(self, self.tr("自选股"), self.tr("您设置的交易数量不能少于100，请重新输入参数:"))
                    continue
                else:
                    tmpStockList[6] = int(qStockTradeNumber.__str__())/100*100
            break
        self.stockTradeSave.updateListToFile(xidx, tmpStockList, self.stockTradeSave.stockSaveFile)
        self.stockTableWidgetUpdate()

    def fundActionHandler(self):
        (tmpHighFund, tmpResFund) = self.stockTradeSave.getLastFundInfo()
        while(1):
            qStockFund, ok = QInputDialog.getText(self, self.tr("自选股"), self.tr("请输入最高的使用资金:"),  QLineEdit.Normal, str(0))
            if ok and (not qStockFund.isEmpty()):
                tmpAddFund = float(qStockFund.__str__())
                if (tmpResFund + tmpAddFund) < 0:
                    QMessageBox.information(self, self.tr("自选股"), self.tr("您设置的使用资金不能少于0，请重新输入参数:"))
                    continue
                if tmpAddFund != 0:
                    osDateTime=time.localtime()
                    osDate = '%04d-%02d-%02d'%(osDateTime.tm_year, osDateTime.tm_mon, osDateTime.tm_mday)
                    osTime = '%02d:%02d:%02d'%(osDateTime.tm_hour, osDateTime.tm_min, osDateTime.tm_sec)
                    if tmpAddFund > 0:
                        tmpFundStatus = 'add'
                    else:
                        tmpFundStatus = 'del'
                    tmpFundList=[osDate, osTime, tmpFundStatus, tmpHighFund+tmpAddFund, tmpResFund+tmpAddFund]
                    self.stockTradeSave.updateListToFile(-1, tmpFundList, self.stockTradeSave.fundSaveFile)
            break

    def stockTableWidgetUpdate(self):
        tmpStockDef=self.stockTradeSave.getDefInStockTrade(self.stockTradeSave.stockSaveFile)
        self.stockTableWidget.setRowCount(len(tmpStockDef.index))
        del self.stockRadioButtonList[0:len(self.stockRadioButtonList)]
        for xidx in range(len(tmpStockDef.index)):
            for yidx in range(len(tmpStockDef.columns)):
                if yidx == 0:
                    self.stockRadioButtonList.append(QRadioButton())
                    self.stockRadioButtonList[xidx].setChecked(tmpStockDef.ix[xidx, yidx])
                    self.stockTableWidget.setCellWidget(xidx, yidx, self.stockRadioButtonList[xidx])
                    self.connect(self.stockRadioButtonList[xidx], SIGNAL("clicked()"), self.stockRadioButtonChange)
                else:
                    self.stockTableWidget.setItem(xidx, yidx, QTableWidgetItem(self.tr(str(tmpStockDef.ix[xidx, yidx]))))

    def tradeTableWidgetUpdate(self):
        tmpTradeDef=self.stockTradeSave.getDefInStockTrade(self.stockTradeSave.tradeSaveFile)
        tmpTradeCode=self.stockTradeSave.getFileCodeBySelect()
        tradeCodeCount = 0
        for xidx in range(len(tmpTradeDef.index)):
            if tmpTradeCode==tmpTradeDef.ix[xidx, self.stockTradeSave.tradeColumns[1]]:
                tradeCodeCount += 1
        self.tradeTableWidget.setRowCount(tradeCodeCount)
        tradeCodeCount=0
        for xidx in range(len(tmpTradeDef.index)):
            if tmpTradeCode==tmpTradeDef.ix[xidx, self.stockTradeSave.tradeColumns[1]]:
                tradeCodeCount += 1
                for yidx in range(len(tmpTradeDef.columns)):
                    self.tradeTableWidget.setItem(tradeCodeCount-1, yidx, QTableWidgetItem(self.tr(str(tmpTradeDef.ix[xidx, yidx]))))

    def stockRadioButtonChange(self):
        for idx in range(len(self.stockRadioButtonList)):
            if self.sender() == self.stockRadioButtonList[idx]:
                self.stockTradeSave.updateSelectToFile(idx, self.stockTradeSave.stockSaveFile)
        self.tradeTableWidget.clearContents()
        self.labelRealTradeUpdate()

    def setRealTradeLabelColor(self, tradeValueLabel, color):
        tmpColorPalette=tradeValueLabel.palette()
        tmpColorPalette.setColor(QPalette.WindowText, color)
        tradeValueLabel.setPalette(tmpColorPalette)

    def labelRealTradeUpdate(self):
        self.tradeTableWidgetUpdate()
        tmpTradeSelectCode=self.stockTradeSave.getFileCodeBySelect()
        tmpTradeCodeList=self.stockTradeSave.getCodeListInStockFile()
        tmpStockName=self.stockTradeSave.getStockNameByCode(tmpTradeSelectCode)
        (tmpBuyCount, tmpBuyPrice, tmpSellCount, tmpSellPrice)=self.stockTradeSave.getNextTradeByCode(tmpTradeSelectCode)
        (tmpHighFund, tmpResFund) = self.stockTradeSave.getLastFundInfo()
        self.stockNameValueLabel.setText(self.tr(tmpStockName))
        self.nextBuyPriceValueLabel.setText(self.tr(' %.2f'%tmpBuyPrice))
        self.nextBuyNumberValueLabel.setText(self.tr(' %d'%tmpBuyCount))
        self.nextSellPriceValueLabel.setText(self.tr(' %.2f'%tmpSellPrice))
        self.nextSellNumberValueLabel.setText(self.tr(' %d'%tmpSellCount))
        self.fundValueLabel.setText(self.tr('%.2f'%tmpHighFund))
        self.setRealTradeLabelColor(self.fundValueLabel, Qt.blue)
        self.resFundValueLabel.setText(self.tr('%.2f'%tmpResFund))
        self.setRealTradeLabelColor(self.resFundValueLabel, Qt.blue)
        self.stockRealTrade.stockUpdate(tmpTradeSelectCode)
        tmpPrice=self.stockRealTrade.stockGetPrice()
        if tmpPrice==0:
            return
        tmpPrevPrice=self.stockRealTrade.stockGetPrevPrice()
        tmpDates=self.stockRealTrade.stockGetDate()
        tmpTimes=self.stockRealTrade.stockGetTime()
        tmpPrecent=self.stockRealTrade.stockGetPercent()
        (tmpRaise, tmpDecline, tmpMulti, tmpTradeNumber)=self.stockTradeSave.getStockInfoByCode(tmpTradeSelectCode)
        tmpOneDayProfit=self.stockTradeSave.getTradeDayProfit(tmpTradeSelectCode, tmpPrice, tmpPrevPrice, tmpDates)
        tmpOneAsset=self.stockTradeSave.getTradeAsset(tmpTradeSelectCode, tmpPrice)
        tmpTotalTradeAsset=0.0
        for tmpTradeCode in tmpTradeCodeList:
            tmpTradePrice=self.stockRealTrade.getPirceByCode(tmpTradeCode)
            if tmpTradePrice == 0:
                tmpTotalTradeAsset=0.0
                break
            else:
                tmpTotalTradeAsset+=self.stockTradeSave.getTradeAsset(tmpTradeCode, tmpTradePrice)
        if tmpTotalTradeAsset != 0.0:
            tmpTotalProfit=tmpResFund+tmpTotalTradeAsset-tmpHighFund
            self.assetValueLabel.setText(self.tr('%.2f'%(tmpTotalTradeAsset+tmpResFund)))
            self.totalProfitValueLabel.setText(self.tr('%.2f'%tmpTotalProfit))
            if  tmpTotalProfit > 0:
                tmpColor=Qt.red
            elif tmpTotalProfit == 0:
                tmpColor=Qt.gray
            else:
                tmpColor=Qt.green
            self.setRealTradeLabelColor(self.totalProfitValueLabel, tmpColor)
        (tmpBuyAverPrice,tmpSellAverPrice)=self.stockTradeSave.getTradeAverPrice(tmpTradeSelectCode)
        if tmpPrevPrice>0:
            tmpFuctuationRange = 100*(self.stockRealTrade.stockGetHighPrice()-self.stockRealTrade.stockGetLowPrice())/tmpPrevPrice
        else:
            tmpFuctuationRange = 0.0
        self.currentPriceValueLabel.setText(self.tr('%.2f'%tmpPrice))
        self.currentPercentValueLabel.setText(self.tr('%.2f'%tmpPrecent+'%'))
        self.oneAssetValueLabel.setText(self.tr('%.2f'%tmpOneAsset))
        self.oneDayProfitValueLabel.setText(self.tr('%.2f'%tmpOneDayProfit))
        self.currentDateValueLabel.setText(self.tr(tmpDates))
        self.currentTimeValueLabel.setText(self.tr(tmpTimes))
        self.averBuyPriceValueLabel.setText(self.tr('%.2f'%tmpBuyAverPrice))
        self.averSellPriceValueLabel.setText(self.tr('%.2f'%tmpSellAverPrice))
        self.fluctuationRangeValueLabel.setText(self.tr('%.2f'%tmpFuctuationRange+'%'))
        if  tmpPrecent > 0:
            tmpColor=Qt.red
        elif tmpPrecent == 0:
            tmpColor=Qt.gray
        else:
            tmpColor=Qt.green
        self.setRealTradeLabelColor(self.currentPriceValueLabel, tmpColor)
        self.setRealTradeLabelColor(self.currentPercentValueLabel, tmpColor)
        self.setRealTradeLabelColor(self.assetValueLabel, Qt.blue)
        if  tmpOneDayProfit > 0:
            tmpColor=Qt.red
        elif tmpOneDayProfit == 0:
            tmpColor=Qt.gray
        else:
            tmpColor=Qt.green
        self.setRealTradeLabelColor(self.oneDayProfitValueLabel, tmpColor)
        self.setRealTradeLabelColor(self.oneAssetValueLabel, Qt.blue)
        self.setRealTradeLabelColor(self.averBuyPriceValueLabel, Qt.blue)
        self.setRealTradeLabelColor(self.averSellPriceValueLabel, Qt.blue)
        self.setRealTradeLabelColor(self.fluctuationRangeValueLabel, Qt.blue)
        tmpNumberList=self.stockRealTrade.stockGetNumberInfo()
        if len(tmpNumberList) != 0:
            for xIndex in range(len(self.stockRealTrade.numberList)):
                tmpNumberCode = tmpNumberList[xIndex*len(self.stockRealTrade.numberColumns)+0]
                tmpNumberValue = tmpNumberList[xIndex*len(self.stockRealTrade.numberColumns)+3]
                tmpNumberChange = tmpNumberList[xIndex*len(self.stockRealTrade.numberColumns)+2]
                if tmpNumberChange > 0:
                    tmpColor=Qt.red
                elif tmpNumberChange == 0:
                    tmpColor=Qt.gray
                else:
                    tmpColor=Qt.green
                if tmpNumberCode == self.stockRealTrade.numberList[0]:
                    self.shNumberValueLabel.setText(self.tr('%.2f   '%tmpNumberValue+'%.2f'%tmpNumberChange+'%'))
                    self.setRealTradeLabelColor(self.shNumberValueLabel, tmpColor)
                elif tmpNumberCode == self.stockRealTrade.numberList[1]:
                    self.szNumberValueLabel.setText(self.tr('%.2f   '%tmpNumberValue+'%.2f'%tmpNumberChange+'%'))
                    self.setRealTradeLabelColor(self.szNumberValueLabel, tmpColor)
                elif tmpNumberCode == self.stockRealTrade.numberList[2]:
                    self.cybNumberValueLabel.setText(self.tr('%.2f   '%tmpNumberValue+'%.2f'%tmpNumberChange+'%'))
                    self.setRealTradeLabelColor(self.cybNumberValueLabel, tmpColor)
                else:
                    print "code"+tmpNumberCode+"not found"

if __name__ == '__main__':
    app=QApplication(sys.argv)
    stockDialog=StockDialog()
    stockDialog.showMaximized()
    app.exec_()

