from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str

    class Config:
        env_file = ".env"

settings = Settings()
print("Database URL:", settings.database_url)
print("Secret Key:", settings.secret_key)
