import subprocess
from os import listdir
from os.path import isfile, join
import pandas as pd
from numpy import linalg as LA
import numpy as np

benchmarks = {'Q1-flight_delays_out.png': [45, 12],
              'Q2-consumer_complaints_out.png': [65800, 10],
              'Q3-consumer_complaints_out.png': [221000, 6],
              'Q4-health-facilities-gh_out.png': [735, 10],
              'Q5-grades_out.png': [225, 8],
              'Q6-output-avocado.png': [2, 4],
              'Q7-output-avocado.png': [6200000000, 4],
              'Q8-output-avocado.png': [1330000000, 3],
              'Q9-output-titanic.png': [270, 2],
              'Q10-output-titanic.png': [445, 3],
              'Q11-output-titanic.png': [285, 5],
              'Q12-output-bikes.png': [815, 5],
              'Q13-output-bikes.png': [40, 5],
              'Q14-airline-sentiment_out.png': [3525, 10],
              'Q15-output-bank.png': [1330, 2],
              'Q16-output-bank.png': [4605, 6],
              'Q17-output-work.png': [250, 2],
              'Q18-output-work.png': [1, 10],
              'Q19-output-work.png': [6810, 6],
              'Q20-instacart_out.png': [1, 2],
              'Q21-crimes-in-boston_out.png': [40500, 10],
              'Q22-immigrants_by_nationality_out.png': [6695, 10],
              'Q23-deaths-barcelona_out.png': [8120, 11],
              'Q24-population-barcelona_out.png': [70, 2],
               #25
              'Q26-youtube-traffic_out.png': [115, 10],
              'Q27-youtube-traffic_out.png': [5140, 10],
              'Q28-youtube-traffic_out.png': [15100, 10],
              'Q29-youtube-traffic_out.png': [535, 10],
              'Q30-output-wine.png': [90 ,5],
              'Q31-output-wine.png': [3180, 5],
              'Q32-output-pokemon.png': [100, 2],
              'Q33-output-pokemon.png': [195, 6],
              'Q34-output-pokemon.png': [145, 5],
              'Q35-airbnb-nyc_out.png': [1, 5],
              'Q36-airbnb-nyc_out.png': [1, 3],
              'Q37-airbnb-nyc_out.png': [175, 5],
              'Q38-airbnb-nyc_out.png': [360, 11],
              'Q39-gun-violence_out.png': [610, 6],
              'Q40-gun-violence_out.png': [3, 14],
              'Q41-gun-violence_out.png': [355, 7],
              'Q42-employee_out.png': [615, 5],
              'Q43-employee_out.png': [3170, 2],
              'Q44-members_out.png': [735, 14],
              'Q45-members_out.png': [430, 7],
              'Q46-members_out.png': [1020, 10],
              'Q47-members_out.png': [1590, 3],
              'Q48-videogame_out.png': [9725, 5],
              'Q49-videogame_out.png': [11200, 10],
              'Q50-videogame_out.png': [80, 10],
              'Q51-aircraft_out.png': [15, 10],
              'Q52-appstore_out.png': [20, 7],
              'Q53-appstore_out.png': [10800, 7],
              'Q54-appstore_out.png': [11500, 4],
              'Q55-appstore_out.png': [20, 3]
              }
neural_n = ''
web_n = ''
neural_dict = {}
web_dict = {}

outputs = ['benchmarks/real_output_tables/' + f for f in listdir('benchmarks/real_output_tables/')]
nn = ['benchmarks/noisy_output_tables/' + f for f in listdir('benchmarks/noisy_output_tables/')]
webplot = ['benchmarks/webplotdigitizer_outputs/' + f for f in listdir('benchmarks/webplotdigitizer_outputs/')]


for i in range(1, 56):
    query = 'Q{}-'.format(i)
    real = next(filter(lambda x: query in x, outputs), None)
    neural = next(filter(lambda x: query in x, nn), None)
    web = next(filter(lambda x: query in x, webplot), None)
    for key in benchmarks:
        if query in key:
            maximum = benchmarks[key][0]
            length = benchmarks[key][1]
    if real is not None:
        col = pd.read_csv(real, names=["val1", "val2"])
        real = np.array([float(e) for e in col['val2'].values[1:]])
        col = pd.read_csv(neural, names=["val1", "val2"])
        neural = np.array([float(e) for e in col['val2'].values[1:]])
        col = pd.read_csv(web, names=["val1", "val2"])
        web = np.array([float(e) for e in col['val2'].values[1:]])
        if len(neural) == length:
            norm = LA.norm(np.subtract(real/maximum, neural/maximum), ord=1)
            neural_n += 'nn' + ' ' + query[:-1] + ' ' + str(norm/length) + '\n'
            neural_dict[query] = norm/length
        else:
            neural_n += 'nn' + ' ' + query[:-1] + ' fail n bars, real:{}, nn:{}'.format(length, len(neural)) + '\n'
        if len(web) == length:
            norm = LA.norm(np.subtract(real/maximum, web/maximum), ord=1)
            web_n += 'web' + ' ' + query[:-1] + ' ' + str(norm/length) + '\n'
            web_dict[query] = norm/length
        else:
            web_n += 'web' + ' ' + query[:-1] + ' fail n bars, real:{}, nn:{}'.format(length, len(web)) + '\n'

print(web_n)
print(neural_n)

print("web", sum(web_dict.values())/len(web_dict.values()) * 100)
print("nn", sum(neural_dict.values())/len(neural_dict.values()) * 100)

