CREATE SEQUENCE ufo_campaign_item_seq;

CREATE TABLE ufo_campaign_item (
 id INT PRIMARY KEY DEFAULT nextval('ufo_campaign_item_seq'),
 campaign_id int,
 product_id int,
 bid float,
 status int,
 destination text,
 clicks int,
 impressions int,
 ctr float,
 avg_cpc float,
 cost float);

ALTER TABLE ONLY "ufo_campaign_item ADD CONSTRAINT campaign_id_cons FOREIGN KEY ("campaign_id") REFERENCES "campaign"("id");
ALTER TABLE ONLY "ufo_campaign_item ADD CONSTRAINT product_id_cons FOREIGN KEY ("product_id") REFERENCES "product"("id");
ALTER TABLE ONLY "ufo_campaign_item ADD CONSTRAINT status_cons FOREIGN KEY ("status") REFERENCES "campaign_item_status"("id");
