# Code Review: upsert_persons_merge.sql

## Summary

The procedure upsert_persons_merge processes rows from the stg_persons_load table in batches limited by the input parameter p_limit. For each batch, it bulk inserts data into the gtt_stg_persons global temporary table, then performs two MERGE operations into the persons table: the first merges rows with non-null emails matching on email, and the second merges rows with null emails but non-null person_id matching on person_id. The procedure commits after each batch and outputs batch size and merge row counts using dbms_output. Timing and error tracking variables are declared but not fully utilized, and some related code is commented out.

## Issue Categories

### Performance

- *(none detected)*

### Error Handling

- *(none detected)*

### Logic Correctness

- *(none detected)*

### Maintainability

- *(none detected)*

### Security

- *(none detected)*

### Data Integrity

- *(none detected)*

### Uncertainty / Open Questions

- *(none detected)*

## Risks

- No exception handling around the FORALL insert and MERGE statements may cause the entire batch to fail without detailed error reporting.
- Use of DBMS_OUTPUT for logging may not be suitable for large volumes of data or production environments.
- Potential data inconsistency if concurrent executions of this procedure occur due to use of a global temporary table without explicit session or transaction handling.
- The procedure assumes person_seq.nextval is available and correctly configured for generating new person_id values.
- No validation or cleansing of input data from stg_persons_load before insertion into gtt_stg_persons.
- The procedure commits inside the loop, which may lead to partial data processing if an error occurs in later batches.

## Assumptions

- gtt_stg_persons is a global temporary table structured identically to stg_persons_load.
- persons table has unique constraints or indexes on email and person_id to support MERGE operations.
- person_seq is a sequence object used to generate new person_id values.
- stg_persons_load contains the source data to be merged into persons.
- The procedure is intended to be run in a controlled environment where DBMS_OUTPUT is monitored.
- UNKNOWN: exact error handling strategy and requirements are not provided.
- UNKNOWN: the reason for separating merges based on email being NULL or NOT NULL is not explained.

## Refactor Suggestions (Optional / Future Work)

- This version does not yet include automated refactor output.
- Future versions may generate a behavior-preserving refactor using a dedicated prompt.
