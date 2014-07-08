/*
野手成績をインポートするSQL

エクスポート
\copy (select * from seisekis) TO 'batter_data.tsv' DELIMITER E'\t'

インポート
\i /Users/Ryosuke/Desktop/create_table_batter_data.sql
*/

drop table batter_data;
create table batter_data(
	name varchar(64),
	year integer,
	age integer,
	team varchar(32),
	league varchar(32),
	lev varchar(32),
	games integer,
	pa integer,
	ab integer,
	runs integer,
	hits integer,
	doubles integer,
	triples integer,
	hr integer,
	rbi integer,
	sb integer,
	cs integer,
	bb integer,
	so integer,
	ba double precision,
	obp double precision,
	slg double precision,
	ops double precision,
	tb integer,
	gdp integer,
	hbp integer,
	sh integer,
	sf integer,
	ibb integer
);
\copy batter_data from '/Users/Ryosuke/Desktop/batter_data.tsv'