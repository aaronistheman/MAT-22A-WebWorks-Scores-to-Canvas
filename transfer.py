#!/usr/bin/python3
#
# Transfer WebWorks scores from <ww totals csv> to <canvas input csv> and
# puts the resulting csv file into <canvas output csv>. Ignores the scores
# of students who have dropped the class (i.e. whose names are not in
# <canvas input csv>.
#
# Usage:
# python3 <this script> <ww totals csv> <canvas input csv> <canvas output csv>
# 
# Example usage:
# python3 ./transfer.py MAT22A-Puckett-Spring-2019_totals.csv 2019-06-11T1036_Grades-MAT_022A_002_SQ_2019.csv output.csv

import sys

def load_ww_scores(ww_totals_csv):
    # Ignore the first HEADER_LENGTH lines, as these contain metadata/headers.
    # After this, @line will contain the first line containing student data.
    HEADER_LENGTH = 8
    line_num = 1
    line = ww_totals_csv.readline()
    while line_num < 9:
        line_num += 1
        line = ww_totals_csv.readline()

    # Read in all of the students' scores.
    NUM_WEB_WORK_ASSIGNMENTS = 10  # WebWorks 0 through 9.
    ww_scores = {}  # map: student_id -> list of 10 WebWork scores
    while not line == '':  # until EOF
        line_pieces = line.split(',')
        student_id = line_pieces[0].strip()
        student_scores = line_pieces[6:(6+NUM_WEB_WORK_ASSIGNMENTS)]  # this student's WebWork scores
        ww_scores[student_id] = list(map(float, student_scores))  # convert to numbers

        # Read the next line.
        line = ww_totals_csv.readline()

    # for id in ww_scores:
    #     print("ww_scores[{}] = {}".format(id, ww_scores[id]))
    return ww_scores

def transfer_ww_scores(ww_scores, canvas_input_csv, canvas_output_csv):
    HEADER_LENGTH = 3
    # Read in the first HEADER_LENGTH lines, without making any changes,
    # since these lines are metadata/header lines.
    # After this loop, @line will contain the first line with student data.
    line_num = 1
    line = canvas_input_csv.readline()
    while line_num < HEADER_LENGTH + 1:
        canvas_output_csv.write(line)
        line_num += 1
        line = canvas_input_csv.readline()

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
        WW_START_INDEX = 7
        for (ww_num,score) in enumerate(ww_scores_for_this_student):
            line_pieces[WW_START_INDEX + ww_num] = str(score)

        # Recombine line pices into a line.
        updated_line = ','.join(line_pieces)
        # Write current line and get next line.
        canvas_output_csv.write(updated_line)
        line = canvas_input_csv.readline()

NUM_ARGS = 4
if __name__ == "__main__":  # begin execution here
    if len(sys.argv) != NUM_ARGS:
        print("Usage: {} <ww totals csv> <canvas input csv> <canvas output csv>".format(
                sys.argv[0]),
                file=sys.stderr)
        exit(-1)

    ww_totals_csv = open(sys.argv[1], "r")
    canvas_input_csv = open(sys.argv[2], "r")
    canvas_output_csv = open(sys.argv[3], "w")

    ww_scores = load_ww_scores(ww_totals_csv)
    transfer_ww_scores(ww_scores, canvas_input_csv, canvas_output_csv)

    ww_totals_csv.close()
    canvas_input_csv.close()
    canvas_output_csv.close()