import subprocess
from os import listdir
from os.path import isfile, join

MAX_LOC = 6
outputs = ['benchmarks/real_output_tables/' + f for f in listdir('benchmarks/real_output_tables/')]

template = 'python3 synthesizer.py -i0 INPUT -o OUTPUT -l LINES -d DEPTH -t dsl.tyrell -m MAX'
benchmarks = { #1
              'benchmarks/input_tables/Q2-consumer_complaints.csv': [65800, 3, 4],
              'benchmarks/input_tables/Q3-consumer_complaints.csv': [221000, 3, 4],
              'benchmarks/input_tables/Q4-health-facilities-gh.csv': [735, 3, 4],
              'benchmarks/input_tables/Q6-input-avocado.csv': [2, 3, 4],
              'benchmarks/input_tables/Q7-input-avocado.csv': [6200000000, 2, 3],
              'benchmarks/preprocessed_input_tables/Q8-input-avocado.csv': [1330000000, 3, 4],
              'benchmarks/preprocessed_input_tables/Q9-input-titanic.csv': [270, 2, 3],
              'benchmarks/preprocessed_input_tables/Q10-input-titanic.csv': [445, 2, 3],
              'benchmarks/preprocessed_input_tables/Q11-input-titanic.csv': [285, 2, 3],
              'benchmarks/input_tables/Q12-input-bikes.csv': [815, 2, 3],
              'benchmarks/input_tables/Q13-input-bikes.csv': [40, 2, 3],
              'benchmarks/input_tables/Q14-airline-sentiment.csv': [3525, 3, 4],
              'benchmarks/preprocessed_input_tables/Q15-input-bank.csv': [1330, 2, 3],
              'benchmarks/preprocessed_input_tables/Q16-input-bank.csv': [4605, 2, 3],
              'benchmarks/input_tables/Q17-input-work.csv': [250, 2, 3],
               #18
              'benchmarks/preprocessed_input_tables/Q19-input-work.csv': [6180, 2, 3],
              'benchmarks/input_tables/Q20-instacart.csv': [1, 3, 4],
              'benchmarks/input_tables/Q21-crimes-in-boston.csv': [40500, 3, 4],
              'benchmarks/preprocessed_input_tables/Q22-immigrants_by_nationality.csv': [6695, 3, 4],
              'benchmarks/preprocessed_input_tables/Q23-deaths-barcelona.csv': [1, 3, 4],
              'benchmarks/input_tables/Q24-population-barcelona.csv': [70, 3, 4],
               #25
              'benchmarks/input_tables/Q26-youtube-traffic.csv': [115, 3, 4],
              'benchmarks/input_tables/Q27-youtube-traffic.csv': [5140, 3, 4],
              'benchmarks/input_tables/Q28-youtube-traffic.csv': [15100, 4, 5],
              'benchmarks/input_tables/Q29-youtube-traffic_out.png': [535, 3, 4],
              'benchmarks/preprocessed_input_tables/Q30-wine-input.csv': [90, 4, 5],
               #31
               #32
              'benchmarks/input_tables/Q33-input-pokemon.csv': [195, 2, 3],
              'benchmarks/input_tables/Q34-input-pokemon.csv': [145, 3, 4],
              'benchmarks/input_tables/Q35-airbnb-nyc.csv': [1, 3, 4],
              'benchmarks/input_tables/Q36-airbnb-nyc.csv': [1, 3, 4],
              'benchmarks/input_tables/Q37-airbnb-nyc.csv': [175, 2, 3],
              'benchmarks/input_tables/Q38-airbnb-nyc.csv': [360, 3, 4],
              'benchmarks/input_tables/Q39-gun-violence.csv': [610, 3, 4],
               #40
              'benchmarks/input_tables/Q41-gun-violence.csv': [355, 3, 4],
              'benchmarks/input_tables/Q42-employee.csv': [615, 2, 3],
              'benchmarks/input_tables/Q43-employee.csv': [3170, 2, 3],
              'benchmarks/input_tables/Q44-employee.csv': [735, 3, 4],
              'benchmarks/input_tables/Q45-members.csv': [430, 3, 4],
              'benchmarks/input_tables/Q46-members.csv': [1020, 2, 3],
              'benchmarks/input_tables/Q47-members.csv': [1590, 2, 3],
              'benchmarks/input_tables/Q48-videogame.csv': [9725, 3, 4],
              'benchmarks/input_tables/Q49-videogame.csv': [11200, 2, 3],
              'benchmarks/input_tables/Q50-videogame.csv': [80, 3, 4],
              'benchmarks/input_tables/Q51-aircraft.csv': [15, 4, 5],
              'benchmarks/input_tables/Q52-appstore.csv': [20, 3, 4],
              'benchmarks/input_tables/Q53-appstore.csv': [10800, 2, 3],
              'benchmarks/input_tables/Q54-appstore.csv': [11500, 2, 3],
              'benchmarks/input_tables/Q55-appstore.csv': [20, 3, 4]
              }

for name in benchmarks:
    for i in range(2, MAX_LOC):
        args = template.replace('INPUT', name)
        args = args.replace('MAX', str(benchmarks[name][0]))
        args = args.replace('LINES', str(i))
        args = args.replace('DEPTH', str(i + 1))

        string = name[name.find('input_tables/Q') + len('input_tables/Q'):]
        first, second = string[0], string[1]
        query = ''
        if second.isdigit():
            query = 'Q' + first + second + '-'
        else:
            query = 'Q' + first + '-'

        output = next(filter(lambda x: query in x, outputs))
        args = args.replace('OUTPUT', output)
        with open('results/' + query[:-1] + '_depth{}'.format(i) + '.txt', 'a+') as err:
            subprocess.Popen(args.split(), stderr=err).wait()
