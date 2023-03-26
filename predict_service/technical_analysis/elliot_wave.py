import requests
import numpy as np
from scipy.interpolate import UnivariateSpline

'''
This script analyzes historical price data to identify Elliott Wave patterns and generate trading signals ('buy', 'hold', or 'sell')
based on the last detected pattern. Elliott Wave Theory is a form of technical analysis used to predict market trends.

The script fetches price data, smooths it, identifies significant price changes, and then finds patterns in these changes. 
The trading signal is generated based on the completion of the wave patterns.

 Please note that this is a simplified approach, and real-world trading applications should use more sophisticated analysis and risk management strategies.
'''

def smooth_prices(prices, smoothing_factor=3):
    x = np.arange(len(prices))
    spline = UnivariateSpline(x, prices, k=smoothing_factor)
    return spline(x)

def zigzag(prices, percent_change):
    def next_extreme(i, direction):
        threshold = prices[i] * (1 + (percent_change / 100) * direction)
        for j, price in enumerate(prices[i + 1:], start=i + 1):
            if price * direction >= threshold * direction:
                return j
        return None

    zz = [0]
    direction = 1

    while True:
        next_point = next_extreme(zz[-1], direction)
        if next_point is None:
            break

        zz.append(next_point)
        direction = -direction

    return zz

def is_fibonacci_retracement(a, b, c, prices, tolerance=0.05):
    retracement = abs((prices[c] - prices[b]) / (prices[b] - prices[a]))

    # Fibonacci retracement levels
    fibonacci_levels = [0.236, 0.382, 0.5, 0.618, 0.786]

    for level in fibonacci_levels:
        if abs(retracement - level) <= tolerance:
            return True

    return False

def is_triangle(points, prices):
    if len(points) < 5:
        return False

    x = np.array(points)
    y = prices[x]

    # Fit trendlines
    trendline1 = np.polyfit(x[:3], y[:3], 1)
    trendline2 = np.polyfit(x[2:], y[2:], 1)

    # Calculate intersection point
    intersection_x = (trendline2[1] - trendline1[1]) / (trendline1[0] - trendline2[0])
    intersection_y = trendline1[0] * intersection_x + trendline1[1]

    # Check if intersection point is within the triangle
    if not (x[1] <= intersection_x <= x[-1]):
        return False

    # Check if the triangle is converging
    if np.sign(trendline1[0]) == np.sign(trendline2[0]):
        return False

    return True

def elliot_wave(market_data):
    data = market_data.copy()

    # Extract closing prices
    closing_prices = [float(item[4]) for item in data]
    prices =  np.array(closing_prices)

    percent_change=2
    smoothed_prices = smooth_prices(prices)
    zz = zigzag(smoothed_prices, percent_change)

    wave_patterns = []
    zz_start = 0

    while zz_start + 6 < len(zz):
        zz_wave = zz[zz_start:zz_start + 7]

        # Check if the price swings follow the Elliott Wave rules
        def valid_elliott_wave():
            for i in range(0, 5, 2):
                if smoothed_prices[zz_wave[i]] >= smoothed_prices[zz_wave[i + 2]]:
                    return False
            for i in range(1, 5, 2):
                if smoothed_prices[zz_wave[i]] <= smoothed_prices[zz_wave[i + 2]]:
                    return False

            # Check if waves 2 and 4 are Fibonacci retracements
            if not (is_fibonacci_retracement(zz_wave[0], zz_wave[1], zz_wave[2], smoothed_prices) and
                    is_fibonacci_retracement(zz_wave[2], zz_wave[3], zz_wave[4], smoothed_prices)):
                return False

            # Check for wave extensions
            wave_lengths = [abs(smoothed_prices[zz_wave[i + 1]] - smoothed_prices[zz_wave[i]]) for i in range(5)]
            wave_ratios = [wave_lengths[i] / wave_lengths[i + 1] for i in range(0, 4, 2)]
            if any(ratio > 1.618 for ratio in wave_ratios):
                return False

            # Check for wave truncations
            if smoothed_prices[zz_wave[4]] > smoothed_prices[zz_wave[2]]:
                return False

            return True

        if valid_elliott_wave():
            waves = ["1", "2", "3", "4", "5", "A", "B", "C"]
            waves.extend(zz_wave[:5])

            # Find corrective waves (A, B, C)
            if len(zz_wave) > 5:
                waves.extend(zz_wave[5:])

            # Find triangle pattern in wave B
            if len(zz_wave) > 7:
                zz_wave_b = zz_wave[7:12]
                if is_triangle(zz_wave_b, smoothed_prices):
                    waves[6] = "B (triangle)"

            wave_patterns.append((waves, zz_wave))
            zz_start += 2
        else:
            zz_start += 1

    # get trading signal
    if not wave_patterns:
        return 'hold'

    # Get the last wave pattern
    last_pattern = wave_patterns[-1]
    waves, zz_wave = last_pattern

    # Check if the pattern is a complete 5-3 wave cycle
    if len(waves) == 8 and len(zz_wave) == 7:
        # Check if wave 5 is complete
        if waves[4] == "5":
            # Check if corrective waves (A, B, C) are complete
            if waves[5] == "A" and waves[6] == "B" and waves[7] == "C":
                return 'buy'
            else:
                return 'hold'
        else:
            return 'sell'
    else:
        return 'hold'
