from connect import ElasticSearch_connect, Mysql_connect

es_connect = ElasticSearch_connect()
mysql_connect = Mysql_connect()

indices = es_connect.get_index_list()
for index in indices:
    if index not in mysql_connect.get_tables_list():
        fields = es_connect.get_index_fields(index)
        mysql_connect.create_table(index, fields)
    last_time = mysql_connect.get_last_time(index)
    records = es_connect.get_last_records(index, last_time)
    if len(records) > 0:
        mysql_connect.insert_record(index, records)
