#  This file is part of OctoBot-Script (https://github.com/Drakkar-Software/OctoBot-Script)
#  Copyright (c) 2023 Drakkar-Software, All rights reserved.
#
#  OctoBot is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  OctoBot is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public
#  License along with OctoBot-Script. If not, see <https://www.gnu.org/licenses/>.

import pytest
import os
import tulipy

import octobot_script as obs
from tests.functionnal import one_day_btc_usdt_data


# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


async def test_precomputed_vs_iteration_rsi(one_day_btc_usdt_data):
    # 1. pre-compute entries at first iteration only
    async def _pre_compute_update(ctx):
        if run_data["entries"] is None:
            closes = await obs.Close(ctx, max_history=True)
            times = await obs.Time(ctx, max_history=True, use_close_time=True)
            rsi_v = tulipy.rsi(closes, period=ctx.tentacle.trading_config["period"])
            delta = len(closes) - len(rsi_v)
            run_data["entries"] = {
                times[index + delta]
                for index, rsi_val in enumerate(rsi_v)
                if rsi_val < ctx.tentacle.trading_config["rsi_value_buy_threshold"]
            }
            await obs.plot_indicator(ctx, "RSI", times[delta:], rsi_v, run_data["entries"])
        if obs.current_live_time(ctx) in run_data["entries"]:
            await obs.market(ctx, "buy", amount="10%", stop_loss_offset="-15%", take_profit_offset="25%")
    run_data = {
        "entries": None,
    }
    config = {
        "period": 10,
        "rsi_value_buy_threshold": 28,
    }
    res = await obs.run(
        one_day_btc_usdt_data, _pre_compute_update, config,
        enable_logs=False, enable_storage=True
    )
    # ensure run happened
    assert res.backtesting_data is not None
    assert res.strategy_config is not None
    assert res.independent_backtesting is not None
    assert res.bot_id is not None
    assert res.report['bot_report']['profitability']['binance'] != 0
    assert res.report["bot_report"]['end_portfolio']['binance'] != \
           res.report["bot_report"]['starting_portfolio']['binance']
    assert res.duration < 10
    assert res.candles_count == 1947
    await _check_report(res)

    # ensure second run gives the same result
    run_data = {
        "entries": None,
    }
    res_2 = await obs.run(
        one_day_btc_usdt_data, _pre_compute_update, config,
        enable_logs=True, enable_storage=False
    )
    assert res_2.bot_id != res.bot_id
    assert res_2.report['bot_report']['profitability'] == res.report['bot_report']['profitability']
    assert res_2.report["bot_report"]['end_portfolio']['binance'] != \
           res_2.report["bot_report"]['starting_portfolio']['binance']

    # try with different config
    run_data = {
        "entries": None,
    }
    config = {
        "period": 10,
        "rsi_value_buy_threshold": 10,
    }
    res_3 = await obs.run(
        one_day_btc_usdt_data, _pre_compute_update, config,
        enable_logs=False, enable_storage=False
    )
    assert res_3.bot_id is not None
    assert res_3.bot_id != res.bot_id
    assert res_3.report['bot_report']['profitability'] != res.report['bot_report']['profitability']
    assert res_3.report["bot_report"]['end_portfolio']['binance'] != \
           res_3.report["bot_report"]['starting_portfolio']['binance']

    # 2. iteration computed entries at each iteration
    async def _iterations_update(ctx):
        if obs.current_live_time(ctx) != await obs.current_candle_time(
                ctx, use_close_time=True):
            return
        close = await obs.Close(ctx)
        if len(close) <= ctx.tentacle.trading_config["period"]:
            return
        rsi_v = tulipy.rsi(close, period=ctx.tentacle.trading_config["period"])
        if rsi_v[-1] < ctx.tentacle.trading_config["rsi_value_buy_threshold"]:
            await obs.market(ctx, "buy", amount="10%", stop_loss_offset="-15%", take_profit_offset="25%")

    res_iteration = await obs.run(
        one_day_btc_usdt_data, _iterations_update, config,
        enable_logs=False, enable_storage=False
    )
    # same result as pre_computed with the same config
    assert res_iteration.report['bot_report']['profitability'] == res_3.report['bot_report']['profitability']


async def _check_report(res):
    description = res.describe()
    assert str(res.strategy_config) in description
    report = "report.html"
    await res.plot(report_file=report, show=False)
    with open(report) as rep:
        report_content = rep.read()
    for key, val in res.strategy_config.items():
        assert str(key) in report_content
        assert str(val) in report_content
    assert "BTC/USDT" in report_content
    assert "1d" in report_content
    assert "Binance" in report_content
    os.remove(report)
