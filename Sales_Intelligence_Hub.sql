--- creating branches table
create table branches (
branch_id serial primary key, 
branch_name varchar(100), 
branch_admin_name varchar(100)
);

--- creating customer_sales table
create table customer_sales (
sale_id serial primary key,
branch_id int,
date date,
name varchar(100),
mobile_number varchar(15),
product_name varchar(30),
gross_sales decimal(12,2),
received_amount decimal(12,2),
pending_Amount decimal(12,2) generated always as (gross_sales - received_amount) stored,
status varchar(10) generated always as (case when gross_sales = received_amount then 'close' else 'open' end) stored,
constraint fk_branch_id
foreign key(branch_id) 
references branches(branch_id)
);

--- creating users table
create table users (
user_id serial primary key,
username varchar(100),
password varchar(255),
branch_id int,
role varchar (20) not null,
email varchar(255) unique,
constraint fk_branch_id
foreign key(branch_id) 
references branches(branch_id)
);

--- creating payment_splits table
create table payment_splits (
payment_id serial primary key,
sale_id int,
payment_date date,
amount_paid decimal(12,2),
payment_method varchar(50),
constraint fk_sale_id
foreign key (sale_id) 
references customer_sales(sale_id)
);

--- create trigger function

CREATE OR REPLACE FUNCTION sales_payment_update()
RETURNS TRIGGER AS $$
BEGIN

    
    IF (TG_OP = 'INSERT') THEN
        UPDATE customer_sales

        SET received_amount = COALESCE(received_amount, 0) + NEW.amount_paid
        WHERE sale_id = NEW.sale_id;
        RETURN NEW;


    ELSIF (TG_OP = 'UPDATE') THEN
        IF OLD.sale_id IS DISTINCT FROM NEW.sale_id THEN
            UPDATE customer_sales 
            SET received_amount = COALESCE(received_amount, 0) - OLD.amount_paid 
            WHERE sale_id = OLD.sale_id;
            
            UPDATE customer_sales 
            SET received_amount = COALESCE(received_amount, 0) + NEW.amount_paid 
            WHERE sale_id = NEW.sale_id;
        ELSE
            UPDATE customer_sales
            SET received_amount = COALESCE(received_amount, 0) - OLD.amount_paid + NEW.amount_paid
            WHERE sale_id = NEW.sale_id;
        END IF;
        RETURN NEW;


    ELSIF (TG_OP = 'DELETE') THEN
        UPDATE customer_sales
        SET received_amount = COALESCE(received_amount, 0) - OLD.amount_paid
        WHERE sale_id = OLD.sale_id;
        RETURN OLD;
    END IF;

END;
$$ LANGUAGE plpgsql;



--- Clean up any partial old trigger
DROP TRIGGER IF EXISTS trg_sales_payment_update ON payment_splits;

--- function to automatically change to payment_splits
CREATE TRIGGER trg_sales_payment_update
AFTER INSERT OR UPDATE OR DELETE ON payment_splits
FOR EACH ROW
EXECUTE FUNCTION sales_payment_update();



--- to fix serial issue
SELECT setval(pg_get_serial_sequence('customer_sales', 'sale_id'), COALESCE(MAX(sale_id), 0) + 1, false) FROM customer_sales;

SELECT setval(pg_get_serial_sequence('payment_splits', 'payment_id'), COALESCE(MAX(payment_id), 0) + 1, false) FROM payment_splits;

--- sample check

---TRUNCATE TABLE customer_sales, payment_splits, branches, users;
--delete from payment_splits where sale_id = 1005;
--delete from customer_sales where sale_id = 1005;

---insert into branches (branch_name, branch_admin_name) values ('selvam','super_admin');

---select * from branches;

--insert into customer_sales (branch_id,date,name,mobile_number,product_name,gross_sales,received_amount)
---values (1,'2026-04-01','arun','56457889','belt',25000.00,00.00);

--select * from customer_sales;

--insert into users (username, password, branch_id, role, email) values ('ram', '234567', 1, 'super_admin', 'ram@gmail.com');

--select * from users;

--insert into payment_splits (sale_id, payment_date, amount_paid, payment_method) values (1, '2026-04-03', 5000.00, 'cash');
--insert into payment_splits (sale_id, payment_date, amount_paid, payment_method) values (1, '2026-04-04', 7000.00, 'cash');
--insert into payment_splits (sale_id, payment_date, amount_paid, payment_method) values (1, '2026-04-05', 12000.00, 'cash');
--insert into payment_splits (sale_id, payment_date, amount_paid, payment_method) values (1, '2026-04-06', 1000.00, 'cash');

--select * from payment_splits;

