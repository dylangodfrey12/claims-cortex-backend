-- Create the Users table
CREATE TABLE Account (
    Username VARCHAR(255) NOT NULL,
    Password VARCHAR(255) NOT NULL,
    Address VARCHAR(255) NOT NULL,
    FullName VARCHAR(255) NOT NULL,
    Email VARCHAR(255)NOT NULL,
    PRIMARY KEY (Username)
);

-- Optionally, to ensure Email is unique
-- ALTER TABLE Users ADD CONSTRAINT UC_Email UNIQUE (Email);
