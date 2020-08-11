BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "project" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL,
	"last_link_scrapped"	INTEGER DEFAULT 0,
	"pagination_mask"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("last_link_scrapped") REFERENCES "link"("id")
);
CREATE TABLE IF NOT EXISTS "link" (
	"id"	INTEGER NOT NULL UNIQUE,
	"fk_project"	INTEGER NOT NULL,
	"link"	TEXT NOT NULL,
	"created"	INTEGER NOT NULL,
	"passed"	INTEGER NOT NULL DEFAULT 0,
	"valid"	INTEGER NOT NULL DEFAULT 1,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("fk_project") REFERENCES "project"("id")
);
CREATE TABLE IF NOT EXISTS "selector" (
	"id"	INTEGER NOT NULL UNIQUE,
	"fk_project"	INTEGER NOT NULL,
	"field"	TEXT NOT NULL UNIQUE,
	"selector"	TEXT,
	"created"	INTEGER NOT NULL,
	"edited"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("fk_project") REFERENCES "project"("id")
);
CREATE TABLE IF NOT EXISTS "scrapped_data" (
	"id"	INTEGER NOT NULL UNIQUE,
	"fk_project"	INTEGER NOT NULL,
	"link"	TEXT NOT NULL,
	"data"	TEXT NOT NULL,
	"created"	INTEGER NOT NULL,
	"edited"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("fk_project") REFERENCES "project"("id"),
	FOREIGN KEY("link") REFERENCES "link"("id")
);
COMMIT;
