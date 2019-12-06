import random
import csv
import os
import subprocess
import math

def tikz_template(plots, symbolic, n_bars, max_val):
    TEMPLATE = """\\documentclass[crop]{standalone}
\\usepackage[dvipsnames]{xcolor}
\\usepackage{natbib}
\\usepackage{graphicx}
\\usepackage{pgfplots}
\\usepackage{tikz}
\\pgfplotsset{compat=1.16}
\\definecolor{color1}{rgb}{REP1A,REP1B,REP1C}
\\definecolor{color2}{rgb}{REP2A,REP2B,REP2C}
\\definecolor{color3}{rgb}{REP3A,REP3B,REP3C}
\\begin{document}
\\begin{tikzpicture}
    \\centering
        \\begin{axis}[
            ybar stacked, axis on top, height=CHOSEN_HEIGHTcm, width=CHOSEN_WIDTHcm, bar width=RANDOM_WIDTHcm,
            ymin = 0,
            ymax = MAX_VAL,
            ytick = {TICKS},    
            ylabel style={align=center},
            symbolic x coords={SYMBOLIC_COORDS},
            xtick=data,
            x tick label style={font=\\small,text width=1cm,rotate=0,anchor=north, align=center},
            legend style={at={(0.5,-0.1.5)},
                    anchor=north,legend columns=-1},
            ]
            \\addplot[fill=color1] coordinates {
PLOTS
            };
        \\end{axis}
    \\label{fig:example}
\\end{tikzpicture}
\\end{document}""".replace("PLOTS", plots).replace("SYMBOLIC_COORDS", symbolic)
    for color in ["REP1A", "REP1B", "REP1C", "REP2A", "REP2B", "REP2C", "REP3A", "REP3B", "REP3C"]:
        TEMPLATE = TEMPLATE.replace(color, str(round(random.random(), 2)))

    bar_width = round(1 - random.random()*2/3,2)
    min_width = max((bar_width*n_bars*10)/3.6, 8)
    min_height = 10

    max_val = math.ceil((max_val)*(1+1/3 * random.random()))
    if max_val > 5:
        max_val = 5 * round(max_val/5)

    ticks = "0, "
    prev = 0
    for i in range(5):
        prev += round(max_val/5,2)
        ticks += str(prev) + ", "

    width = round(min_width*(1+random.random()),2)
    height = round(min_height*(1-random.random()/6), 2)
    TEMPLATE = TEMPLATE.replace("CHOSEN_WIDTH", str(width)).replace("CHOSEN_HEIGHT", str(height)).replace("RANDOM_WIDTH", 
        str(bar_width)).replace("TICKS", ticks[:-2]).replace("MAX_VAL", str(max_val*1.001))


    return TEMPLATE


def csv_to_tikz(input_path, output_path):
    with open(input_path, "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

        header = []
        rows = []
        total_bars = 0
        for row in csv_reader:
            if header == []: 
                header = row
            else: 
                total_bars += 1
                rows += [row]

        symbolic_coords = ""
        coords = ""
        max_val = 0
        count = 0
        for row in rows:
            symb = row[0].replace("_", "").replace(" ", "").replace("&", "")
            if len(symb) > 4:
                symb = symb[:4] + str(count)
            symbolic_coords += symb + ","
            coords += "                (" + ", ".join([symb] + [str(x) for x in row[1:]]) + ")" + os.linesep
            max_val = max([eval(x) for x in row[1:]] + [max_val])
            count += 1


        script = tikz_template(coords[:-1], symbolic_coords[:-1], total_bars, max_val)
        #print(script)
        #input()
        with open(output_path, "a+") as output:
            output.write(script)

def tikz_to_pdf(input_path):
    subprocess.run(["pdflatex", input_path])

def pdf_to_png(input_path):
    subprocess.run(["convert", "-density", "150", input_path, input_path.replace("pdf", "png")])



files = [f for f in os.listdir('.') if ".csv" in f]
for file in files:
    print(file)
    csv_to_tikz(file, file.replace("csv", "tex"))
    tikz_to_pdf(file.replace("csv", "tex"))
    pdf_to_png(file.replace("csv", "pdf"))
