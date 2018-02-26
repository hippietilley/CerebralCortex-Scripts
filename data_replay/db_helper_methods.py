# Copyright (c) 2017, MD2K Center of Excellence
# - Nasir Ali <nasir.ali08@gmail.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import mysql.connector
import mysql.connector.pooling
import json
import yaml

class SqlData():
    def __init__(self):

        with open("config.yml") as ymlfile:
            self.config = yaml.load(ymlfile)

        self.hostIP = self.config['mysql']['host']
        self.hostPort = self.config['mysql']['port']
        self.database = self.config['mysql']['database']
        self.dbUser = self.config['mysql']['db_user']
        self.dbPassword = self.config['mysql']['db_pass']
        self.datastreamTable = self.config['mysql']['datastream_table']
        self.kafkaOffsetsTable = self.config['mysql']['kafka_offsets_table']
        self.userTable = self.config['mysql']['user_table']
        self.poolName = self.config['mysql']['connection_pool_name']
        self.poolSize = self.config['mysql']['connection_pool_size']
        self.pool = self.create_pool(pool_name=self.poolName, pool_size=self.poolSize)


    def create_pool(self, pool_name="CC_Pool", pool_size=10):
        """
        Create a connection pool, after created, the request of connecting
        MySQL could get a connection from this pool instead of request to
        create a connection.
        :param pool_name: the name of pool, default is "CC_Pool"
        :param pool_size: the size of pool, default is 10
        :return: connection pool
        """
        dbconfig = {
            "host":self.hostIP,
            "port":self.hostPort,
            "user":self.dbUser,
            "password":self.dbPassword,
            "database":self.database,
        }

        pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name=pool_name,
            pool_size=pool_size,
            pool_reset_session=True,
            **dbconfig)
        return pool

    def close(self, conn, cursor):
        """
        close connection of mysql.
        :param conn:
        :param cursor:
        :return:
        """
        try:
            cursor.close()
            conn.close()
        except Exception as exp:
            self.logging.log(error_message="Cannot close connection: "+str(exp), error_type=self.logtypes.DEBUG)

    def execute(self, sql, args=None, commit=False):
        """
        Execute a sql, it could be with args and with out args. The usage is
        similar with execute() function in module pymysql.
        :param sql: sql clause
        :param args: args need by sql clause
        :param commit: whether to commit
        :return: if commit, return None, else, return result
        """
        # get connection form connection pool instead of create one.
        conn = self.pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        if args:
            cursor.execute(sql, args)
        else:
            cursor.execute(sql)
        if commit is True:
            conn.commit()
            self.close(conn, cursor)
            return None
        else:
            res = cursor.fetchall()
            self.close(conn, cursor)
            return res

    def add_to_db(self, owner_id, stream_id, stream_name, day, files_list, dir_size, metadata):
        qry = "INSERT IGNORE INTO data_replay (owner_id, stream_id, stream_name, day, files_list, dir_size, metadata) VALUES(%s, %s, %s, %s, %s, %s, %s)"
        vals = str(owner_id), str(stream_id), str(stream_name), str(day), json.dumps(files_list), dir_size, json.dumps(metadata)
        self.execute(qry, vals, commit=True)

    def get_data(self, participant_ids, bl_regex):
        fields = None
        if len(participant_ids)>0:
            for participant_id in participant_ids:
                fields += '%s=%s and ' % ("owner_id", participant_id)

            qry = "select * from data_replay where "+fields+" processed=0 and stream_name NOT REGEX "+bl_regex
        else:
            qry = "select * from data_replay where stream_name NOT REGEX "+bl_regex+" and processed=0 ordered by id limit 20"

        return self.execute(qry)