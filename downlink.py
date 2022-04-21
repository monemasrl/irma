import os
import sys
import base64
import grpc
from chirpstack_api.as_pb.external import api

# Configuration.

# This must point to the API interface.
server = "localhost:8080"

# The DevEUI for which you want to enqueue the downlink.
dev_eui = bytes([0x22, 0x32, 0x33, 0x00, 0x00, 0x88, 0x88, 0x02])

# The API token (retrieved using the web-interface).
api_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcGlfa2V5X2lkIjoiNWRkOThjZmYtYjJlOS00YTI5LTgwOWYtNmM4MjJjYjc1MDgwIiwiYXVkIjoiYXMiLCJpc3MiOiJhcyIsIm5iZiI6MTY1MDUzODA2Niwic3ViIjoiYXBpX2tleSJ9.2Qdm4GgZloFFFXiJvM55bAzNCWopHCrn2nLBgSNJ9qY"

if __name__ == "__main__":
  # Connect without using TLS.
  channel = grpc.insecure_channel(server)

  # Device-queue API client.
  client = api.DeviceQueueServiceStub(channel)

  # Define the API key meta-data.
  auth_token = [("authorization", "Bearer %s" % api_token)]
  msg= bytes("Start", 'utf-8')

  # Construct request.
  req = api.EnqueueDeviceQueueItemRequest()
  req.device_queue_item.confirmed = False
  req.device_queue_item.data = base64.b16encode(msg)
  req.device_queue_item.dev_eui = dev_eui.hex()
  req.device_queue_item.f_port = 10

  resp = client.Enqueue(req, metadata=auth_token)

  # Print the downlink frame-counter value.
  print(resp.f_cnt)