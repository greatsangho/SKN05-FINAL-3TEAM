# from functools import lru_cache
# from pydantic_settings import BaseSettings, SettingsConfigDict

# class Settings(BaseSettings):
#     model_config = SettingsConfigDict(
#         env_file=".env",
#         env_file_encoding="utf-8",
#     )

#     database_username: str
#     database_password: str
#     google_client_id: str
#     google_client_secret: str

# @lru_cache
# def get_settings():
#     return Settings()