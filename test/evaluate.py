from __future__ import print_function
import MySQLdb
import warnings
import re
import _mysql_exceptions

DEBUG = False


def prepare_query(q, timeout):
    """
    Prepare query by reformating and adding a time constraint

    :param q: query to prepare
    :param timeout: timeout value
    :return: prepared query
    """
    q = q.replace(' (', '(').replace('< =', '<=').replace('> =', '>=').replace('< >', '<>').replace('! =', '!=')
    q = re.sub('SELECT ', 'SELECT /*+ MAX_EXECUTION_TIME(' + str(timeout) + ') */ ', q, 1)
    q = re.sub('select ', 'SELECT /*+ MAX_EXECUTION_TIME(' + str(timeout) + ') */ ', q, 1)
    return q


def run_query(q, timeout, dbconn, selected_fields=None):
    """
    Run a given query and additionally return result as list of dicts.
    If selected_fields is not None, only the columns with the given name will be returned

    :param q: query
    :param timeout: timeout for the query
    :param dbconn: connection to database
    :param selected_fields: list of fields to return (if None, all fields will be returned)
    :return: answer object {row_count, tuples, cols, fields, rows, status}
    """
    q = prepare_query(q, timeout)
    cu = dbconn.cursor()
    cu.execute(q)
    result = {'row_count': cu.rowcount, 'tuples': cu.fetchall()}

    if cu.description:
        result['cols'] = [col[0] for col in cu.description]
        result['fields'] = set(result['cols'])
        result['rows'] = [
            {k: v for (k, v) in zip(result['cols'], row) if selected_fields is None or k in selected_fields} for row in
            result['tuples']]
        result['status'] = True
    else:
        result['status'] = False

    cu.close()
    return result


def compare(query, gold, nl, dbconn):
    """
    Compute the accuracy of a given query

    :param gold: gold standard sql query to compare query to
    :param query: sql query to test
    :param nl: natural language query the sql query represents
    :param dbconn: database connection
    :return: evaluation result tuple (correct, gold, query)
    """

    # Output buffer
    sb = query.replace(' (', '(').replace('< =', '<=').replace('> =', '>=').replace('< >', '<>').replace('! =', '!=')

    # Run gold query
    try:
        res_gold = run_query(gold, 10000, dbconn)
    except (_mysql_exceptions.ProgrammingError, _mysql_exceptions.InterfaceError, _mysql_exceptions.OperationalError,
            _mysql_exceptions.NotSupportedError) as e:
        if DEBUG:
            print(type(e))
        sb = '(INCORRECT) [Gold Query failed] ' + sb
        print(sb)
        return False, gold, query

    # Ran gold query successfully?
    if res_gold['status']:
        # Run predicted query (query to test)
        try:
            res_query = run_query(query, 10000, dbconn)  # , selected_fields=res_gold["fields"])
        except (
        _mysql_exceptions.ProgrammingError, _mysql_exceptions.InterfaceError, _mysql_exceptions.OperationalError,
        _mysql_exceptions.NotSupportedError) as e:
            if DEBUG:
                print(type(e))
            sb = '(INCORRECT) [Query failed] ' + sb
            print(sb)
            return False, gold, query

        # Print some debug information
        if DEBUG:
            print("Results query: ", res_query['rows'], res_query['tuples'])
            print("Results gold: ", res_gold['rows'], res_gold['tuples'])

        # Generate sets of resulting lines (string-represented, order/attributes not changed)
        # of gold and query for comparison
        res_query_tuple_set = set(str(t) for t in res_query['tuples'])
        res_gold_tuple_set = set(str(t) for t in res_gold['tuples'])

        # Are the lines returned entirely correct?
        if len(res_query_tuple_set) == len(res_gold_tuple_set) and res_query_tuple_set == res_gold_tuple_set:
            sb = '(CORRECT) [EXACT LINES] ' + sb
            print(sb)
            return True, gold, query
        # If not, do the attributes returned cover all requested attributes
        # and does the result contain the expected entries?
        else:
            res_query_dict_set = set(str(d) for d in res_query['rows'])
            res_gold_tuple_set = set(str(d) for d in res_gold['rows'])

            # Check amount of distinct rows returned
            if len(res_query_dict_set) != len(res_gold_tuple_set):
                sb = '(INCORRECT) [AMOUNT RETURNED] ' + sb
                print(sb)
                return False, gold, query
            elif (len(res_query_dict_set) == len(res_gold_tuple_set) and len(res_gold_tuple_set) == 0):
                sb = '(INCORRECT) [BOTH ZERO RETURNED] ' + sb
                print(sb)
                return False, gold, query
            else:
                goldcolnames = res_gold['rows'][0].keys()
                goldcols = []
                for goldcolname in goldcolnames:
                    goldcols.append(set(map(lambda x: x[goldcolname], res_gold['rows'])))

                querycolnames = res_query['rows'][0].keys()
                querycols = []
                for querycolname in querycolnames:
                    querycols.append(set(map(lambda x: x[querycolname], res_query['rows'])))

                alwaystrue = False
                for goldcol in goldcols:
                    for querycol in querycols:
                        if goldcol == querycol:
                            alwaystrue = True

                if alwaystrue:
                    sb = '(CORRECT) [ATTRIBUTE SUBSET] ' + sb
                    print(sb)
                    return True, gold, query

            # Compare returned entries
            if res_query_dict_set == res_gold_tuple_set:
                sb = '(CORRECT) [ATTRIBUTE SUBSET] ' + sb
                print(sb)
                return True, gold, query

    # Something went wrong
    sb = '(INCORRECT) ' + sb
    print(sb)
    return False, gold, query


def get_connection(host, user, passwd, db_name):
    """
    Get a database connection with the given parameters

    :param host: hostname of the database
    :param user: username for database connection
    :param passwd: password for database connection
    :param db_name: database name to connect to
    :return: db connection
    """
    # Database connection
    dbconn = MySQLdb.connect(
        host=host,
        user=user,
        passwd=passwd,
        db=db_name
    )
    warnings.filterwarnings('ignore', category=MySQLdb.Warning)
    return dbconn


def compare_queries(queries, gold_queries, nl_representations, dbconn):
    """
    Compare the given lists of queries

    :param queries: queries to compare
    :param gold_queries: gold standard queries
    :param nl_representations: nl sentences the queries represent
    :param dbconn: database connection
    :return: list of result-triples (correctness, gold, query)
    """
    return [compare(query, gold, nl, dbconn) for query, gold, nl in zip(queries, gold_queries, nl_representations)]


if __name__ == '__main__':
    dbconn = get_connection(
        host="localhost",
        user="root",
        passwd="root123",
        db_name="patients"
    )

    queries = ["SELECT * FROM patients WHERE age=50;"]
    gold_queries = ["SELECT length_of_stay FROM patients WHERE age=50;"]
    nl_representations = ["Give me the lengths of stays for 50 year old patients"]

    results = compare_queries(queries, gold_queries, nl_representations, dbconn)
    count_correct = sum(c for c, _, _ in results)
    print("Correct: ", count_correct, "/", len(results))

    dbconn.close()
