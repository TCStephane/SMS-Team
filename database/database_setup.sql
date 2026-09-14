-- Active: 1789410485152@@127.0.0.1@3306
CREATE DATABASE IF NOT EXISTS momo_sms;

USE momo_sms;


CREATE TABLE users (
    userId INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique identifier for each user',
    firstName VARCHAR(50) NOT NULL COMMENT 'User first name',
    lastName VARCHAR(50) NOT NULL COMMENT 'User last name',
    phoneNumber VARCHAR(15) NOT NULL UNIQUE COMMENT 'Mobile money subscriber',
    dateOfBirth DATE COMMENT 'User date of birth',
    gender VARCHAR(10) COMMENT 'User gender',
    kycTier VARCHAR(20) COMMENT 'KYC verification level',
    momoBalance DECIMAL(12, 2) DEFAULT 0.00 CHECK (momoBalance >= 0) COMMENT 'Current mobile money balance',
    identifier VARCHAR(50) COMMENT 'National ID or external system identifier'
) COMMENT = 'Stores registered MoMo system users';

CREATE TABLE transactions (
    transactionId INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique identifier for each transaction',
    senderId INT NOT NULL COMMENT 'FK to the sending user',
    receiverId INT NOT NULL COMMENT 'FK to the receiving user',
    transactionTimestamp DATETIME NOT NULL COMMENT 'Date and time the transaction occurred',
    status VARCHAR(20) NOT NULL COMMENT 'Transaction status e.g. success, failed, pending',
    currentAmount DECIMAL(12,2) NOT NULL CHECK (currentAmount >= 0) COMMENT 'Transaction amount',
    transactionFee DECIMAL(10,2) DEFAULT 0.00 CHECK (transactionFee >= 0) COMMENT 'Fee charged for the transaction',
    governmentTax DECIMAL(10,2) DEFAULT 0.00 CHECK (governmentTax >= 0) COMMENT 'Government tax applied',
    senderBalanceAfter DECIMAL(12,2) COMMENT 'Sender balance after transaction',
    receiverBalanceAfter DECIMAL(12,2) COMMENT 'Receiver balance after transaction',
    referenceText VARCHAR(255) COMMENT 'Free-text reference or note for the transaction',
    FOREIGN KEY (senderId) REFERENCES users(userId),
    FOREIGN KEY (receiverId) REFERENCES users(userId)
) COMMENT = 'Stores MoMo transaction records';

CREATE TABLE transaction_categories (
    transCategoryId INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique identifier for transaction category',
    transCategoryName VARCHAR(50) NOT NULL COMMENT 'Name of the category',
    description VARCHAR(255) COMMENT 'Description of the category'
) COMMENT = 'Stores categories for classifying transactions';

CREATE TABLE transaction_map (
    transactionId INT COMMENT 'FK to the transaction',
    transCategoryId INT COMMENT 'FK to the transaction category',
    PRIMARY KEY (transactionId, transCategoryId),
    FOREIGN KEY (transactionId) REFERENCES transactions(transactionId) ON DELETE CASCADE,
    FOREIGN KEY (transCategoryId) REFERENCES transaction_categories(transCategoryId) ON DELETE CASCADE
) COMMENT = 'Mapping table linking transactions to categories';

CREATE TABLE system_logs (
    sysLogId INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique identifier for the system log entry',
    transactionId INT COMMENT 'FK to the related transaction',
    logLevel VARCHAR(20) NOT NULL COMMENT 'Severity level of the log e.g., INFO, ERROR, WARN',
    message VARCHAR(255) NOT NULL COMMENT 'Log message detail',
    logTimestamp DATETIME NOT NULL COMMENT 'Timestamp when the log was recorded',
    FOREIGN KEY (transactionId) REFERENCES transactions(transactionId) ON DELETE SET NULL
) COMMENT = 'Stores system logs associated with transactions';

INSERT INTO users (firstName, lastName, phoneNumber, dateOfBirth, gender, kycTier, momoBalance) VALUES
('Dorcase', 'Lesly', '0788111222', '1999-03-14', 'Female', 'Tier2', 15000.00),
('Stephane', 'Tchatchum', '0788333444', '2000-07-22', 'Male', 'Tier3', 45000.00),
('Melissa', 'Elise', '0788555666', '2001-11-05', 'Female', 'Tier1', 2500.00),
('David', 'Ange', '0788777888', '1998-01-30', 'Male', 'Tier2', 12300.00),
('George', 'Edwin', '0788999000', '1997-09-18', 'Male', 'Tier3', 89000.00);