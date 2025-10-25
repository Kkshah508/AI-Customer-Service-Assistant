import asyncio
import logging
import os
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def download_models():
    logger.info("="*60)
    logger.info("LiveKit Model Downloader")
    logger.info("="*60)
    
    models_dir = Path("livekit_models")
    models_dir.mkdir(exist_ok=True)
    
    logger.info("Downloading required models for LiveKit agent...")
    logger.info("This may take several minutes (~200MB download)")
    logger.info("")
    
    try:
        logger.info("1/3 Downloading Silero VAD models...")
        from livekit.plugins import silero
        vad = silero.VAD.load()
        logger.info("✓ Silero VAD models downloaded")
        
    except Exception as e:
        logger.error(f"Failed to download Silero VAD: {e}")
        logger.error("Please run: pip install livekit-plugins-silero")
    
    try:
        logger.info("2/3 Downloading Turn Detection models...")
        from livekit.plugins.turn_detector.multilingual import MultilingualModel
        turn_model = MultilingualModel()
        logger.info("✓ Turn Detection models downloaded")
        
    except Exception as e:
        logger.error(f"Failed to download Turn Detection models: {e}")
        logger.error("Please run: pip install livekit-agents[turn-detector]")
    
    try:
        logger.info("3/3 Downloading Noise Cancellation models...")
        from livekit.plugins import noise_cancellation
        logger.info("✓ Noise Cancellation models ready")
        
    except Exception as e:
        logger.error(f"Failed to load Noise Cancellation: {e}")
        logger.error("Please run: pip install livekit-plugins-noise-cancellation")
    
    logger.info("")
    logger.info("="*60)
    logger.info("Model download complete!")
    logger.info("You can now run the LiveKit agent with:")
    logger.info("  python livekit_agent.py console    (test in terminal)")
    logger.info("  python livekit_agent.py dev        (connect to LiveKit Cloud)")
    logger.info("="*60)


if __name__ == "__main__":
    asyncio.run(download_models())
