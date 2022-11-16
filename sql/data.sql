PRAGMA foreign_keys = ON;
INSERT INTO users(username, fullname, email, "filename", "password")
VALUES ('awdeorio', 'Andrew DeOrio', 'awdeorio@umich.edu', 'e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg','sha512$a45ffdcc71884853a2cba9e6bc55e812$c739cef1aec45c6e345c8463136dc1ae2fe19963106cf748baf87c7102937aa96928aa1db7fe1d8da6bd343428ff3167f4500c8a61095fb771957b4367868fb8');

INSERT INTO users(username, fullname, email, "filename", "password")
VALUES ('jflinn', 'Jason Flinn', 'jflinn@umich.edu', '505083b8b56c97429a728b68f31b0b2a089e5113.jpg','sha512$a45ffdcc71884853a2cba9e6bc55e812$c739cef1aec45c6e345c8463136dc1ae2fe19963106cf748baf87c7102937aa96928aa1db7fe1d8da6bd343428ff3167f4500c8a61095fb771957b4367868fb8');

INSERT INTO users(username, fullname, email, "filename", "password")
VALUES ('michjc', 'Michael Cafarella', 'michjc@umich.edu', '5ecde7677b83304132cb2871516ea50032ff7a4f.jpg','sha512$a45ffdcc71884853a2cba9e6bc55e812$c739cef1aec45c6e345c8463136dc1ae2fe19963106cf748baf87c7102937aa96928aa1db7fe1d8da6bd343428ff3167f4500c8a61095fb771957b4367868fb8');

INSERT INTO users(username, fullname, email, "filename", "password")
VALUES('jag', 'H.V. Jagadish', 'jag@umich.edu', '73ab33bd357c3fd42292487b825880958c595655.jpg', 'sha512$a45ffdcc71884853a2cba9e6bc55e812$c739cef1aec45c6e345c8463136dc1ae2fe19963106cf748baf87c7102937aa96928aa1db7fe1d8da6bd343428ff3167f4500c8a61095fb771957b4367868fb8');

INSERT INTO posts("filename", "owner")
VALUES
    ('122a7d27ca1d7420a1072f695d9290fad4501a41.jpg', 'awdeorio'),
    ('ad7790405c539894d25ab8dcf0b79eed3341e109.jpg', 'jflinn'),
    ('9887e06812ef434d291e4936417d125cd594b38a.jpg', 'awdeorio'),
    ('2ec7cf8ae158b3b1f40065abfb33e81143707842.jpg', 'jag');

INSERT INTO likes("owner", postid)
VALUES 
    ('awdeorio', 1),
    ('michjc', 1),
    ('jflinn', 1),
    ('awdeorio', 2),
    ('michjc', 2),
    ('awdeorio', 3);

INSERT INTO comments( "owner", "text", postid)
VALUES
     ('awdeorio','#chickensofinstagram', 3 ),
     ('jflinn','I <3 chickens', 3 ),
     ('michjc','Cute overload!' , 3),
     ('awdeorio','Sick #crossword' , 2),
     ('jflinn','Walking the plank #chickensofinstagram' , 1),
     ('awdeorio','This was after trying to teach them to do a #crossword', 1 ),
     ('jag','Saw this on the diag yesterday!', 4 );


INSERT INTO "following"(username1, username2)
VALUES
     ('awdeorio','jflinn'),
     ('awdeorio','michjc' ),
     ('jflinn','awdeorio' ),
     ('jflinn','michjc' ),
     ('michjc','awdeorio' ),
     ('michjc','jag' ),
     ('jag','michjc' );