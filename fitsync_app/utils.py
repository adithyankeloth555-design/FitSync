import threading
import time
import logging

logger = logging.getLogger(__name__)

def send_whatsapp_async(phone_number, message_body):
    """
    Simulates sending a WhatsApp or SMS message.
    Since we don't have a real API key (Twilio/Interakt/Whitesms),
    this simulates the delay and logs the transmission.
    """
    def _send():
        # Simulate network latency
        time.sleep(1.5)
        
        print("\n" + "="*50)
        print(f"📲 WHATSAPP/SMS SENT SUCCESSFULLY")
        print(f"Recipient: {phone_number}")
        print("-" * 50)
        print(f"{message_body}")
        print("="*50 + "\n")
        
        logger.info(f"WhatsApp message sent to {phone_number}")

    thread = threading.Thread(target=_send, daemon=True)
    thread.start()
