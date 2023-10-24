import argparse
import pandas as pd
import numpy as np
import re
import requests
import json
import ipywidgets as widgets
from IPython.display import display
import matplotlib.pyplot as plt
import plotly.express as px

argp = argparse.ArgumentParser()
argp.add_argument('GEOJSON_URL', type=str, help='The GeoJSON URL coming from a Search in the EAMENA database', default='')

print(argp.GEOJSON_URL)
