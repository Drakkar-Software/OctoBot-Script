# pylint: disable=E1101
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

async def plot_indicator(ctx, name, x, y, signals=None):
    # lazy import
    import octobot_script as obs

    await obs.plot(ctx, name, x=list(x), y=list(y))
    value_by_x = {
        x: y
        for x, y in zip(x, y)
    }
    if signals:
        await obs.plot(ctx, "signals", x=list(signals), y=[value_by_x[x] for x in signals], mode="markers")

