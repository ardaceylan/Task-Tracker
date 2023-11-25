CREATE DATABASE IF NOT EXISTS cs353hw4db;
USE cs353hw4db;

CREATE TABLE User (
    id INT PRIMARY KEY AUTO_INCREMENT,
    password VARCHAR (50) NOT NULL,
    username VARCHAR (50) NOT NULL,
    email VARCHAR (255)
);

CREATE TABLE TaskType (
    type VARCHAR (50) PRIMARY KEY
);

CREATE TABLE Task (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR (50) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(20),
    deadline DATETIME,
    creation_time DATETIME,
    done_time DATETIME,
    user_id INT NOT NULL,
    task_type VARCHAR (50) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User (id),
    FOREIGN KEY (task_type) REFERENCES TaskType (type)
);



INSERT INTO User (id, password, username, email)
VALUES 
	(1, "pass123", "user1", "etc@exm.com"),
    (2, "password2", "user2", "etc2@exm.com");



INSERT INTO TaskType (type)
VALUES 
	("Health"),
    ("Job"),
    ("Lifestyle"),
    ("Family"),
    ("Hobbies");


INSERT INTO Task (id, title, description, status, user_id, task_type)
VALUES 
	(1, "Go walk", "at least 30 min", "Done", 1, "Job" );