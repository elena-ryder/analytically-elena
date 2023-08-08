---
layout: default
---

### **Set up Dummy Database**

**Download `AdventureWorks2022.bak` file from** [AdventureWorks Sample Databases](https://learn.microsoft.com/en-us/sql/samples/adventureworks-install-configure)

#### **Steps:**

1. Place file into `C:\Program Files\Microsoft SQL Server\MSSQL16.SQLEXPRESS\MSSQL\Backup`
2. Open Microsoft SQL Server Studio
3. Right-click "Databases" and select "Restore Database..."
4. Select "Device" under Source and select ellipses on right
5. Select "Add"
6. Double-click `AdventureWorks2022.bak`
7. Click "OK"
8. Verify that "Restore" is checked. Click "OK"
9. Select "New Query" from tool ribbon - Query Input:
   ```sql
   USE AdventureWorks2022

   SELECT TOP 1 *
   FROM Sales.Customer;
   ```
10. Execute

    | CustomerID | PersonID | StoreID | TerritoryID | AccountNumber | rowguid                                | ModifiedDate              |
    |------------|----------|---------|-------------|---------------|----------------------------------------|---------------------------|
    | 1          | NULL     | 934     | 1           | AW00000001    | 3F5AE95E-B87D-4AED-95B4-C3797AFCB74F    | 2014-09-12 11:15:07.263   |

**Success! AdventureWorks2022 Database is Ready**

### **Exploratory Analysis**

**Define the Objective:** <i>Prompt is "Analyze the sales data to understand the performance of different products across various regions, identify top customers, and assess sales trends over time."

I need to identify which tables I will be using for my analysis to later import into Power BI.</i>

#### **Steps:**

1. Determine need for sales, product, customer, and region tables

2. Visually scan database in Object Explorer

3. Identify possible fact table for model - Query Input:
   ```sql
   USE AdventureWorks2022

   SELECT TOP 1 *
   FROM Sales.SalesOrderHeader;
   ```
4. Execute

    | SalesOrderID | RevisionNumber | OrderDate                 | DueDate                   | ShipDate                  | Status | OnlineOrderFlag | SalesOrderNumber | PurchaseOrderNumber | AccountNumber   | CustomerID | SalesPersonID | TerritoryID | BillToAddressID | ShipToAddressID | ShipMethodID | CreditCardID | CreditCardApprovalCode | CurrencyRateID | SubTotal    | TaxAmt    | Freight  | TotalDue     | Comment | rowguid                                 | ModifiedDate           |
    |--------------|----------------|---------------------------|---------------------------|---------------------------|--------|-----------------|------------------|---------------------|-----------------|------------|---------------|-------------|-----------------|------------------|--------------|--------------|------------------------|----------------|-------------|------------|----------|---------------|---------|----------------------------------------|------------------------|
    | 43659        | 8              | 2011-05-31 00:00:00.000   | 2011-06-12 00:00:00.000   | 2011-06-07 00:00:00.000   | 5      | 0               | SO43659          | PO522145787         | 10-4020-000676   | 29825      | 279           | 5           | 985             | 985               | 5            | 16281        | 105041Vi84182          | NULL           | 20565.6206  | 1971.5149 | 616.0984 | 23153.2339    | NULL    | 79B65321-39CA-4115-9CBA-8FE0903E12E6   | 2011-06-07 00:00:00.000 |


5. Discover multiple foreign keys in Sales.SalesOrderHeader. Examples:

    * OrderDate
    * CustomerID
    * SalesPersonID
    * TerritoryID
    * ShipToAddressID
    <br>
    <br>

6. Explore individual Tables in Object Explorer

7. Expand "Keys" folders to view primary keys

  <i>During this section, I encountered composite keys, an interesting database concept that I was unfamiliar with. This allowed me to gain a better understanding of the AdventureWorks data model and relational databases as a whole.</i>

8. Identify relationships between:

    * `Sales.SalesOrderHeader` and `Sales.SalesOrderDetail` on SalesOrderID,
    * `Sales.SalesOrderDetail` and `Production.Product` on ProductID,
    * `Production.Product` and `Production.ProductSubcategory` on ProductSubcategoryID,
    * `Production.ProductSubcategory` and `Production.ProductCategory` on ProductCategoryID
    * `Sales.SalesOrderHeader` and `Sales.Customer` on CustomerID,
    * `Sales.SalesOrderHeader` and `Sales.Territory` on TerritoryID
    <br>
    <br>

  <i>I noticed a lot of null values in the PersonID column for Sales.Customer and so I decided to investigate."</i>

9. Query Input:

    ```sql
    USE AdventureWorks2022

    SELECT COUNT(*) AS quantity_null,
        (SELECT COUNT(*)
        FROM Sales.Customer
        WHERE PersonID IS NOT NULL) AS quantity_not_null
    FROM Sales.Customer
    WHERE PersonID IS NULL 
    ```

10. Execute

    | quantity_null | quantity_not_null |
    |---------------|-------------------|
    | 701           | 19119             |


  <i>Then I expected to find PersonID as a primary key in the Person.Person table but was unable to find it. I decided to run a query to search for all columns in the database called 'PersonID'</i>

11. Query Input:

    ```sql
    USE AdventureWorks2022

    SELECT TABLE_NAME, COLUMN_NAME
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE COLUMN_NAME = 'PersonID';
    ```

12. Execute

    | TABLE_NAME            | COLUMN_NAME |
    |-----------------------|-------------|
    | BusinessEntityContact | PersonID    |
    | Customer              | PersonID    |


13. Identify relationships between:

    * `Sales.Customer` and `Person.BusinessEntityContact` on PersonID,
    * `Person.BusinessEntityContact` and `Person.Person` on BusinessEntityID
    <br>
    <br>

14. Query Input:

    ```sql
    USE AdventureWorks2022

    SELECT TOP 1 *
    FROM Person.Person;
    ```

15. Execute

    | BusinessEntityID | PersonType | NameStyle | Title | FirstName | MiddleName | LastName | Suffix | EmailPromotion | AdditionalContactInfo | Demographics                                                                                   | rowguid                              | ModifiedDate           |    
    |------------------|------------|-----------|-------|-----------|------------|----------|--------|----------------|-----------------------|------------------------------------------------------------------------------------------------|--------------------------------------|------------------------|
    | 1                | EM         | 0         | NULL  | Ken       | J          | Sánchez  | NULL   | 0              | NULL                  | &lt;IndividualSurvey xmlns="http://schemas.microsoft.com/sqlserver/2004/07/adventure-works/IndividualSurvey"&gt;&lt;TotalPurchaseYTD&gt;0&lt;/TotalPurchaseYTD&gt;&lt;/IndividualSurvey&gt; | 92C4279F-1207-48A3-8448-4636514EB7E2 | 2009-01-07 00:00:00.000 |


<i>This table contains the customer names I was looking for.</i>

16. Identify the following tables for use:

    * `Sales.SalesOrderHeader`,
    * `Sales.SalesOrderDetail`,
    * `Sales.Customer`,
    * `Sales.SalesTerritory`,
    * `Sales.Store`,
    * `Production.Product`,
    * `Production.ProductSubcategory`,
    * `Product.ProductCategory`,
    * `Person.BusinessEntityContact`,
    * `Person.Person`

### **End**