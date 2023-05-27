import json
import matplotlib.pyplot as plt
import numpy as np

with open('data.json') as f:
    data = json.load(f)

row_progress = data["row_progress"]
column_progress = data["col_progress"]
box_progress = data["box_progress"]
avg_progress = data["avg_progress"]

x = np.arange(len(row_progress))  # the label locations

# Plotting the data
plt.plot(x, row_progress, label='row_progress')

plt.plot(x, column_progress, label='column_progress')

plt.plot(x, box_progress, label='box_progress')

plt.plot(x, avg_progress, label='avg_progress')


# Adding labels and title
plt.xlabel('Steps')
plt.ylabel('Value')
plt.title('Progression')

# Adding a legend
plt.legend()

# Displaying the plot
plt.show()
