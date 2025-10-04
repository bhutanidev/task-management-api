from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str = "development"  # Options: development, staging, production
    
    # Database URL (will be set as a secret)
    DATABASE_URL: Optional[str] = None  # Made optional since we'll construct it from params

    # Database settings
    DB_USER: str = "postgres"
    DB_PASSWORD: str
    DB_NAME: str = "postgres"
    DB_HOST: str = "127.0.0.1"
    DB_PORT: str = "5432"
    
    # Auth settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 129600  # 90 days
    SECRET_KEY: str

    def get_database_url(self, async_driver: bool = True) -> str:
        """
        Construct database URL from individual parameters
        Args:
            async_driver: If True, uses asyncpg driver, otherwise uses sync driver
        """
            
        driver = "postgresql+asyncpg" if async_driver else "postgresql"
        base_url = f"{driver}://" + "{user}:{password}@{host}:{port}/{db}"
        
        # Local or other connection
        return base_url.format(
            user=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            db=self.DB_NAME
        )

    class Config:
        env_file = ".env"

settings = Settings()