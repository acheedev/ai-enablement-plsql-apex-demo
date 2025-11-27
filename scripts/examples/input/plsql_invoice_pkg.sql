CREATE OR REPLACE PACKAGE invoice_pkg AS
  -- Public API for basic invoice operations

  -- Create a new invoice and return its ID
    FUNCTION create_invoice (
        p_customer_id   IN NUMBER,
        p_invoice_date  IN DATE,
        p_currency_code IN VARCHAR2 DEFAULT 'USD'
    ) RETURN NUMBER;

  -- Add a line to an invoice
    PROCEDURE add_line (
        p_invoice_id  IN NUMBER,
        p_line_number IN NUMBER,
        p_description IN VARCHAR2,
        p_quantity    IN NUMBER,
        p_unit_price  IN NUMBER
    );

  -- Apply a payment to an invoice
    PROCEDURE apply_payment (
        p_invoice_id IN NUMBER,
        p_payment_id IN NUMBER,
        p_amount     IN NUMBER
    );

  -- Get current open balance of an invoice
    FUNCTION get_balance (
        p_invoice_id IN NUMBER
    ) RETURN NUMBER;

  -- Cancel an invoice (soft cancel)
    PROCEDURE cancel_invoice (
        p_invoice_id IN NUMBER,
        p_reason     IN VARCHAR2
    );
END invoice_pkg;
/
show errors;

CREATE OR REPLACE PACKAGE BODY invoice_pkg AS

    FUNCTION create_invoice (
        p_customer_id   IN NUMBER,
        p_invoice_date  IN DATE,
        p_currency_code IN VARCHAR2 DEFAULT 'USD'
    ) RETURN NUMBER IS
        l_invoice_id invoices.invoice_id%TYPE;
    BEGIN
        INSERT INTO invoices (
            invoice_id,
            customer_id,
            invoice_date,
            currency_code,
            status,
            created_at
        ) VALUES ( invoices_seq.NEXTVAL,
                   p_customer_id,
                   p_invoice_date,
                   p_currency_code,
                   'OPEN',
                   systimestamp ) RETURNING invoice_id INTO l_invoice_id;

        RETURN l_invoice_id;
    EXCEPTION
        WHEN OTHERS THEN
      -- In a real system, you'd call a logging package instead of dbms_output
            dbms_output.put_line('create_invoice failed: ' || sqlerrm);
            RAISE;
    END create_invoice;


    PROCEDURE add_line (
        p_invoice_id  IN NUMBER,
        p_line_number IN NUMBER,
        p_description IN VARCHAR2,
        p_quantity    IN NUMBER,
        p_unit_price  IN NUMBER
    ) IS
    BEGIN
        IF p_quantity <= 0 THEN
            raise_application_error(
                -20001,
                'Quantity must be > 0'
            );
        END IF;
        INSERT INTO invoice_lines (
            invoice_id,
            line_number,
            description,
            quantity,
            unit_price,
            line_total
        ) VALUES ( p_invoice_id,
                   p_line_number,
                   p_description,
                   p_quantity,
                   p_unit_price,
                   p_quantity * p_unit_price );
    EXCEPTION
        WHEN dup_val_on_index THEN
            raise_application_error(
                -20002,
                'Duplicate line number for invoice'
            );
        WHEN OTHERS THEN
            dbms_output.put_line('add_line failed: ' || sqlerrm);
            RAISE;
    END add_line;


    PROCEDURE apply_payment (
        p_invoice_id IN NUMBER,
        p_payment_id IN NUMBER,
        p_amount     IN NUMBER
    ) IS
        l_balance_before NUMBER;
    BEGIN
        IF p_amount <= 0 THEN
            raise_application_error(
                -20003,
                'Payment amount must be > 0'
            );
        END IF;
        l_balance_before := get_balance(p_invoice_id);
        INSERT INTO invoice_payments (
            invoice_id,
            payment_id,
            amount,
            applied_at
        ) VALUES ( p_invoice_id,
                   p_payment_id,
                   p_amount,
                   systimestamp );

        IF get_balance(p_invoice_id) < 0 THEN
            raise_application_error(
                -20004,
                'Overpayment detected for invoice'
            );
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            dbms_output.put_line('apply_payment failed: ' || sqlerrm);
            RAISE;
    END apply_payment;


    FUNCTION get_balance (
        p_invoice_id IN NUMBER
    ) RETURN NUMBER IS
        l_total_lines NUMBER;
        l_total_paid  NUMBER;
    BEGIN
        SELECT nvl(
            sum(line_total),
            0
        )
          INTO l_total_lines
          FROM invoice_lines
         WHERE invoice_id = p_invoice_id;

        SELECT nvl(
            sum(amount),
            0
        )
          INTO l_total_paid
          FROM invoice_payments
         WHERE invoice_id = p_invoice_id;

        RETURN l_total_lines - l_total_paid;
    EXCEPTION
        WHEN no_data_found THEN
            RETURN 0;
    END get_balance;


    PROCEDURE cancel_invoice (
        p_invoice_id IN NUMBER,
        p_reason     IN VARCHAR2
    ) IS
    BEGIN
        UPDATE invoices
           SET status = 'CANCELLED',
               cancel_reason = p_reason,
               cancelled_at = systimestamp
         WHERE invoice_id = p_invoice_id;

        IF SQL%rowcount = 0 THEN
            raise_application_error(
                -20005,
                'Invoice not found'
            );
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            dbms_output.put_line('cancel_invoice failed: ' || sqlerrm);
            RAISE;
    END cancel_invoice;

END invoice_pkg;
/
show errors;