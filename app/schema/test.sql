CREATE DATABASE testDB default CHARACTER SET UTF8;

use testDB;


CREATE TABLE category(
   CID INTEGER PRIMARY KEY AUTO_INCREMENT,
   category_name VARCHAR(50) NOT NULL
);

CREATE TABLE institution(
   institution_name VARCHAR(200) PRIMARY KEY,
   institution_url VARCHAR(600),
   major_cid INTEGER,
   FOREIGN KEY (major_cid) REFERENCES category(CID)
);

CREATE TABLE writer(
   WID INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY,
   writer_name VARCHAR(200),
   UNIQUE KEY writername (writer_name)
);

CREATE TABLE research(
 RID INTEGER PRIMARY KEY AUTO_INCREMENT,
 title VARCHAR(200) NOT NULL,
 research_url VARCHAR(600) NOT NULL,
 institution_name VARCHAR(200),
 CID INTEGER,
 WID INTEGER,
 tot_word_cnt INTEGER NOT NULL,
 FOREIGN KEY (institution_name) REFERENCES institution(institution_name),
 FOREIGN KEY (CID) REFERENCES category(CID),
 FOREIGN KEY (WID) REFERENCES writer(WID)
);

CREATE TABLE pub_date(
   RID INTEGER,
   year INTEGER NOT NULL,
   month INTEGER NULL,
   date INTEGER NULL,
   FOREIGN KEY (RID) REFERENCES research(RID)
);

CREATE TABLE keyword(
   word VARCHAR(100) NOT NULL,
   RID INTEGER,
   freq INTEGER NOT NULL,
   FOREIGN KEY (RID) REFERENCES research(RID),
   PRIMARY KEY (word, RID)
);

CREATE TABLE content_date(
   RID INTEGER,
   decade INTEGER,
   FOREIGN KEY (RID) REFERENCES research(RID)
);

