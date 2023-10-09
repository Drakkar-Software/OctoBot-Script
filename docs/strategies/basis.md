# OctoBot-Script strategies

On OctoBot-Script, a trading strategy is a python async function that will be called at new price data.
``` python
async def strategy(ctx):
    # your strategy content
```

In most cases, a strategy will:
1. Read price data
2. Use technical evaluators or statistics
3. Decide to take (or not take) action depending on its configuration 
4. Create / cancel or edit orders (see [Creating orders](../../docs/trading/orders.md))

As OctoBot-Script strategies are meant for backtesting, it is possible to create a strategy in 2 ways:
## Pre-computed strategies
Pre-computed are only possible in backtesting: since the data is already known, when dealing with technical 
evaluator based strategies, it is possible to compute the values of the evaluators for the whole backtest at once. 
This approach is faster than iterative strategies as evaluators call only called once. 

Warning: when writing a pre-computed strategy, always make sure to associate the evaluator values to the 
right time otherwise you might be reading data from the past of the future when running the strategy.

``` python
config = {
    "period": 10,
    "rsi_value_buy_threshold": 28,
}
run_data = {
    "entries": None,
}
async def strategy(ctx):
    if run_data["entries"] is None:
        # 1. Read price data
        closes = await op.Close(ctx, max_history=True)
        times = await op.Time(ctx, max_history=True, use_close_time=True)
        # 2. Use technical evaluators or statistics 
        rsi_v = tulipy.rsi(closes, period=ctx.tentacle.trading_config["period"])
        delta = len(closes) - len(rsi_v)
        # 3. Decide to take (or not take) action depending on its configuration 
        run_data["entries"] = {
            times[index + delta]
            for index, rsi_val in enumerate(rsi_v)
            if rsi_val < ctx.tentacle.trading_config["rsi_value_buy_threshold"]
        }
        await op.plot_indicator(ctx, "RSI", times[delta:], rsi_v, run_data["entries"])
    if op.current_live_time(ctx) in run_data["entries"]:
        # 4. Create / cancel or edit orders
        await op.market(ctx, "buy", amount="10%", stop_loss_offset="-15%", take_profit_offset="25%")
```
This pre-computed strategy computes entries using the RSI: times of favorable entries are stored into 
`run_data["entries"]` which is defined outside on the `strategy` function in order to keep its values 
throughout iterations.

Please note the `max_history=True` in `op.Close` and `op.Time` keywords. This is allowing to select 
data using the whole run available data and only call `tulipy.rsi` once and populate `run_data["entries"]` 
only once.

In each subsequent call, `run_data["entries"] is None` will be `True` and only the last 2 lines of 
the strategy will be executed. 

## Iterative strategies
``` python
config = {
    "period": 10,
    "rsi_value_buy_threshold": 28,
}
async def strategy(ctx):
    # 1. Read price data
    close = await op.Close(ctx)
    if len(close) <= ctx.tentacle.trading_config["period"]:
        # not enough data to compute RSI
        return
    # 2. Use technical evaluators or statistics 
    rsi_v = tulipy.rsi(close, period=ctx.tentacle.trading_config["period"])
    # 3. Decide to take (or not take) action depending on its configuration 
    if rsi_v[-1] < ctx.tentacle.trading_config["rsi_value_buy_threshold"]:
        # 4. Create / cancel or edit orders
        await op.market(ctx, "buy", amount="10%", stop_loss_offset="-15%", take_profit_offset="25%")
```
This iterative strategy is similar to the above pre-computed strategy except that it is evaluating the RSI 
at each candle to know if an entry should be created.

This type of strategy is simpler to create than a pre-computed strategy and can be used in 
OctoBot live trading.

## Running a strategy

When running a backtest, a strategy should be referenced alongside:
- The [data it should be run on](../../docs/data/fetching_data.md) using `op.run`:
- Its configuration (a dict in above examples, it could be anything)

``` python
res = await op.run(data, strategy, config)
```

Have a look [here](../../#script) for a full example of 
how to run a strategy within a python script.
