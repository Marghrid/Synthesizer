import subprocess

template = 'python3 NN/predict.py -i PATH -m MAX'

args = template.replace('PATH', 'benchmarks/bar_charts/Q3-consumer_complaints_out.png')
args = args.replace('MAX', str(221000))
output = subprocess.check_output(args.split())
output = output.decode('utf-8')
n_bars, values = eval(output)

bars = [('bar{}'.format(i), values[i]) for i in range(n_bars)]
with open('NN/' + 'Q3-consumer_complaints_out.png'.replace('.png', '-nn.csv'), "a+") as f:
    print('{},{}'.format('col0','col1'), file=f)
    for bar in bars:
        print('{},{}'.format(bar[0],bar[1]), file=f)

