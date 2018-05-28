"""initial migration

Revision ID: bbc8124343e3
Revises: 
Create Date: 2018-05-25 18:44:27.282315

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision = 'bbc8124343e3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    conn.execute(text('''
        begin;

        create type api_key_env as enum ('prod', 'staging', 'dev', 'local');
        create type api_key_status as enum ('active', 'revoked');

        create table authentication (
            id serial primary key,
            client_name varchar(64) not null,
            api_client_id varchar(64) not null,
            api_key varchar(128) not null,
            environment api_key_env not null,
            status api_key_status not null
        );

        create schema {brand};

        create table {brand}.stores (
            id serial primary key,
            store_id varchar(32),
            brand varchar(16),
            store_type varchar(32),
            zip_code varchar(16),
            state varchar(16),
            country char(2),
            enable_ship_from_store boolean default false,
            shipments_capacity int
        );

        create table {brand}.inventory (
            store_id varchar(32),
            sku varchar(32),
            quantity int,
            time_stamp timestamp without time zone default now()
        );

        create table processed_transaction_file (
            processed_files varchar(10),
            processed_at timestamp default current_timestamp
        );

        create table processed_periodic_demand_file (
            last_processed_date text,
            processed_at timestamp without time zone
        );

        create table created_periodic_demand (
            end_date text,
            period int,
            csv_directories text,
            processed_at timestamp without time zone default now(),
            loaded boolean default 'f',
            primary key (end_date, period)
        );

        create table filter_rules (
            id serial primary key,
            name varchar(64),
            rule_type varchar(32)
        );

        create table attribute_filters (
            id serial primary key,
            attribute_name varchar(32),
            attribute_value text,
            attribute_type varchar(32),
            operator varchar(32)
        );

        create table filter_rule_attribute_filters (
            filter_rule_id int references filter_rules (id),
            attribute_filter_id int references attribute_filters (id),
            primary key (filter_rule_id, attribute_filter_id)
        );

        create table table_filters (
            id serial primary key,
            attribute_name varchar(32),
            attribute_value text,
            attribute_type varchar(32),
            table_name varchar(64),
            operator varchar(32)
        );

        create table filter_rule_table_filters (
            filter_rule_id int references filter_rules (id),
            table_filter_id int references table_filters (id),
            primary key (filter_rule_id, table_filter_id)
        );

        insert into filter_rules (
            id, name, rule_type
        ) values (
            1, 'regular_stores_only', 'include'
        );
        insert into table_filters (
            id, attribute_name, attribute_value, attribute_type, table_name, operator
        ) values (
            1, 'store_type', 'REGULAR_STORE', 'str', 'stores', 'equals'
        );
        insert into filter_rule_table_filters (
            filter_rule_id, table_filter_id
        ) values (
            1, 1
        );

        insert into filter_rules (
            id, name, rule_type
        ) values (
            2, 'ship_enabled', 'include'
        );
        insert into table_filters (
            id, attribute_name, attribute_value, attribute_type, table_name, operator
        ) values (
            2, 'enable_ship_from_store', 'True', 'bool', 'stores', 'equals'
        );
        insert into filter_rule_table_filters (
            filter_rule_id, table_filter_id
        ) values (
            2, 2
        );

        commit;
    '''.format(brand=brand)))

    conn.execute(text('''
        begin;

        create index stores_store_id_idx on {brand}.stores using btree (store_id);
        create index stores_zip_code_idx on {brand}.stores using btree (zip_code);
        create index stores_state_idx on {brand}.stores using btree (state);
        create index stores_country_idx on {brand}.stores using btree (country);
        create index inventory_store_id_idx on {brand}.inventory using btree (store_id);
        create index inventory_sku_idx on {brand}.inventory using btree (sku);

        commit;
    '''.format(brand=brand)))


def downgrade():
    pass
