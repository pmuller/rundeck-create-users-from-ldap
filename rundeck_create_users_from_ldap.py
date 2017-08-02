#!/usr/bin/env python

from datetime import datetime
from argparse import ArgumentParser
import logging
import os

import ldap
import jaydebeapi


VERSION = '0.1.0'
LOGGER = logging.getLogger()
SQL_USER_INSERT = """\
INSERT INTO rduser (
    email, first_name, last_name, version, date_created, last_updated, login
) VALUES (
    '{email}', '{first_name}', '{last_name}', {version}, '{date_created}',
    '{last_updated}', '{login}'
)
"""
SQL_USER_UPDATE = """\
UPDATE rduser
SET email='{email}', first_name='{first_name}', last_name='{last_name}'
WHERE id={id}
"""


def get_ldap_users(ldap_uri, bind_dn, bind_password, search_base, search_filter):
    result = {}

    conn = ldap.initialize(ldap_uri)
    conn.simple_bind_s(bind_dn, bind_password)

    for _, data in conn.search_s(search_base, ldap.SCOPE_ONELEVEL, filterstr=search_filter):
        result[data['uid'][0]] = {
            'email': data['mail'][0],
            'first_name': data['givenName'][0],
            'last_name': data['sn'][0],
        }

    return result


def get_rundeck_users(cursor):
    result = {}
    cursor.execute(
        'select id, version, email, first_name, last_name, login from rduser')

    for id_, version, email, first_name, last_name, login in cursor.fetchall():
        result[login] = {
            'id': id_.value,
            'version': version.value,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
        }

    return result


def update_rundeck_users(cursor, ldap_users, rundeck_users):
    timestamp = str(datetime.utcnow())

    for ldap_username, ldap_data in ldap_users.items():
        if ldap_username in rundeck_users:
            rundeck_data = rundeck_users[ldap_username]

            if ldap_data['email'] != rundeck_data['email'] or \
                    ldap_data['first_name'] != rundeck_data['first_name'] or \
                    ldap_data['last_name'] != rundeck_data['last_name']:
                update_data = ldap_data.copy()
                update_data.update(version=rundeck_data['version'] + 1,
                                   last_updated=timestamp,
                                   id=rundeck_data['id'])
                cursor.execute(SQL_USER_UPDATE.format(**update_data))
                LOGGER.debug('Updated user: %r', update_data)

        else:
            insert_data = ldap_data.copy()
            insert_data.update(version=0, date_created=timestamp,
                               last_updated=timestamp, login=ldap_username)
            cursor.execute(SQL_USER_INSERT.format(**insert_data))
            LOGGER.debug('Created user: %r', insert_data)


def parse_cli_arguments():
    parser = ArgumentParser()

    parser.add_argument('-D', '--debug', default=False, action='store_true')
    parser.add_argument('--ldap-search-base', required=True)
    parser.add_argument('--ldap-filter', default='(objectClass=*)')
    parser.add_argument('--ldap-uri', required=True)
    parser.add_argument('--ldap-bind-dn', required=True)
    parser.add_argument('--ldap-bind-password', required=True)
    parser.add_argument('--db-uri',
                        default='jdbc:h2:/var/lib/rundeck/data/rundeckdb')
    parser.add_argument('--db-driver', default='org.h2.Driver')
    parser.add_argument('--db-username', default='sa')
    parser.add_argument('--db-password', default='')
    parser.add_argument('--java-classpath')

    return parser.parse_args()


def main():
    arguments = parse_cli_arguments()
    logging.basicConfig(
        level=logging.DEBUG if arguments.debug else logging.INFO)

    ldap_users = get_ldap_users(
        arguments.ldap_uri, arguments.ldap_bind_dn,
        arguments.ldap_bind_password, arguments.ldap_search_base, arguments.ldap_filter)
    LOGGER.debug('LDAP users: %r', ldap_users)

    if arguments.java_classpath:
        os.environ['CLASSPATH'] = arguments.java_classpath

    db_conn = jaydebeapi.connect(
        arguments.db_driver, arguments.db_uri,
        [arguments.db_username, arguments.db_password])
    cursor = db_conn.cursor()
    rundeck_users = get_rundeck_users(cursor)
    LOGGER.debug('Rundeck users: %r', rundeck_users)
    update_rundeck_users(cursor, ldap_users, rundeck_users)

    db_conn.commit()
    LOGGER.debug('DB committed')
    db_conn.close()
    LOGGER.debug('DB closed')


if __name__ == '__main__':
    main()
