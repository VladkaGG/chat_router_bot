def create_tables(cursor):
    with cursor as curs:
        curs.execute('''CREATE TABLE IF NOT EXISTS "Groups"(
        "Id" SERIAL PRIMARY KEY NOT NULL,
        "Name" VARCHAR(50) NOT NULL,
        "Parent_group" INT REFERENCES "Groups" ("Id") ON DELETE CASCADE);''')

    with cursor as curs:
        curs.execute('''CREATE TABLE IF NOT EXISTS "Chats"(
        "Id" SERIAL PRIMARY KEY NOT NULL,
        "Name" VARCHAR(50) NOT NULL,
        "Ref" VARCHAR(50),
        "Group_id" INT REFERENCES "Groups" ("Id") ON DELETE CASCADE);''')

    with cursor as curs:
        curs.execute('''CREATE TABLE IF NOT EXISTS "Users"(
        "Id" SERIAL PRIMARY KEY NOT NULL,
        "Name" VARCHAR(50) NOT NULL,
        "Group_id" INT REFERENCES "Groups" ("Id") ON DELETE CASCADE);''')