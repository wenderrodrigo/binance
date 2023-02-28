#// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/

#// Credits to the original Script - Range Filter DonovanWall https://www.tradingview.com/script/lut7sBgG-Range-Filter-DW/
#// This version is the old version of the Range Filter with less settings to tinker with

#//@version=4
from array import array
import numpy as np

#study(title="Range Filter - B&S Signals", shorttitle="RF - B&S Signals", overlay=true)

#//-----------------------------------------------------------------------------------------------------------------------------------------------------------------
#//Functions
#//-----------------------------------------------------------------------------------------------------------------------------------------------------------------

#def ema(x, y):
#    alfa = 2 / (y + 1)
#    return alfa * x + (1 - alfa) * ema[1]

def isnumber(value):
    try:
         float(value)
    except ValueError:
         return False
    return True

def sma(x, y):
    sum = 0.0
    i = 0
    while i <= (y - 1):
        sum = sum + x[i] / y
        i=i+1

    return sum

def nz(x):
    qtd = x.count()
    if x[(qtd-1)]==None or x[(qtd-1)]=='NaN':
        x[(qtd-1)]=0
    return x[(qtd-1)]


#//the same on pine
def ema(src, length):
    alpha = 2 / (length + 1)
    sum = 0.0
    try:
        sum = sma(src, length) if isnumber(sum[1]) else float(alpha) * float(src) + float(1 - alpha) * float(nz(sum[1]))
    except:
        pass

    return sum


#plot(ema(close,15))

#//Range Size Function
def rng_size(x, qty, n):
    qtd = x.count()
    #//    AC       = Cond_EMA(abs(x - x[1]), 1, n)
    wper      = (n*2) - 1
    avrng     = ema(abs(x[0] - x[1]), n)
    AC = ema(avrng, wper)*qty
    return AC  #rng_size = AC

#//Range Filter Function
def rng_filt(x, rng_, n):
    r          = rng_
    array = [2, x]
    rfilt  = 0#array.push(2, x)
    array[rfilt, 1] = array[rfilt, 0]
    if x - r > array[rfilt, 1]:
        array[rfilt, 0] = x - r
    if x + r < array[rfilt, 1]:
        array[rfilt, 0] = x + r
    rng_filt1 = array[rfilt, 0]

    hi_band   = rng_filt1 + r
    lo_band   = rng_filt1 - r
    rng_filt  = rng_filt1
    return [hi_band, lo_band, rng_filt]
#
# #//-----------------------------------------------------------------------------------------------------------------------------------------------------------------
# #//Inputs
# #//-----------------------------------------------------------------------------------------------------------------------------------------------------------------
#
# #//Range Source
# rng_src = 'close' #input(defval=close, type=input.source, title="Swing Source")
#
# #//Range Period
# rng_per = 20 #input(defval=20, minval=1, title="Swing Period")
#
# #//Range Size Inputs
# rng_qty   = 3.5 #input(defval=3.5, minval=0.0000001, title="Swing Multiplier")
#
# #//Bar Colors
# use_barcolor = False #input(defval=false, type=input.bool, title="Bar Colors On/Off")
#
# #//-----------------------------------------------------------------------------------------------------------------------------------------------------------------
# #//Definitions
# #//-----------------------------------------------------------------------------------------------------------------------------------------------------------------
#
# #//Range Filter Values
# [h_band, l_band, filt] = rng_filt(rng_src, rng_size(rng_src, rng_qty, rng_per), rng_per)
#
# #//Direction Conditions
# fdir = 0.0
# fdir    = 1 if filt > filt[1] else -1 if filt < filt[1] else fdir
# upward   = 1 if fdir==1 else 0
# downward = 1 if fdir==-1 else 0
#
# #//Trading Condition
# longCond = rng_src > filt and rng_src > rng_src[1] and upward > 0 or rng_src > filt and rng_src < rng_src[1] and upward > 0
# shortCond = rng_src < filt and rng_src < rng_src[1] and downward > 0 or rng_src < filt and rng_src > rng_src[1] and downward > 0
#
# CondIni = 0
# CondIni = 1 if longCond else -1 if shortCond else CondIni[1]
# #CondIni = longCond ? 1 : shortCond ? -1 : CondIni[1]
# longCondition = longCond and CondIni[1] == -1
# shortCondition = shortCond and CondIni[1] == 1
#
# #//Colors
# filt_color = '#05ff9b' if upward else '#ff0583' if downward else '#cccccc'
# bar_color  = ('#05ff9b' if rng_src > rng_src[1] else '#00b36b') if upward and (rng_src > filt) else ('#ff0583' if rng_src < rng_src[1] else '#b8005d') if downward and (rng_src < filt) else '#cccccc'

#//-----------------------------------------------------------------------------------------------------------------------------------------------------------------
#//Outputs
#//-----------------------------------------------------------------------------------------------------------------------------------------------------------------

#//Filter Plot
#filt_plot = plot(filt, color=filt_color, transp=67, linewidth=3, title="Filter")

#//Band Plots
#h_band_plot = plot(h_band, color=color.new('#05ff9b', 100), title="High Band")
#l_band_plot = plot(l_band, color=color.new('#ff0583', 100), title="Low Band")

#//Band Fills
#fill(h_band_plot, filt_plot, color=color.new('#00b36b', 92), title="High Band Fill")
#fill(l_band_plot, filt_plot, color=color.new('#b8005d', 92), title="Low Band Fill")

#//Bar Color
#barcolor(use_barcolor ? bar_color : na)

#//Plot Buy and Sell Labels
#plotshape(longCondition, title = "Buy Signal", text ="BUY", textcolor = color.white, style=shape.labelup, size = size.normal, location=location.belowbar, color = color.new(color.green, 0))
#lotshape(shortCondition, title = "Sell Signal", text ="SELL", textcolor = color.white, style=shape.labeldown, size = size.normal, location=location.abovebar, color = color.new(color.red, 0))

#//Alerts
#alertcondition(longCondition, title="Buy Alert", message = "BUY")
#alertcondition(shortCondition, title="Sell Alert", message = "SELL")