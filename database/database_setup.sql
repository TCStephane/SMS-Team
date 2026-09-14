CREATE DATABASE IF NOT EXISTS momo_sms;

USE momo_sms;

CREATE TABLE users (
    userId INT PRIMARY KEY AUTO_INCREMENT,
    firstName VARCHAR(50) NOT NULL,
    lastName VARCHAR(50) NOT NULL,
    phoneNumber INT NOT NULL,
    dateOfBirth DATE,
    gender VARCHAR(10),
    kycTier VARCHAR(20),
    momoBalance DECIMAL(12, 2) DEFAULT 0.00,
    identifier VARCHAR(50)
);

CREATE TABLE transactions (
    transactionId INT PRIMARY KEY AUTO_INCREMENT,
    senderId INT NOT NULL,
    receiverId INT NOT NULL,
    timestamp DATETIME NOT NULL,
    status VARCHAR(20) NOT NULL,
    currentAmount DECIMAL(12,2) NOT NULL,
    transactionFee DECIMAL(10,2) DEFAULT 0.00,
    governmentTax DECIMAL(10,2) DEFAULT 0.00,
    senderBalanceAfter DECIMAL(12,2),
    receiverBalanceAfter DECIMAL(12,2),
    referenceText VARCHAR(255),
    FOREIGN KEY (senderId) REFERENCES users(userId),
    FOREIGN KEY (receiverId) REFERENCES users(userId)
);

CREATE TABLE transaction_categories (
    transCategoryId INT PRIMARY KEY AUTO_INCREMENT,
    transCategoryName VARCHAR(50) NOT NULL,
    description VARCHAR(255)
);

CREATE TABLE transaction_map (
    transactionId INT,
    transCategoryId INT,
    PRIMARY KEY (transactionId, transCategoryId),
    FOREIGN KEY (transactionId) REFERENCES transactions(transactionId) ON DELETE CASCADE,
    FOREIGN KEY (transCategoryId) REFERENCES transaction_categories(transCategoryId) ON DELETE CASCADE
);

CREATE TABLE system_logs (
    sysLogId INT PRIMARY KEY AUTO_INCREMENT,
    transactionId INT,
    logLevel VARCHAR(20) NOT NULL,
    message VARCHAR(255) NOT NULL,
    timestamp DATETIME NOT NULL,
    FOREIGN KEY (transactionId) REFERENCES transactions(transactionId) ON DELETE SET NULL
);