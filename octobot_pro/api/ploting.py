async def plot_indicator(ctx, name, x, y, signals=None):
    # lazy import
    import octobot_pro as op

    await op.plot(ctx, name, x=list(x), y=list(y))
    value_by_x = {
        x: y
        for x, y in zip(x, y)
    }
    if signals:
        await op.plot(ctx, "signals", x=list(signals), y=[value_by_x[x] for x in signals], mode="markers")

