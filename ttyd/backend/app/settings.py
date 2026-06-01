import os
from pydantic_settings import BaseSettings, SettingsConfigDict

AWS_ENABLED: bool = os.getenv("AWS_ENABLED", "false").lower() == "true"
LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "mock")


class AppSettings(BaseSettings):
    aws_region: str = "us-east-1"
    bedrock_model: str = "amazon.titan-embed-text-v1"
    app_env: str = "dev"
    env_file: str = ".env.local"

    model_config = SettingsConfigDict(
        env_file=".env.local",
        extra="allow",
    )


app_settings = AppSettings()

print(f"⚙️ Loading environment: {app_settings.app_env}")
print(f"📄 ENV file: {app_settings.env_file}")

if app_settings.app_env == "dev":
    os.environ["AWS_PROFILE"] = "dev"

if app_settings.app_env == "local":
    os.environ["AWS_PROFILE"] = "local"

if app_settings.app_env == "prod":
    os.environ["AWS_PROFILE"] = "prod"


class Settings(BaseSettings):
    app_env: str = app_settings.app_env
    aws_region: str = app_settings.aws_region
    bedrock_model: str = app_settings.bedrock_model

    model_config = SettingsConfigDict(
        env_file=app_settings.env_file,
        extra="allow",
    )


settings = Settings()


def new_func(settings):
    print(f"📄 ENV file: {settings.env_file}")


if __name__ == "__main__":
    print(settings)

    new_func(settings)
