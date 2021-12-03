DROP TABLE IF EXISTS board CASCADE;
CREATE TABLE board
(
	board_id              SERIAL,
	clan_id               INTEGER NULL
);

ALTER TABLE board
ADD PRIMARY KEY (board_id);

DROP TABLE IF EXISTS clan CASCADE;
CREATE TABLE clan
(
	clan_id               SERIAL,
	name                 VARCHAR(64) NOT NULL,
	leader_id            INTEGER NOT NULL
);

ALTER TABLE clan
ADD PRIMARY KEY (clan_id);

DROP TABLE IF EXISTS comment CASCADE;
CREATE TABLE comment
(
	comment_id            SERIAL,
	content              VARCHAR(256) NOT NULL,
	create_datetime      TIMESTAMP NOT NULL,
	service_user_id               INTEGER NOT NULL,
	post_id               INTEGER NOT NULL
);

ALTER TABLE comment
ADD PRIMARY KEY (comment_id);

DROP TABLE IF EXISTS game CASCADE;
CREATE TABLE game
(
	game_id               SERIAL,
	name                 VARCHAR(128) NOT NULL
);

ALTER TABLE game
ADD PRIMARY KEY (game_id);

DROP TABLE IF EXISTS game_tag CASCADE;
CREATE TABLE game_tag
(
	game_id               INTEGER NOT NULL,
	tag_id                INTEGER NOT NULL
);

ALTER TABLE game_tag
ADD PRIMARY KEY (game_id,tag_id);

DROP TABLE IF EXISTS game_review CASCADE;
CREATE TABLE game_review
(
	review_id             INTEGER NOT NULL,
	game_id               INTEGER NOT NULL
);

ALTER TABLE game_review
ADD PRIMARY KEY (review_id);

DROP TABLE IF EXISTS party CASCADE;
CREATE TABLE party
(
	party_id              SERIAL,
	name                 VARCHAR(64) NOT NULL,
	playstart_datetime  TIMESTAMP NOT NULL,
	leader_id            INTEGER NOT NULL,
	joinLink            VARCHAR(512) NOT NULL,
	game_id               INTEGER NOT NULL
);

ALTER TABLE party
ADD PRIMARY KEY (party_id);

DROP TABLE IF EXISTS post CASCADE;
CREATE TABLE post
(
	post_id               SERIAL,
	title                VARCHAR(128) NOT NULL,
	content              TEXT NOT NULL,
	create_datetime      TIMESTAMP NOT NULL,
	isNotice            BOOLEAN NOT NULL DEFAULT false,
	thumbsUp            INTEGER NOT NULL DEFAULT 0,
	thumbsDown          INTEGER NOT NULL DEFAULT 0,
	viewCount           INTEGER NOT NULL DEFAULT 0,
	service_user_id               INTEGER NOT NULL,
	board_id              INTEGER NULL
);

ALTER TABLE post
ADD PRIMARY KEY (post_id);

DROP TABLE IF EXISTS review CASCADE;
CREATE TABLE review
(
	review_id             SERIAL,
	create_datetime      TIMESTAMP NOT NULL,
	content              VARCHAR(512) NULL,
	score                INTEGER NOT NULL
);

ALTER TABLE review
ADD PRIMARY KEY (review_id);

DROP TABLE IF EXISTS tag CASCADE;
CREATE TABLE tag
(
	tag_id                SERIAL,
	name                 VARCHAR(64) NOT NULL
);

ALTER TABLE tag
ADD PRIMARY KEY (tag_id);

DROP TABLE IF EXISTS service_user CASCADE;
CREATE TABLE service_user
(
	service_user_id               SERIAL,
	email                VARCHAR(128) NOT NULL,
	encrypted_password   VARCHAR(256) NOT NULL,
	nickname             VARCHAR(64) NOT NULL,
	isAdmin             BOOLEAN NOT NULL DEFAULT false,
	clan_id               INTEGER NULL
);

ALTER TABLE service_user
ADD PRIMARY KEY (service_user_id);

DROP TABLE IF EXISTS service_user_party CASCADE;
CREATE TABLE service_user_party
(
	service_user_id               INTEGER NOT NULL,
	party_id              INTEGER NOT NULL
);

ALTER TABLE service_user_party
ADD PRIMARY KEY (service_user_id,party_id);

DROP TABLE IF EXISTS service_user_review CASCADE;
CREATE TABLE service_user_review
(
	review_id             INTEGER NOT NULL,
	service_user_id               INTEGER NOT NULL
);

ALTER TABLE service_user_review
ADD PRIMARY KEY (review_id);

ALTER TABLE board
ADD CONSTRAINT clan_board FOREIGN KEY (clan_id) REFERENCES clan (clan_id);

ALTER TABLE comment
ADD CONSTRAINT service_user_comment FOREIGN KEY (service_user_id) REFERENCES service_user (service_user_id);

ALTER TABLE comment
ADD CONSTRAINT post_comment FOREIGN KEY (post_id) REFERENCES post (post_id);

ALTER TABLE game_tag
ADD CONSTRAINT R_19 FOREIGN KEY (game_id) REFERENCES game (game_id);

ALTER TABLE game_tag
ADD CONSTRAINT R_20 FOREIGN KEY (tag_id) REFERENCES tag (tag_id);

ALTER TABLE game_review
ADD CONSTRAINT review_game_review FOREIGN KEY (review_id) REFERENCES review (review_id)
		ON DELETE CASCADE;

ALTER TABLE game_review
ADD CONSTRAINT game_game_review FOREIGN KEY (game_id) REFERENCES game (game_id);

ALTER TABLE party
ADD CONSTRAINT game_party FOREIGN KEY (game_id) REFERENCES game (game_id);

ALTER TABLE post
ADD CONSTRAINT service_user_post FOREIGN KEY (service_user_id) REFERENCES service_user (service_user_id);

ALTER TABLE post
ADD CONSTRAINT board_post FOREIGN KEY (board_id) REFERENCES board (board_id);

ALTER TABLE service_user
ADD CONSTRAINT clan_User FOREIGN KEY (clan_id) REFERENCES clan (clan_id);

ALTER TABLE service_user_party
ADD CONSTRAINT R_22 FOREIGN KEY (service_user_id) REFERENCES service_user (service_user_id);

ALTER TABLE service_user_party
ADD CONSTRAINT R_23 FOREIGN KEY (party_id) REFERENCES party (party_id);

ALTER TABLE service_user_review
ADD CONSTRAINT review_User_review FOREIGN KEY (review_id) REFERENCES review (review_id)
		ON DELETE CASCADE;

ALTER TABLE service_user_review
ADD CONSTRAINT service_user_User_review FOREIGN KEY (service_user_id) REFERENCES service_user (service_user_id);
