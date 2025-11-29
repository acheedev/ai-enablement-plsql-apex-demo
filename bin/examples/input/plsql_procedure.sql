CREATE OR REPLACE PROCEDURE upsert_persons_merge (
    p_limit IN PLS_INTEGER DEFAULT 1000
) AS
    TYPE t_stg_persons_tab IS
        TABLE OF gtt_stg_persons%rowtype;
    t_stg_persons_batch t_stg_persons_tab;
    l_start_time        PLS_INTEGER;
    l_end_time          PLS_INTEGER;
    l_batch_fails       PLS_INTEGER := 0;
    l_num_errors        PLS_INTEGER := 0;
    l_num_success       PLS_INTEGER := 0;
    l_num_process       PLS_INTEGER := 0;
    l_duration          PLS_INTEGER := 0;
    CURSOR c_stg_persons IS
    SELECT *
      FROM stg_persons_load
     ORDER BY src_id;

BEGIN
    l_start_time := dbms_utility.get_time;
    OPEN c_stg_persons;
    LOOP
        FETCH c_stg_persons
        BULK COLLECT INTO t_stg_persons_batch LIMIT p_limit;
        EXIT WHEN t_stg_persons_batch.count = 0;
        BEGIN
            FORALL i IN t_stg_persons_batch.first..t_stg_persons_batch.last --SAVE EXCEPTIONS

                INSERT INTO gtt_stg_persons (
                    src_id,
                    person_id,
                    first_name,
                    last_name,
                    email,
                    created_at
                ) VALUES ( t_stg_persons_batch(i).src_id,
                           t_stg_persons_batch(i).person_id,
                           t_stg_persons_batch(i).first_name,
                           t_stg_persons_batch(i).last_name,
                           t_stg_persons_batch(i).email,
                           t_stg_persons_batch(i).created_at );

            dbms_output.put_line('Batch size: ' || t_stg_persons_batch.count);
            MERGE INTO persons p
            USING (
                SELECT *
                  FROM gtt_stg_persons
                 WHERE email IS NOT NULL
            ) s ON ( s.email = p.email )
            WHEN MATCHED THEN UPDATE
            SET p.person_id = s.person_id,
                p.first_name = s.first_name,
                p.last_name = s.last_name,
                p.created_at = s.created_at
            WHEN NOT MATCHED THEN
            INSERT (
                person_id,
                first_name,
                last_name,
                email,
                created_at )
            VALUES
                ( nvl(
                    s.person_id,
                    person_seq.nextval
                ),
                  s.first_name,
                  s.last_name,
                  s.email,
                  s.created_at );

            dbms_output.put_line('First merge: ' || SQL%rowcount);
            MERGE INTO persons p
            USING (
                SELECT *
                  FROM gtt_stg_persons
                 WHERE email IS NULL
                   AND person_id IS NOT NULL
            ) s ON ( p.person_id = s.person_id )
            WHEN MATCHED THEN UPDATE
            SET p.person_id = s.person_id,
                p.first_name = s.first_name,
                p.last_name = s.last_name,
                p.email = s.email,
                p.created_at = s.created_at
            WHEN NOT MATCHED THEN
            INSERT (
                person_id,
                first_name,
                last_name,
                email,
                created_at )
            VALUES
                ( nvl(
                    s.person_id,
                    person_seq.nextval
                ),
                  s.first_name,
                  s.last_name,
                  NULL,
                  s.created_at );

            COMMIT;
            dbms_output.put_line('Second merge: ' || SQL%rowcount);
        END;
        dbms_output.put_line('FORALL completed with '
                             || l_batch_fails || ' error(s).');
    END LOOP;
    COMMIT;
    dbms_output.put_line('FORALL completed with '
                         || l_batch_fails || ' error(s).');
    --l_end_time := DBMS_UTILITY.GET_TIME;
    --l_duration := (l_end_time - l_start_time) * 10;
    --print_report(l_num_process, l_num_success, l_num_errors, l_duration);
END;