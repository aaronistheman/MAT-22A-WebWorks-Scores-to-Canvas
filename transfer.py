#!/usr/bin/python3
#
# Transfer WebWorks scores from @ww_totals_csv to @canvas_input_csv and
# puts the resulting csv file into @canvas_output_csv. Ignores the scores
# of students who have dropped the class (i.e. whose names are not in
# @canvas_input_csv).
#
# Usage:
# python3 this_script ww_totals_csv num_ww_assignments canvas_input_csv ww_scores_start_column canvas_output_csv
#   where:
#       @ww_totals_csv: the WebWorks scores, downloaded from the Totals section.
#       @num_ww_assignments: the number of WebWorks assignments.
#       @canvas_input_csv: the Canvas scores, exported from the gradebook as a csv file.
#                          NOTE: assumes the WebWorks columns are all contiguous.
#       @ww_scores_start_column: the column index of the first WebWorks assignment in @canvas_input_csv
#                                (starts at index #0)
#       @canvas_output_csv: name of the output csv file. This can be imported into the Canvas gradebook.
# 
# Example usage:
# python3 ./transfer.py MAT22A-Puckett-Spring-2019_totals.csv 10 2019-06-11T1036_Grades-MAT_022A_002_SQ_2019.csv 6 output.csv

import sys

def load_ww_scores(ww_totals_csv, num_ww_assignments):
    # Ignore the first HEADER_LENGTH lines, as these contain metadata/headers.
    # After this, @line will contain the first line containing student data.
    HEADER_LENGTH = 8
    line_num = 1
    line = ww_totals_csv.readline()
    while line_num < 9:
        line_num += 1
        line = ww_totals_csv.readline()

    # Read in all of the students' scores.
    ww_scores = {}  # map: student_id -> list of 10 WebWork scores
    while not line == '':  # until EOF
        line_pieces = line.split(',')
        student_id = line_pieces[0].strip()

        # Assuming the WebWorks csv file was downloaded from
        # the Totals section -- and the format hasn't changed --
        # the scores should start at the 7th field.
        student_scores = line_pieces[6:(6+num_ww_assignments)]  # this student's WebWork scores

        ww_scores[student_id] = list(map(float, student_scores))  # convert to numbers

        # Read the next line.
        line = ww_totals_csv.readline()

    return ww_scores

def transfer_ww_scores(ww_scores, canvas_input_csv, canvas_output_csv, ww_scores_start_column):
    # Read in the first HEADER_LENGTH lines, without making any changes,
    # since these lines are metadata/header lines.
    # After this loop, @line will contain the first line with student data.
    HEADER_LENGTH = 3
    line_num = 1
    line = canvas_input_csv.readline()
    while line_num < HEADER_LENGTH + 1:
        canvas_output_csv.write(line)
        line_num += 1
        line = canvas_input_csv.readline()

    overwrote_previous_value = False

    # Read in each student's row of Canvas scores and update them.
    while not line == '':
        # Since I'm using the comma as delimiter, the name field
        # awkwardly becomes two fields instead of one.
        line_pieces = line.split(',')
        STUDENT_ID_INDEX = 3
        student_id = line_pieces[STUDENT_ID_INDEX]
        if student_id == None or student_id == "":  # if hit last line in the file (the "test student")
            canvas_output_csv.write(line)  # copy it as-is
            break

        # Assign each webwork score.
        ww_scores_for_this_student = ww_scores[student_id]
        ww_start_index = ww_scores_start_column + 1  # the name column becomes two columns,
                                                     # due to use of "," as delimeter
        for (ww_num,score) in enumerate(ww_scores_for_this_student):
            if not overwrote_previous_value and line_pieces[ww_start_index + ww_num] != "":
                print("Warning: overwrote at least one previous value in the gradebook.",
                    file=sys.stderr)
                overwrote_previous_value = True  # don't flood standard output with these warnings
            line_pieces[ww_start_index + ww_num] = str(score)

        # Recombine line pices into a line.
        updated_line = ','.join(line_pieces)
        # Write current line and get next line.
        canvas_output_csv.write(updated_line)
        line = canvas_input_csv.readline()

def print_usage_and_die():
    print("Usage: {} ww_totals_csv num_ww_assignments canvas_input_csv ww_scores_start_column canvas_output_csv".format(
            sys.argv[0]),
            file=sys.stderr)
    exit(-1)

if __name__ == "__main__":  # begin execution here
    NUM_ARGS = 6
    if len(sys.argv) != NUM_ARGS:
        print_usage_and_die()

    if sys.argv[3] == sys.argv[5]:
        print("Error: cannot give the same Canvas csv filename for both input and output",
            file=sys.stderr)
        print_usage_and_die()

    try:
        num_ww_assignments = int(sys.argv[2])
        ww_scores_start_column = int(sys.argv[4])
    except:
        print("Error: num_ww_assignments and ww_scores_start_column must be integers.", file=sys.stderr)
        print_usage_and_die()
    try:
        ww_totals_csv = open(sys.argv[1], "r")
        canvas_input_csv = open(sys.argv[3], "r")
        canvas_output_csv = open(sys.argv[5], "w")
    except:
        print("Error: failed to open one of {}, {}, or {}".format(
            sys.argv[1], sys.argv[3], sys.argv[5]), file=sys.stderr)
        print_usage_and_die()

    ww_scores = load_ww_scores(ww_totals_csv, num_ww_assignments)
    transfer_ww_scores(ww_scores, canvas_input_csv, canvas_output_csv, ww_scores_start_column)

    ww_totals_csv.close()
    canvas_input_csv.close()
    canvas_output_csv.close()