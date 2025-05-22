-- Create the first database
CREATE DATABASE IF NOT EXISTS aibomgen
    DEFAULT CHARACTER SET = 'utf8mb4';

-- Create the second database
CREATE DATABASE IF NOT EXISTS celery_results
    DEFAULT CHARACTER SET = 'utf8mb4';

-- Grant privileges to the user for both databases
GRANT ALL PRIVILEGES ON aibomgen.* TO 'aibomgen_user'@'%';
GRANT ALL PRIVILEGES ON celery_results.* TO 'aibomgen_user'@'%';
FLUSH PRIVILEGES;