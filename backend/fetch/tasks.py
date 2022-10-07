from background_task import background


@background(schedule=5)
def update_subroutine(database_id: int):
    print(f"Updating database {database_id}")
    pass
