from os import listdir

dir = ['results/' + f for f in listdir('results/')]
starts = len('[info] Found program ')
w_score = len(' with score ')
queries = {i: [] for i in range(1, 56)}
queries_attempts = {i: 0 for i in range(1, 56)}


for i in range(1, 56):
    query = 'Q{}_'.format(i)
    files = list(filter(lambda x: query in x, dir))
    for file in files:
        depth = int(file[file.find('depth')+5:-4])
        attempts = 0
        with open(file, 'r') as f:
            for line in f:
                if '[info] Found program ' in line:
                    score = float(line[line.find(' with score ') + w_score:-1])
                    program = line[starts:line.find(' with score ')]
                    queries[i] += [(program, depth, score)]
                if '[info] Attempts ' in line:
                    print(line)
                    attempts = int(line[len('[info] Attempts '):-1])
        queries_attempts[i] += attempts
        print(line, end='')


print(queries)
print(queries_attempts)
