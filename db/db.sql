CREATE TABLE message (
  id int(11) NOT NULL DEFAULT 0,
  user_id int(11) NOT NULL DEFAULT 0,
  content text COLLATE utf8_bin NOT NULL,
  published_at datetime NOT NULL,
  PRIMARY KEY (id),
  KEY message_user_id (user_id),
  CONSTRAINT user_id_user_id FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE NO ACTION ON UPDATE NO ACTION
)


CREATE TABLE relationship (
  id int(11) NOT NULL DEFAULT 0,
  from_user_id int(11) NOT NULL DEFAULT 0,
  to_user_id int(11) NOT NULL DEFAULT 0,
  published_at datetime NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY relationship_from_user_id_to_user_id (from_user_id,to_user_id),
  KEY relationship_from_user_id (from_user_id),
  KEY relationship_to_user_id (to_user_id),
  CONSTRAINT from_user_id_user_id FOREIGN KEY (from_user_id) REFERENCES user (id) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT to_user_id_user_id FOREIGN KEY (to_user_id) REFERENCES user (id) ON DELETE NO ACTION ON UPDATE NO ACTION
)


CREATE TABLE user (
  id int(11) NOT NULL DEFAULT 0,
  username varchar(255) COLLATE utf8_bin NOT NULL,
  password varchar(255) COLLATE utf8_bin NOT NULL,
  email varchar(255) COLLATE utf8_bin NOT NULL,
  join_at datetime NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY user_username (username),
  UNIQUE KEY user_email (email)
)




INSERT INTO message 
VALUES (1,1,'Test post one, ciee','2022-04-19 18:49:46'),
(2,1,'COntent post 2','2022-04-19 21:47:12'),
(3,1,'Try post 3','2022-04-20 00:52:56'),
(4,2,'Test post by haikal','2022-04-22 03:40:23'),
(6,4,'Bbbbb','2022-04-23 13:20:47'),
(9,5,'aaaaaD','2022-04-23 14:37:02'),
(10,2,'Gue ganteng xD','2022-04-23 15:59:15');


INSERT INTO relationship 
VALUES (3,2,1,'2022-04-22 03:40:23'),
(4,3,2,'2022-04-22 14:53:00'),
(5,1,2,'2022-04-22 16:17:14'),
(6,1,5,'2022-04-23 15:59:15');


INSERT INTO user 
VALUES (1,'ya','202cb962ac59075b964b07152d234b70','ya@gmail.com','2022-04-19 17:25:00'),
(2,'haikal','202cb962ac59075b964b07152d234b70','ekal.ehmm@gmail.com','2022-04-21 10:14:53'),
(3,'Megawati','202cb962ac59075b964b07152d234b70','megawatiiie@gmail.com','2022-04-22 14:35:18'),
(4,'LifeStlR','827ccb0eea8a706c4c34a16891f84e7b','dancingmiraclemv45@gmail.com','2022-04-23 13:14:01'),
(5,'Aaaaa','827ccb0eea8a706c4c34a16891f84e7b','Abcdefg@gmail.com','2022-04-23 13:20:47');


