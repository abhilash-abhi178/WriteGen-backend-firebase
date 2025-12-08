# Dependency Injection for Repositories
from app.data.repository.user_repository import UserRepository
from app.data.repository.sample_repository import SampleRepository
from app.data.repository.style_repository import StyleRepository
from app.data.repository.generation_repository import GenerationRepository

user_repository = UserRepository()
sample_repository = SampleRepository()
style_repository = StyleRepository()
generation_repository = GenerationRepository()
