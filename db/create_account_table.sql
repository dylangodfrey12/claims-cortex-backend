CREATE TABLE Account (
    AccountID UNIQUEIDENTIFIER NOT NULL DEFAULT NEWID(),
    Username VARCHAR(255) NOT NULL,
    Password VARCHAR(255) NOT NULL,
    Address VARCHAR(255) NOT NULL,
    FullName VARCHAR(255) NOT NULL,
    Email VARCHAR(255) NOT NULL,
    PRIMARY KEY (AccountID)
);
