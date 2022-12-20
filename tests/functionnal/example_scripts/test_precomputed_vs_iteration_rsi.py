import pytest
import os
import tulipy

import octobot_pro as op
from tests.functionnal import one_day_btc_usdt_data


# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


async def test_precomputed_vs_iteration_rsi(one_day_btc_usdt_data):
    # 1. pre-compute entries at first iteration only
    async def _pre_compute_update(ctx):
        if run_data["entries"] is None:
            closes = await op.Close(ctx, max_history=True)
            times = await op.Time(ctx, max_history=True, use_close_time=True)
            rsi_v = tulipy.rsi(closes, period=ctx.tentacle.trading_config["period"])
            delta = len(closes) - len(rsi_v)
            run_data["entries"] = {
                times[index + delta]: rsi_val
                for index, rsi_val in enumerate(rsi_v)
                if rsi_val < ctx.tentacle.trading_config["rsi_value_buy_threshold"]
            }
            await op.plot(ctx, "RSI", x=times[delta-1:], y=rsi_v)
            await op.plot(ctx, "entries", x=list(run_data["entries"]), y=list(run_data["entries"].values()), mode="markers")
        if op.current_live_time(ctx) in run_data["entries"]:
            await op.market(ctx, "buy", amount="10%", stop_loss_offset="-15%", take_profit_offset="25%")
    run_data = {
        "entries": None,
    }
    config = {
        "period": 10,
        "rsi_value_buy_threshold": 28,
    }
    res = await op.run(
        one_day_btc_usdt_data, _pre_compute_update, config,
        enable_logs=False, enable_storage=True
    )
    # ensure run happened
    assert res.backtesting_data is not None
    assert res.strategy_config is not None
    assert res.independent_backtesting is not None
    assert res.bot_id is not None
    assert res.report['bot_report']['profitability']['binance'] > 0
    assert res.duration < 10
    assert res.candles_count == 1932
    await _check_plot_report(res)

    # ensure second run gives the same result
    run_data = {
        "entries": None,
    }
    res_2 = await op.run(
        one_day_btc_usdt_data, _pre_compute_update, config,
        enable_logs=True, enable_storage=False
    )
    assert res_2.bot_id != res.bot_id
    assert res_2.report['bot_report']['profitability'] == res.report['bot_report']['profitability']

    # try with different config
    run_data = {
        "entries": None,
    }
    config = {
        "period": 10,
        "rsi_value_buy_threshold": 10,
    }
    res_3 = await op.run(
        one_day_btc_usdt_data, _pre_compute_update, config,
        enable_logs=False, enable_storage=False
    )
    assert res_3.bot_id is not None
    assert res_3.bot_id != res.bot_id
    assert res_3.report['bot_report']['profitability'] != res.report['bot_report']['profitability']

    # 2. iteration computed entries at each iteration
    async def _iterations_update(ctx):
        if op.current_live_time(ctx) != await op.current_candle_time(
                ctx, use_close_time=True):
            return
        close = await op.Close(ctx)
        if len(close) <= ctx.tentacle.trading_config["period"]:
            return
        rsi_v = tulipy.rsi(close, period=ctx.tentacle.trading_config["period"])
        if rsi_v[-1] < ctx.tentacle.trading_config["rsi_value_buy_threshold"]:
            await op.market(ctx, "buy", amount="10%", stop_loss_offset="-15%", take_profit_offset="25%")

    res_iteration = await op.run(
        one_day_btc_usdt_data, _iterations_update, config,
        enable_logs=False, enable_storage=False
    )
    # same result as pre_computed with the same config
    assert res_iteration.report['bot_report']['profitability'] == res_3.report['bot_report']['profitability']


async def _check_plot_report(res):
    report = "report.html"
    await res.plot(report_file=report)
    with open(report) as rep:
        report_content = rep.read()
    for key, val in res.strategy_config.items():
        assert str(key) in report_content
        assert str(val) in report_content
    assert "BTC/USDT" in report_content
    assert "1d" in report_content
    assert "Binance" in report_content
    os.remove(report)
