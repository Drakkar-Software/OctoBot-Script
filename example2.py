import asyncio
import tulipy     # Can be any TA library.
import octobot_script as obs
import numpy as np
import pandas as pd
import talib as tl

#--------------------------INPUTS--------------------------------
global closes
global times
global volume

global medie_close
global medie_volum

IS_length_min = 20  # nr pozitii minime intre varfuri
interval_stabil = 150

proc_intre_vrf_line_IS = 0.1  #(2%)
pr_vrf_dif_medie = 0.025  #(2.5%)
procent_spargere_IS = 0.05  #(5%)

procent_volum_max = 0.3 # (80%)  # volume mari pe buy [only]
procent_high_close_cross = 0.3 # (20% diferenta intre ele)
var_nr_volume = 3  #cate volume mari sa fie in IS
medie_close_period = 7

cross_max = 0
cross_min = 0
crossed = False
wider_line_max = False
wider_line_min = False

# Array to store local maxima
local_maxim = [0]
local_minim = [0]
line_max = []
line_min = []

smma = [0]

# MACD Section
lengthMA = 34
lengthSignal = 9
macd_max_delta = 0.18

#--------------------------FUNCTIONS------------------------------
async def calc_smma(src, length):
    global smma
    if len(smma) == 1:
        smma = tulipy.sma(src,length)
    else:
        smma = (smma[1] * (length-1) + src) / length
    return smma

async def calc_smma2(src: np.ndarray, length: int) -> np.ndarray:
    """
    Calculate Smoothed Moving Average (SMMA) for a given numpy array `src` with a specified `length`.

    :param src: A numpy ndarray of shape (n,) containing the input values of float64 dtype.
    :param length: An integer representing the length of the SMMA window.
    :return: A numpy ndarray of the same shape as `src` containing the SMMA values.
    """
    smma = np.full_like(src, fill_value=np.nan)
    sma = tl.SMA(src, length)

    for i in range(1, len(src)):
        smma[i] = (
            sma[i]
            if np.isnan(smma[i - 1])
            else (smma[i - 1] * (length - 1) + src[i]) / length
        )

    return smma

async def calc_zlema(src, length):
    ema1 = tulipy.ema(src, length)
    ema2 = tulipy.ema(ema1, length)
    d = ema1 - ema2
    return ema1+d

async def calc_zlema2(src: np.ndarray, length: int) -> np.ndarray:
    """
    Calculates the zero-lag exponential moving average (ZLEMA) of the given price series.

    :param src: The input price series of float64 dtype to calculate the ZLEMA for.
    :param length: int The number of bars to use for the calculation of the ZLEMA.
    :return: A numpy ndarray of ZLEMA values for the input price series.
    """
    ema1 = tl.EMA(src, length)
    ema2 = tl.EMA(ema1, length)
    d = ema1 - ema2
    return ema1 + d

async def stability_interval():
    async def strategy(ctx):
         # Will be called at each candle.
        interval_stabilitate = False

        if run_data["entries"] is None:
             # Compute entries only once per backtest.
            
            closes = await obs.Close(ctx, max_history=True)
            high = await obs.High(ctx, max_history=True)
            low = await obs.Low(ctx, max_history=True)
            times = await obs.Time(ctx, max_history=True, use_close_time=True)
            volume = await obs.Volume(ctx, max_history=True)
            hlc3 = (high + low + closes)/3

            medie_close = tulipy.sma(closes, medie_close_period)
            medie_volum = tulipy.sma(volume, 35)

            #Start of MACD
            src=hlc3
            hi= await calc_smma2(high, lengthMA) #needs smma !!! --------
            lo= await calc_smma2(low, lengthMA) #needs smma !!! --------
            mi= await calc_zlema2(src, lengthMA) # needs smma !!! -------

            md = np.full_like(mi, fill_value=np.nan)

            conditions = [mi > hi, mi < lo]
            choices = [mi - hi, mi - lo]

            md = np.select(conditions, choices, default=0)

            sb = tulipy.sma(md, lengthSignal)        #"ImpulseMACDCDSignal": sb
            md = md[md.size-sb.size:]                #"ImpulseMACD": md
            sh = md - sb                             #"ImpulseHisto": sh
            #end of MACD

            for count_a in range(medie_close_period,len(closes)-1):
                if closes[count_a-1] < closes[count_a] and closes[count_a] > closes[count_a+1]:
                    if closes[count_a] / medie_close[count_a-medie_close_period] >= 1 + pr_vrf_dif_medie:
                        local_maxim.append(closes[count_a])
                    else:
                        local_maxim.append(0)
                else:
                    local_maxim.append(0)
            local_maxim.append(0) # to be removed !!! -------

            #Build the local_minim list
            for count_a in range(medie_close_period,len(closes)-1):
                if closes[count_a-1] > closes[count_a] and closes[count_a] < closes[count_a+1]:
                    if closes[count_a] / medie_close[count_a-medie_close_period] <= 1 - pr_vrf_dif_medie:
                        local_minim.append(-closes[count_a])
                    else:
                        local_minim.append(0)
                else:
                    local_minim.append(0)
            local_minim.append(0) # to be removed !!! -------


            #rsi_v = tulipy.rsi(closes, period=ctx.tentacle.trading_config["period"])
             #meu = tulipy.ema(closes, period=ctx.tentacle.trading_config["period"])
            delta = len(closes) - len(local_maxim)
             # Populate entries with timestamps of candles where RSI is
             # bellow the "rsi_value_buy_threshold" configuration.
            run_data["entries"] = {
                times[index + delta]
                for index, max_val in enumerate(local_maxim)
                if max_val > ctx.tentacle.trading_config["max_val"]
                #times[index + delta]
                #for index, rsi_val in enumerate(rsi_v)
                #if rsi_val < ctx.tentacle.trading_config["rsi_value_buy_threshold"]
            }

            #await obs.plot_indicator(ctx, "Local_Maxim", times[delta:], local_maxim, run_data["entries"])
            #await obs.plot_indicator(ctx, "Local_Maxim2", times[delta:], local_maxim, run_data["entries2"])
            await obs.plot(ctx, "Medie_close", times[:], medie_close, mode="lines",color="blue")
            await obs.plot(ctx, "Local_maxim", times[:], local_maxim, mode="lines",color="white")
            await obs.plot(ctx, "Local_minim", times[:], local_minim, mode="lines",color="green")
            
            ### PRINT MACD
            await obs.plot(ctx, "ImpulseMACD", times[:], md, mode="scatter",color="blue", chart="main-chart")
            await obs.plot(ctx, "ImpulseHisto", times[:], sh, mode="scatter",color="white", chart="main-chart")
            await obs.plot(ctx, "ImpulseMACDCDSignal", times[:], sb, mode="lines",color="green", chart="main-chart")

        last_pos_max = 0
        last_pos_min = 0
        ultimul_x = 0
        suma_varfuri_high = 0
        inc = 0
        line_max_exists = False
        line_max_exists = False
        procent_max = 0
        procent_min = 0

        for i in range(0, len(local_maxim)-interval_stabil):
            for j in range(0, interval_stabil):
                
                # Cu cat % este diferenta intre maxime ?
                if ( local_maxim[i+j+1] != 0 ):
                    procent_max = local_maxim[i+j] / local_maxim[i+j+1]
                if ( local_minim[i+j+1] != 0 ):
                    procent_min = local_minim[i+j] / local_minim[i+j+1]
                
                if i>100:
                    print("i>100")

                #if there is a much higher peak than the maximum peaks - no stability interval
                if procent_max > 1 + proc_intre_vrf_line_IS: 
                    break

                #if there is a much lower peak than the minimum peaks - no stability interval
                if procent_min < 1-proc_intre_vrf_line_IS:
                    break
                
                if abs(sb[i+j]) >= macd_max_delta:
                    break
                
                if procent_max <= 1+proc_intre_vrf_line_IS and procent_max >= 1-proc_intre_vrf_line_IS:
                    last_pos_max=i+j
                
                if procent_min <= 1+proc_intre_vrf_line_IS and procent_min >= 1-proc_intre_vrf_line_IS:
                    last_pos_min=i+j

                # _____ verific daca exista alta linie de maxime intre varfuri _______
                #conditie pentru a face verificari doar dupa ce nr de bar-uri este suficient pentru a interoga indexul "interval_stabil"
                if len(line_max) >= interval_stabil:
                    if line_max[i+j-1] != 0:
                        line_max_exists = True
                
                # _____ verific daca exista alta linie de minime intre varfuri ______
                if len(line_min) >= interval_stabil:
                    if line_min[i+j-1] != 0:
                        line_min_exists = True
                
            ## ______ Definire interval stabilitate ______
            if last_pos_max !=0 and last_pos_max >=IS_length_min and line_max_exists == false:
                line_max.append(high[i+j+1]-last_pos_max-1)
                #array.push(line_max,line.new(bar_index - last_pos_max-1, (high[last_pos_max] + high[1])/2, bar_index-1, (high[last_pos_max] + high[1])/2,color=color.green,width = 4))
                #log.info("Found max line with high[{1}] = {0}", high[last_pos_max], last_pos_max)
            else:
                #____ Verific daca am un interval mai mare de stabilitate ____
                if last_pos_max !=0 and last_pos_max >=IS_length_min and line_max_exists == true and math.abs(sb)-macd_max_delta <=0 and math.abs(sb[last_pos_max])<= macd_max_delta:
                    #log.info("sb = {0}, abs(sb)={1}", sb, math.abs(sb)-macd_max_delta)
                    #log.info("Found wider max line with high[{1}] = {0}", high[last_pos_max], last_pos_max)
                    wider_line_max = True
                    line_max.append(0)
                else:
                    line_max.append(0)
                    #array.push(line_max,na)
                    #log.info("pushed max_na")
            
            if last_pos_min !=0 and last_pos_min >=IS_length_min and line_min_exists == false:
                line_min.append(low[i+j+1]-last_pos_min-1)
                #array.push(line_min,line.new(bar_index - last_pos_min-1, (low[last_pos_min] + low[1])/2, bar_index-1, (low[last_pos_min] + low[1])/2,color=color.red,width = 4))
                #log.info("Found min line with low[{1}] = {0}", low[last_pos_min], last_pos_min)
            else:
                if last_pos_min !=0 and last_pos_min >=IS_length_min and line_min_exists == true and math.abs(sb)-macd_max_delta <=0 and math.abs(sb[last_pos_min])<= macd_max_delta:
                    #log.info("sb = {0}, abs(sb)={1}", sb, math.abs(sb)-macd_max_delta)
                    #log.info("Found wider min line with low[{1}] = {0}", low[last_pos_min], last_pos_min)
                    wider_line_min = True
                    line_min.append(0)
                    #array.push(line_min,na)
                else:
                    line_min.append(0)
                    #array.push(line_min,na)
                    #log.info("pushed min_na")
        
        times = await obs.Time(ctx, max_history=True, use_close_time=True) # to be improved !!!!
        await obs.plot(ctx, "Interval_stabil_max", times[:], line_max, mode="lines",color="pink")

        if obs.current_live_time(ctx) in run_data["entries"]:
             # Uses pre-computed entries times to enter positions when relevant.
             # Also, instantly set take profits and stop losses.
             # Position exists could also be set separately.
            await obs.market(ctx, "buy", amount="1%", stop_loss_offset="-15%", take_profit_offset="35%")

     # Configuration that will be passed to each run.
     # It will be accessible under "ctx.tentacle.trading_config".
    config = {
        "IS_length_min": 20,  # nr pozitii minime intre varfuri
        "interval_stabil": 150,
        "proc_intre_vrf_line_IS": 0.1,  #(2%)
        "pr_vrf_dif_medie": 0.025,  #(2.5%)
        "procent_spargere_IS": 0.05,  #(5%)

        "procent_volum_max": 0.3, # (80%)  # volume mari pe buy [only]
        "procent_high_close_cross": 0.3, # (20% diferenta intre ele)
        "var_nr_volume": 3,  #cate volume mari sa fie in IS
        "max_val": 2500,
    }


     # Read and cache candle data to make subsequent backtesting runs faster.
    datafile = "ExchangeHistoryDataCollector_1725784408.359507.data"
     #data = await obs.get_data("ETH/USDT", "1d") #, start_timestamp=1720410417)
    data = await obs.get_data("ETH/USDT", "1d", data_file=datafile,)
    run_data = {
        "entries": None,
    }
     # Run a backtest using the above data, strategy and configuration.
    res = await obs.run(data, strategy, config)
    
    print(res.describe())
     # Generate and open report including indicators plots
    await res.plot(show=True)
     # Stop data to release local databases.

    await data.stop()


 # Call the execution of the script inside "asyncio.run" as
 # OctoBot-Script runs using the python asyncio framework.
asyncio.run(stability_interval())
