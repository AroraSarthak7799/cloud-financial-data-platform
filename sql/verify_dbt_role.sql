-- Check current Snowflake session context
SELECT
    CURRENT_USER() AS USER_NAME,
    CURRENT_ORGANIZATION_NAME() || '-' || CURRENT_ACCOUNT_NAME() AS ACCOUNT_IDENTIFIER,
    CURRENT_ROLE() AS CURRENT_ROLE,
    CURRENT_REGION() AS REGION;

-- Switch to the restricted dbt role
USE ROLE DBT_TRANSFORM_ROLE;

-- Verify warehouse and database access
USE WAREHOUSE CLOUD_FINANCIAL_WH;
USE DATABASE CLOUD_FINANCIAL_DB;

-- Verify the role can read RAW data
SELECT COUNT(*) AS CUSTOMER_ROW_COUNT
FROM RAW.CUSTOMERS;

-- Inspect privileges assigned to the role
SHOW GRANTS TO ROLE DBT_TRANSFORM_ROLE;