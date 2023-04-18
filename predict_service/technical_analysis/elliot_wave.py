from typing import List, Tuple

def elliot_wave(market_data, impulse_peak: int = 1, corrective_peak: int = 1, retracement_buy: float = 0.382, retracement_sell: float = 0.618) -> str:
    def find_waves(data: List[float]) -> Tuple[float, float, float]:
        # Implement a simple peak and trough detection algorithm
        peaks = []
        troughs = []

        for i in range(1, len(data) - 1):
            if data[i] > data[i - 1] and data[i] > data[i + 1]:
                peaks.append((i, data[i]))
            elif data[i] < data[i - 1] and data[i] < data[i + 1]:
                troughs.append((i, data[i]))

        # Identify impulse and corrective waves (use simple wave counting)
        if len(peaks) < 2 or len(troughs) < 2:
            return None, None, None

        impulse_wave = (troughs[0][1], peaks[impulse_peak][1])
        corrective_wave = (peaks[impulse_peak][1], troughs[corrective_peak][1])

        return impulse_wave, corrective_wave, troughs[0][1]

    closing_prices = [float(data[4]) for data in market_data]
    impulse_wave, corrective_wave, start_price = find_waves(closing_prices)

    if not impulse_wave:
        return "hold"

    impulse_size = impulse_wave[1] - impulse_wave[0]
    corrective_size = corrective_wave[0] - corrective_wave[1]

    retracement_ratio = corrective_size / impulse_size

    # Make a trading recommendation based on the retracement ratio
    if retracement_ratio < retracement_buy:
        return "buy"
    elif retracement_ratio < retracement_sell:
        return "hold"
    else:
        return "sell"
