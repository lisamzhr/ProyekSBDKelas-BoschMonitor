import pandas as pd
import numpy as np
from scipy import stats
from scipy.fft import fft, fftfreq

def load_data_to_dataframe(measurements_list):
    if not measurements_list:
        return pd.DataFrame()
    df = pd.DataFrame(measurements_list)
    df['t'] = pd.to_datetime(df['t'])
    return df

def calculate_rms_vibration(df):
    if df.empty:
        return 0.0
    
    rms_value = np.sqrt(np.mean(df['ax']**2+df['ay']**2+df['az']**2))
    return round(float(rms_value),4)

def calculate_temperature_trend(df, window_size=5):
    if df.empty:
        return []
    df['temp_trend'] = df['temp'].rolling(window=window_size).mean()
    df['temp_trend'] = df['temp_trend'].fillna(df['temp'])
    return df['temp_trend'].tolist()

def detect_anomalies_zscore(df, column_name='temp', threshold=3.0):
    if df.empty or df[column_name].std()==0:
        return []
    z_scores = np.abs(stats.zscore(df[column_name]))
    anomalies  = df[z_scores>threshold]
    return anomalies.to_dict(orient='records')

def calculate_fft_spectrum(df, axis_column='az', sample_rate=50):
    if df.empty:
        return {
            "frequencies": [],
            "magnitudes": []
        }
    
    N = len(df)

    if N<2:
        return {
            "positive_frequencies": [],
            "magnitudes": []
        }

    y_freq = fft(df[axis_column].values)
    x_freq = fftfreq(N, 1/sample_rate)

    positive_frequencies = x_freq[:N//2]
    magnitudes = np.abs(y_freq[0:N//2])

    return {"frequencies": positive_frequencies.tolist(), "magnitudes": magnitudes.tolist()}
