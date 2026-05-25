import asyncio
from app.database import async_session
from sqlalchemy import delete
from app.models.upload import UploadLog
from app.models.face import FaceEmbedding, PersonCluster
from app.services import vector_store as vs_mod
from app.config import settings

async def clear():
    async with async_session() as session:
        # Clear database tables
        await session.execute(delete(FaceEmbedding))
        await session.execute(delete(PersonCluster))
        await session.execute(delete(UploadLog))
        await session.commit()
    print("Cleared FaceEmbedding, PersonCluster, and UploadLog database tables!")

    # Reset Qdrant collection
    try:
        vs = vs_mod.VectorStore(settings.QDRANT_STORAGE_PATH)
        vs.client.delete_collection("face_embeddings")
        vs._ensure_collection()
        print("Reset and recreated Qdrant 'face_embeddings' collection!")
    except Exception as e:
        print(f"Failed to reset Qdrant collection: {e}")

if __name__ == "__main__":
    asyncio.run(clear())
