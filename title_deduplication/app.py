# ==================================================================================================================
# ==================================================================================================================
import os
from fuzzywuzzy import fuzz
from utils import acronyms_list_form, job_titles_list_form, seniority_list_form, \
                  replace_acronyms, seniority_detection, similarity_factor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

true_job_titles = os.path.join(BASE_DIR, 'fixtures', 'true-job-titles.xlsx')
seniority_descriptors = os.path.join(BASE_DIR, 'fixtures', 'seniority-descriptors.xlsx')
acronyms_job_title = os.path.join(BASE_DIR, 'fixtures', 'acronyms-job-title.xlsx')

    # read acronyms-job-title.xlsx, true-job-titles.xlsx and read seniority-descriptors.xlsx
acronyms_job_title_list = acronyms_list_form(acronyms_job_title)
true_job_titles_list = job_titles_list_form(true_job_titles, acronyms_job_title_list)
seniority_descriptors_list = seniority_list_form(seniority_descriptors)
seniority_descriptors_grouped_list = {}
for sen in seniority_descriptors_list:
    len_sen = len(sen.split(" "))
    try:
        seniority_descriptors_grouped_list[len_sen].append(sen)
    except:
        seniority_descriptors_grouped_list[len_sen] = [sen]
# ==================================================================================================================
# ==================================================================================================================



from flask import Flask, render_template, request, jsonify
from flask_esclient import ESClient

app = Flask(__name__)

app.config['ELASTICSEARCH_URL'] = 'http://localhost:9200/'
esclient = ESClient(app)


@app.route('/')
def main():
    return render_template('base.html')


@app.route('/search', methods=['GET'])
def search():
    input_job_title = seniority_detection(request.args.get('job_title'), seniority_descriptors_grouped_list, acronyms_job_title_list)
    results_true_job_titles = []

    for job_title in true_job_titles_list:

        input_job_title_without_seniority = input_job_title[0]
        for sen in input_job_title[1]:
            if sen not in job_title.keys()[0]:
                input_job_title_without_seniority = input_job_title_without_seniority.replace(sen.lower(), '')
        input_job_title_without_seniority = input_job_title_without_seniority.replace(" "*2, " ").strip().lower()

        similarity_factor_value = max(similarity_factor(input_job_title[0], job_title.values()[0]),
                                      similarity_factor(input_job_title_without_seniority, job_title.values()[0])
                                      )
        results_true_job_titles.append({
                                        'Similarity factor': similarity_factor_value,
                                        'Canonical job title': job_title.keys()[0],
                                        'Seniority': input_job_title[1]
                                        })

    results_true_job_titles = sorted(results_true_job_titles, key=lambda k: k['Similarity factor'], reverse=True)[:10]

    need_change_list = False
    for num, item in enumerate(results_true_job_titles):
        if num == 0 and item['Canonical job title'].lower() in input_job_title[0] \
                    and fuzz.partial_ratio(item['Canonical job title'].lower(), input_job_title[0]) == 100 \
                    and input_job_title[0][:input_job_title[0].find(item['Canonical job title'].lower())-1].capitalize() in item['Seniority']:
            break
        elif item['Canonical job title'].lower() in input_job_title[0] \
                    and fuzz.partial_ratio(item['Canonical job title'].lower(), input_job_title[0]) == 100 \
                    and input_job_title[0][:input_job_title[0].find(item['Canonical job title'].lower())-1].capitalize() not in item['Seniority']:
            need_change_list = True
            short_input_job_title = input_job_title[0][input_job_title[0].find(item['Canonical job title'].lower()):]
            break

    if need_change_list:
        for item in results_true_job_titles:
            item['Similarity factor'] = (item['Similarity factor'] + similarity_factor(short_input_job_title, item['Canonical job title'].lower()))/2.
        results_true_job_titles = sorted(results_true_job_titles, key=lambda k: k['Similarity factor'], reverse=True)

    output_results = []
    for item in results_true_job_titles[:3]:
        seniorities = list(filter(lambda x: x not in item['Canonical job title'] and\
                                            len(filter(lambda y: y in replace_acronyms(item['Canonical job title'],
                                                                                       acronyms_job_title_list),
                                                       x.split())) == 0,
                                  item['Seniority']))
        if item['Seniority'] == [] or seniorities == []:
            output_results.append('({0}) {1}'.format(round(item['Similarity factor'], 1), item['Canonical job title']))
        else:
            output_results.append('({0}) {1}, {2}'.format(round(item['Similarity factor'], 1),
                                                          item['Canonical job title'], ', '.join(seniorities)))

    return jsonify(true_job_title=output_results)


if __name__ == '__main__':
    app.run()

