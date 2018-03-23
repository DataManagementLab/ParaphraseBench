*Introducing ParaphraseBench -- a benchmark to evaluate the robustness of NLIDBs.*

Current benchmarks like the GeoQuery benchmark to not explicitly test different linguistic variations which is important to understand the robustness of an NLIDB. For testing different linguistic variants in a principled manner, we therefore curated a new benchmark as part of our paper on DBPal that covers different linguistic variations for the user NL input and maps it to an expected SQL output.

The schema of our new benchmark models a medical database which contains only one table comprises of hospital’s patients attributes such as name, age, and disease. In total, the benchmark consists of 290 pairs of NL-SQL queries. The queries are grouped into one of the following categories depending on the linguistic variation that is used in the NL query: naıve, syntactic paraphrases, morphological paraphrases, and lexical paraphrases as well as a set of queries with missing information.

While the NL queries in the naıve category represent a direct translation of their SQL counterpart, the other categories are more challenging: syntactic paraphrases emphasize structural variances, lexical paraphrases pose challenges such as alternative phrases, semantic paraphrases use semantic similarities such as synonyms, morphological paraphrases add affixes, apply stemming, etc., and the NL queries with missing information stress implicit and incomplete NL queries.

In the following, we show an example query for each of these categories in our benchmark:

* Naıve: ”What is the average length of stay of patients where age is 80?”
* Syntactic: ”Where age is 80, what is the average length of stay of patients?”
* Morphological: ”What is the averaged length of stay of patients where age equaled 80?”
* Lexical: ”What is the mean length of stay of patients where age is 80 years?”
* Semantic: ”What is the average length of stay of patients older than 80?”
* Missing Information: ”What is the average stay of patients who are 80?”

Please cite the following paper when using this benchmark:

> TBA

Read about [how to use the benchmark](usage.md).