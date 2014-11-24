CREATE TABLE LOCATIONS (id int primary key not null, name varchar, lat float not null, long float not null);
CREATE TABLE USERS (gt_id varchar primary key not null, first_name varchar not null, last_name varchar not null, def_dest_id int references locations, email varchar);
CREATE TABLE GROUPS (ID INT PRIMARY KEY NOT NULL, NAME TEXT NOT NULL, final_dest_id int NOT NULL references locations);
CREATE TABLE WALKERS (gt_id varchar primary key references users, src_id int not null references locations, dest_id int not null references locations, start_time timestamp with time zone not null, grp_id int references groups);

INSERT INTO LOCATIONS VALUES (1, 'City Station', 33.790791, -84.401657);
INSERT INTO LOCATIONS VALUES (2, 'RPI Parking', 33.787561, -84.405133);
INSERT INTO LOCATIONS VALUES (3, '13th Street', 33.777862, -84.408678);
INSERT INTO LOCATIONS VALUES (4, 'M Street Apts.', 33.777139, -84.408485);
INSERT INTO LOCATIONS VALUES (5, 'Art Foundry Condos', 33.789634, -84.400579);
INSERT INTO LOCATIONS VALUES (6, 'Student Lofts', 33.778825, -84.412444);
INSERT INTO LOCATIONS VALUES (7, 'Voorheas Computing Bldg.', 33.777677, -84.396206);
INSERT INTO LOCATIONS VALUES (8, 'TSRB', 33.777061, -84.390200);

INSERT INTO USERS VALUES ('nnair34', 'Nidish', 'Nair', 1, 'nid@gatech.edu');
INSERT INTO USERS VALUES ('sejal99', 'Sejal', 'Shinde', 2, 'sejal@gatech.edu');
INSERT INTO USERS VALUES ('adwait99', 'Adwait', 'Purandare', 2, 'adwait@gatech.edu');
INSERT INTO USERS VALUES ('aishv99', 'Aishvarya', 'Krishnan', 2, 'aishv@gatech.edu');
INSERT INTO USERS VALUES ('string17', 'Stringer', 'Bell', 1, 'string@gatech.edu');
INSERT INTO USERS VALUES ('burdell07', 'George', 'Burdell', 3, 'burdell07@gatech.edu');
INSERT INTO USERS VALUES ('reek07', 'Theon', 'Greyjoy', 1, 'reek@gatech.edu');

INSERT INTO GROUPS VALUES (1, 'Group1', 1);
INSERT INTO GROUPS VALUES (2, 'Group2', 2);
INSERT INTO GROUPS VALUES (3, 'Group3', 3);

INSERT INTO WALKERS VALUES ('sejal99', 8, 2, '2014-10-26 20:30:00 EDT', null);
INSERT INTO WALKERS VALUES ('nnair34', 7, 1, '2014-10-26 22:30:00 EDT', 2);
INSERT INTO WALKERS VALUES ('adwait99', 7, 2, '2014-10-26 21:30:00 EDT', null);
INSERT INTO WALKERS VALUES ('aishv99', 8, 1, '2014-10-26 21:30:00 EDT', 1);
INSERT INTO WALKERS VALUES ('string17', 8, 1, '2014-10-26 21:30:00 EDT', 2);

SELECT u.gt_id, u.first_name, u.last_name, w.start_time, w.grp_id, g.name, l.name 
FROM ((walkers w INNER JOIN locations l ON w.dest_id=l.id) INNER JOIN users u on u.gt_id = w.gt_id) LEFT OUTER JOIN groups g on g.id=w.grp_id;
update walkers set dest_id = 2 where gt_id = 'nnair34';

CREATE TABLE WALKERS (gt_id varchar primary key not null, src_id int not null, dest_id int not null, start_time timestamp with time zone not null, grp_id int);
