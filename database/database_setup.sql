CREATE DATABASE IF NOT EXISTS momo_sms;

USE momo_sms;

CREATE TABLE Users (
    userId INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique identifier for each user',
    phoneNumber VARCHAR(15) NOT NULL UNIQUE COMMENT 'Mobile money subscriber MSISDN',
    firstName VARCHAR(50) NOT NULL COMMENT 'User first name',
    lastName VARCHAR(50) NOT NULL COMMENT 'User last name',
    dateOfBirth DATE COMMENT 'User date of birth',
    gender VARCHAR(10) COMMENT 'User gender',
    kycTier INT DEFAULT 1 CHECK (kycTier IN (1, 2, 3)) COMMENT 'KYC verification level',
    momoBalance DECIMAL(12, 2) DEFAULT 0.00 CHECK (momoBalance >= 0) COMMENT 'Current mobile money balance'
) COMMENT = 'Stores registered MoMo system users';

CREATE TABLE transactions (
    transactionId INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique identifier for each transaction',
    transactionTimestamp DATETIME NOT NULL COMMENT 'Date and time the transaction occurred',
    status VARCHAR(20) NOT NULL COMMENT 'Transaction status e.g. success, failed, pending',
    senderId INT NOT NULL COMMENT 'FK to the sending user',
    receiverId INT NOT NULL COMMENT 'FK to the receiving user',
    currentAmount DECIMAL(12,2) NOT NULL CHECK (currentAmount >= 0) COMMENT 'Transaction amount',
    transactionFee DECIMAL(10,2) DEFAULT 0.00 CHECK (transactionFee >= 0) COMMENT 'Fee charged for the transaction',
    governmentTax DECIMAL(10,2) DEFAULT 0.00 CHECK (governmentTax >= 0) COMMENT 'Government tax applied',
    senderBalanceAfter DECIMAL(12,2) COMMENT 'Sender balance after transaction',
    receiverBalanceAfter DECIMAL(12,2) COMMENT 'Receiver balance after transaction',
    referenceText VARCHAR(255) COMMENT 'Free-text reference or note for the transaction',
    FOREIGN KEY (senderId) REFERENCES users(userId),
    FOREIGN KEY (receiverId) REFERENCES users(userId)
) COMMENT = 'Stores MoMo transaction records';

CREATE TABLE Transaction_Categories (
    transCategoryId INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique identifier for transaction category',
    transCategoryName VARCHAR(50) NOT NULL COMMENT 'Name of the category',
    description VARCHAR(255) COMMENT 'Description of the category'
) COMMENT = 'Stores categories for classifying transactions';