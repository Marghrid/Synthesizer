import subprocess

template = 'python3 predict.py -i PATH -m MAX'

args = template.replace('PATH', 'benchmarks/bar_charts/Q3-consumer_complaints_out.png')
args = args.replace('MAX', str(221000))
process = subprocess.check_output(args.split())
