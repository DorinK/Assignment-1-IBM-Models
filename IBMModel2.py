from nltk.stem.snowball import EnglishStemmer, FrenchStemmer
from collections import defaultdict
import time
import os
import sys

FRENCH_FILE = str(sys.argv[1])
ENGLISH_FILE = str(sys.argv[2])


class IBMModel2:

    """
    This class implements IBM Model 2, an algorithm for word-alignment given a sentence-aligned corpus.
    """

    def __init__(self, trans_table=None):

        print("Starting initialization of Model 2")
        start_time = time.time()

        self.e_stemmer = EnglishStemmer()
        self.f_stemmer = FrenchStemmer()

        self.corpus = self.load_data()
        self.q = self.initialize_alignments_probability()
        self.french_vocab, self.english_vocab = self.create_vocabularies()
        self.fr_word_to_idx, self.en_word_to_idx = self.create_mapping_to_indexes()
        self.convert_to_idx()

        if trans_table is not None:
            self.t = trans_table
        else:
            self.t = self.initialize_translation_probability()

        print("Finished initialization in {} minutes\n".format((time.time() - start_time) / 60))

    def load_data(self):

        with open(FRENCH_FILE, 'r', encoding='utf-8') as f:
            f_data = f.readlines()

        with open(ENGLISH_FILE, 'r', encoding='utf-8') as e:
            e_data = e.readlines()

        return [[sentence.strip().split() for sentence in pair] for pair in zip(f_data, e_data)]

    def initialize_alignments_probability(self):

        q = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 0.0))))

        sent_lengths = set()
        for (f_sent, e_sent) in self.corpus:

            l = len(f_sent)
            m = len(e_sent)

            if (l, m) not in sent_lengths:
                sent_lengths.add((l, m))
                initial_prob = 1 / (l + 1)
                for i in range(0, l + 1):
                    for j in range(m):
                        q[i][j][l][m] = initial_prob

        return q

    def create_vocabularies(self):

        unique_french, unique_english = ["NULL"], []

        for (f_sent, e_sent) in self.corpus:

            for i in range(len(f_sent)):
                stem = self.f_stemmer.stem(f_sent[i].lower())
                if f_sent[i] != stem:
                    f_sent[i] = stem
                if f_sent[i] not in unique_french:
                    unique_french.append(f_sent[i])

            f_sent.append("NULL")

            for i in range(len(e_sent)):
                stem = self.e_stemmer.stem(e_sent[i].lower())
                if e_sent[i] != stem:
                    e_sent[i] = stem
                if e_sent[i] not in unique_english:
                    unique_english.append(e_sent[i])

        return unique_french, unique_english

    def create_mapping_to_indexes(self):

        fr_word_to_idx = dict(zip(self.french_vocab, range(len(self.french_vocab))))
        en_word_to_idx = dict(zip(self.english_vocab, range(len(self.english_vocab))))

        return fr_word_to_idx, en_word_to_idx

    def convert_to_idx(self):

        self.corpus = [
            ([self.fr_word_to_idx[f_word] for f_word in f_sent], [self.en_word_to_idx[e_word] for e_word in e_sent]) for
            (f_sent, e_sent) in self.corpus]

        self.french_vocab = [self.fr_word_to_idx[f_word] for f_word in self.french_vocab]
        self.english_vocab = [self.en_word_to_idx[e_word] for e_word in self.english_vocab]

    def initialize_translation_probability(self):

        t = defaultdict(lambda: defaultdict(lambda: (1 / len(self.french_vocab))))
        return t

    def train_model(self):

        print("Start Training")

        for epoch in range(8):

            print("Starting epoch no. {}".format(epoch + 1))
            start_time = time.time()

            count_e_given_f = defaultdict(lambda: defaultdict(lambda: 0.0))
            total = defaultdict(lambda: 0.0)
            count_q_i_j_l_m = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 0.0))))
            total_q_j_l_m = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 0.0)))

            for idx, (foreign_sent, english_sent) in enumerate(self.corpus):

                l = len(foreign_sent)  # with null
                m = len(english_sent)

                sentence_total = defaultdict(lambda: 0.0)

                for j, e_word in enumerate(english_sent):
                    for i, f_word in enumerate(foreign_sent):
                        sentence_total[e_word] += self.t[e_word][f_word] * self.q[i][j][l - 1][m]

                for j, e_word in enumerate(english_sent):
                    for i, f_word in enumerate(foreign_sent):
                        result = (self.t[e_word][f_word] * self.q[i][j][l - 1][m]) / sentence_total[e_word]

                        count_e_given_f[e_word][f_word] += result
                        total[f_word] += result
                        count_q_i_j_l_m[i][j][l][m] += result
                        total_q_j_l_m[j][l][m] += result

            for e_word, f_words in count_e_given_f.items():
                for f_word in f_words:
                    self.t[e_word][f_word] = count_e_given_f[e_word][f_word] / total[f_word]

            for i, j_s in count_q_i_j_l_m.items():
                for j, f_sent_lengths in j_s.items():
                    for l, e_sent_lengths in f_sent_lengths.items():
                        for m in e_sent_lengths:
                            self.q[i][j][l][m] = count_q_i_j_l_m[i][j][l][m] / total_q_j_l_m[j][l][m]

            print("Finished epoch no. {} in {} minutes".format(epoch + 1, (time.time() - start_time) / 60))

    def produce_alignments_file(self, file_name):

        if os.path.exists(file_name):
            os.remove(file_name)
        f = open(file_name, "a+")

        for (f_sent, e_sent) in self.corpus:
            sent_alignments = []

            l = len(f_sent)
            m = len(e_sent)

            for j, e_word in enumerate(e_sent):
                best_prob = self.t[e_word][0] * self.q[0][j][l][m]
                alignment_idx = None
                for i, f_word in enumerate(f_sent[:-1]):
                    prob = (self.t[e_word][f_word] * self.q[i][j][l][m])
                    if prob >= best_prob:
                        best_prob = prob
                        alignment_idx = i

                if alignment_idx is not None:
                    sent_alignments.append((alignment_idx, j))

            sent_alignments.sort(key=lambda tup: tup[0])

            for (f_idx, e_idx) in sent_alignments:
                f.write("{0}-{1} ".format(f_idx, e_idx))

            f.write("\n")

        f.close()


if __name__ == "__main__":
    model2 = IBMModel2()
    model2.train_model()
    model2.produce_alignments_file("./Model2_alignmentsFile.txt")
