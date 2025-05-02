import speedtest
from utils.log import logger


async def run_speed_test(query: str) -> str | None:    
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = st.download() / 1_000_000  # Mbps
        upload_speed = st.upload() / 1_000_000      # Mbps
        ping = st.results.ping

        speedtest_results = f"""User: {query}
        Internet Speed Test Results:
        - Download Speed: {download_speed:.2f} Mbps
        - Upload Speed: {upload_speed:.2f} Mbps
        - Ping: {ping:.2f} ms
        """
        logger.info(speedtest_results.strip())
        return speedtest_results.strip()

    except Exception as e:
        logger.error(f"Speedtest failed: {e}")
        return "Internet speed test failed."
