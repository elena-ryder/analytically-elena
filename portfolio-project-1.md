---
layout: post
title: "How to tell a story"
tagline: Single Page
date: 2016-05-26 13:23
categories: [Storyline]
tags: [Storyline, How To, Tips]
image: img-03.jpg
---

This is a step-by-step process on a project utilizing the AdventureWorks sample database provided by Microsoft. Read along as I start from initiating the database, finding and extracting relevant data, and putting that data to use to create a Power BI report.


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

  <i>While exploring the database I saw the Person.Person table contained valuable customer name information, so I tried looking for a relationship to connect it back to Sales.Customer.</i>

  <i>I noticed a lot of null values in the PersonID column for Sales.Customer and decided to investigate.</i>

9. Query Input:

    ```sql
    USE AdventureWorks2022

    SELECT COUNT(*) AS quantity_null,
        (SELECT COUNT(*)
        FROM Sales.Customer
        WHERE PersonID IS NOT NULL) AS quantity_not_null
    FROM Sales.Customer
    WHERE PersonID IS NULL;
    ```

10. Execute

    | quantity_null | quantity_not_null |
    |---------------|-------------------|
    | 701           | 19119             |


  <i>These null values weren't too concerning to me and are actually because some of the customers are stored as BussinessEntityID and not PersonID which is an intentional feature of this database. 
  
  I expected to find PersonID as a primary key in the Person.Person table but was unable to find it. I used the system views in SSMS and decided to search for all columns containing the name "PersonID".</i>

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

<i>Initially, I thought this meant I would need to link Sales.Customer and Person.Person using Person.BusinessEntityContact as an intermediary, but I was getting some ill results. Eventually, after using the internet as a resource and reviewing an entity relationship diagram for AdventureWorks, I discovered that BussinessEntityID in Person.Person is equivalent to PersonID in Sales.Customer.

I was concerned about the integrity of the relationship between PersonID and BusinessEntityID, due to the possibility that they could be similar but very different indicators. I ran a query to verify.</i>

13. Query Input:    

    ```SQL
    USE AdventureWorks2022

    SELECT PersonID, BusinessEntityID
    FROM Sales.Customer AS c
    FULL OUTER JOIN Person.Person AS p
    ON c.PersonID = p.BusinessEntityID
    WHERE PersonID <> BusinessEntityID; -- Checks if there are any instances where these do not match
    ```
14. Execute

| PersonID | BusinessEntityID |
|----------|------------------|

<i>I was relieved to see that the query returned an empty table. Using these same methods I also verified the connection between Sales.Customer and Sales.Store, as store locations are also considered customers.</i>


14. Identify relationship between:

    * `Sales.Customer` and `Person.Person` on PersonID = BusinessEntityID
    * `Sales.Customer` and `Sales.Store` on StoreID = BusinessEntityID
    <br>
    <br>



17. Identify the following tables for use:

    * `Sales.SalesOrderHeader`,
    * `Sales.SalesOrderDetail`,
    * `Sales.Customer`,
    * `Sales.SalesTerritory`,
    * `Sales.Store`,
    * `Production.Product`,
    * `Production.ProductSubcategory`,
    * `Product.ProductCategory`,
    * `Person.Person`

<i>Lastly, before I finish up in SQL Server Management Studio, I'm going to create some views to consolidate and denormalize my Sales, Customer, and Product tables and prepare them to conform to a star schema in my Power BI data model.</i>

18. Query Inputs:

    ```SQL
    CREATE VIEW Product_Dim AS

    SELECT		ProductID, 
                Name, 
                ProductNumber, 
                Color, 
                Size, 
                StandardCost, 
                ListPrice, 
                p1.ProductSubcategoryID, 
                p2.ProductCategoryID, 
                SubcategoryName,
                CategoryName
    FROM AdventureWorks2022.Production.Product AS p1
    LEFT JOIN   (
                SELECT ProductSubcategoryID, ProductCategoryID, Name AS SubcategoryName 
                FROM AdventureWorks2022.Production.ProductSubcategory
                ) AS p2
    ON p1.ProductSubcategoryID = p2.ProductSubcategoryID
    LEFT JOIN   (
                SELECT ProductCategoryID, Name AS CategoryName
                FROM AdventureWorks2022.Production.ProductCategory
                ) AS p3
    ON p2.ProductCategoryID = p3.ProductCategoryID;
    ```
    <br>

    ```SQL
    CREATE VIEW Customer_Dim AS

    SELECT  CustomerID,
            PersonID,
            StoreID,
            TerritoryID,
            PersonType,
            Title,
            FirstName,
            MiddleName,
            LastName,
            Suffix,
            s.Name AS BusinessName
    FROM AdventureWorks2022.Sales.Customer AS c
    LEFT JOIN AdventureWorks2022.Person.Person AS p
    ON c.PersonID = p.BusinessEntityID
    LEFT JOIN AdventureWorks2022.Sales.Store AS s
    ON c.StoreID = s.BusinessEntityID;
    ```
    <br>

    ```SQL
    CREATE VIEW Sales_Fact AS

    SELECT	s1.SalesOrderID,
            OrderDate,
            CustomerID,
            SalesPersonID,
            TerritoryID,
            SubTotal,
            TaxAmt,
            Freight,
            TotalDue,
            OrderQty,
            ProductID,
            UnitPrice,
            UnitPriceDiscount
    FROM AdventureWorks2022.Sales.SalesOrderHeader AS s1
    LEFT JOIN AdventureWorks2022.Sales.SalesOrderDetail AS s2
    ON s1.SalesOrderID = s2.SalesOrderID;
    ```

### **Loading and Modelling the Data**

1. Open Power BI Desktop

2. Select File > Options > Options and Settings

3. Under the "Current File" section, select "Data Load"

4. Deselect "Autodetect new relationships after data is loaded" and "Auto date/time"

<i>This allows me to create my own relationships in my model and my own date table.</i>

5. Click "OK"

6. Select File > Save As > Browse this device

7. Save file as `AdventureWorksAnalysis.pbix`

8. Select "Get Data" from the Home Ribbon and choose "SQL Server"

9. Server: localhost\SQLEXPRESS Database: AdventureWorks2022 Data Connectivity Mode: Import

10. In the Navigator, select the following tables

    * `Customer_Dim`,
    * `Product_Dim`,
    * `Sales_Fact`,
    * `Sales.SalesTerritory`,
    <br><br>

11. Click "Transform Data"

12. Sales_Fact - Format UnitPriceDiscount as Percentage

13. Sales.SalesTerritory - Rename as Territory_Dim - Remove columns:

    * rowguid
    * ModifiedDate
    <br><br>

15. Close and Apply

16. In the Data tab, open Sales_Fact table

17. Sort OrderDate by ASC then DESC to find the MIN and MAX OrderDate

<i>I did this to notate the date range for our data model and use that information for the next step.</i>

18. In the Home ribbon select "New Table"

19. DAX Input: 
 
    ```dax
    Date_Dim =
    ADDCOLUMNS(
        CALENDAR(DATE(2011,5,31), DATE(2014,6,30)),
        "Year", YEAR([Date]),
        "Quarter", "Q" & FORMAT([Date], "Q"),
        "Month", FORMAT([Date], "mmmm"),
        "Week", WEEKNUM([Date]),
        "Day", DAY([Date]),
        "Day of Week", FORMAT([Date], "dddd")
    )
    ```

<i>Having a dedicated date table like this is a best practice and may be of use later.</i>

20. In the Model tab, create the following relationships:

    * Product_Dim `ProductID` -> One-to-Many -> Sales_Fact `ProductID`
    * Date_Dim `Date` -> One-to-Many -> Sales_Fact `OrderDate`
    * Customer_Dim `CustomerID` -> One-to-Many -> Sales_Fact `CustomerID`
    * Territory_Dim `TerritoryID` -> One-to-Many -> Sales_Fact `TerritoryID`
    <br><br>

![Alt text](data-model.jpg)

### **Calculated Columns and Measures**

1. Create a blank new table for storing DAX measures - Input:

    ```dax
    Measure_Table = 
    ```

2. Create the first DAX measure for the Measure_Table - Input:

    ```dax
    Revenue =  
    SUMX(
        Sales_Fact,
        Sales_Fact[OrderQty] * Sales_Fact[UnitPrice] * (1 - Sales_Fact[UnitPriceDiscount])
    )
    ```
3. Select empty column from Measure_Table and selecet "Hide in Report View"

<i>I would normally choose Delete from model here but wasn't getting the option. Either way, this will promote the Measure_Table to the top of the list and give it a calculator icon to designate it explicitly for measures.</i>

4. Create the following DAX measures:

* Revenue - Input:

    ```dax
    Revenue = 
    SUMX(
        Sales_Fact,
        Sales_Fact[OrderQty] * Sales_Fact[UnitPrice] * (1 - Sales_Fact[UnitPriceDiscount])
    )
    ```

* All Revenue - Input:

    ```dax
    All Revenu = 
    CALCULATE(
        [Revenue],
        ALL(Sales_Fact)
    )
    ```
    
* % of All Revenue - Input:

    ```dax
    % of All Revenue = 
    DIVIDE(
        [Revenue], [All Revenue]
    )
    ```


* Profit - Input:

    ```dax
    Profit = 
    SUMX(
        Sales_Fact,
        [Revenue] - (Sales_Fact[OrderQty] * RELATED(Product_Dim[StandardCost]))
    )
    ```

* All Profit - Input:

    ```dax
    All Profit = 
    CALCULATE(
        [Profit],
        ALL(Sales_Fact)
    )
    ```

* % of All Profit - Input:

    ```dax
    % of All Profit = 
    DIVIDE(
        [Profit], [All Profit]
    )
    ```

* Profit Margin - Input:

    ```dax
    Profit Margin = 
    Divide(
        [Profit], [Revenue]
    )
    ```
* Total Cost - Input:

    ```dax
    Total Cost = 
    [Revenue] - [Profit]
    ```

5. Create calculated column in Customer_Dim for name concatenation - Input:

    ```dax
    FullName = 
    TRIM(
        Customer_Dim[Title] & " " & 
        Customer_Dim[FirstName] & " " & 
        Customer_Dim[MiddleName] & " " &
        Customer_Dim[LastName] & " " & 
        Customer_Dim[Suffix]
    )
    ```

<i>At this point I was doing some testing with a KPI chart and retroactively updated all of the currency columns to use 2 decimal values. This increased readability. Additionally, I wasn't getting the Trend Axis sorting that I wanted out of the Month column, so I:</i>

6. Create calculated column in Date_Dim for Start of Month - Input:

    ```dax
    Start of Month = 
    STARTOFMONTH(
        Date_Dim[Date]
    )
    ```
<i>This worked out much better and gave me the proper trending line chart in the KPI background that I was looking for.</i>

7. Create Hierarchy from Year - Add Quarter, Month, Week, Date

<i>I continued to have issues with the dates and Start of Month on my KPI charts. While digging deeper into the data, I found that despite the fact that the month of June 2014 was fully populated with Sales data, all of those orders were significantly low value. I cross referenced the SQL database to confirm what I was seeing here.</i>

8. Input:

    ```sql
    USE AdventureWorks2022;
    GO

    SELECT	ROUND(SUM(SubTotal),2) AS June2014_Revenue,
            (
                SELECT ROUND(SUM(SubTotal),2)
                FROM Sales.SalesOrderHeader 
                WHERE OrderDate BETWEEN '2014-05-01' AND '2014-05-31'
            ) AS May2014_Revenue
    FROM Sales.SalesOrderHeader 
    WHERE OrderDate BETWEEN '2014-06-01' AND '2014-06-30';
    ```
9. Execute

    | June2014_Revenue | May2014_Revenue |
    |-----------------:|----------------:|
    |         49005.84 |      5366674.97 |

<i>Wow! May's numbers were in the millions and June's were in the 10's of thousands. It's as if AdventureWorks as a company had gone bankrupt and liquidated all assets. This wasn't helping me get what I wanted out of this dataset, so I decided to exclude June 2014.</i>

10. Apply Report-Level Filter for "Start of Month," selecting all options except for 6/1/2014

11. 

### **On Power BI Service**

Select Workspaces > New Workspace > Name it "Portfolio Project 1" No Description, Select Apply.

In Power BI, select "Publish" from the Home Ribbon.

Choose "Portfolio Project 1," click "Select," and "Got it"

Open `AdventureWorksAnalysis` in Power BI Service, verify everything looks good

Click the Edit button at the top ribbon.

Once in Edit Mode, choose File > Publish to Web

Select "Create Embed Code" and "Publish"

Final URL: 

https://app.powerbi.com/view?r=eyJrIjoiNGUxNWMwODEtMmQzMC00OWZlLWE4MTktY2Y0ZjkxYzc0MWYxIiwidCI6ImQ3MWZkNmE4LThiMDktNDUzZC04NTIzLWJlMTY2NmVhOWY2ZiIsImMiOjF9

<iframe title="AdventureWorksAnalysis - Report" width="600" height="373.5" src="https://app.powerbi.com/view?r=eyJrIjoiNGUxNWMwODEtMmQzMC00OWZlLWE4MTktY2Y0ZjkxYzc0MWYxIiwidCI6ImQ3MWZkNmE4LThiMDktNDUzZC04NTIzLWJlMTY2NmVhOWY2ZiIsImMiOjF9" frameborder="0" allowFullScreen="true"></iframe>
