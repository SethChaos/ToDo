TORTOISE_ORM = {
    "connections": {
        "default": "mysql://admin:admin@localhost:3306/todo"
    },
    "apps": {
        "models": {
            "models": ["models", "aerich.models"],
            "default_connection": "default",
        },
    },
}