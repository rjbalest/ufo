CREATE SEQUENCE ufo_campaign_seq;

CREATE TABLE ufo_campaign (
 id INT PRIMARY KEY DEFAULT nextval('ufo_campaign_seq'),
 uid INT UNSIGNED,
 status int DEFAULT 0,
 clicks int DEFAULT 0,
 impressions int DEFAULT 0,
 ctr float DEFAULT 0,
 avg_cpc float DEFAULT 0.0,
 cost float DEFAULT 0.0,
 name text,
 description text DEFAULT "Unknown",
 budget float DEFAULT 0.0);

ALTER TABLE ONLY "ufo_campaign ADD CONSTRAINT status_cons FOREIGN KEY ("status") REFERENCES "campaign_status"("id");
