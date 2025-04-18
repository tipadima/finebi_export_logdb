from bestconfig import Config
from elasticsearch import Elasticsearch
from elasticsearch8_dsl import Q, Search
import logging
import mysql.connector


class ElasticSearch_connect(object):

    def __init__(self):
        self._cfg = Config('config.json')
        self._level = logging.getLevelName(self._cfg.get('log_level', 'INFO'))
        logging.basicConfig(
            level=self._level,
            format='%(asctime)s [%(name)s] %(levelname)s:  %(message)s',
            handlers=[
                logging.StreamHandler()
            ]
        )
        self._es_hosts = self._cfg.elasticsearch.address.replace(' ', '')
        self._es_username = self._cfg.elasticsearch.username
        self._es_password = self._cfg.elasticsearch.password
        self._elastic_client = Elasticsearch(
            self._es_hosts.split(','),
            basic_auth=(self._es_username, self._es_password),
            verify_certs=False
        )

    def __del__(self):
        self._elastic_client.close()

    def get_index_list(self):
        index_list = list(self._elastic_client.indices.get_alias(index="fine_*").keys())
        logging.debug(f'ElasticSearch index list: {str(index_list)}')
        return index_list

    def get_index_fields(self, index_name):
        dict_index_fields = {}
        mapping = self._elastic_client.indices.get_mapping(index=index_name)
        for field in mapping[index_name]['mappings']['properties']:
            type = mapping[index_name]['mappings']['properties'][field]['type']
            dict_index_fields[field] = type
        logging.debug(f'ElasticSearch index {index_name} fields: {str(dict_index_fields)}')
        return dict_index_fields

    def get_last_records(self, index_name, time):
        result = []
        q=Q('bool', must=[
            Q({'range': {'time' : { 'gt': time}}}),
        ])
        search = Search(using=self._elastic_client, index=index_name).query(q)
        search = search.source()
        for hit in search.scan():
            result.append(hit.to_dict())
        return result

class Mysql_connect(object):
    def __init__(self):
        self._cfg = Config('config.json')
        self._level = logging.getLevelName(self._cfg.get('log_level', 'INFO'))
        logging.basicConfig(
            level=self._level,
            format='%(asctime)s [%(name)s] %(levelname)s:  %(message)s',
            handlers=[
                logging.StreamHandler()
            ]
        )
        self._mysql_hosts = self._cfg.mysql.address
        self._mysql_database = self._cfg.mysql.get('database', 'logdb')
        self._mysql_username = self._cfg.mysql.username
        self._mysql_password = self._cfg.mysql.password
        self._mysql_client = mysql.connector.connect(
            host=self._mysql_hosts.split(':')[0],
            port=self._mysql_hosts.split(':')[1],
            user=self._mysql_username,
            password=self._mysql_password,
            database=self._mysql_database
        )
        self._cursor = self._mysql_client.cursor(buffered=True)
        self._batch_size = self._cfg.mysql.get('batch_size', 1000)

    def __del__(self):
        self._cursor.close()
        self._mysql_client.close()

    def _execute_sql(self, queue):
        logging.debug(f'MySQL execute sql: {queue}')
        try:
            self._cursor.execute(queue)
        except  mysql.connector.Error as err:
            logging.error(err)
            logging.error(f"Error Code: {err.errno}")
            logging.error(f"SQLSTATE {err.sqlstate}")
            logging.error(f"Message {err.msg}")
            logging.error(f"Queue: {queue}")
        finally:
            self._mysql_client.commit()
        return self._cursor

    def create_table(self, table_name, fields):
        queue = "CREATE TABLE IF NOT EXISTS " + table_name + "("
        for field_name, field_type in fields.items():
            match field_type:
                case 'text':
                    queue += f'`{field_name}` TEXT, '
                case 'integer':
                    queue += f'`{field_name}` INTEGER, '
                case 'long':
                    queue += f'`{field_name}` BIGINT, '
                case 'boolean':
                    queue += f'`{field_name}` BOOLEAN, '
        queue = queue[:-2]
        queue += ")"
        logging.info(f'MySQL create table {table_name}')

        self._execute_sql(queue)

    def get_last_time(self, table_name):
        queue = "SELECT `time` FROM " + table_name + " ORDER BY time DESC LIMIT 1"
        result = self._execute_sql(queue).fetchall()
        if len(result) > 0:
            return result[0][0]
        else:
            return '0'

    def get_tables_list(self):
        queue = "SHOW TABLES"
        result = list(map(lambda x: x[0], self._execute_sql(queue).fetchall()))
        logging.debug(f'Mysql tables list: {str(result)}')
        return result

    def insert_record(self, table_name, records):
        count = 0
        field_names = set(records[0].keys())
        queue_header = "INSERT INTO " + table_name + " ("
        for field in field_names:
            queue_header += "`" + field + "`, "
        queue_header = queue_header[:-2]
        queue_header += ") VALUES "
        queue = queue_header
        for record in records:
            queue += "("
            for field_name in field_names:
                field_value = record.get(field_name, None)
                if field_value == True:
                    field_value = 1
                if field_value == False:
                    field_value = 0
                if field_value is not None:
                    queue += "'" + str(field_value).replace("\'", "\\'") + "', "
                else:
                    queue += "NULL, "
            queue = queue[:-2]
            queue += "), "
            count += 1
            if count == self._batch_size:
                queue = queue[:-2]
                logging.info(f'Mysql insert {count} records to {table_name}')
                self._execute_sql(queue)
                count = 0
                queue = queue_header

        queue = queue[:-2]
        logging.info(f'Mysql insert {count} records to {table_name}')
        self._execute_sql(queue)

