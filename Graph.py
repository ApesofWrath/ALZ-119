import plotly
import plotly.graph_objs as go
from plotly.offline import *
import numpy as np

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

file = open("graphing_data.txt", "r")

x_data = [x for x in range(0, file_len("graphing_data.txt"))]
left_data = []
right_data = []
center_data = []

for line in file:
    spaces = [pos for pos, char in enumerate(line) if char == " "]
    left_data.append(line[0:spaces[0]])
    right_data.append(line[spaces[0] + 1: spaces[1]])
    center_data.append(line[spaces[1] + 1: len(line)])


# Create a trace
left = go.Scatter(
    x = x_data,
    y = left_data,
    name = 'Left Tape'
)

right = go.Scatter(
    x = x_data,
    y = right_data,
    name = 'Right Tape'
)

center = go.Scatter(
    x = x_data,
    y = center_data,
    name = 'Center Tape'
)

data = [left, right, center]

layout = dict(title = 'Center Distance Error',
              xaxis = dict(title = 'Distance (m)'),
              yaxis = dict(title = 'Iteration Point'),
              )

fig = dict(data=data, layout=layout)
plotly.offline.plot(fig, filename='center_distance_error.html')
