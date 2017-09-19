def score_evaluator(file_path):

    with open(file_path, 'r') as File:
        score_holder = 0.0
        for each_line in File:
            # print each_line.split(' ')[1].strip('\n')
            score_holder += float(each_line.split(' ')[1].strip('\n'))
            # raw_input()
        # print score_holder
        return score_holder

# score =

hub_score = score_evaluator("hub.txt")
# auth_score = score_evaluator(path_to_auth)
print('Total hub score:', hub_score)