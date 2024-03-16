# Utilities

### Notes

Database schema used:

```sql
CREATE TABLE metrics(
    ID INT NOT NULL AUTO_INCREMENT,
    Source VARCHAR(100) NOT NULL,
    Technology VARCHAR(100) NOT NULL,
    Value DOUBLE NOT NULL,
    Recorded DATETIME NOT NULL,
    MetricType VARCHAR(100) NOT NULL,
    PRIMARY KEY(id)
);
```
