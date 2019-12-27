Q = {}

Q[23] = "python3 synthesizer.py -i0 benchmarks/preprocessed_input_tables/Q23-deaths-barcelona.csv -o benchmarks/real_output_tables/Q23-deaths-barcelona_out.csv -l 3 -d 4 -t dsl.tyrell -m  1"


Q[30] = "python3 synthesizer.py -i0 benchmarks/preprocessed_input_tables/Q30-wine-input.csv -o benchmarks/noisy_output_tables/Q30-output-nn-wine.csv -l 4 -d 5 -t dsl.tyrell -m 90"
Q[22] = "python3 synthesizer.py -i0 benchmarks/preprocessed_input_tables/Q22-immigrants_by_nationality.csv -o benchmarks/noisy_output_tables/Q22-immigrants_by_nationality_nn-out.csv -l 3 -d 4 -t dsl.tyrell -m 6695"
Q[15] = "python3 synthesizer.py -i0 benchmarks/preprocessed_input_tables/Q15-input-bank.csv -o benchmarks/noisy_output_tables/Q15-output-nn-bank.csv -l 2 -d 3 -t dsl.tyrell -m 1330"
Q[11] = "python3 synthesizer.py -i0 benchmarks/preprocessed_input_tables/Q11-input-titanic.csv -o benchmarks/noisy_output_tables/Q11-output-nn-titanic.csv -l 2 -d 3 -t dsl.tyrell -m 285"
Q[10] = "python3 synthesizer.py -i0 benchmarks/preprocessed_input_tables/Q10-input-titanic.csv -o benchmarks/noisy_output_tables/Q10-output-nn-titanic.csv -l 2 -d 3 -t dsl.tyrell -m 445"
Q[9] = "python3 synthesizer.py -i0 benchmarks/preprocessed_input_tables/Q9-input-titanic.csv -o benchmarks/noisy_output_tables/Q9-output-nn-titanic.csv -l 2 -d 3 -t dsl.tyrell -m 270"
Q[8] = "python3 synthesizer.py -i0 benchmarks/preprocessed_input_tables/Q8-input-avocado.csv -o benchmarks/noisy_output_tables/Q8-output-nn-avocado.csv -l 3 -d 4 -t dsl.tyrell -m 1330000000"
Q[5] = "python3 synthesizer.py -i0 benchmarks/preprocessed_input_tables/grades.csv -o benchmarks/real_output_tables/grades_nn-out.csv -l 3 -d 4 -t dsl.tyrell -m 225"