CREATE SEQUENCE ufo_product_seq;

CREATE TABLE ufo_product (
 id INT PRIMARY KEY DEFAULT nextval('ufo_product_seq'),
 uid INT UNSIGNED,
 name text,
 description text);

