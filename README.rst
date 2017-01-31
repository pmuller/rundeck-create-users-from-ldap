Create users in Rundeck's H2 database
=====================================

The script connects to a LDAP server, fetches users,
then creates them in a Rundeck H2 database.

Its main purpose is to re-use users' email, first name and last name attributes
stored in a LDAP directory when integrating Rundeck with LDAP or Crowd.

It will become useless once these issues will be solved:
* LDAP_
* Crowd_

.. _LDAP: https://github.com/rundeck/rundeck/issues/946
.. _Crowd: https://github.com/flopma/crowd-jaas/issues/9


Usage
-----

.. code-block:: console

    $ rundeck-create-users-from-ldap --debug \
        --ldap-uri ldaps://ldap.foo.bar \
        --ldap-bind-dn cn=readonly,ou=Roles,o=foobar \
        --ldap-bind-password t0ps3kr3t \
        --ldap-search-base ou=Users,o=foobar \
        --java-classpath /var/lib/rundeck/exp/webapp/WEB-INF/lib/h2-1.4.193.jar
