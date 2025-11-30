from app.data.dto.sample_dto import SampleDTO

class SampleMapper:
    @staticmethod
    def to_minimal_dict(sample: SampleDTO):
        return {
            "id": sample.id,
            "filename": sample.filename,
            "status": sample.status,
            "public_url": sample.public_url,
        }
