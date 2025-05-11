import json

def callback_url(ch, method, properties, body):
    message = json.loads(body)
    
    print("== Received Full Message ==")
    print(json.dumps(message, indent=4)) 
    
    # xử lý file tại đây...
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(f"✅ File with ID {message.get('Id')} processed and acknowledged.")
