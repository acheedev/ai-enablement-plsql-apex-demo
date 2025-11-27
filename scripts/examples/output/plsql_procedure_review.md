# Code Review: plsql_procedure.sql

## Summary

The procedure upsert_persons_merge processes rows from the stg_persons_load table in batches limited by the input parameter p_limit. For each batch, it bulk inserts data into the global temporary table gtt_stg_persons, then performs two MERGE operations into the persons table: the first merges rows with non-null emails matching on email, and the second merges rows with null emails but non-null person_id matching on person_id. The procedure outputs batch sizes and row counts after each merge, commits after each batch, and repeats until all rows are processed. Some timing and reporting code is present but commented out.

## Issue Categories

### Performance

- Using two separate MERGE statements on the same target table within each batch may cause unnecessary overhead and reduce performance.
- No use of SAVE EXCEPTIONS in FORALL, which could improve error handling and performance when bulk processing.

### Error Handling

- No exception handling block present, so any runtime errors will cause the procedure to fail without graceful recovery or logging.
- Variables l_batch_fails, l_num_errors, l_num_success, and l_num_process are declared but never updated or used for error tracking.

### Logic Correctness

- The procedure inserts all rows from stg_persons_load into gtt_stg_persons without clearing gtt_stg_persons between batches, potentially causing data duplication or incorrect merges.
- The use of NVL(s.person_id, person_seq.nextval) in the INSERT clause may cause inconsistent person_id assignment if s.person_id is NULL, especially since person_seq.nextval is called per row but not guaranteed unique in bulk operations.
- The second MERGE updates p.person_id = s.person_id even though p.person_id is the join key, which may cause unintended changes to primary key values.

### Maintainability

- Commented-out timing and reporting code at the end reduces code clarity and should be removed or properly implemented.
- Use of dbms_output.put_line for logging is not ideal for production environments and may clutter output.

### Security

- *(none detected)*

### Data Integrity

- No validation or checks on input data from stg_persons_load before inserting into gtt_stg_persons, which may lead to invalid or inconsistent data.
- Committing inside the loop after each batch may cause partial commits and complicate rollback in case of errors.

### Uncertainty / Open Questions

- Unclear if gtt_stg_persons is a global temporary table and whether it is session-specific or transaction-specific, which affects data visibility and cleanup.
- Unclear if person_seq.nextval usage in bulk inserts is safe and consistent without explicit sequencing control.

## Risks

- *(none explicitly identified)*

## Assumptions

- *(none explicitly identified)*

## Refactor Suggestions (Optional / Future Work)

- This version does not yet include automated refactor output.
- Future versions may generate a behavior-preserving refactor using a dedicated prompt.
