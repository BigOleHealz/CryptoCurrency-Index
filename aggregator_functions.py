#!/usr/bin/env python3
import pandas as pd
import numpy as numpy

def movingAverage(values, window):
    arr_avg = values.rolling(window).mean()

	return arr_avg