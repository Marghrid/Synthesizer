import subprocess

template = 'python3 NN/predict.py -i PATH -m MAX'
benchmarks = {'Q1-flight_delays_out.png': [45, 12],
              'Q2-consumer_complaints_out.png': [65800, 10],
              'Q3-consumer_complaints_out.png': [221000, 6],
              'Q4-health-facilities-gh_out.png': [735, 10],
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
              'Q24-population-barcelona_out.png': [70, 2],
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

for name in benchmarks:
    args = template.replace('PATH', 'benchmarks/bar_charts/' + name)
    args = args.replace('MAX', str(benchmarks[name][0]))
    output = subprocess.check_output(args.split())
    output = output.decode('utf-8')
    n_bars, values = eval(output)
    bars = [('bar{}'.format(i), values[i]) for i in range(n_bars)]
    with open('NN/' + name.replace('.png', '-nn.csv'), "a+") as f:
        print('{},{}'.format('col0', 'col1'), file=f)
        for bar in bars:
            print('{},{}'.format(bar[0], bar[1]), file=f)

