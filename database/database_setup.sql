CREATE TABLE users (
    userId INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique identifier for each user',
    phoneNumber VARCHAR(15) NOT NULL UNIQUE COMMENT 'Mobile money subscriber MSISDN',
    firstName VARCHAR(50) NOT NULL COMMENT 'User first name',
    lastName VARCHAR(50) NOT NULL COMMENT 'User last name',
    dateOfBirth DATE COMMENT 'User date of birth',
    gender VARCHAR(10) COMMENT 'User gender',
    kycTier INT DEFAULT 1 CHECK (kycTier IN (1, 2, 3)) COMMENT 'KYC verification level',
    momoBalance DECIMAL(12, 2) DEFAULT 0.00 CHECK (momoBalance >= 0) COMMENT 'Current mobile money balance'
) COMMENT = 'Stores registered MoMo system users';