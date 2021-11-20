
CREATE TABLE Board
(
	BoardID              INTEGER NOT NULL,
	ClanID               INTEGER NOT NULL
);

ALTER TABLE Board
ADD PRIMARY KEY (BoardID);

CREATE TABLE Clan
(
	ClanID               INTEGER NOT NULL,
	name                 VARCHAR(64) NOT NULL,
	leader_id            INTEGER NOT NULL
);

ALTER TABLE Clan
ADD PRIMARY KEY (ClanID);

CREATE TABLE Comment
(
	CommentID            INTEGER NOT NULL,
	content              VARCHAR(256) NOT NULL,
	create_datetime      TIMESTAMP NOT NULL,
	UserID               INTEGER NOT NULL,
	PostID               INTEGER NOT NULL
);

ALTER TABLE Comment
ADD PRIMARY KEY (CommentID);

CREATE TABLE Game
(
	GameID               INTEGER NOT NULL,
	name                 VARCHAR(128) NOT NULL
);

ALTER TABLE Game
ADD PRIMARY KEY (GameID);

CREATE TABLE Game_Tag
(
	GameID               INTEGER NOT NULL,
	TagID                INTEGER NOT NULL
);

ALTER TABLE Game_Tag
ADD PRIMARY KEY (GameID,TagID);

CREATE TABLE GameReview
(
	ReviewID             INTEGER NOT NULL,
	GameID               INTEGER NOT NULL
);

ALTER TABLE GameReview
ADD PRIMARY KEY (ReviewID);

CREATE TABLE Party
(
	PartyID              INTEGER NOT NULL,
	name                 VARCHAR(64) NOT NULL,
	play_start_datetime  DATE NOT NULL,
	leader_id            INTEGER NOT NULL,
	join_link            VARCHAR(512) NOT NULL,
	GameID               INTEGER NOT NULL
);

ALTER TABLE Party
ADD PRIMARY KEY (PartyID);

CREATE TABLE Post
(
	PostID               INTEGER NOT NULL,
	title                VARCHAR(128) NOT NULL,
	content              LONG VARCHAR NOT NULL,
	create_datetime      TIMESTAMP NOT NULL,
	is_notice            BIT NOT NULL DEFAULT 0,
	thumbs_up            INTEGER NOT NULL DEFAULT 0,
	thumbs_down          INTEGER NOT NULL DEFAULT 0,
	view_count           INTEGER NOT NULL DEFAULT 0,
	UserID               INTEGER NOT NULL,
	BoardID              INTEGER NULL
);

ALTER TABLE Post
ADD PRIMARY KEY (PostID);

CREATE TABLE Review
(
	ReviewID             INTEGER NOT NULL,
	create_datetime      TIMESTAMP NOT NULL,
	content              VARCHAR(512) NULL,
	score                INTEGER NOT NULL
);

ALTER TABLE Review
ADD PRIMARY KEY (ReviewID);

CREATE TABLE Tag
(
	TagID                INTEGER NOT NULL,
	name                 VARCHAR(64) NOT NULL
);

ALTER TABLE Tag
ADD PRIMARY KEY (TagID);

CREATE TABLE User
(
	UserID               INTEGER NOT NULL,
	email                VARCHAR(128) NOT NULL,
	encrypted_password   VARCHAR(256) NOT NULL,
	nickname             VARCHAR(64) NOT NULL,
	is_admin             BIT NOT NULL DEFAULT 0,
	ClanID               INTEGER NULL
);

ALTER TABLE User
ADD PRIMARY KEY (UserID);

CREATE TABLE User_Party
(
	UserID               INTEGER NOT NULL,
	PartyID              INTEGER NOT NULL
);

ALTER TABLE User_Party
ADD PRIMARY KEY (UserID,PartyID);

CREATE TABLE UserReview
(
	ReviewID             INTEGER NOT NULL,
	UserID               INTEGER NOT NULL
);

ALTER TABLE UserReview
ADD PRIMARY KEY (ReviewID);

ALTER TABLE Board
ADD CONSTRAINT Clan_Board FOREIGN KEY (ClanID) REFERENCES Clan (ClanID);

ALTER TABLE Comment
ADD CONSTRAINT User_Comment FOREIGN KEY (UserID) REFERENCES User (UserID);

ALTER TABLE Comment
ADD CONSTRAINT Post_Comment FOREIGN KEY (PostID) REFERENCES Post (PostID);

ALTER TABLE Game_Tag
ADD CONSTRAINT R_19 FOREIGN KEY (GameID) REFERENCES Game (GameID);

ALTER TABLE Game_Tag
ADD CONSTRAINT R_20 FOREIGN KEY (TagID) REFERENCES Tag (TagID);

ALTER TABLE GameReview
ADD CONSTRAINT Review_GameReview FOREIGN KEY (ReviewID) REFERENCES Review (ReviewID)
		ON DELETE CASCADE;

ALTER TABLE GameReview
ADD CONSTRAINT Game_GameReview FOREIGN KEY (GameID) REFERENCES Game (GameID);

ALTER TABLE Party
ADD CONSTRAINT Game_Party FOREIGN KEY (GameID) REFERENCES Game (GameID);

ALTER TABLE Post
ADD CONSTRAINT User_Post FOREIGN KEY (UserID) REFERENCES User (UserID);

ALTER TABLE Post
ADD CONSTRAINT Board_Post FOREIGN KEY (BoardID) REFERENCES Board (BoardID);

ALTER TABLE User
ADD CONSTRAINT Clan_User FOREIGN KEY (ClanID) REFERENCES Clan (ClanID);

ALTER TABLE User_Party
ADD CONSTRAINT R_22 FOREIGN KEY (UserID) REFERENCES User (UserID);

ALTER TABLE User_Party
ADD CONSTRAINT R_23 FOREIGN KEY (PartyID) REFERENCES Party (PartyID);

ALTER TABLE UserReview
ADD CONSTRAINT Review_UserReview FOREIGN KEY (ReviewID) REFERENCES Review (ReviewID)
		ON DELETE CASCADE;

ALTER TABLE UserReview
ADD CONSTRAINT User_UserReview FOREIGN KEY (UserID) REFERENCES User (UserID);
