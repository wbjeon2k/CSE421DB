
CREATE TABLE Board
(
	boardID              SERIAL,
	clanID               INTEGER NULL
);

ALTER TABLE Board
ADD PRIMARY KEY (boardID);

CREATE TABLE Clan
(
	clanID               SERIAL,
	name                 VARCHAR(64) NOT NULL,
	leaderID            INTEGER NOT NULL
);

ALTER TABLE Clan
ADD PRIMARY KEY (clanID);

CREATE TABLE Comment
(
	commentID            SERIAL,
	content              VARCHAR(256) NOT NULL,
	createDatetime      TIMESTAMP NOT NULL,
	serviceUserID               INTEGER NOT NULL,
	postID               INTEGER NOT NULL
);

ALTER TABLE Comment
ADD PRIMARY KEY (commentID);

CREATE TABLE Game
(
	gameID               SERIAL,
	name                 VARCHAR(128) NOT NULL
);

ALTER TABLE Game
ADD PRIMARY KEY (gameID);

CREATE TABLE Game_Tag
(
	gameID               INTEGER NOT NULL,
	tagID                INTEGER NOT NULL
);

ALTER TABLE Game_Tag
ADD PRIMARY KEY (gameID,tagID);

CREATE TABLE GameReview
(
	reviewID             INTEGER NOT NULL,
	gameID               INTEGER NOT NULL
);

ALTER TABLE GameReview
ADD PRIMARY KEY (reviewID);

CREATE TABLE Party
(
	partyID              SERIAL,
	name                 VARCHAR(64) NOT NULL,
	playStartDatetime  TIMESTAMP NOT NULL,
	leaderID            INTEGER NOT NULL,
	joinLink            VARCHAR(512) NOT NULL,
	gameID               INTEGER NOT NULL
);

ALTER TABLE Party
ADD PRIMARY KEY (partyID);

CREATE TABLE Post
(
	postID               SERIAL,
	title                VARCHAR(128) NOT NULL,
	content              TEXT NOT NULL,
	createDatetime      TIMESTAMP NOT NULL,
	isNotice            BOOLEAN NOT NULL DEFAULT false,
	thumbsUp            INTEGER NOT NULL DEFAULT 0,
	thumbsDown          INTEGER NOT NULL DEFAULT 0,
	viewCount           INTEGER NOT NULL DEFAULT 0,
	serviceUserID               INTEGER NOT NULL,
	boardID              INTEGER NULL
);

ALTER TABLE Post
ADD PRIMARY KEY (postID);

CREATE TABLE Review
(
	reviewID             SERIAL,
	createDatetime      TIMESTAMP NOT NULL,
	content              VARCHAR(512) NULL,
	score                INTEGER NOT NULL
);

ALTER TABLE Review
ADD PRIMARY KEY (reviewID);

CREATE TABLE Tag
(
	tagID                SERIAL,
	name                 VARCHAR(64) NOT NULL
);

ALTER TABLE Tag
ADD PRIMARY KEY (tagID);

CREATE TABLE ServiceUser
(
	serviceUserID               SERIAL,
	email                VARCHAR(128) NOT NULL,
	encryptedPassword   VARCHAR(256) NOT NULL,
	salt               VARCHAR(256) NOT NULL,
	nickname             VARCHAR(64) NOT NULL,
	isAdmin             BOOLEAN NOT NULL DEFAULT false,
	clanID               INTEGER NULL
);

ALTER TABLE ServiceUser
ADD PRIMARY KEY (serviceUserID);

CREATE TABLE ServiceUser_Party
(
	serviceUserID               INTEGER NOT NULL,
	partyID              INTEGER NOT NULL
);

ALTER TABLE ServiceUser_Party
ADD PRIMARY KEY (serviceUserID,partyID);

CREATE TABLE ServiceUserReview
(
	reviewID             INTEGER NOT NULL,
	serviceUserID               INTEGER NOT NULL
);

ALTER TABLE ServiceUserReview
ADD PRIMARY KEY (reviewID);

ALTER TABLE Board
ADD CONSTRAINT Clan_Board FOREIGN KEY (clanID) REFERENCES Clan (clanID);

ALTER TABLE Comment
ADD CONSTRAINT ServiceUser_Comment FOREIGN KEY (serviceUserID) REFERENCES ServiceUser (serviceUserID);

ALTER TABLE Comment
ADD CONSTRAINT Post_Comment FOREIGN KEY (postID) REFERENCES Post (postID);

ALTER TABLE Game_Tag
ADD CONSTRAINT R_19 FOREIGN KEY (gameID) REFERENCES Game (gameID);

ALTER TABLE Game_Tag
ADD CONSTRAINT R_20 FOREIGN KEY (tagID) REFERENCES Tag (tagID);

ALTER TABLE GameReview
ADD CONSTRAINT Review_GameReview FOREIGN KEY (reviewID) REFERENCES Review (reviewID)
		ON DELETE CASCADE;

ALTER TABLE GameReview
ADD CONSTRAINT Game_GameReview FOREIGN KEY (gameID) REFERENCES Game (gameID);

ALTER TABLE Party
ADD CONSTRAINT Game_Party FOREIGN KEY (gameID) REFERENCES Game (gameID);

ALTER TABLE Post
ADD CONSTRAINT ServiceUser_Post FOREIGN KEY (serviceUserID) REFERENCES ServiceUser (serviceUserID);

ALTER TABLE Post
ADD CONSTRAINT Board_Post FOREIGN KEY (boardID) REFERENCES Board (boardID);

ALTER TABLE ServiceUser
ADD CONSTRAINT Clan_User FOREIGN KEY (clanID) REFERENCES Clan (clanID);

ALTER TABLE ServiceUser_Party
ADD CONSTRAINT R_22 FOREIGN KEY (serviceUserID) REFERENCES ServiceUser (serviceUserID);

ALTER TABLE ServiceUser_Party
ADD CONSTRAINT R_23 FOREIGN KEY (partyID) REFERENCES Party (partyID);

ALTER TABLE ServiceUserReview
ADD CONSTRAINT Review_UserReview FOREIGN KEY (reviewID) REFERENCES Review (reviewID)
		ON DELETE CASCADE;

ALTER TABLE ServiceUserReview
ADD CONSTRAINT ServiceUser_UserReview FOREIGN KEY (serviceUserID) REFERENCES ServiceUser (serviceUserID);
