import spacy
from data_ingestion import settings
import os
from .rel_pipe import make_relation_extractor, score_relations
from .rel_model import create_relation_model, create_classification_layer, create_instances, create_tensors


class NerRelationExtractor:
    def __init__(self, text):
        self.relation_dict = {'PATIENTGENDER': ['PATIENTONSETAGE', 'PATIENTSEX'],
                              'PATIENTCOUNTRY': ['PATIENTONSETAGE', 'PRIMARYSOURCECOUNTRY'],
                              'PATIENTSUSPECT': ['PATIENTONSETAGE', 'SUSPECTPRODUCT'],
                              'PATIENTCONCOMITANT': ['PATIENTONSETAGE', 'CONCOMITANTPRODUCT'],
                              'SUSPECTREACTION': ['SUSPECTPRODUCT', 'PRIMARYSOURCEREACTION'],
                              'SUSPECTDOSAGETEXT': ['SUSPECTPRODUCT', 'DRUGDOSAGETEXT'],
                              'SUSPECTDRUGINDICATION': ['SUSPECTPRODUCT', 'DRUGINDICATION'],
                              'SUSPECTDRUGRESULT': ['SUSPECTPRODUCT', 'DRUGRESULT'],
                              'CONCOMITANTDOSAGETEXT': ['CONCOMITANTPRODUCT', 'DRUGDOSAGETEXT'],
                              'CONCOMITANTDRUGINDICATION': ['CONCOMITANTPRODUCT', 'DRUGINDICATION'],
                              'CONCOMITANTDRUGRESULT': ['CONCOMITANTPRODUCT', 'DRUGRESULT'],
                              'REACTIONTEST': ['PRIMARYSOURCEREACTION', 'TESTNAME'],
                              'REACTIONTESTRESULT': ['TESTNAME', 'TESTRESULT'],
                              'TESTLOWRANGE': ['TESTNAME', 'LOWTESTRANGE'],
                              'TESTHIGHRANGE': ['TESTNAME', 'HIGHTESTRANGE']
                              }
        self.text = text

        self.nlp = spacy.load(os.path.join(settings.STATICFILES_LOCAL,
                                           "data/models/output/ner/training_gpu_ner_05-12-2023/model-best"))

        self.nlp.add_pipe('sentencizer')
        self.nlp2 = spacy.load(os.path.join(settings.STATICFILES_LOCAL,
                                            "data/models/output/relation_extractor/training_bk_05-12-2023_GPU_binds_max_limit_50/model-best"))


    def get_ner_relations(self):

        try:
            doc = self.nlp(self.text)
            span = []
            for e in doc.ents:
                span.append((e.start, e.text, e.label_))
            print(span)
            print(len(span))
            for name, proc in self.nlp2.pipeline:
                doc = proc(doc)
            # Here, we split the paragraph into sentences and apply the relation extraction for each pair of entities found in each sentence.
            predicted_relations = []
            for value, rel_dict in doc._.rel.items():
                for sent in doc.sents:

                    for e in sent.ents:

                        for b in sent.ents:

                            if e.start == value[0] and b.start == value[1]:
                                for rel_val in rel_dict:
                                    if rel_dict[rel_val] > 0.25:
                                        # print("*******************************************************")
                                        temp_dict = {'predicted_relation': rel_val, 'accuracy': rel_dict[rel_val],
                                                     'entities': [{e.label_: e.text}, {b.label_: b.text}]}
                                        predicted_relations.append(temp_dict)
                                        # print(rel_val, rel_dict[rel_val])
                                        # print(f" entities: {e.label_, e.text, b.label_, b.text} --> predicted relation: {rel_dict}")

            # print(predicted_relations)
            # predicted_relations=[{'predicted_relation': 'PATIENTCOUNTRY', 'accuracy': 0.7638525, 'entities': [{'PATIENTONSETAGE': '23-year-old'}, {'PRIMARYSOURCECOUNTRY': 'Serbia'}]}, {'predicted_relation': 'PATIENTGENDER', 'accuracy': 0.7749691, 'entities': [{'PATIENTONSETAGE': '23-year-old'}, {'PATIENTSEX': 'female'}]}, {'predicted_relation': 'PATIENTSUSPECT', 'accuracy': 0.7270575, 'entities': [{'PATIENTONSETAGE': '23-year-old'}, {'SUSPECTPRODUCT': 'lomustine'}]}, {'predicted_relation': 'PATIENTSUSPECT', 'accuracy': 0.7269075, 'entities': [{'PATIENTONSETAGE': '23-year-old'}, {'SUSPECTPRODUCT': 'vincristine'}]}, {'predicted_relation': 'PATIENTSUSPECT', 'accuracy': 0.5921519, 'entities': [{'PATIENTONSETAGE': '23-year-old'}, {'SUSPECTPRODUCT': 'cisplatin'}]}, {'predicted_relation': 'REACTIONTESTRESULT', 'accuracy': 0.50642467, 'entities': [{'TESTNAME': 'Clinical examination'}, {'TESTRESULT': 'presence of granulations and blood in the left external auditory canal'}]}, {'predicted_relation': 'REACTIONTESTRESULT', 'accuracy': 0.4062819, 'entities': [{'TESTNAME': 'Digital Subtraction Angiography'}, {'TESTRESULT': 'hyper-vascular tumor in the projection of the left temporal bone'}]}, {'predicted_relation': 'REACTIONTESTRESULT', 'accuracy': 0.5372175, 'entities': [{'TESTNAME': 'Chest CT scan'}, {'TESTRESULT': 'numerous, predominantly calcified, micro- and macronodular changes in the lungs'}]}, {'predicted_relation': 'REACTIONTESTRESULT', 'accuracy': 0.53125644, 'entities': [{'TESTNAME': 'Ultrasound examination'}, {'TESTRESULT': 'normal'}]},{'predicted_relation': 'SUSPECTREACTION', 'accuracy': 0.7270575, 'entities': [{'SUSPECTPRODUCT': 'lomustine'},{'PRIMARYSOURCEREACTION': 'fever'}]}, {'predicted_relation': 'SUSPECTREACTION', 'accuracy': 0.7269075, 'entities': [{'SUSPECTPRODUCT': 'vincristine'},{'PRIMARYSOURCEREACTION': 'diarrhea'}]}, {'predicted_relation': 'SUSPECTREACTION', 'accuracy': 0.5921519, 'entities': [{'SUSPECTPRODUCT': 'cisplatin'},{'PRIMARYSOURCEREACTION': 'psoriasis'}]}]
            data = {"error": 0,'relations': predicted_relations}
        except Exception as e:
            data = {"error": 1, "description": e}
            print(e)
        return data


# current_file = open('input_data/current_file1.txt', 'r', encoding="utf8").read()
# result = NerRelationExtractor(current_file).get_ner_relations()
# print(result)
