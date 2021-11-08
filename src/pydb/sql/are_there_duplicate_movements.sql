create or replace function are_there_duplicate_movements()
RETURNS BOOLEAN AS $$
    DECLARE does BOOLEAN;
BEGIN
    select EXISTS(select 1 from (select count(1) as num from movement m
        group by m.description, m.actual_date, m.effective_date, m.amount, m.person_id, m.remaining_balance) as ml
        where ml.num > 1) into does;

     return does;
END;
$$  LANGUAGE plpgsql