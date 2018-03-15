---
title: Usage
---

## Usage

[Back to overview](. "Back to overview")

### The database -- scheme and data

We provide a sql file containing a database scheme and a dump of entries as well as a machine-readable version of the scheme together with some meta information in json format. Both can be found in the `db/` folder.

The database only contains one relation named *patients* with the following structure.

    CREATE TABLE `patients` (
		`id` mediumint(8) unsigned NOT NULL auto_increment,
	  	`first_name` varchar(255) default NULL,
	  	`last_name` varchar(255) default NULL,
	  	`diagnosis` varchar(255) default NULL,
	  	`length_of_stay` mediumint default NULL,
	  	`age` mediumint default NULL,
	  	`gender` varchar(255) default NULL,
	  	PRIMARY KEY (`id`)
	) AUTO_INCREMENT=1;

To use the benchmark, simply import the dump into a relational database.


### Test

The actual test consists of a range of natural language queries with associated sql queries. They can be used to test the coverage and the robustness against variations of natural language of your NLIDB. All tests can be found in the `test/` folder.

The test cases consist of 57 different queries in 6 variations each and the associated sql queries. The variations of the naive query are: *Syntactic, Morphological, Lexical, Semantic, Missing Information*. Each variant can be found in a file called `<variant>_source.txt`, the corresponding sql queries are located in the corresponding lines of the file `patients_test.sql`.

To test your NLIDB run the results of your system against the database provided above and compare the results to those of the gold standard. We propose the following metric: A query is counted as correctly translated when it produces the exact result (attributes and rows returned) or at least the expected rows and a superset of the expected attributes/columns.

[Back to overview](. "Back to overview")