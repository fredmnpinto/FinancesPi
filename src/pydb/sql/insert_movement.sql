create or replace function insert_movement(i_actual_date date, i_effective_date date, i_description varchar, i_amount float, i_remaining_balance float)
RETURNS BOOLEAN AS $$
DECLARE already_existed BOOLEAN;
BEGIN
        select exists(select 1 from movement
            where actual_date = i_actual_date and
                  effective_date = i_effective_date and
                  description = i_description and
                  amount = i_amount and
                  remaining_balance = i_remaining_balance) into already_existed;

        if (already_existed) then
            return true;
        else
            insert into movement (actual_date, effective_date, description, amount, remaining_balance) values (i_actual_date, i_effective_date, i_description, i_amount, i_remaining_balance);
            return false;
        end if;
END;
$$  LANGUAGE plpgsql